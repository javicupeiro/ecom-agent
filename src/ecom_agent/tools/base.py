"""A polymorphic tool: `definition()` (what the model sees) + `execute()` (what
the harness runs). The model only knows the tool exists; the harness runs it.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ecom_agent.domain.types import ToolDef


@dataclass
class ToolResult:
    content: str
    is_error: bool = False


class Tool(ABC):
    name: str = ""
    requires_permission: bool = False

    @abstractmethod
    def definition(self) -> ToolDef: ...

    @abstractmethod
    def execute(self, tool_input: dict, ctx) -> ToolResult: ...