"""Search the SaborMix product catalog."""

from __future__ import annotations

from pathlib import Path

from ecom_agent.domain.types import ToolDef
from ecom_agent.tools.base import Tool, ToolResult
from ecom_agent.tools.registry import tool


@tool
class SearchProductsTool(Tool):
    name = "search_products"
    requires_permission = False

    def definition(self) -> ToolDef:
        return ToolDef(
            name=self.name,
            description=(
                "Search the SaborMix product catalog (models, pricing, shipping, "
                "returns). Use it when the customer asks about products or buying."
            ),
            input_schema={
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        )

    def execute(self, tool_input: dict, ctx) -> ToolResult:
        folder = Path("SaborMix/products") / getattr(ctx, "lang", "es")
        query = set(tool_input.get("query", "").lower().split())
        best: list[tuple[int, str]] = []
        for path in folder.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            score = len(query & set(text.lower().split()))
            if score:
                best.append((score, text))
        best.sort(key=lambda x: x[0], reverse=True)
        if not best:
            return ToolResult("No matches in the product catalog.")
        return ToolResult("\n\n---\n\n".join(t for _, t in best[:2]))