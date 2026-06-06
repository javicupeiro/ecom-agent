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
    """Language model configuration."""

    provider: str = "anthropic"  # anthropic | openai
    name: str = "claude-sonnet-4-6"
    max_tokens: int = 1024
    temperature: float = 0.1
    top_p: float | None = None


class AgentCfg(BaseModel):
    """Conversation loop settings."""

    max_steps: int = 6
    default_language: str = "es"

class DbCfg(BaseModel):
    """Database storage settings."""

    path: str = "./.data/orders.db"

class RagCfg(BaseModel):
    """Knowledge base indexing and retrieval settings."""

    kb_root: str = "SaborMix"
    collection: str = "sabormix"
    persist_dir: str = "./.data/chroma"
    embedding_model: str = "text-embedding-3-small"
    top_k: int = 10

class CompactionCfg(BaseModel):
    """Conversation history compaction settings."""

    strategy: str = "none"   # none | sliding | summarize
    threshold: int = 20
    keep_recent: int = 6


class VoiceCfg(BaseModel):
    """Voice reply settings for text-to-speech output."""

    model_id: str = "eleven_multilingual_v2"
    audio_format: str = "mp3_44100_128"
    spanish_voice_id: str = "MF3mGyEYCl7XYWbV9V6O"
    english_voice_id: str = "EXAVITQu4vr4xnSDxMaL"
    spanish_voice_label: str = "Mujer · Espanol"
    english_voice_label: str = "Woman · US English"
    stability: float = 0.35
    similarity_boost: float = 0.75
    style: float = 0.2
    use_speaker_boost: bool = True
    timeout_seconds: float = 30.0


class SttCfg(BaseModel):
    """Speech-to-text settings for incoming customer audio."""

    model: str = "gpt-4o-mini-transcribe"
    timeout_seconds: float = 30.0

class Settings(BaseSettings):
    """Top-level application settings object."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        toml_file="config.toml",
        extra="ignore",
    )

    anthropic_api_key: str = ""  # from .env, never from config.toml
    openai_api_key: str = ""     # from .env
    elevenlab_api_key: str = ""  # from .env
    llm: LlmCfg = LlmCfg()
    agent: AgentCfg = AgentCfg()
    db: DbCfg = DbCfg()
    rag: RagCfg = RagCfg()
    compaction: CompactionCfg = CompactionCfg()
    voice: VoiceCfg = VoiceCfg()
    stt: SttCfg = SttCfg()

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Define the settings source order from highest to lowest priority."""
        return (init_settings, env_settings, dotenv_settings, TomlConfigSettingsSource(settings_cls))


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance for the process."""

    return Settings()