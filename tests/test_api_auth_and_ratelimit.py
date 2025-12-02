from __future__ import annotations

import importlib
import sys
from pathlib import Path

from fastapi.testclient import TestClient


def test_auth_optional(tmp_path: Path, monkeypatch) -> None:
    # With token set, /health stays public but /k/series requires auth
    monkeypatch.setenv("KOSMIC_API_TOKEN", "secret")
    if "historical_k.api" in sys.modules:
        del sys.modules["historical_k.api"]
    import historical_k.api as api  # type: ignore
    importlib.reload(api)

    (tmp_path / "logs" / "historical_k").mkdir(parents=True)
    (tmp_path / "logs" / "historical_k" / "k_t_series.csv").write_text("year,K\n1800,0.8\n", encoding="utf-8")
    from fastapi.testclient import TestClient

    monkeypatch.chdir(tmp_path)
    client = TestClient(api.app)

    # Public
    r = client.get("/health")
    assert r.status_code == 200

    # Protected (no token)
    r = client.get("/k/series")
    assert r.status_code == 401
    # With token (Authorization)
    r = client.get("/k/series", headers={"Authorization": "Bearer secret"})
    assert r.status_code == 200
    # With API key header
    r = client.get("/k/series", headers={"X-API-Key": "secret"})
    assert r.status_code == 200


def test_rate_limit_basic(tmp_path: Path, monkeypatch) -> None:
    # Limit to 2 requests per 60 seconds
    monkeypatch.setenv("KOSMIC_API_RATE_LIMIT", "2")
    monkeypatch.setenv("KOSMIC_API_RATE_WINDOW", "60")
    if "historical_k.api" in sys.modules:
        del sys.modules["historical_k.api"]
    import historical_k.api as api  # type: ignore
    importlib.reload(api)

    (tmp_path / "logs" / "historical_k").mkdir(parents=True)
    (tmp_path / "logs" / "historical_k" / "k_t_series.csv").write_text("year,K\n1800,0.8\n", encoding="utf-8")
    from fastapi.testclient import TestClient

    monkeypatch.chdir(tmp_path)
    client = TestClient(api.app)
    r1 = client.get("/k/series")
    # Headers should include rate limit info
    assert r1.headers.get("X-RateLimit-Limit") and r1.headers.get("X-RateLimit-Remaining")
    r2 = client.get("/k/series")
    assert r2.headers.get("X-RateLimit-Remaining") is not None
    r3 = client.get("/k/series")
    assert r1.status_code == 200 and r2.status_code == 200
    assert r3.status_code == 429
    assert r3.headers.get("retry-after")
    assert r3.json().get("error", {}).get("status_code") == 429
