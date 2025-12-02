from __future__ import annotations

from fastapi.testclient import TestClient

from historical_k.api import app


def test_server_timing_header_present() -> None:
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.headers.get("server-timing", "").startswith("app;dur=")

