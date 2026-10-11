"""Offline, deterministic speech-to-text provider for tests and keyless demos. Ignores the audio content."""


class MockSTTProvider:
    name = "mock"

    async def transcribe(self, wav_bytes: bytes, duration_ms: int) -> str:
        seconds = max(1, round(duration_ms / 1000))
        return f"This is a mock transcript of about {seconds} seconds of speech."
