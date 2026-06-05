"""Tool registry. Each tool self-registers via @tool when its module is imported.
`dispatch` applies permissions and never lets a tool crash the loop.
"""

from __future__ import annotations

from ecom_agent.domain.types import ToolDef
from ecom_agent.permissions import PermissionPolicy
from ecom_agent.tools.base import Tool, ToolResult


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool_cls: type[Tool]) -> type[Tool]:
        instance = tool_cls()
        self._tools[instance.name] = instance
        return tool_cls

    def definitions(self) -> list[ToolDef]:
        return [t.definition() for t in self._tools.values()]

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def dispatch(self, name: str, tool_input: dict, ctx, policy: PermissionPolicy) -> ToolResult:
        tool = self.get(name)
        if tool is None:
            return ToolResult(f"Unknown tool: {name}", is_error=True)
        if tool.requires_permission and not policy.allows(name, tool_input):
            return ToolResult(f"Action '{name}' was not authorized.", is_error=True)
        try:
            return tool.execute(tool_input, ctx)
        except Exception as exc:  # noqa: BLE001 - a tool must never crash the loop
            return ToolResult(f"Error running '{name}': {exc}", is_error=True)


default_registry = ToolRegistry()


def tool(cls: type[Tool]) -> type[Tool]:
    """Register the tool in the default registry."""
    return default_registry.register(cls)