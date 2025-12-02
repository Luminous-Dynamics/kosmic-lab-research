from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from historical_k.api import app


def test_head_series_returns_headers(tmp_path: Path, monkeypatch) -> None:
    base = tmp_path / "logs" / "historical_k"
    base.mkdir(parents=True)
    (base / "k_t_series.csv").write_text("year,K\n1800,0.8\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    client = TestClient(app)
    r = client.head("/k/series")
    assert r.status_code == 200
    assert "etag" in {k.lower(): v for k, v in r.headers.items()}

