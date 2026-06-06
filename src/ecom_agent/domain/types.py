"""Provider-agnostic message and tool types used by the core agent."""

from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field

class TextBlock(BaseModel):
    """Plain text emitted by a participant."""

    type: Literal["text"] = "text"
    text: str


class ToolUseBlock(BaseModel):
    """Tool call requested by the model."""

    type: Literal["tool_use"] = "tool_use"
    id: str
    name: str
    input: dict = Field(default_factory=dict)


class ToolResultBlock(BaseModel):
    """Result returned to the model after a tool call."""

    type: Literal["tool_result"] = "tool_result"
    tool_use_id: str
    content: str
    is_error: bool = False


Block = Annotated[
    Union[TextBlock, ToolUseBlock, ToolResultBlock], Field(discriminator="type")
]


class Message(BaseModel):
    """Conversation message composed of typed content blocks."""

    role: Literal["system", "user", "assistant"]
    content: list[Block]

    @classmethod
    def system(cls, text: str) -> "Message":
        """Build a system message from plain text."""

        return cls(role="system", content=[TextBlock(text=text)])

    @classmethod
    def user(cls, text: str) -> "Message":
        """Build a user message from plain text."""

        return cls(role="user", content=[TextBlock(text=text)])

    @classmethod
    def assistant(cls, text: str) -> "Message":
        """Build an assistant message from plain text."""

        return cls(role="assistant", content=[TextBlock(text=text)])

    def text(self) -> str:
        """Concatenate all text blocks in the message."""

        return "".join(b.text for b in self.content if isinstance(b, TextBlock))


class ToolDef(BaseModel):
    """Tool schema exposed to the model."""

    name: str
    description: str
    input_schema: dict = Field(default_factory=dict)


StopReason = Literal["end_turn", "tool_use", "max_tokens"]

class Usage(BaseModel):
    """Token usage for one provider call or a sum of calls."""

    input_tokens: int = 0
    output_tokens: int = 0

    def __add__(self, other: "Usage") -> "Usage":
        """Combine two usage counters."""

        return Usage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
        )

class Response(BaseModel):
    """Normalized provider response."""

    blocks: list[Block]
    stop_reason: StopReason = "end_turn"
    usage: Usage = Field(default_factory=Usage)
    model: str = ""

    def tool_uses(self) -> list[ToolUseBlock]:
        """Return only tool call blocks."""

        return [b for b in self.blocks if isinstance(b, ToolUseBlock)]

    def text(self) -> str:
        """Concatenate visible text emitted by the provider."""

        return "".join(b.text for b in self.blocks if isinstance(b, TextBlock))