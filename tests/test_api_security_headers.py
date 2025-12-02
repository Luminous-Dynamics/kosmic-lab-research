from __future__ import annotations

from fastapi.testclient import TestClient

from historical_k.api import app


def test_security_headers_present() -> None:
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    headers = {k.lower(): v for k, v in r.headers.items()}
    assert headers.get("x-content-type-options") == "nosniff"
    assert headers.get("x-frame-options") == "deny"
    assert headers.get("referrer-policy") == "no-referrer"
    assert headers.get("x-xss-protection") == "0"

