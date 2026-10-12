"""Tests for Firebase login (AUTH_MODE=firebase) and per-user isolation on /api/me.

Tokens are real RS256 JWTs signed with a throwaway test key, so google-auth's real signature,
expiry and audience checks run. Only the download of Google's public keys is faked.
"""

import json
import time

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from google.auth import crypt, jwt
from google.auth import exceptions as google_exceptions
from pydantic import ValidationError

from app import firebase_auth
from app.config import get_settings
from tests.conftest import offline_settings

PROJECT = "test-project"
KEY_ID = "test-key"


def new_signer(key_id: str = KEY_ID) -> tuple[crypt.RSASigner, bytes]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    )
    public_pem = key.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return crypt.RSASigner.from_string(private_pem, key_id=key_id), public_pem


SIGNER, PUBLIC_PEM = new_signer()
OTHER_SIGNER, _ = new_signer()  # same key id, different key: a forged token


def make_token(uid: str = "user-a", signer: crypt.RSASigner = SIGNER, **overrides) -> str:
    now = int(time.time())
    claims = {
        "iss": f"https://securetoken.google.com/{PROJECT}",
        "aud": PROJECT,
        "sub": uid,
        "auth_time": now - 60,
        "iat": now - 60,
        "exp": now + 3600,
        "email": f"{uid}@example.com",
        "name": uid.title(),
    }
    claims.update(overrides)
    return jwt.encode(signer, claims).decode()


def bearer(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


class FakeKeyResponse:
    status = 200

    def __init__(self, body: dict):
        self.data = json.dumps(body).encode()


def serve_test_keys(url, method="GET", **kwargs):
    return FakeKeyResponse({KEY_ID: PUBLIC_PEM.decode()})


def keys_offline(url, method="GET", **kwargs):
    raise google_exceptions.TransportError("network down")


@pytest.fixture
def firebase_client(client, monkeypatch):
    settings = offline_settings(auth_mode="firebase", firebase_project_id=PROJECT)
    client.app.dependency_overrides[get_settings] = lambda: settings
    monkeypatch.setattr(firebase_auth, "_request", serve_test_keys)
    return client


def assert_401(response):
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


# --- Rejections -------------------------------------------------------------


def test_missing_token_is_401(firebase_client):
    assert_401(firebase_client.get("/api/me"))


def test_non_bearer_header_is_401(firebase_client):
    assert_401(firebase_client.get("/api/me", headers={"Authorization": f"Token {make_token()}"}))


def test_malformed_token_is_401(firebase_client):
    assert_401(firebase_client.get("/api/me", headers=bearer("not-a-jwt")))


def test_oversized_token_is_401(firebase_client):
    assert_401(firebase_client.get("/api/me", headers=bearer("a" * 5000)))


def test_expired_token_is_401_with_plain_message(firebase_client):
    now = int(time.time())
    response = firebase_client.get("/api/me", headers=bearer(make_token(iat=now - 7200, exp=now - 3600)))
    assert_401(response)
    assert "expired" in response.json()["error"]["message"]


def test_token_for_another_project_is_401(firebase_client):
    response = firebase_client.get("/api/me", headers=bearer(make_token(aud="someone-elses-project")))
    assert_401(response)
    assert "different Firebase project" in response.json()["error"]["message"]


def test_wrong_issuer_is_401(firebase_client):
    token = make_token(iss="https://securetoken.google.com/someone-elses-project")
    assert_401(firebase_client.get("/api/me", headers=bearer(token)))


def test_token_signed_with_unknown_key_is_401(firebase_client):
    assert_401(firebase_client.get("/api/me", headers=bearer(make_token(signer=OTHER_SIGNER))))


def test_tampered_token_is_401(firebase_client):
    header, payload, signature = make_token().split(".")
    forged_payload = make_token(uid="admin").split(".")[1]
    forged = ".".join([header, forged_payload, signature])
    assert payload != forged_payload
    assert_401(firebase_client.get("/api/me", headers=bearer(forged)))


def test_empty_user_id_is_401(firebase_client):
    assert_401(firebase_client.get("/api/me", headers=bearer(make_token(uid=""))))


def test_future_auth_time_is_401(firebase_client):
    token = make_token(auth_time=int(time.time()) + 3600)
    assert_401(firebase_client.get("/api/me", headers=bearer(token)))


def test_dev_header_is_ignored_in_firebase_mode(firebase_client):
    assert_401(firebase_client.get("/api/me", headers={"X-Dev-User": "asha"}))


def test_key_download_failure_is_503(firebase_client, monkeypatch):
    monkeypatch.setattr(firebase_auth, "_request", keys_offline)
    response = firebase_client.get("/api/me", headers=bearer(make_token()))
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "auth_unavailable"


def test_firebase_mode_without_project_id_refuses_to_start():
    with pytest.raises(ValidationError):
        offline_settings(auth_mode="firebase", firebase_project_id="  ")


# --- Valid tokens and isolation ---------------------------------------------


def test_valid_token_returns_and_stores_user(firebase_client, fake_db):
    response = firebase_client.get("/api/me", headers=bearer(make_token("user-a")))
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "user-a"
    assert body["email"] == "user-a@example.com"
    assert fake_db.users.docs[0]["firebase_uid"] == "user-a"


def test_me_twice_creates_one_document(firebase_client, fake_db):
    firebase_client.get("/api/me", headers=bearer(make_token("user-a")))
    firebase_client.get("/api/me", headers=bearer(make_token("user-a")))
    assert len(fake_db.users.docs) == 1


def test_each_user_only_sees_their_own_record(firebase_client, fake_db):
    a = firebase_client.get("/api/me", headers=bearer(make_token("user-a"))).json()
    b = firebase_client.get("/api/me", headers=bearer(make_token("user-b"))).json()
    a_again = firebase_client.get("/api/me", headers=bearer(make_token("user-a"))).json()

    assert len(fake_db.users.docs) == 2
    assert (a["user_id"], a["email"]) == ("user-a", "user-a@example.com")
    assert (b["user_id"], b["email"]) == ("user-b", "user-b@example.com")
    assert a_again == a


def test_identity_comes_only_from_the_token(firebase_client, fake_db):
    # A signed-in user cannot claim to be someone else through other headers.
    headers = {**bearer(make_token("user-a")), "X-Dev-User": "user-b"}
    body = firebase_client.get("/api/me", headers=headers).json()
    assert body["user_id"] == "user-a"
    assert [d["firebase_uid"] for d in fake_db.users.docs] == ["user-a"]
