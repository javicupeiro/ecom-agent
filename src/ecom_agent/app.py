from __future__ import annotations

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

SYSTEM_PROMPT = (
    "You are a helpful assistant for SaborMix, a kitchen robot brand. "
    "Always reply in the customer's language."
)

_sessions: dict[str, Conversation] = {}


@app.get("/")
def index() -> FileResponse:
    return FileResponse("ui/index.html")

class ChatIn(BaseModel):
    session_id: str = "default"
    message: str
    lang: str | None = None

def _conversation(session_id: str, lang: str) -> Conversation:
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

@app.post("/chat")
def chat(body: ChatIn) -> dict:
    conv = _conversation(body.session_id, body.lang or settings.agent.default_language)
    result = conv.send(body.message)
    return {
        "reply": result.reply,
        "trace": {
            "provider_calls": result.trace.provider_calls,
            "tools_used": result.trace.tools_used,
            "usage": result.trace.usage.model_dump(),
            "steps": result.trace.steps,
        },
    }

@app.post("/summary")
def summary(session_id: str = "default") -> dict:
    conv = _sessions.get(session_id)
    if conv is None:
        return {"summary": "", "session_id": session_id}
    return conv.summarize()

