from __future__ import annotations

from fastapi.testclient import TestClient

from historical_k.api import app


def test_root_index_links_and_version() -> None:
    client = TestClient(app)
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert "version" in body
    links = body.get("_links", {})
    assert all(k in links for k in ("health", "ready", "meta", "series"))
    # Non-cacheable
    assert r.headers.get("cache-control") == "no-store"

