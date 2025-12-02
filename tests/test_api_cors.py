from __future__ import annotations

import importlib
import sys
from pathlib import Path

from fastapi.testclient import TestClient


def test_cors_headers_when_enabled(tmp_path: Path, monkeypatch) -> None:
    # Ensure fresh import of module with CORS env set
    monkeypatch.setenv("KOSMIC_API_CORS_ORIGINS", "http://example.com")
    if "historical_k.api" in sys.modules:
        del sys.modules["historical_k.api"]
    import historical_k.api as api  # type: ignore
    importlib.reload(api)

    # Minimal artifact for a GET route
    logs = tmp_path / "logs" / "historical_k"
    logs.mkdir(parents=True)
    (logs / "k_t_series.csv").write_text("year,K\n1800,0.8\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    client = TestClient(api.app)
    # Simple GET with Origin header should echo Access-Control-Allow-Origin
    origin = "http://example.com"
    r = client.get("/k/series", headers={"Origin": origin})
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") == origin
    # Expose headers include ETag and X-Request-ID
    exposed = r.headers.get("access-control-expose-headers", "")
    low = exposed.lower()
    assert "etag" in low
    assert "x-request-id" in low
    assert "x-ratelimit-limit" in low
    assert "retry-after" in low

    # OPTIONS preflight
    pre = client.options(
        "/k/series",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
        },
    )
    assert pre.status_code in (200, 204)
    assert pre.headers.get("access-control-allow-origin") == origin
