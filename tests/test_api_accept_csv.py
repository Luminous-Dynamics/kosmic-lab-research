from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from historical_k.api import app


def test_series_respects_accept_header_csv(tmp_path: Path, monkeypatch) -> None:
    base = tmp_path / "logs" / "historical_k"
    base.mkdir(parents=True)
    (base / "k_t_series.csv").write_text("year,K\n1800,0.8\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    client = TestClient(app)

    r = client.get("/k/series", headers={"Accept": "text/csv"})
    assert r.status_code == 200
    assert "text/csv" in r.headers.get("content-type", "")
    assert r.text.startswith("year,K\n")
    # Vary header should include Accept to inform caches
    assert "accept" in (r.headers.get("vary", "").lower())
