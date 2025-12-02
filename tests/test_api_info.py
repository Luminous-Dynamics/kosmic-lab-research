from __future__ import annotations

from fastapi.testclient import TestClient

from historical_k.api import app


def test_info_alias_of_meta() -> None:
    client = TestClient(app)
    r = client.get("/info")
    assert r.status_code == 200
    body = r.json()
    assert "version" in body and "config" in body and "artifacts" in body

