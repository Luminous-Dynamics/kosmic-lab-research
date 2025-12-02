from __future__ import annotations

from fastapi.testclient import TestClient

from historical_k.api import app


def test_metrics_has_no_store_cache_control() -> None:
    client = TestClient(app)
    r = client.get("/metrics")
    assert r.status_code == 200
    assert r.headers.get("cache-control") == "no-store"

