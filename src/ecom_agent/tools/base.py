"""Base abstractions for tools exposed to the model."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ecom_agent.domain.types import ToolDef


@dataclass
class ToolResult:
    """Serialized tool output returned to the agent loop."""

    content: str
    is_error: bool = False


class Tool(ABC):
    """Common interface implemented by every tool."""

    name: str = ""
    requires_permission: bool = False

    @abstractmethod
    def definition(self) -> ToolDef: ...

    @abstractmethod
    def execute(self, tool_input: dict, ctx) -> ToolResult: ...