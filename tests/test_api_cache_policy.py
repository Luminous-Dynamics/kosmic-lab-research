from __future__ import annotations

import importlib
import sys
from pathlib import Path

from fastapi.testclient import TestClient


def test_weak_etag_and_cache_control(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("KOSMIC_API_ETAG", "weak")
    monkeypatch.setenv("KOSMIC_API_CACHE_SECONDS", "123")
    # Force fresh module import to pick up env
    if "historical_k.api" in sys.modules:
        del sys.modules["historical_k.api"]
    import historical_k.api as api  # type: ignore
    importlib.reload(api)

    # Prepare artifact
    base = tmp_path / "logs" / "historical_k"
    base.mkdir(parents=True)
    (base / "k_t_series.csv").write_text("year,K\n1800,0.8\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    client = TestClient(api.app)
    r = client.get("/k/series")
    assert r.status_code == 200
    cc = r.headers.get("Cache-Control", "")
    assert "max-age=123" in cc
    etag = r.headers.get("ETag", "")
    assert etag.startswith("W/")

