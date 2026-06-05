"""LLM provider port. The rest of the system only talks to models through this."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ecom_agent.domain.types import Message, Response


class LLMProvider(ABC):
    @abstractmethod
    def send(self, messages: list[Message]) -> Response:
        """Send the conversation context and return a generic response."""

    @property
    @abstractmethod
    def model(self) -> str: ...

    @abstractmethod
    def set_model(self, name: str) -> None:
        """Swap the model at runtime without rebuilding the provider."""