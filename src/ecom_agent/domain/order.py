"""Structured, validated input for the order write tool."""

from __future__ import annotations

import re
from typing import Optional

from pydantic import BaseModel, field_validator

ORDER_RE = re.compile(r"^ORD-\d{6}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STATUSES = {"processing", "shipped", "delivered", "cancelled"}


class OrderInput(BaseModel):
    order_id: str
    customer_name: Optional[str] = None
    customer_surname: Optional[str] = None
    product: Optional[str] = None
    address: Optional[str] = None
    purchase_date: Optional[str] = None
    ship_date: Optional[str] = None
    status: Optional[str] = None

    @field_validator("order_id")
    @classmethod
    def _check_id(cls, v: str) -> str:
        v = v.strip().upper()
        if not ORDER_RE.match(v):
            raise ValueError("order_id must look like ORD-123456")
        return v

    @field_validator("purchase_date", "ship_date")
    @classmethod
    def _check_date(cls, v: Optional[str]) -> Optional[str]:
        if v and not DATE_RE.match(v):
            raise ValueError("dates must be YYYY-MM-DD")
        return v

    @field_validator("status")
    @classmethod
    def _check_status(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in STATUSES:
            raise ValueError(f"status must be one of {sorted(STATUSES)}")
        return v