from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from historical_k.api import app


def test_missing_series_returns_json_error(tmp_path: Path, monkeypatch) -> None:
    # Ensure logs path exists but no series file
    (tmp_path / "logs" / "historical_k").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    client = TestClient(app)
    r = client.get("/k/series")
    assert r.status_code == 404
    body = r.json()
    assert "error" in body and isinstance(body["error"], dict)
    assert body["error"].get("status_code") == 404
    # Request-ID header should be present (auto-generated)
    assert r.headers.get("x-request-id")

