from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ecom_agent.config import get_settings
from ecom_agent.domain.types import Message
from ecom_agent.providers.factory import build_provider

app = FastAPI(title="SaborMix Agent")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

settings = get_settings()
provider = build_provider(settings)

SYSTEM_PROMPT = (
    "You are a helpful assistant for SaborMix, a kitchen robot brand. "
    "Always reply in the customer's language."
)


class ChatIn(BaseModel):
    message: str


@app.post("/chat")
def chat(body: ChatIn) -> dict:
    messages = [Message.system(SYSTEM_PROMPT), Message.user(body.message)]
    return {"reply": provider.send(messages).text}