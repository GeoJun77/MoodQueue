"""Checks the exact request sent to Groq, using the real SDK with a fake HTTP layer."""
import asyncio
import json

import httpx
import pytest

from app.core.config import settings
from app.services import mood_service


def _fake_groq(captured: list, content: str):
    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(json.loads(request.content))
        return httpx.Response(200, json={
            "id": "x", "object": "chat.completion", "created": 0,
            "model": captured[-1]["model"],
            "choices": [{"index": 0, "finish_reason": "stop",
                         "message": {"role": "assistant", "content": content}}],
        })

    from groq import AsyncGroq
    return AsyncGroq(api_key="gsk_fake", http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))


def test_reasoning_model_gets_effort_and_headroom(monkeypatch):
    captured: list = []
    monkeypatch.setattr(settings, "GROQ_MODEL", "openai/gpt-oss-20b")
    monkeypatch.setattr(mood_service, "_client", _fake_groq(captured, "Golden Hour 🌅"))
    out = asyncio.run(mood_service._chat([{"role": "user", "content": "hi"}], 0.5, 50))
    assert out == "Golden Hour 🌅"
    body = captured[0]
    assert body["model"] == "openai/gpt-oss-20b"
    assert body["reasoning_effort"] == "low"
    assert body["max_tokens"] == 50 + settings.AI_REASONING_TOKENS


def test_classic_model_unchanged(monkeypatch):
    captured: list = []
    monkeypatch.setattr(settings, "GROQ_MODEL", "some-classic-model")
    monkeypatch.setattr(mood_service, "_client", _fake_groq(captured, "ok"))
    asyncio.run(mood_service._chat([{"role": "user", "content": "hi"}], 0.5, 50))
    assert "reasoning_effort" not in captured[0]
    assert captured[0]["max_tokens"] == 50


def test_empty_answer_raises_so_local_fallback_is_used(monkeypatch):
    monkeypatch.setattr(mood_service, "_client", _fake_groq([], ""))
    with pytest.raises(ValueError):
        asyncio.run(mood_service._chat([{"role": "user", "content": "hi"}], 0.5, 50))


def test_default_model_is_still_supported():
    # llama-3.1-8b-instant was shut down on 2026-08-16
    assert settings.GROQ_MODEL == "openai/gpt-oss-20b"
