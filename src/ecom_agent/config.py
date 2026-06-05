"""Typed configuration loaded from `config.toml` (tunables) and `.env` (secrets).

Precedence (highest first): environment variables > .env > config.toml > defaults.
Edit config.toml to play with parameters; override a single value per run with a
nested env var, e.g. LLM__TEMPERATURE=0.2 or LLM__PROVIDER=openai.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class LlmCfg(BaseModel):
    provider: str = "anthropic"  # anthropic | openai
    name: str = "claude-sonnet-4-6"
    max_tokens: int = 1024
    temperature: float = 0.1
    top_p: float | None = None


class AgentCfg(BaseModel):
    max_steps: int = 6
    default_language: str = "es"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        toml_file="config.toml",
        extra="ignore",
    )

    anthropic_api_key: str = ""  # from .env, never from config.toml
    openai_api_key: str = ""     # from .env
    llm: LlmCfg = LlmCfg()
    agent: AgentCfg = AgentCfg()

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # Order defines precedence (first wins).
        return (init_settings, env_settings, dotenv_settings, TomlConfigSettingsSource(settings_cls))


@lru_cache
def get_settings() -> Settings:
    return Settings()