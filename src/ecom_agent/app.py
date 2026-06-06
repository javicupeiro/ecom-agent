"""FastAPI entrypoint for the e-commerce support agent."""

from __future__ import annotations

import base64
from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ecom_agent.config import get_settings
from ecom_agent.db.orders import OrdersDB
from ecom_agent.providers.factory import build_provider
from ecom_agent.orchestrator import Conversation
from ecom_agent.rag.index import KnowledgeBase
from ecom_agent.permissions import AllowList
from ecom_agent.memory.store import JSONFileStore
from ecom_agent.compaction.factory import build_compactor
from ecom_agent.stt import OpenAITranscriptionService, TranscriptionError
from ecom_agent.voice import ElevenLabsVoiceService, VoiceSynthesisError

app = FastAPI(title="SaborMix Agent")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)
app.mount("/static", StaticFiles(directory="ui"), name="static")

settings = get_settings()
provider = build_provider(settings)
db = OrdersDB(settings.db.path)
kb = KnowledgeBase(
    settings.rag.persist_dir, settings.rag.collection, settings.openai_api_key,
    settings.rag.embedding_model, settings.rag.top_k,
)
store = JSONFileStore()
compactor = build_compactor(settings, provider)
voice_service = ElevenLabsVoiceService(provider, settings)
stt_service = OpenAITranscriptionService(settings)

_sessions: dict[str, Conversation] = {}


@app.get("/")
def index() -> FileResponse:
    """Serve the single-page UI."""
    return FileResponse("ui/index.html")

class ChatIn(BaseModel):
    """Incoming chat payload from the web UI."""

    session_id: str = "default"
    message: str
    lang: str | None = None
    response_mode: Literal["text", "voice"] = "text"


class AudioChatIn(BaseModel):
    """Incoming audio payload from the web UI."""

    session_id: str = "default"
    audio_base64: str
    mime_type: str = "audio/webm"
    filename: str = "recording.webm"
    lang: str | None = None
    response_mode: Literal["text", "voice"] = "text"

def _conversation(session_id: str, lang: str) -> Conversation:
    """Return the cached conversation for a session-language pair."""

    conv = _sessions.get(session_id)
    if conv is None or conv.lang != lang:
        conv = Conversation(
            provider, db=db, kb=kb, lang=lang, store=store, session_id=session_id,
            policy=AllowList(["query_orders", "search_knowledge_base"]),
            compactor=compactor,
            max_steps=settings.agent.max_steps,
        )
        _sessions[session_id] = conv
    return conv


def _build_output(reply: str, *, lang: str, response_mode: str) -> dict:
    """Build the UI output payload for text or voice responses."""

    output = {
        "mode": "text",
        "text": reply,
    }
    if response_mode == "voice":
        try:
            clip = voice_service.render(reply, lang=lang)
            output = {
                "mode": "voice",
                "text": reply,
                "voice_script": clip.script,
                "audio_base64": clip.audio_base64,
                "mime_type": clip.mime_type,
                "voice_id": clip.voice_id,
                "voice_label": clip.voice_label,
            }
        except VoiceSynthesisError as exc:
            output["voice_error"] = str(exc)
    return output


def _run_turn(
    *,
    session_id: str,
    message: str,
    lang: str | None,
    response_mode: str,
    input_mode: str = "text",
    transcript: str | None = None,
) -> dict:
    """Run one customer turn and return the normalized UI payload."""

    resolved_lang = lang or settings.agent.default_language
    conv = _conversation(session_id, resolved_lang)
    result = conv.send(message)
    return {
        "reply": result.reply,
        "input_mode": input_mode,
        "input_text": transcript or message,
        "output": _build_output(result.reply, lang=conv.lang, response_mode=response_mode),
        "model": result.trace.calls[-1]["model"] if result.trace.calls else "",
        "trace": {
            "provider_calls": result.trace.provider_calls,
            "tools_used": result.trace.tools_used,
            "usage": result.trace.usage.model_dump(),
            "calls": result.trace.calls,
            "steps": result.trace.steps,
            "extraction": result.trace.extraction.model_dump(),
        },
    }

@app.post("/chat")
def chat(body: ChatIn) -> dict:
    """Process one user turn and return the assistant reply plus debug data."""

    return _run_turn(
        session_id=body.session_id,
        message=body.message,
        lang=body.lang,
        response_mode=body.response_mode,
    )


@app.post("/chat/audio")
def chat_audio(body: AudioChatIn) -> dict:
    """Transcribe one audio turn and process it like a normal chat message."""

    audio_bytes = base64.b64decode(body.audio_base64.encode("ascii"), validate=True)
    transcript = stt_service.transcribe(
        audio_bytes,
        mime_type=body.mime_type,
        filename=body.filename,
        lang=body.lang,
    )
    return _run_turn(
        session_id=body.session_id,
        message=transcript.text,
        lang=body.lang,
        response_mode=body.response_mode,
        input_mode="audio",
        transcript=transcript.text,
    )

@app.post("/summary")
def summary(session_id: str = "default") -> dict:
    """Return a conversation summary for the requested session."""

    conv = _sessions.get(session_id)
    if conv is None:
        return {"summary": "", "session_id": session_id}
    return conv.summarize()

