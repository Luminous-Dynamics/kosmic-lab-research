from __future__ import annotations

import importlib
import sys
from pathlib import Path

from fastapi.testclient import TestClient


def test_gzip_enabled_with_env(tmp_path: Path, monkeypatch) -> None:
    # Force small min-size so even tiny payloads get gzipped
    monkeypatch.setenv("KOSMIC_API_GZIP_MIN_SIZE", "1")
    if "historical_k.api" in sys.modules:
        del sys.modules["historical_k.api"]
    import historical_k.api as api  # type: ignore
    importlib.reload(api)

    # Prepare an artifact
    base = tmp_path / "logs" / "historical_k"
    base.mkdir(parents=True)
    (base / "k_t_series.csv").write_text("year,K\n" + "\n".join([f"{1800+i*10},1.0" for i in range(10)]), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    client = TestClient(api.app)
    r = client.get("/k/series", headers={"Accept-Encoding": "gzip"})
    assert r.status_code == 200
    assert r.headers.get("content-encoding") == "gzip"

