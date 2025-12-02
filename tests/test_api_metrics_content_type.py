from __future__ import annotations

from fastapi.testclient import TestClient

from historical_k.api import app


def test_metrics_content_type_is_plain_text() -> None:
    client = TestClient(app)
    r = client.get("/metrics")
    assert r.status_code == 200
    ctype = r.headers.get("content-type", "")
    assert ctype.startswith("text/plain")

