"""Shared test fixtures: safe offline settings, an in-memory fake database, and a test client.

Tests never need MongoDB, API keys or a network connection.
"""

import pytest
from fastapi.testclient import TestClient
from pymongo import ReturnDocument

from app import database
from app.config import Settings, get_settings
from app.main import create_app


def offline_settings(**overrides) -> Settings:
    # _env_file=None so a developer's real backend/.env never leaks into tests.
    values = {"env": "development", "auth_mode": "dev", "llm_chain": "mock", "stt_chain": "mock"}
    values.update(overrides)
    return Settings(_env_file=None, **values)


class FakeCollection:
    """Just enough of a Mongo collection for the queries the app makes, kept in a list."""

    def __init__(self):
        self.docs: list[dict] = []

    async def find_one_and_update(self, query, update, upsert=False, return_document=ReturnDocument.BEFORE):
        doc = next((d for d in self.docs if all(d.get(k) == v for k, v in query.items())), None)
        if doc is None:
            if not upsert:
                return None
            doc = dict(query)
            doc.update(update.get("$setOnInsert", {}))
            self.docs.append(doc)
        doc.update(update.get("$set", {}))
        return dict(doc)


class FakeDb:
    def __init__(self):
        self.users = FakeCollection()


@pytest.fixture
def fake_db() -> FakeDb:
    return FakeDb()


@pytest.fixture
def client(fake_db, monkeypatch) -> TestClient:
    settings = offline_settings()
    app = create_app()
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[database.get_db] = lambda: fake_db

    # Skip the real MongoDB connection during app startup.
    async def no_connect(_settings):
        return False

    monkeypatch.setattr(database, "connect", no_connect)
    with TestClient(app) as test_client:
        yield test_client
