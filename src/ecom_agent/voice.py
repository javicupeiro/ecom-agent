"""Voice reply post-processing and ElevenLabs synthesis."""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from pathlib import Path
from urllib import error, request

from ecom_agent.config import Settings
from ecom_agent.domain.types import Message
from ecom_agent.prompt_loader import load_prompt
from ecom_agent.providers.base import LLMProvider

_PROMPTS_DIR = Path(__file__).parent / "prompts"


class VoiceSynthesisError(RuntimeError):
    """Raised when the voice pipeline cannot synthesize audio."""


@dataclass(frozen=True)
class VoiceClip:
    """Synthesized voice reply returned to the UI."""

    script: str
    audio_base64: str
    mime_type: str
    voice_id: str
    voice_label: str


@dataclass(frozen=True)
class VoiceProfile:
    """Language-specific voice selection."""

    voice_id: str
    voice_label: str


class ElevenLabsVoiceService:
    """Adapts a text reply into listenable copy and synthesizes it."""

    def __init__(self, provider: LLMProvider, settings: Settings) -> None:
        self.provider = provider
        self.api_key = settings.elevenlab_api_key.strip()
        self.model_id = settings.voice.model_id
        self.audio_format = settings.voice.audio_format
        self.timeout_seconds = settings.voice.timeout_seconds
        self.stability = settings.voice.stability
        self.similarity_boost = settings.voice.similarity_boost
        self.style = settings.voice.style
        self.use_speaker_boost = settings.voice.use_speaker_boost
        self.profiles = {
            "es": VoiceProfile(
                voice_id=settings.voice.spanish_voice_id,
                voice_label=settings.voice.spanish_voice_label,
            ),
            "en": VoiceProfile(
                voice_id=settings.voice.english_voice_id,
                voice_label=settings.voice.english_voice_label,
            ),
        }
        self.fallback_profiles = {
            "es": VoiceProfile(
                voice_id="EXAVITQu4vr4xnSDxMaL",
                voice_label="Mujer · voz multilingue",
            ),
            "en": VoiceProfile(
                voice_id="EXAVITQu4vr4xnSDxMaL",
                voice_label="Woman · US English",
            ),
        }

    @property
    def enabled(self) -> bool:
        """Return True when the service has enough configuration to run."""

        return bool(self.api_key)

    def render(self, reply_text: str, *, lang: str) -> VoiceClip:
        """Convert the final assistant reply into an audio clip."""

        if not self.enabled:
            raise VoiceSynthesisError("Missing ELEVENLAB_API_KEY.")
        profile = self._profile_for(lang)
        script = self._adapt_script(reply_text, lang=lang)
        selected_profile = profile
        try:
            audio = self._synthesize(script, profile.voice_id)
        except VoiceSynthesisError as exc:
            fallback = self.fallback_profiles.get(lang)
            if not self._should_retry_with_fallback(exc, profile, fallback):
                raise
            audio = self._synthesize(script, fallback.voice_id)
            selected_profile = fallback
        return VoiceClip(
            script=script,
            audio_base64=base64.b64encode(audio).decode("ascii"),
            mime_type="audio/mpeg",
            voice_id=selected_profile.voice_id,
            voice_label=selected_profile.voice_label,
        )

    def _should_retry_with_fallback(
        self,
        exc: VoiceSynthesisError,
        profile: VoiceProfile,
        fallback: VoiceProfile | None,
    ) -> bool:
        """Return True when synthesis should retry with a public fallback voice."""

        if fallback is None or fallback.voice_id == profile.voice_id:
            return False
        message = str(exc).lower()
        return "paid_plan_required" in message or "payment_required" in message

    def _profile_for(self, lang: str) -> VoiceProfile:
        """Resolve the voice profile for the current UI language."""

        return self.profiles.get(lang, self.profiles["es"])

    def _adapt_script(self, reply_text: str, *, lang: str) -> str:
        """Rewrite the chat reply into natural listening-first copy."""

        source = reply_text.strip()
        if not source:
            raise VoiceSynthesisError("Cannot synthesize an empty reply.")
        prompt = load_prompt(_PROMPTS_DIR, "voice_reply", lang)
        resp = self.provider.send([Message.system(prompt), Message.user(source)], [])
        script = resp.text().strip()
        return script or source

    def _synthesize(self, script: str, voice_id: str) -> bytes:
        """Call ElevenLabs and return the raw audio bytes."""

        payload = json.dumps(
            {
                "text": script,
                "model_id": self.model_id,
                "output_format": self.audio_format,
                "voice_settings": {
                    "stability": self.stability,
                    "similarity_boost": self.similarity_boost,
                    "style": self.style,
                    "use_speaker_boost": self.use_speaker_boost,
                },
            }
        ).encode("utf-8")
        req = request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            data=payload,
            headers={
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key,
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                return response.read()
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore").strip()
            message = detail[:300] if detail else exc.reason
            raise VoiceSynthesisError(f"ElevenLabs HTTP {exc.code}: {message}") from exc
        except error.URLError as exc:
            raise VoiceSynthesisError(f"Could not contact ElevenLabs: {exc.reason}") from exc
