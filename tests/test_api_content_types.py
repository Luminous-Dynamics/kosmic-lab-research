from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from historical_k.api import app


def test_series_csv_content_type(tmp_path: Path, monkeypatch) -> None:
    base = tmp_path / "logs" / "historical_k"
    base.mkdir(parents=True)
    (base / "k_t_series.csv").write_text("year,K\n1800,0.8\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    client = TestClient(app)
    r = client.get("/k/series", params={"as_json": False})
    assert r.status_code == 200
    assert "text/csv" in r.headers.get("content-type", "")
    assert "year,K" in r.text
    # Download disposition when requested
    r2 = client.get("/k/series", params={"as_json": False, "download": True})
    assert r2.status_code == 200
    assert "attachment" in r2.headers.get("content-disposition", "").lower()


def test_regimes_csv_content_type(tmp_path: Path, monkeypatch) -> None:
    base = tmp_path / "logs" / "regimes"
    base.mkdir(parents=True)
    (base / "regimes.csv").write_text("regime_id,start_year,end_year\n1,1800,1830\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    client = TestClient(app)
    r = client.get("/regimes", params={"download": True})
    assert r.status_code == 200
    assert "text/csv" in r.headers.get("content-type", "")
    # Content-Disposition present when download requested
    assert "attachment" in r.headers.get("content-disposition", "").lower()


def test_plot_png_content_type(tmp_path: Path, monkeypatch) -> None:
    base = tmp_path / "logs" / "historical_k"
    base.mkdir(parents=True)
    (base / "k_t_plot.png").write_bytes(b"")
    monkeypatch.chdir(tmp_path)
    client = TestClient(app)
    r = client.get("/k/plot", params={"download": True})
    assert r.status_code == 200
    assert "image/png" in r.headers.get("content-type", "")
    assert "attachment" in r.headers.get("content-disposition", "").lower()


def test_forecast_prefers_json_then_png(tmp_path: Path, monkeypatch) -> None:
    base = tmp_path / "logs" / "forecasting"
    base.mkdir(parents=True)
    # Both present: JSON should take precedence
    (base / "forecast.json").write_text('{"years":[2030],"forecast":[1.0],"ci_lower":[0.9],"ci_upper":[1.1]}', encoding="utf-8")
    (base / "forecast_plot.png").write_bytes(b"")
    monkeypatch.chdir(tmp_path)
    client = TestClient(app)
    r_json = client.get("/forecast")
    assert r_json.status_code == 200
    assert "application/json" in r_json.headers.get("content-type", "")

    # Remove JSON to fallback to PNG
    (base / "forecast.json").unlink()
    r_png = client.get("/forecast")
    assert r_png.status_code == 200
    assert "image/png" in r_png.headers.get("content-type", "")


def test_forecast_format_param(tmp_path: Path, monkeypatch) -> None:
    base = tmp_path / "logs" / "forecasting"
    base.mkdir(parents=True)
    (base / "forecast.json").write_text('{"years":[2030],"forecast":[1.0],"ci_lower":[0.9],"ci_upper":[1.1]}', encoding="utf-8")
    (base / "forecast_plot.png").write_bytes(b"")
    monkeypatch.chdir(tmp_path)
    client = TestClient(app)

    # Explicit JSON
    rj = client.get("/forecast", params={"format": "json"})
    assert rj.status_code == 200
    assert "application/json" in rj.headers.get("content-type", "")

    # Explicit plot
    rp = client.get("/forecast", params={"format": "plot"})
    assert rp.status_code == 200
    assert "image/png" in rp.headers.get("content-type", "")

    # Remove plot and request plot strictly → 404
    (base / "forecast_plot.png").unlink()
    r404 = client.get("/forecast", params={"format": "plot"})
    assert r404.status_code == 404


def test_forecast_download_disposition(tmp_path: Path, monkeypatch) -> None:
    base = tmp_path / "logs" / "forecasting"
    base.mkdir(parents=True)
    # Only plot present to force PNG path
    (base / "forecast_plot.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    monkeypatch.chdir(tmp_path)
    client = TestClient(app)
    r = client.get("/forecast", params={"download": True})
    assert r.status_code == 200
    assert "image/png" in r.headers.get("content-type", "")
    assert "attachment" in r.headers.get("content-disposition", "").lower()
