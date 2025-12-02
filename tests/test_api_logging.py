from __future__ import annotations

import logging
from pathlib import Path

from fastapi.testclient import TestClient

from historical_k.api import app


def test_access_log_contains_request_id(tmp_path: Path, monkeypatch, caplog) -> None:
    base = tmp_path / "logs" / "historical_k"
    base.mkdir(parents=True)
    (base / "k_t_series.csv").write_text("year,K\n1800,0.8\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    caplog.set_level(logging.INFO, logger="historical_k.api")
    client = TestClient(app)
    r = client.get("/k/series")
    assert r.status_code == 200
    # Ensure at least one access log record was emitted
    assert any("http_access" in rec.message for rec in caplog.records)

