"""Tests for the LLM and STT chains using the offline mock and small fake providers."""

import asyncio

import pytest

from app.ai import llm_client
from app.ai.schemas import PingResult
from app.ai.speech import stt_client
from tests.conftest import offline_settings


class BrokenProvider:
    """Always raises, like a provider that is down or rate-limited."""

    name = "broken"

    def __init__(self):
        self.calls = 0

    async def complete(self, task, system, user, json_schema):
        self.calls += 1
        raise RuntimeError("service down")

    async def transcribe(self, wav_bytes, duration_ms):
        self.calls += 1
        raise RuntimeError("service down")


class GarbageProvider:
    """Always answers with text that is not valid JSON for the schema."""

    name = "garbage"

    def __init__(self):
        self.calls = 0

    async def complete(self, task, system, user, json_schema):
        self.calls += 1
        return "Sure! Here is your answer: ok"


def run(coro):
    return asyncio.run(coro)


def test_mock_chain_returns_valid_json():
    chain = llm_client.build_chain(["mock"], offline_settings())
    result = run(llm_client.generate(chain, "ping", "system", "user", PingResult))
    assert result.ok is True


def test_unknown_provider_names_are_skipped():
    chain = llm_client.build_chain(["nonexistent", "mock"], offline_settings())
    assert [p.name for p in chain] == ["mock"]


def test_failing_provider_falls_through_to_next():
    broken = BrokenProvider()
    chain = [broken, *llm_client.build_chain(["mock"], offline_settings())]
    result = run(llm_client.generate(chain, "ping", "s", "u", PingResult))
    assert result.message == "pong from mock"
    assert broken.calls == 1


def test_invalid_json_is_retried_once_then_fallback_used():
    garbage = GarbageProvider()
    fallback = PingResult(ok=False, message="fallback")
    result = run(llm_client.generate([garbage], "ping", "s", "u", PingResult, fallback=fallback))
    assert garbage.calls == 2
    assert result == fallback


def test_no_working_provider_and_no_fallback_raises():
    with pytest.raises(llm_client.LLMUnavailable):
        run(llm_client.generate([BrokenProvider()], "ping", "s", "u", PingResult))


def test_mock_stt_is_deterministic():
    chain = stt_client.build_chain(["mock"], offline_settings())
    first = run(stt_client.transcribe(chain, b"RIFF", 4200))
    second = run(stt_client.transcribe(chain, b"RIFF", 4200))
    assert first.text == second.text
    assert first.provider == "mock"


def test_stt_falls_through_to_next_provider():
    chain = [BrokenProvider(), *stt_client.build_chain(["mock"], offline_settings())]
    result = run(stt_client.transcribe(chain, b"RIFF", 1000))
    assert result.provider == "mock"


def test_stt_all_failing_raises():
    with pytest.raises(stt_client.STTUnavailable):
        run(stt_client.transcribe([BrokenProvider()], b"RIFF", 1000))
