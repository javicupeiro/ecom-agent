"""Speech-to-text helpers for customer audio messages."""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Any

from ecom_agent.config import Settings


class TranscriptionError(RuntimeError):
    """Raised when customer audio cannot be transcribed."""


@dataclass(frozen=True)
class Transcript:
    """Normalized transcript returned by the STT layer."""

    text: str


class OpenAITranscriptionService:
    """Transcribe uploaded audio using the OpenAI audio API."""

    def __init__(self, settings: Settings, client: Any | None = None) -> None:
        self.api_key = settings.openai_api_key.strip()
        self.model = settings.stt.model
        self.timeout_seconds = settings.stt.timeout_seconds
        self._client = client

    @property
    def enabled(self) -> bool:
        """Return True when the service has credentials configured."""

        return bool(self.api_key) or self._client is not None

    def transcribe(
        self,
        audio_bytes: bytes,
        *,
        mime_type: str,
        filename: str,
        lang: str | None = None,
    ) -> Transcript:
        """Convert one uploaded audio clip into text."""

        if not self.enabled:
            raise TranscriptionError("Missing OPENAI_API_KEY.")
        payload = audio_bytes.strip()
        if not payload:
            raise TranscriptionError("Received an empty audio clip.")

        audio_file = BytesIO(payload)
        audio_file.name = filename or self._filename_for(mime_type)
        kwargs: dict[str, Any] = {
            "model": self.model,
            "file": audio_file,
        }
        if lang in {"es", "en"}:
            kwargs["language"] = lang
        try:
            response = self._client_or_create().audio.transcriptions.create(**kwargs)
        except Exception as exc:  # noqa: BLE001 - normalize SDK failures for the UI
            raise TranscriptionError(f"Could not transcribe audio: {exc}") from exc

        text = self._extract_text(response).strip()
        if not text:
            raise TranscriptionError("The audio could not be transcribed.")
        return Transcript(text=text)

    def _client_or_create(self):
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(api_key=self.api_key, timeout=self.timeout_seconds)
        return self._client

    def _extract_text(self, response: Any) -> str:
        """Normalize different SDK response shapes to plain text."""

        if isinstance(response, str):
            return response
        if hasattr(response, "text"):
            return str(response.text)
        if isinstance(response, dict):
            return str(response.get("text", ""))
        return str(response)

    def _filename_for(self, mime_type: str) -> str:
        """Infer a usable filename from the browser mime type."""

        if "webm" in mime_type:
            return "recording.webm"
        if "ogg" in mime_type:
            return "recording.ogg"
        if "mp4" in mime_type or "m4a" in mime_type:
            return "recording.m4a"
        if "mpeg" in mime_type or "mp3" in mime_type:
            return "recording.mp3"
        if "wav" in mime_type:
            return "recording.wav"
        return "recording.bin"
