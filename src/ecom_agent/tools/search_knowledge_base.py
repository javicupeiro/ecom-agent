"""Retrieve relevant passages from the SaborMix knowledge base (RAG)."""

from __future__ import annotations

from ecom_agent.domain.types import ToolDef
from ecom_agent.tools.base import Tool, ToolResult
from ecom_agent.tools.registry import tool


@tool
class SearchKnowledgeBaseTool(Tool):
    name = "search_knowledge_base"
    requires_permission = False

    def definition(self) -> ToolDef:
        return ToolDef(
            name=self.name,
            description=(
                "Search the SaborMix knowledge base (products, recipes, troubleshooting) "
                "to answer the customer. Use it whenever they ask about a product, a recipe, "
                "or how to fix something."
            ),
            input_schema={
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        )

    def execute(self, tool_input: dict, ctx) -> ToolResult:
        hits = ctx.kb.search(tool_input.get("query", ""), lang=ctx.lang)
        if not hits:
            return ToolResult("No relevant passages found in the knowledge base.")
        return ToolResult("\n\n".join(f"[{h.title}] {h.text}" for h in hits))