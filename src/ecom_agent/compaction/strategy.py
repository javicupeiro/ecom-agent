
"""History compaction. `safe_split_point` avoids cutting between a tool_use and
its tool_result (the API would return a 400). `Summarize` doubles as the recap.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from ecom_agent.domain.types import Message, ToolResultBlock, ToolUseBlock
from ecom_agent.providers.base import LLMProvider
from ecom_agent.prompt_loader import load_prompt

_PROMPTS_DIR = Path(__file__).parent / "prompts"


def _has(msg: Message, block_type) -> bool:
    """Return True when a message contains at least one block of the given type."""

    return any(isinstance(b, block_type) for b in msg.content)


def safe_split_point(messages: list[Message], k: int) -> int:
    """Move a split point left until it no longer breaks a tool exchange."""

    k = max(0, min(k, len(messages)))
    while 0 < k < len(messages) and (
        _has(messages[k], ToolResultBlock) or _has(messages[k - 1], ToolUseBlock)
    ):
        k -= 1
    return k


class CompactionStrategy(ABC):
    """Contract for history compaction policies."""

    @abstractmethod
    def compact(self, messages: list[Message]) -> list[Message]: ...


class NoCompaction(CompactionStrategy):
    """Keep the full message history unchanged."""

    def compact(self, messages: list[Message]) -> list[Message]:
        """Return the original history."""

        return messages


class SlidingWindow(CompactionStrategy):
    """Keep only the most recent non-system messages."""

    def __init__(self, keep_last: int = 10) -> None:
        """Store the target number of recent messages to preserve."""

        self.keep_last = keep_last

    def compact(self, messages: list[Message]) -> list[Message]:
        """Trim older history while preserving the system prompt."""

        system = [m for m in messages if m.role == "system"]
        body = [m for m in messages if m.role != "system"]
        if len(body) <= self.keep_last:
            return messages
        k = safe_split_point(body, len(body) - self.keep_last)
        return system + body[k:]


class Summarize(CompactionStrategy):
    """Replace older history with a provider-generated summary."""

    def __init__(self, 
                 provider: LLMProvider, 
                 threshold: int = 20, 
                 keep_recent: int = 6) -> None:
        """Store the provider and compaction thresholds."""

        self.provider = provider
        self.threshold = threshold
        self.keep_recent = keep_recent

    def compact(self, messages: list[Message]) -> list[Message]:
        """Summarize older messages once the threshold is exceeded."""

        system = [m for m in messages if m.role == "system"]
        body = [m for m in messages if m.role != "system"]
        if len(body) <= self.threshold:
            return messages
        k = safe_split_point(body, len(body) - self.keep_recent)
        older, recent = body[:k], body[k:]
        # Only plain text is summarized; tool protocol remains in the recent window.
        transcript = "\n".join(f"{m.role}: {m.text()}" for m in older if m.text())
        compact_instr = load_prompt(_PROMPTS_DIR, "summarize_compact")
        prompt = [
            Message.system(compact_instr),
            Message.user(transcript),
        ]
        summary = Message.system("Summary so far:\n" + self.provider.send(prompt, []).text())
        return system + [summary] + recent