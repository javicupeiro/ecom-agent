"""OpenAI (GPT) adapter. The only module aware of this SDK's wire format."""

from __future__ import annotations

import os

from ecom_agent.domain.types import Message, Response, Usage
from ecom_agent.providers.base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(
        self,
        model: str = "gpt-4.1-mini",
        api_key: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.1,
        top_p: float | None = None,
    ):
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key or os.environ["OPENAI_API_KEY"])
        self._model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p

    def send(self, messages: list[Message]) -> Response:
        payload = [{"role": m.role, "content": m.content} for m in messages]
        kwargs: dict = {
            "model": self._model,
            "messages": payload,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,  # some newer models use max_completion_tokens
        }
        if self.top_p is not None:
            kwargs["top_p"] = self.top_p

        completion = self._client.chat.completions.create(**kwargs)
        usage = completion.usage
        return Response(
            text=completion.choices[0].message.content or "",
            usage=Usage(
                input_tokens=getattr(usage, "prompt_tokens", 0),
                output_tokens=getattr(usage, "completion_tokens", 0),
            ),
            model=self._model,
        )

    @property
    def model(self) -> str:
        return self._model

    def set_model(self, name: str) -> None:
        self._model = name