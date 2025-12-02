from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from historical_k.api import app


def test_api_success_endpoints(tmp_path, monkeypatch) -> None:
    # Arrange: create expected artifact files under logs/
    logs = tmp_path / "logs"
    hk = logs / "historical_k"
    regimes = logs / "regimes"
    forecast = logs / "forecasting"
    hk.mkdir(parents=True)
    regimes.mkdir(parents=True)
    forecast.mkdir(parents=True)

    # Historical series CSV
    (hk / "k_t_series.csv").write_text("year,K\n1800,0.8\n1810,0.9\n", encoding="utf-8")
    # Summary JSON
    (hk / "k_t_summary.json").write_text('{\n  "mean_K": 0.85\n}\n', encoding="utf-8")
    # Plot placeholder file
    (hk / "k_t_plot.png").write_bytes(b"")

    # Regimes CSV
    (regimes / "regimes.csv").write_text(
        "regime_id,start_year,end_year\n1,1800,1830\n", encoding="utf-8"
    )
    # Forecast JSON
    (forecast / "forecast.json").write_text(
        '{\n  "years": [1820,1830], \n  "forecast": [0.9, 1.0], \n  "ci_lower": [0.8, 0.9], \n  "ci_upper": [1.0, 1.1]\n}\n',
        encoding="utf-8",
    )

    # Run under this temp cwd so API reads our logs/
    monkeypatch.chdir(tmp_path)
    client = TestClient(app)

    # Act & Assert
    r = client.get("/k/series")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    r = client.get("/k/summary")
    assert r.status_code == 200
    assert "mean_K" in r.json()
    # Caching headers present
    assert "etag" in {k.lower(): v for k, v in r.headers.items()}

    r = client.get("/k/plot")
    assert r.status_code == 200
    assert "etag" in {k.lower(): v for k, v in r.headers.items()}

    r = client.get("/regimes")
    assert r.status_code == 200
    assert "etag" in {k.lower(): v for k, v in r.headers.items()}

    r = client.get("/forecast")
    assert r.status_code == 200
