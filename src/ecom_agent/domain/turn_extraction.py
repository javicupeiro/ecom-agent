"""Structured metadata extracted from a single customer message."""

from __future__ import annotations

from pydantic import BaseModel, field_validator


class TurnExtraction(BaseModel):
    """Structured metadata inferred from a single customer message."""

    order_number: str | None = None
    problem_category: str | None = None
    problem_description: str | None = None
    frustration: float = 0.0
    urgency_level: str | None = None

    @field_validator("order_number")
    @classmethod
    def _normalize_order_number(cls, value: str | None) -> str | None:
        """Normalize the extracted order number."""

        if value is None:
            return None
        normalized = value.strip().upper()
        return normalized or None

    @field_validator("problem_category", "problem_description", "urgency_level")
    @classmethod
    def _normalize_text(cls, value: str | None) -> str | None:
        """Strip extracted text fields and convert blanks to None."""

        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @field_validator("frustration")
    @classmethod
    def _clamp_frustration(cls, value: float) -> float:
        """Clamp the frustration score to the supported range."""

        return max(0.0, min(1.0, float(value)))

    def merged(self, update: "TurnExtraction") -> "TurnExtraction":
        """Combine this extraction with a later turn-level update."""

        return TurnExtraction(
            order_number=update.order_number or self.order_number,
            problem_category=update.problem_category or self.problem_category,
            problem_description=update.problem_description or self.problem_description,
            frustration=max(self.frustration, update.frustration),
            urgency_level=self._merge_urgency(update.urgency_level),
        )

    def _merge_urgency(self, next_urgency: str | None) -> str | None:
        """Keep the highest known urgency across the conversation."""

        current = self.urgency_level
        if next_urgency is None:
            return current
        if current is None:
            return next_urgency

        rank = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        current_rank = rank.get(current)
        next_rank = rank.get(next_urgency)
        if current_rank is None or next_rank is None:
            return next_urgency
        return next_urgency if next_rank >= current_rank else current
