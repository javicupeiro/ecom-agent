
"""History compaction. `safe_split_point` avoids cutting between a tool_use and
its tool_result (the API would return a 400). `Summarize` doubles as the recap.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ecom_agent.domain.types import Message, ToolResultBlock, ToolUseBlock
from ecom_agent.providers.base import LLMProvider


def _has(msg: Message, block_type) -> bool:
    return any(isinstance(b, block_type) for b in msg.content)


def safe_split_point(messages: list[Message], k: int) -> int:
    k = max(0, min(k, len(messages)))
    while 0 < k < len(messages) and (
        _has(messages[k], ToolResultBlock) or _has(messages[k - 1], ToolUseBlock)
    ):
        k -= 1
    return k


class CompactionStrategy(ABC):
    @abstractmethod
    def compact(self, messages: list[Message]) -> list[Message]: ...


class NoCompaction(CompactionStrategy):
    def compact(self, messages: list[Message]) -> list[Message]:
        return messages


class SlidingWindow(CompactionStrategy):
    def __init__(self, keep_last: int = 10) -> None:
        self.keep_last = keep_last

    def compact(self, messages: list[Message]) -> list[Message]:
        system = [m for m in messages if m.role == "system"]
        body = [m for m in messages if m.role != "system"]
        if len(body) <= self.keep_last:
            return messages
        k = safe_split_point(body, len(body) - self.keep_last)
        return system + body[k:]


class Summarize(CompactionStrategy):
    def __init__(self, 
                 provider: LLMProvider, 
                 threshold: int = 20, 
                 keep_recent: int = 6) -> None:
        self.provider = provider
        self.threshold = threshold
        self.keep_recent = keep_recent

    def compact(self, messages: list[Message]) -> list[Message]:
        system = [m for m in messages if m.role == "system"]
        body = [m for m in messages if m.role != "system"]
        if len(body) <= self.threshold:
            return messages
        k = safe_split_point(body, len(body) - self.keep_recent)
        older, recent = body[:k], body[k:]
        transcript = "\n".join(f"{m.role}: {m.text()}" for m in older if m.text())
        prompt = [
            Message.system("Summarize the conversation concisely, keeping extracted data."),
            Message.user(transcript),
        ]
        summary = Message.system("Summary so far:\n" + self.provider.send(prompt, []).text())
        return system + [summary] + recent