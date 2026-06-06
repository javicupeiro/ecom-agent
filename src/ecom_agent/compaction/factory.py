"""Build the compaction strategy from settings."""

from __future__ import annotations

from ecom_agent.compaction.strategy import (
    CompactionStrategy, NoCompaction, SlidingWindow, Summarize,
)
from ecom_agent.config import Settings
from ecom_agent.providers.base import LLMProvider


def build_compactor(settings: Settings, provider: LLMProvider) -> CompactionStrategy:
    """Build the configured conversation compaction strategy."""

    cfg = settings.compaction
    if cfg.strategy == "sliding":
        return SlidingWindow(keep_last=cfg.keep_recent)
    if cfg.strategy == "summarize":
        return Summarize(provider, threshold=cfg.threshold, keep_recent=cfg.keep_recent)
    return NoCompaction()