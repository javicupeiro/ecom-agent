"""Generic, provider-agnostic conversation types (anti-corruption layer).

The core only speaks these types. Each provider adapter translates its SDK's
wire format to/from these models, so swapping models never ripples outward.
These are OUR types, not any SDK's — that is what makes the seam real.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Role = Literal["system", "user", "assistant"]


class Message(BaseModel):
    role: Role
    content: str

    @classmethod
    def system(cls, text: str) -> "Message":
        return cls(role="system", content=text)

    @classmethod
    def user(cls, text: str) -> "Message":
        return cls(role="user", content=text)

    @classmethod
    def assistant(cls, text: str) -> "Message":
        return cls(role="assistant", content=text)


class Usage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0

    def __add__(self, other: "Usage") -> "Usage":
        return Usage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
        )


class Response(BaseModel):
    text: str = ""
    usage: Usage = Field(default_factory=Usage)
    model: str = ""