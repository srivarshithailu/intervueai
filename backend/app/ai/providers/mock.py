"""Offline, deterministic LLM provider. Lets the whole app and every test run with no API keys.

Each task name maps to a function that builds a fixed answer, so the same input always gives the same output.
"""

import json
from collections.abc import Callable


def ping(_: str) -> dict:
    return {"ok": True, "message": "pong from mock"}


# Later milestones add one entry per task (resume_analysis, interview_plan, turn, final_report).
MOCK_TASKS: dict[str, Callable[[str], dict]] = {
    "ping": ping,
}


class MockLLMProvider:
    name = "mock"

    async def complete(self, task: str, system: str, user: str, json_schema: dict) -> str:
        """Return raw JSON text, like a real provider would. system and json_schema are unused here."""
        builder = MOCK_TASKS.get(task)
        if builder is None:
            raise ValueError(f"mock provider has no answer for task '{task}'")
        return json.dumps(builder(user))
