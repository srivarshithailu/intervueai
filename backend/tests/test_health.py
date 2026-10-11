"""Tests for GET /api/health and the shared error shape."""


def test_health_reports_status_and_chains(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["llm_chain"] == ["mock"]
    assert body["stt_chain"] == ["mock"]
    assert body["auth_mode"] == "dev"


def test_unknown_route_uses_error_shape(client):
    response = client.get("/api/does-not-exist")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
