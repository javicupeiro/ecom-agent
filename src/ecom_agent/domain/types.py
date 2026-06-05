"""Generic, provider-agnostic conversation types (anti-corruption layer).

The core only speaks these types. Each provider adapter translates its SDK's
wire format to/from these models, so swapping models never ripples outward.
These are OUR types, not any SDK's — that is what makes the seam real.
"""

from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field

class TextBlock(BaseModel):
    type: Literal["text"] = "text"
    text: str


class ToolUseBlock(BaseModel):
    type: Literal["tool_use"] = "tool_use"
    id: str
    name: str
    input: dict = Field(default_factory=dict)


class ToolResultBlock(BaseModel):
    type: Literal["tool_result"] = "tool_result"
    tool_use_id: str
    content: str
    is_error: bool = False


Block = Annotated[
    Union[TextBlock, ToolUseBlock, ToolResultBlock], Field(discriminator="type")
]


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: list[Block]

    @classmethod
    def system(cls, text: str) -> "Message":
        return cls(role="system", content=[TextBlock(text=text)])

    @classmethod
    def user(cls, text: str) -> "Message":
        return cls(role="user", content=[TextBlock(text=text)])

    @classmethod
    def assistant(cls, text: str) -> "Message":
        return cls(role="assistant", content=[TextBlock(text=text)])

    def text(self) -> str:
        return "".join(b.text for b in self.content if isinstance(b, TextBlock))


class ToolDef(BaseModel):
    name: str
    description: str
    input_schema: dict = Field(default_factory=dict)


StopReason = Literal["end_turn", "tool_use", "max_tokens"]

class Usage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0

    def __add__(self, other: "Usage") -> "Usage":
        return Usage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
        )

class Response(BaseModel):
    blocks: list[Block]
    stop_reason: StopReason = "end_turn"
    usage: Usage = Field(default_factory=Usage)
    model: str = ""

    def tool_uses(self) -> list[ToolUseBlock]:
        return [b for b in self.blocks if isinstance(b, ToolUseBlock)]

    def text(self) -> str:
        return "".join(b.text for b in self.blocks if isinstance(b, TextBlock))