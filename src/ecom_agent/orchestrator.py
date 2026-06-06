"""Outer loop (one REPL 'eval' per user message) + inner agent loop (the model
requests tools until it stops). Returns a DebugTrace per turn — the data the
front debug panel renders.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from ecom_agent.domain.turn_extraction import TurnExtraction
from ecom_agent.domain.types import Message, ToolResultBlock, Usage
from ecom_agent.permissions import AlwaysAllow, PermissionPolicy
from ecom_agent.providers.base import LLMProvider
from ecom_agent.prompt_loader import load_prompt
from ecom_agent.tools.registry import ToolRegistry, default_registry
from ecom_agent.compaction.strategy import NoCompaction

_PROMPTS_DIR = Path(__file__).parent / "prompts"


@dataclass
class DebugTrace:
    provider_calls: int = 0
    tools_used: list[str] = field(default_factory=list)
    usage: Usage = field(default_factory=Usage)
    steps: list[dict] = field(default_factory=list)
    calls: list[dict] = field(default_factory=list)
    extraction: TurnExtraction = field(default_factory=TurnExtraction)


@dataclass
class TurnResult:
    reply: str
    trace: DebugTrace


@dataclass
class Ctx:
    lang: str = "es"  
    db: object | None = None      # OrdersDB
    kb: object | None = None      # KnowledgeBase
    store: object | None = None   # Store for recall/remember
    session_id: str = "default"


class Conversation:
    def __init__(
        self,
        provider: LLMProvider,
        *,
        registry: ToolRegistry | None = None,
        policy: PermissionPolicy | None = None,
        lang: str = "es",
        db=None,
        kb=None,
        store=None,
        session_id: str = "default",
        system_prompt: str | None = None,
        compactor=None,
        max_steps: int = 6,
    ) -> None:
        self.provider = provider
        self.registry = registry or default_registry
        self.policy = policy or AlwaysAllow()
        self.lang = lang
        self.db = db
        self.kb = kb
        self.store = store
        self.session_id = session_id
        self.max_steps = max_steps
        if system_prompt is None:
            system_prompt = load_prompt(_PROMPTS_DIR, "system", lang)
        self.messages: list[Message] = [Message.system(system_prompt)]
        self.total_usage = Usage()
        self.compactor = compactor or NoCompaction()

    def _ctx(self) -> Ctx:
        return Ctx(
            lang=self.lang,
            db=self.db,
            kb=self.kb,
            store=self.store,
            session_id=self.session_id,
        )
    
    def _extract_turn_data(self, user_text: str) -> TurnExtraction:
        """One-shot call to extract structured customer metadata. Never raises."""
        try:
            instr = load_prompt(_PROMPTS_DIR, "extract_turn_data", self.lang)
            resp = self.provider.send([Message.system(instr), Message.user(user_text)], [])
            return TurnExtraction.model_validate(json.loads(resp.text()))
        except Exception:  # noqa: BLE001 - extraction must never crash the loop
            return TurnExtraction()

    def send(self, user_text: str) -> TurnResult:
        """One outer-loop eval: feed user input, run inner agent loop until the model stops."""
        self.messages.append(Message.user(user_text))
        if self.store:
            self.store.save(self.session_id, {"role": "user", "text": user_text})
        trace = DebugTrace()
        for _ in range(self.max_steps):
            self.messages = self.compactor.compact(self.messages)
            resp = self.provider.send(self.messages, self.registry.definitions())
            trace.provider_calls += 1
            trace.usage = trace.usage + resp.usage
            self.messages.append(Message(role="assistant", content=resp.blocks))
            visible_text = resp.text().strip()
            tool_names = [u.name for u in resp.tool_uses()]
            trace.calls.append(
                {
                    "index": trace.provider_calls,
                    "model": resp.model,
                    "stop_reason": resp.stop_reason,
                    "visible_text": visible_text,
                    "tool_names": tool_names,
                }
            )

            uses = resp.tool_uses()
            if resp.stop_reason != "tool_use" or not uses:
                if self.store:
                    self.store.save(self.session_id, {"role": "assistant", "text": resp.text()})
                trace.extraction = self._extract_turn_data(user_text)
                return TurnResult(reply=resp.text(), trace=trace)

            result_blocks = []
            for u in uses:
                tr = self.registry.dispatch(u.name, u.input, self._ctx(), self.policy)
                trace.tools_used.append(u.name)
                trace.steps.append(
                    {
                        "call_index": trace.provider_calls,
                        "tool": u.name,
                        "input": u.input,
                        "result": tr.content,
                        "error": tr.is_error,
                    }
                )
                result_blocks.append(
                    ToolResultBlock(tool_use_id=u.id, content=tr.content, is_error=tr.is_error)
                )
            self.messages.append(Message(role="user", content=result_blocks))

        trace.extraction = self._extract_turn_data(user_text)
        return TurnResult(reply="(step limit reached)", trace=trace)
    
    def summarize(self) -> dict:
        body = [m for m in self.messages if m.role != "system"]
        summarize_instr = load_prompt(_PROMPTS_DIR, "summarize")
        prompt = [
            Message.system(summarize_instr),
            *body,
            Message.user("Please summarize the conversation above."),
        ]
        return {"summary": self.provider.send(prompt, []).text(), "session_id": self.session_id}