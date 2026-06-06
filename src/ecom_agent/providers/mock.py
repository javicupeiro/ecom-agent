"""Deterministic provider for tests: exercises the system with no API calls."""

from __future__ import annotations

from collections.abc import Sequence

from ecom_agent.domain.types import Message, Response, TextBlock, Usage
from ecom_agent.providers.base import LLMProvider


class MockProvider(LLMProvider):
    """Deterministic provider used by tests and local smoke checks."""

    def __init__(self, script: Sequence[Response] | None = None, model: str = "mock-1") -> None:
        """Optionally preload a sequence of canned responses."""

        self._script = list(script or [])
        self._model = model

    def send(self, messages, tools) -> Response:
        """Return the next scripted response or a trivial default reply."""

        if self._script:
            return self._script.pop(0)
        return Response(blocks=[TextBlock(text="(mock)")], usage=Usage(input_tokens=1, output_tokens=1))

    @property
    def model(self) -> str:
        """Return the active mock model name."""

        return self._model

    def set_model(self, name: str) -> None:
        """Update the advertised model name."""

        self._model = name