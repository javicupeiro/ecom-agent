"""Deterministic provider for tests: exercises the system with no API calls."""

from __future__ import annotations

from collections.abc import Sequence

from ecom_agent.domain.types import Message, Response, TextBlock, Usage
from ecom_agent.providers.base import LLMProvider


class MockProvider(LLMProvider):
    def __init__(self, script: Sequence[Response] | None = None, model: str = "mock-1") -> None:
        self._script = list(script or [])
        self._model = model

    def send(self, messages, tools) -> Response:
        if self._script:
            return self._script.pop(0)
        return Response(blocks=[TextBlock(text="(mock)")], usage=Usage(input_tokens=1, output_tokens=1))

    @property
    def model(self) -> str:
        return self._model

    def set_model(self, name: str) -> None:
        self._model = name