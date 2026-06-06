"""Search the agent's persistent memory from past sessions."""

from __future__ import annotations

from ecom_agent.domain.types import ToolDef
from ecom_agent.tools.base import Tool, ToolResult
from ecom_agent.tools.registry import tool


@tool
class RecallTool(Tool):
    """Retrieve persisted memory entries that match a query."""

    name = "recall"
    requires_permission = False

    def definition(self) -> ToolDef:
        """Describe the memory search tool to the model."""

        return ToolDef(
            name=self.name,
            description=(
                "Search the agent's memory of past sessions for facts/preferences. Recent "
                "context is already in your prompt — use this only for older information."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer"},
                },
                "required": ["query"],
            },
        )

    def execute(self, tool_input: dict, ctx) -> ToolResult:
        """Search memory and return a short textual result list."""

        hits = ctx.store.recall(tool_input.get("query", ""), tool_input.get("limit") or 5)
        if not hits:
            return ToolResult("no matches.")
        return ToolResult("\n".join(f"- {h.get('content', '')}" for h in hits))