from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ecom_agent.config import get_settings
from ecom_agent.domain.types import Message
from ecom_agent.providers.factory import build_provider
from ecom_agent.orchestrator import Conversation

app = FastAPI(title="SaborMix Agent")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)
app.mount("/static", StaticFiles(directory="ui"), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse("ui/index.html")

settings = get_settings()
provider = build_provider(settings)

SYSTEM_PROMPT = (
    "You are a helpful assistant for SaborMix, a kitchen robot brand. "
    "Always reply in the customer's language."
)

_sessions: dict[str, Conversation] = {}

class ChatIn(BaseModel):
    session_id: str = "default"
    message: str
    lang: str | None = None

@app.post("/chat")
def chat(body: ChatIn) -> dict:
    requested_lang = body.lang or settings.agent.default_language
    if body.session_id not in _sessions or _sessions[body.session_id].lang != requested_lang:
        _sessions[body.session_id] = Conversation(
            provider,
            lang=requested_lang,
            max_steps=settings.agent.max_steps,
        )
    result = _sessions[body.session_id].send(body.message)
    return {
        "reply": result.reply,
        "trace": {
            "provider_calls": result.trace.provider_calls,
            "tools_used": result.trace.tools_used,
            "usage": result.trace.usage.model_dump(),
            "steps": result.trace.steps,
        },
    }