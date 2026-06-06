"""Look up customer orders (read-only)."""

from __future__ import annotations

from ecom_agent.domain.types import ToolDef
from ecom_agent.tools.base import Tool, ToolResult
from ecom_agent.tools.registry import tool


def _format(o: dict) -> str:
    ship = o["ship_date"] or "not shipped yet"
    return (f"{o['order_id']} · {o['customer_name']} {o['customer_surname']} · "
            f"{o['product']} · status={o['status']} · purchased {o['purchase_date']} · "
            f"shipped {ship} · {o['address']}")


@tool
class QueryOrdersTool(Tool):
    name = "query_orders"
    requires_permission = False

    def definition(self) -> ToolDef:
        return ToolDef(
            name=self.name,
            description=(
                "Look up customer orders by order id or by customer surname. Use it to "
                "answer questions about order status, product, and shipping dates."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "Format ORD-123456"},
                    "surname": {"type": "string"},
                },
            },
        )

    def execute(self, tool_input: dict, ctx) -> ToolResult:
        order_id = (tool_input.get("order_id") or "").strip().upper()
        surname = (tool_input.get("surname") or "").strip()
        if order_id:
            order = ctx.db.get(order_id)
            rows = [order] if order else []
        elif surname:
            rows = ctx.db.find_by_surname(surname)
        else:
            return ToolResult("Provide an order_id or a customer surname.", is_error=True)
        if not rows:
            return ToolResult("No matching orders found.")
        return ToolResult("\n".join(_format(o) for o in rows))