"""Anthropic (Claude) adapter. The only module aware of this SDK's wire format.

Anthropic requires `max_tokens` and takes the system prompt as a top-level
argument (not as a message), so this adapter normalizes both.
"""

from __future__ import annotations

import os

from ecom_agent.domain.types import Message, Response, Usage,TextBlock, ToolUseBlock, ToolResultBlock, ToolDef
from ecom_agent.providers.base import LLMProvider


class AnthropicProvider(LLMProvider):
    """Wrap the Anthropic messages API behind the provider interface."""

    def __init__(
        self,
        model: str = "claude-sonnet-4-6",
        api_key: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.1,
        top_p: float | None = None,
    ):
        """Create a configured Anthropic client."""

        import anthropic

        self._client = anthropic.Anthropic(api_key=api_key or os.environ["ANTHROPIC_API_KEY"])
        self._model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p

    def send(self, messages, tools):
        """Send a normalized conversation and return a normalized response."""

        system = " ".join(m.text() for m in messages if m.role == "system")
        kwargs: dict = {
            "model": self._model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [self._to_api(m) for m in messages if m.role != "system"],
        }
        if system:
            kwargs["system"] = system
        if self.top_p is not None:
            kwargs["top_p"] = self.top_p
        if tools:
            kwargs["tools"] = [
                {"name": t.name, "description": t.description,
                 "input_schema": t.input_schema or {"type": "object", "properties": {}}}
                for t in tools
            ]
        return self._from_api(self._client.messages.create(**kwargs))

    def _to_api(self, m):
        """Convert one internal message into Anthropic content blocks."""

        content = []
        for b in m.content:
            if isinstance(b, TextBlock):
                content.append({"type": "text", "text": b.text})
            elif isinstance(b, ToolUseBlock):
                content.append({"type": "tool_use", "id": b.id, "name": b.name, "input": b.input})
            elif isinstance(b, ToolResultBlock):
                content.append({"type": "tool_result", "tool_use_id": b.tool_use_id,
                                "content": b.content, "is_error": b.is_error})
        return {"role": m.role, "content": content}

    def _from_api(self, raw):
        """Map Anthropic response content into core response blocks."""

        blocks = []
        for b in raw.content:
            if b.type == "text":
                blocks.append(TextBlock(text=b.text))
            elif b.type == "tool_use":
                blocks.append(ToolUseBlock(id=b.id, name=b.name, input=dict(b.input)))
        stop = "tool_use" if raw.stop_reason == "tool_use" else "end_turn"
        return Response(blocks=blocks, stop_reason=stop,
                        usage=Usage(input_tokens=raw.usage.input_tokens,
                                    output_tokens=raw.usage.output_tokens),
                        model=self._model)

    @property
    def model(self) -> str:
        """Return the configured model name."""

        return self._model

    def set_model(self, name: str) -> None:
        """Switch to a different model for subsequent requests."""

        self._model = name