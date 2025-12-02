from __future__ import annotations

from fastapi.testclient import TestClient

from historical_k.api import app


def test_metrics_histogram_lines_present() -> None:
    client = TestClient(app)
    # trigger some requests
    for _ in range(3):
        client.get("/health")
    m = client.get("/metrics")
    assert m.status_code == 200
    body = m.text
    assert "# TYPE http_request_duration_ms histogram" in body
    assert "http_request_duration_ms_bucket" in body
    assert "http_request_duration_ms_sum" in body
    assert "http_request_duration_ms_count" in body

