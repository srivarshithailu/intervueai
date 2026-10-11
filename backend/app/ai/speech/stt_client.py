"""Speech-to-text chain: tries each configured provider in order and reports which one answered.

M0 has the mock provider only. Groq Whisper and local faster-whisper come in M4.
"""

import logging
import time
from dataclasses import dataclass
from typing import Protocol

from app.ai.speech.stt_mock import MockSTTProvider
from app.config import Settings

log = logging.getLogger("intervueai.stt")


class STTProvider(Protocol):
    name: str

    async def transcribe(self, wav_bytes: bytes, duration_ms: int) -> str: ...


class STTUnavailable(Exception):
    """Every speech-to-text provider in the chain failed."""


@dataclass
class Transcript:
    text: str
    provider: str
    ms: int


def build_provider(name: str, settings: Settings) -> STTProvider | None:
    if name == "mock":
        return MockSTTProvider()
    log.warning("STT provider '%s' is not available yet; skipping it", name)
    return None


def build_chain(names: list[str], settings: Settings) -> list[STTProvider]:
    providers = [build_provider(name, settings) for name in names]
    return [p for p in providers if p is not None]


async def transcribe(chain: list[STTProvider], wav_bytes: bytes, duration_ms: int) -> Transcript:
    for provider in chain:
        started = time.perf_counter()
        try:
            text = await provider.transcribe(wav_bytes, duration_ms)
        except Exception as exc:  # any provider failure means "try the next provider"
            log.warning("STT %s failed: %s", provider.name, exc)
            continue
        ms = round((time.perf_counter() - started) * 1000)
        log.info("STT provider=%s ms=%d", provider.name, ms)
        return Transcript(text=text.strip(), provider=provider.name, ms=ms)
    raise STTUnavailable("No speech-to-text provider could transcribe the audio")
