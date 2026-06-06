"""Record a fact/preference into the agent's persistent memory."""

from __future__ import annotations

from ecom_agent.domain.types import ToolDef
from ecom_agent.tools.base import Tool, ToolResult
from ecom_agent.tools.registry import tool


@tool
class RememberTool(Tool):
    """Persist a fact or preference for later recall."""

    name = "remember"
    requires_permission = False

    def definition(self) -> ToolDef:
        """Describe the memory write tool to the model."""

        return ToolDef(
            name=self.name,
            description=(
                "Save a fact, decision or preference so it carries across sessions. Use "
                "sparingly for things the customer genuinely wants persisted."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["content"],
            },
        )

    def execute(self, tool_input: dict, ctx) -> ToolResult:
        """Validate and store one memory record."""

        content = (tool_input.get("content") or "").strip()
        if not content:
            return ToolResult("remember: 'content' is required", is_error=True)
        ctx.store.save(ctx.session_id, {"content": content, "tags": tool_input.get("tags", [])})
        return ToolResult("remembered.")