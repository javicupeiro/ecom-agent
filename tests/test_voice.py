import base64

from ecom_agent.config import Settings
from ecom_agent.domain.types import Response, TextBlock
from ecom_agent.providers.mock import MockProvider
from ecom_agent.voice import ElevenLabsVoiceService, VoiceSynthesisError


def test_voice_service_adapts_reply_and_encodes_audio(monkeypatch) -> None:
    provider = MockProvider(script=[Response(blocks=[TextBlock(text="Claro. Primero apaga la maquina y espera diez segundos.")])])
    settings = Settings(
        elevenlab_api_key="test-key",
        voice={
            "spanish_voice_id": "voice-es",
            "english_voice_id": "voice-en",
            "spanish_voice_label": "Mujer ES",
            "english_voice_label": "Woman US",
        },
    )
    service = ElevenLabsVoiceService(provider, settings)

    monkeypatch.setattr(
        service,
        "_synthesize",
        lambda script, voice_id: f"{voice_id}:{script}".encode("utf-8"),
    )

    clip = service.render("Apaga la maquina y espera.", lang="es")

    assert clip.script == "Claro. Primero apaga la maquina y espera diez segundos."
    assert clip.voice_id == "voice-es"
    assert clip.voice_label == "Mujer ES"
    assert base64.b64decode(clip.audio_base64).decode("utf-8").startswith("voice-es:")


def test_voice_service_uses_english_profile(monkeypatch) -> None:
    provider = MockProvider(script=[Response(blocks=[TextBlock(text="Please unplug the mixer for ten seconds.")])])
    settings = Settings(
        elevenlab_api_key="test-key",
        voice={
            "spanish_voice_id": "voice-es",
            "english_voice_id": "voice-en",
            "spanish_voice_label": "Mujer ES",
            "english_voice_label": "Woman US",
        },
    )
    service = ElevenLabsVoiceService(provider, settings)

    seen = {}

    def fake_synthesize(script: str, voice_id: str) -> bytes:
        seen["script"] = script
        seen["voice_id"] = voice_id
        return b"audio"

    monkeypatch.setattr(service, "_synthesize", fake_synthesize)

    clip = service.render("Unplug the mixer.", lang="en")

    assert clip.voice_id == "voice-en"
    assert seen == {
        "script": "Please unplug the mixer for ten seconds.",
        "voice_id": "voice-en",
    }


def test_voice_service_retries_with_public_fallback(monkeypatch) -> None:
    provider = MockProvider(script=[Response(blocks=[TextBlock(text="Hola, esta es una prueba.")])])
    settings = Settings(
        elevenlab_api_key="test-key",
        voice={
            "spanish_voice_id": "voice-es-blocked",
            "english_voice_id": "voice-en",
            "spanish_voice_label": "Mujer ES",
            "english_voice_label": "Woman US",
        },
    )
    service = ElevenLabsVoiceService(provider, settings)

    calls = []

    def fake_synthesize(script: str, voice_id: str) -> bytes:
        calls.append(voice_id)
        if voice_id == "voice-es-blocked":
            raise VoiceSynthesisError("ElevenLabs HTTP 402: paid_plan_required")
        return b"audio"

    monkeypatch.setattr(service, "_synthesize", fake_synthesize)

    clip = service.render("Respuesta", lang="es")

    assert calls == ["voice-es-blocked", "EXAVITQu4vr4xnSDxMaL"]
    assert clip.voice_id == "EXAVITQu4vr4xnSDxMaL"
    assert clip.voice_label == "Mujer · voz multilingue"