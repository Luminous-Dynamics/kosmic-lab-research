from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from historical_k.api import app


def test_meta_and_ready_shape(tmp_path: Path, monkeypatch) -> None:
    # Point API to empty logs structure
    (tmp_path / "logs").mkdir()
    monkeypatch.chdir(tmp_path)
    client = TestClient(app)

    # /meta returns artifact map with expected keys
    r_meta = client.get("/meta")
    assert r_meta.status_code == 200
    meta = r_meta.json()
    assert "version" in meta and "artifacts" in meta
    arts = meta["artifacts"]
    for key in ("k_series", "k_summary", "k_plot", "regimes", "forecast_json", "forecast_plot"):
        assert key in arts
        assert "path" in arts[key]
        assert isinstance(arts[key]["exists"], bool)

    # /ready always ok=True and reports missing list
    r_ready = client.get("/ready")
    assert r_ready.status_code == 200
    body = r_ready.json()
    assert body.get("ok") is True
    assert isinstance(body.get("missing"), list)

