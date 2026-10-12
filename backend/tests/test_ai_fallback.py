"""The Groq path, with the network call replaced by fakes."""
import asyncio
import json

from app.core.config import settings
from app.services import mood_service


def _run(coro):
    return asyncio.run(coro)


def test_ai_success(monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "gsk_fake")

    async def fake_chat(messages, temperature, max_tokens):
        return "```json\n" + json.dumps({
            "mood": "Nostalgic", "confidence": 0.93,
            "explanation": "Tu repenses à ton enfance.",
            "genres": ["2000s pop"], "search_queries": ["hits années 2000"],
        }) + "\n```"

    monkeypatch.setattr(mood_service, "_chat", fake_chat)
    result = _run(mood_service.analyze_mood("je repense à mon enfance"))
    assert result["mood"] == "nostalgic"
    assert result["confidence"] == 0.93
    assert result["source"] == "ai"


def test_ai_unknown_mood_is_mapped(monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "gsk_fake")

    async def fake_chat(*a, **k):
        return json.dumps({"mood": "heartbroken", "confidence": 2,
                           "explanation": "sad breakup, crying"})

    monkeypatch.setattr(mood_service, "_chat", fake_chat)
    result = _run(mood_service.analyze_mood("my girlfriend left me"))
    assert result["mood"] == "sad"
    assert result["confidence"] == 1.0


def test_ai_failure_falls_back(monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "gsk_fake")

    async def broken(*a, **k):
        raise TimeoutError("API down")

    monkeypatch.setattr(mood_service, "_chat", broken)
    result = _run(mood_service.analyze_mood("Je veux faire la fête"))
    assert result["source"] == "local"
    assert result["mood"] == "party"
    assert _run(mood_service.extract_music_preferences("du Drake stp"))["artists"] == ["Drake"]
    assert _run(mood_service.generate_playlist_name("party", ""))


def test_ai_garbage_falls_back(monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "gsk_fake")

    async def garbage(*a, **k):
        return "Sorry, I can't help with that."

    monkeypatch.setattr(mood_service, "_chat", garbage)
    assert _run(mood_service.analyze_mood("I'm so happy"))["source"] == "local"
