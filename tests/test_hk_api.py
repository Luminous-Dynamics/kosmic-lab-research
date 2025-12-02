from __future__ import annotations

from fastapi.testclient import TestClient

from historical_k.api import app


def test_api_health_and_missing_resources() -> None:
    client = TestClient(app)

    # Health
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json().get("status") == "ok"

    # Missing until pipelines run
    for path in ("/k/series", "/k/summary", "/k/plot", "/regimes", "/forecast"):
        r = client.get(path)
        assert r.status_code == 404
