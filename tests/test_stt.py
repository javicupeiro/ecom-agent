from types import SimpleNamespace

import pytest

from ecom_agent.config import Settings
from ecom_agent.stt import OpenAITranscriptionService, TranscriptionError


class _FakeTranscriptions:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


def test_transcription_service_returns_text_from_sdk_object() -> None:
    transcriptions = _FakeTranscriptions(SimpleNamespace(text="Hola desde audio"))
    client = SimpleNamespace(audio=SimpleNamespace(transcriptions=transcriptions))
    service = OpenAITranscriptionService(Settings(openai_api_key="test-key"), client=client)

    transcript = service.transcribe(b"audio-bytes", mime_type="audio/webm", filename="clip.webm", lang="es")

    assert transcript.text == "Hola desde audio"
    assert transcriptions.calls[0]["model"] == "gpt-4o-mini-transcribe"
    assert transcriptions.calls[0]["language"] == "es"


def test_transcription_service_rejects_empty_audio() -> None:
    service = OpenAITranscriptionService(Settings(openai_api_key="test-key"), client=object())

    with pytest.raises(TranscriptionError, match="empty audio"):
        service.transcribe(b"", mime_type="audio/webm", filename="clip.webm")