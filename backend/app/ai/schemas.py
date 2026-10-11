"""Pydantic models for every JSON object an LLM returns. Code only trusts output that validates here."""

from pydantic import BaseModel


class PingResult(BaseModel):
    """Tiny task used by tests and diagnostics to check that a provider answers with valid JSON."""

    ok: bool
    message: str
