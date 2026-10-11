"""The ONLY place that talks to LLM providers. Tries the configured chain in order and validates JSON.

M0 has the mock provider only. Groq, Gemini and NIM adapters, timeouts and the circuit breaker come in M3.
"""

import logging
import time
from typing import Protocol, TypeVar

from pydantic import BaseModel, ValidationError

from app.ai.providers.mock import MockLLMProvider
from app.config import Settings

log = logging.getLogger("intervueai.llm")

T = TypeVar("T", bound=BaseModel)


class LLMProvider(Protocol):
    name: str

    async def complete(self, task: str, system: str, user: str, json_schema: dict) -> str: ...


class LLMUnavailable(Exception):
    """Every provider in the chain failed and the caller gave no fallback."""


def build_provider(name: str, settings: Settings) -> LLMProvider | None:
    if name == "mock":
        return MockLLMProvider()
    log.warning("LLM provider '%s' is not available yet; skipping it", name)
    return None


def build_chain(names: list[str], settings: Settings) -> list[LLMProvider]:
    providers = [build_provider(name, settings) for name in names]
    return [p for p in providers if p is not None]


async def generate(
    chain: list[LLMProvider],
    task: str,
    system: str,
    user: str,
    output_model: type[T],
    fallback: T | None = None,
) -> T:
    """Ask each provider in turn for JSON matching output_model.

    Invalid JSON gets one retry on the same provider; a provider error moves on to the next one.
    If all fail, return the fallback, or raise LLMUnavailable when there is none.
    """
    schema = output_model.model_json_schema()
    for provider in chain:
        for attempt in (1, 2):
            started = time.perf_counter()
            try:
                raw = await provider.complete(task, system, user, schema)
            except Exception as exc:  # any provider failure means "try the next provider"
                log.warning("LLM %s failed on task %s: %s", provider.name, task, exc)
                break
            ms = round((time.perf_counter() - started) * 1000)
            try:
                result = output_model.model_validate_json(raw)
            except ValidationError:
                log.warning("LLM %s gave invalid JSON for %s (attempt %d)", provider.name, task, attempt)
                continue
            log.info("LLM task=%s provider=%s ms=%d", task, provider.name, ms)
            return result
    if fallback is not None:
        log.warning("LLM task %s used its fallback", task)
        return fallback
    raise LLMUnavailable(f"No LLM provider could complete task '{task}'")
