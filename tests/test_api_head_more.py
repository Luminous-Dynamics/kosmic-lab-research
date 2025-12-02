from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from historical_k.api import app


def test_head_regimes_headers(tmp_path: Path, monkeypatch) -> None:
    base = tmp_path / "logs" / "regimes"
    base.mkdir(parents=True)
    (base / "regimes.csv").write_text("regime_id,start_year,end_year\n1,1800,1830\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    client = TestClient(app)
    r = client.head("/regimes")
    assert r.status_code == 200
    assert "etag" in {k.lower(): v for k, v in r.headers.items()}


def test_head_forecast_headers(tmp_path: Path, monkeypatch) -> None:
    base = tmp_path / "logs" / "forecasting"
    base.mkdir(parents=True)
    (base / "forecast.json").write_text('{"years":[2030],"forecast":[1.0],"ci_lower":[0.9],"ci_upper":[1.1]}', encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    client = TestClient(app)
    r = client.head("/forecast")
    # FastAPI routes handle HEAD like GET without body
    assert r.status_code == 200
    assert "etag" in {k.lower(): v for k, v in r.headers.items()}


def test_head_summary_headers(tmp_path: Path, monkeypatch) -> None:
    base = tmp_path / "logs" / "historical_k"
    base.mkdir(parents=True)
    (base / "k_t_summary.json").write_text("{\"mean_K\": 0.85}", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    client = TestClient(app)
    r = client.head("/k/summary")
    assert r.status_code == 200
    assert "etag" in {k.lower(): v for k, v in r.headers.items()}


def test_head_series_bypasses_body_load(tmp_path: Path, monkeypatch) -> None:
    base = tmp_path / "logs" / "historical_k"
    base.mkdir(parents=True)
    (base / "k_t_series.csv").write_text("year,K\n1800,0.8\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    # Raise if read_csv is invoked (HEAD should not read body)
    def boom(*args, **kwargs):
        raise AssertionError("read_csv should not be called for HEAD")

    monkeypatch.setattr("historical_k.api.pd.read_csv", boom)
    client = TestClient(app)
    r = client.head("/k/series")
    assert r.status_code == 200
    assert "etag" in {k.lower(): v for k, v in r.headers.items()}
