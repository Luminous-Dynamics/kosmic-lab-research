from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from historical_k.api import app


def test_request_id_header_generated(tmp_path: Path, monkeypatch) -> None:
    base = tmp_path / "logs" / "historical_k"
    base.mkdir(parents=True)
    (base / "k_t_series.csv").write_text("year,K\n1800,0.8\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    client = TestClient(app)
    r = client.get("/k/series")
    assert r.status_code == 200
    assert r.headers.get("x-request-id")


def test_request_id_header_echo(tmp_path: Path, monkeypatch) -> None:
    base = tmp_path / "logs" / "historical_k"
    base.mkdir(parents=True)
    (base / "k_t_series.csv").write_text("year,K\n1800,0.8\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    client = TestClient(app)
    rid = "test-req-123"
    r = client.get("/k/series", headers={"X-Request-ID": rid})
    assert r.status_code == 200
    assert r.headers.get("x-request-id") == rid

