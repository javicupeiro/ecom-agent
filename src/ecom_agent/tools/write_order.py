"""Create or update a customer order. Side-effecting: needs permission."""

from __future__ import annotations

from pydantic import ValidationError

from ecom_agent.domain.order import OrderInput
from ecom_agent.domain.types import ToolDef
from ecom_agent.tools.base import Tool, ToolResult
from ecom_agent.tools.registry import tool


@tool
class WriteOrderTool(Tool):
    """Create or update order records after validation."""

    name = "write_order"
    requires_permission = True

    def definition(self) -> ToolDef:
        """Describe the order mutation tool to the model."""

        return ToolDef(
            name=self.name,
            description=(
                "Create a new order or update an existing one (register a purchase, set the "
                "shipping date or status). Only call after confirming details with the customer."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "customer_name": {"type": "string"},
                    "customer_surname": {"type": "string"},
                    "product": {"type": "string"},
                    "address": {"type": "string"},
                    "purchase_date": {"type": "string"},
                    "ship_date": {"type": "string"},
                    "status": {"type": "string",
                               "enum": ["processing", "shipped", "delivered", "cancelled"]},
                },
                "required": ["order_id"],
            },
        )

    def execute(self, tool_input: dict, ctx) -> ToolResult:
        """Validate the payload and write it to the orders database."""

        try:
            order = OrderInput(**tool_input)
        except ValidationError as exc:
            return ToolResult(f"Invalid order data: {exc.errors()}", is_error=True)
        action = ctx.db.upsert(order.model_dump(exclude_none=True))
        return ToolResult(f"Order {order.order_id} {action}.")