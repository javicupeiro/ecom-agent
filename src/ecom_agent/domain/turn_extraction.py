"""Structured metadata extracted from a single customer message."""

from __future__ import annotations

from pydantic import BaseModel, field_validator


class TurnExtraction(BaseModel):
    order_number: str | None = None
    problem_category: str | None = None
    problem_description: str | None = None
    frustration: float = 0.0
    urgency_level: str | None = None

    @field_validator("order_number")
    @classmethod
    def _normalize_order_number(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().upper()
        return normalized or None

    @field_validator("problem_category", "problem_description", "urgency_level")
    @classmethod
    def _normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @field_validator("frustration")
    @classmethod
    def _clamp_frustration(cls, value: float) -> float:
        return max(0.0, min(1.0, float(value)))
