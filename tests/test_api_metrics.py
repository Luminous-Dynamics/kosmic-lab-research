from __future__ import annotations

from fastapi.testclient import TestClient

from historical_k.api import app


def test_metrics_exposes_http_counters() -> None:
    client = TestClient(app)
    # Trigger at least one request
    assert client.get("/health").status_code == 200
    m = client.get("/metrics")
    assert m.status_code == 200
    body = m.text
    assert body.startswith("# TYPE http_requests_total counter")
    assert 'path="/health"' in body
    assert 'kosmic_app_info' in body
    assert 'kosmic_uptime_seconds' in body
    assert 'kosmic_etag_cache_hits_total' in body
    assert 'kosmic_etag_cache_misses_total' in body


def test_metrics_uses_lock_for_snapshot(monkeypatch) -> None:
    class FakeLock:
        def __init__(self) -> None:
            self.entered = 0
            self.used = False

        def __enter__(self):
            self.entered += 1
            self.used = True

        def __exit__(self, exc_type, exc, tb):
            self.entered -= 1

    from historical_k.api import AccessLogMiddleware

    lock = FakeLock()
    monkeypatch.setattr(AccessLogMiddleware, "_LOCK", lock)
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert lock.used
    assert lock.entered == 0  # lock released
    assert "# TYPE http_requests_total counter" in resp.text
