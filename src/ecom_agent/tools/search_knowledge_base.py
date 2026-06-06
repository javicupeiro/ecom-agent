"""Retrieve relevant passages from the SaborMix knowledge base (RAG)."""

from __future__ import annotations

from ecom_agent.domain.types import ToolDef
from ecom_agent.tools.base import Tool, ToolResult
from ecom_agent.tools.registry import tool


@tool
class SearchKnowledgeBaseTool(Tool):
    """Retrieve passages from the localized knowledge base."""

    name = "search_knowledge_base"
    requires_permission = False

    def definition(self) -> ToolDef:
        """Describe the retrieval tool to the model."""

        return ToolDef(
            name=self.name,
            description=(
                "Search the SaborMix knowledge base to answer the customer. "
                "Use it whenever they ask about a product, a recipe, or how to fix something. "
                "Set 'area' to narrow the search: 'products' for specs/pricing, "
                "'recipes' for cooking instructions, 'support' for troubleshooting."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "area": {
                        "type": "string",
                        "enum": ["products", "recipes", "support"],
                        "description": "Restrict search to this content area. Omit to search all areas.",
                    },
                },
                "required": ["query"],
            },
        )

    def execute(self, tool_input: dict, ctx) -> ToolResult:
        """Search the knowledge base with the current conversation language."""

        area = tool_input.get("area") or None
        hits = ctx.kb.search(tool_input.get("query", ""), lang=ctx.lang, area=area)
        if not hits:
            return ToolResult("No relevant passages found in the knowledge base.")
        return ToolResult("\n\n".join(f"[{h.title}] {h.text}" for h in hits))