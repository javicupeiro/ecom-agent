"""OpenAI adapter that translates between SDK payloads and core types."""

from __future__ import annotations

import os
import json

from ecom_agent.domain.types import Message, Response, Usage, TextBlock, ToolUseBlock, ToolResultBlock, ToolDef
from ecom_agent.providers.base import LLMProvider


class OpenAIProvider(LLMProvider):
    """Wrap the OpenAI chat completions API behind the provider interface."""

    def __init__(
        self,
        model: str = "gpt-4.1-mini",
        api_key: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.1,
        top_p: float | None = None,
    ):
        """Create a configured OpenAI client."""

        from openai import OpenAI

        self._client = OpenAI(api_key=api_key or os.environ["OPENAI_API_KEY"])
        self._model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p

    def send(self, messages, tools):
        """Send a normalized conversation and return a normalized response."""

        kwargs: dict = {
            "model": self._model,
            "messages": self._to_openai(messages),
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        if tools:
            kwargs["tools"] = [
                {"type": "function",
                 "function": {"name": t.name, "description": t.description,
                              "parameters": t.input_schema or {"type": "object", "properties": {}}}}
                for t in tools
            ]
        return self._from_openai(self._client.chat.completions.create(**kwargs))
    
    def _to_openai(self, messages):
        """Convert internal message blocks into OpenAI chat payloads."""

        out = []
        for m in messages:
            results = [b for b in m.content if isinstance(b, ToolResultBlock)]
            if results:
                # Tool results are sent as synthetic tool-role messages.
                for b in results:
                    out.append({"role": "tool", "tool_call_id": b.tool_use_id, "content": b.content})
                continue
            if m.role == "assistant":
                calls = [
                    {"id": b.id, "type": "function",
                     "function": {"name": b.name, "arguments": json.dumps(b.input)}}
                    for b in m.content if isinstance(b, ToolUseBlock)
                ]
                msg = {"role": "assistant", "content": m.text() or None}
                if calls:
                    msg["tool_calls"] = calls
                out.append(msg)
            else:
                out.append({"role": m.role, "content": m.text()})
        return out
    
    def _from_openai(self, completion):
        """Map the OpenAI completion back to core response blocks."""

        choice = completion.choices[0]
        blocks = []
        if choice.message.content:
            blocks.append(TextBlock(text=choice.message.content))
        for tc in choice.message.tool_calls or []:
            blocks.append(ToolUseBlock(id=tc.id, name=tc.function.name,
                                       input=json.loads(tc.function.arguments or "{}")))
        stop = "tool_use" if choice.finish_reason == "tool_calls" else "end_turn"
        u = completion.usage
        return Response(blocks=blocks, stop_reason=stop,
                        usage=Usage(input_tokens=getattr(u, "prompt_tokens", 0),
                                    output_tokens=getattr(u, "completion_tokens", 0)),
                        model=self._model)

    @property
    def model(self) -> str:
        """Return the configured model name."""

        return self._model

    def set_model(self, name: str) -> None:
        """Switch to a different model for subsequent requests."""

        self._model = name