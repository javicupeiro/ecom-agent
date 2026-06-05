"""Build a provider from settings. The only place that maps config -> a concrete
provider. SDK imports are lazy, so you only load the one you actually use.
"""

from __future__ import annotations

from collections.abc import Callable

from ecom_agent.config import Settings
from ecom_agent.providers.base import LLMProvider


def _anthropic(s: Settings) -> LLMProvider:
    from ecom_agent.providers.anthropic_provider import AnthropicProvider

    return AnthropicProvider(
        model=s.llm.name,
        api_key=s.anthropic_api_key or None,
        max_tokens=s.llm.max_tokens,
        temperature=s.llm.temperature,
        top_p=s.llm.top_p,
    )


def _openai(s: Settings) -> LLMProvider:
    from ecom_agent.providers.openai_provider import OpenAIProvider

    return OpenAIProvider(
        model=s.llm.name,
        api_key=s.openai_api_key or None,
        max_tokens=s.llm.max_tokens,
        temperature=s.llm.temperature,
        top_p=s.llm.top_p,
    )


_BUILDERS: dict[str, Callable[[Settings], LLMProvider]] = {
    "anthropic": _anthropic,
    "openai": _openai,
}


def build_provider(settings: Settings) -> LLMProvider:
    try:
        return _BUILDERS[settings.llm.provider](settings)
    except KeyError:
        raise ValueError(
            f"Unknown provider '{settings.llm.provider}'. Available: {sorted(_BUILDERS)}"
        )