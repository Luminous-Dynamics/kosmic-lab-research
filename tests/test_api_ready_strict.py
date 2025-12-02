from __future__ import annotations

import importlib
import sys
from pathlib import Path


def test_ready_strict_returns_503_when_missing(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("KOSMIC_API_STRICT_READY", "1")
    # ensure fresh import
    if "historical_k.api" in sys.modules:
        del sys.modules["historical_k.api"]
    import historical_k.api as api  # type: ignore
    importlib.reload(api)

    monkeypatch.chdir(tmp_path)
    from fastapi.testclient import TestClient

    client = TestClient(api.app)
    r = client.get("/ready")
    assert r.status_code == 503
    assert r.json().get("ok") is False


def test_ready_strict_ok_when_required_present(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("KOSMIC_API_STRICT_READY", "true")
    if "historical_k.api" in sys.modules:
        del sys.modules["historical_k.api"]
    import historical_k.api as api  # type: ignore
    importlib.reload(api)

    # Create required artifacts
    base = tmp_path / "logs" / "historical_k"
    base.mkdir(parents=True)
    (base / "k_t_series.csv").write_text("year,K\n1800,0.8\n", encoding="utf-8")
    (base / "k_t_summary.json").write_text("{\"mean_K\": 0.85}", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    from fastapi.testclient import TestClient

    client = TestClient(api.app)
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.json().get("ok") is True
