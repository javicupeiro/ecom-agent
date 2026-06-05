"""Anthropic (Claude) adapter. The only module aware of this SDK's wire format.

Anthropic requires `max_tokens` and takes the system prompt as a top-level
argument (not as a message), so this adapter normalizes both.
"""

from __future__ import annotations

import os

from ecom_agent.domain.types import Message, Response, Usage
from ecom_agent.providers.base import LLMProvider


class AnthropicProvider(LLMProvider):
    def __init__(
        self,
        model: str = "claude-sonnet-4-6",
        api_key: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.1,
        top_p: float | None = None,
    ):
        import anthropic

        self._client = anthropic.Anthropic(api_key=api_key or os.environ["ANTHROPIC_API_KEY"])
        self._model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p

    def send(self, messages: list[Message]) -> Response:
        system = " ".join(m.content for m in messages if m.role == "system")
        api_messages = [
            {"role": m.role, "content": m.content} for m in messages if m.role != "system"
        ]
        kwargs: dict = {
            "model": self._model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": api_messages,
        }
        if system:
            kwargs["system"] = system
        if self.top_p is not None:
            kwargs["top_p"] = self.top_p

        raw = self._client.messages.create(**kwargs)
        text = "".join(b.text for b in raw.content if b.type == "text")
        return Response(
            text=text,
            usage=Usage(input_tokens=raw.usage.input_tokens, output_tokens=raw.usage.output_tokens),
            model=self._model,
        )

    @property
    def model(self) -> str:
        return self._model

    def set_model(self, name: str) -> None:
        self._model = name