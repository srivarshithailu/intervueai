"""Tests for dev-mode login, its fail-closed rules, and the /api/me upsert."""

import pytest
from pydantic import ValidationError

from app.config import get_settings
from app.deps import dev_user
from app.errors import ApiError
from tests.conftest import offline_settings


def test_me_without_dev_header_is_401(client):
    response = client.get("/api/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


def test_me_rejects_odd_dev_user_names(client):
    response = client.get("/api/me", headers={"X-Dev-User": "bad name with spaces"})
    assert response.status_code == 401


def test_me_creates_user_once(client, fake_db):
    first = client.get("/api/me", headers={"X-Dev-User": "asha"})
    second = client.get("/api/me", headers={"X-Dev-User": "asha"})
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["user_id"] == "dev-asha"
    assert len(fake_db.users.docs) == 1


def test_different_dev_users_get_different_documents(client, fake_db):
    client.get("/api/me", headers={"X-Dev-User": "asha"})
    client.get("/api/me", headers={"X-Dev-User": "ravi"})
    assert {d["firebase_uid"] for d in fake_db.users.docs} == {"dev-asha", "dev-ravi"}


def test_dev_auth_refused_at_startup_in_production():
    with pytest.raises(ValidationError):
        offline_settings(env="production", auth_mode="dev")


def test_dev_user_refused_outside_development_even_if_config_slips():
    # Build settings that skipped validation, to prove the per-request check still fails closed.
    settings = offline_settings().model_copy(update={"env": "production"})
    with pytest.raises(ApiError) as caught:
        dev_user(settings, "asha")
    assert caught.value.status_code == 401


def test_firebase_mode_rejects_requests_until_m1(client):
    client.app.dependency_overrides[get_settings] = lambda: offline_settings(auth_mode="firebase")
    response = client.get("/api/me", headers={"X-Dev-User": "asha"})
    assert response.status_code == 401
