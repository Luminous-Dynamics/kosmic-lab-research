from __future__ import annotations

import time
from pathlib import Path

from fastapi.testclient import TestClient

from historical_k.api import app


def test_etag_caching_for_series(tmp_path: Path, monkeypatch) -> None:
    # Arrange
    logs = tmp_path / "logs" / "historical_k"
    logs.mkdir(parents=True)
    (logs / "k_t_series.csv").write_text("year,K\n1800,0.8\n1810,0.9\n", encoding="utf-8")

    # Ensure API reads from our temp cwd
    monkeypatch.chdir(tmp_path)
    client = TestClient(app)

    # First request returns 200 with ETag
    r1 = client.get("/k/series")
    assert r1.status_code == 200
    etag = r1.headers.get("ETag")
    assert etag
    # If-Modified-Since using server's Last-Modified should also yield 304
    last_mod = r1.headers.get("Last-Modified")

    # Second request with If-None-Match should be 304
    r2 = client.get("/k/series", headers={"If-None-Match": etag})
    assert r2.status_code == 304
    # Conditional GET with If-Modified-Since
    if last_mod:
        r3 = client.get("/k/series", headers={"If-Modified-Since": last_mod})
        assert r3.status_code == 304


def test_etag_caching_for_regimes_and_forecast(tmp_path: Path, monkeypatch) -> None:
    # Arrange
    base = tmp_path / "logs"
    (base / "regimes").mkdir(parents=True)
    (base / "forecasting").mkdir(parents=True)
    # Minimal artifacts
    (base / "regimes" / "regimes.csv").write_text(
        "regime_id,start_year,end_year\n1,1800,1830\n", encoding="utf-8"
    )
    (base / "forecasting" / "forecast.json").write_text(
        '{"years":[1820],"forecast":[1.0],"ci_lower":[0.9],"ci_upper":[1.1]}',
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    client = TestClient(app)

    # Regimes
    r1 = client.get("/regimes")
    assert r1.status_code == 200
    etag_r = r1.headers.get("ETag")
    assert etag_r
    r2 = client.get("/regimes", headers={"If-None-Match": etag_r})
    assert r2.status_code == 304

    # Forecast JSON
    f1 = client.get("/forecast")
    assert f1.status_code == 200
    etag_f = f1.headers.get("ETag")
    assert etag_f
    f2 = client.get("/forecast", headers={"If-None-Match": etag_f})
    assert f2.status_code == 304


def test_etag_caching_for_summary(tmp_path: Path, monkeypatch) -> None:
    base = tmp_path / "logs" / "historical_k"
    base.mkdir(parents=True)
    (base / "k_t_summary.json").write_text('{"mean_K": 0.85}', encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    client = TestClient(app)
    r1 = client.get("/k/summary")
    assert r1.status_code == 200
    etag = r1.headers.get("ETag")
    assert etag
    r2 = client.get("/k/summary", headers={"If-None-Match": etag})
    assert r2.status_code == 304
    # If-Modified-Since support
    last_mod = r1.headers.get("Last-Modified")
    if last_mod:
        r3 = client.get("/k/summary", headers={"If-Modified-Since": last_mod})
        assert r3.status_code == 304


def test_headers_for_file_caches_strong_etag(tmp_path: Path, monkeypatch) -> None:
    from historical_k import api as hk_api

    hk_api._ETAG_CACHE.clear()
    hk_api._ETAG_CACHE_LOCK = hk_api.threading.Lock()
    path = tmp_path / "k_t_series.csv"
    path.write_text("year,K\n1800,0.8\n", encoding="utf-8")

    calls = 0
    orig_sha256 = hk_api.hashlib.sha256

    def counting(data=b""):
        nonlocal calls
        calls += 1
        return orig_sha256(data)

    monkeypatch.setattr(hk_api.hashlib, "sha256", counting)

    hk_api._headers_for_file(path)
    hk_api._headers_for_file(path)
    assert calls == 1  # cached on second call

    time.sleep(0.01)
    path.write_text("year,K\n1800,1.0\n", encoding="utf-8")
    hk_api._headers_for_file(path)
    assert calls == 2  # recalculated after file changed


def test_headers_for_file_uses_cache_lock(tmp_path: Path, monkeypatch) -> None:
    from historical_k import api as hk_api

    class FakeLock:
        def __init__(self) -> None:
            self.used = 0

        def __enter__(self):
            self.used += 1

        def __exit__(self, exc_type, exc, tb):
            self.used -= 1

    hk_api._ETAG_CACHE.clear()
    lock = FakeLock()
    hk_api._ETAG_CACHE_LOCK = lock
    path = tmp_path / "k_t_series.csv"
    path.write_text("year,K\n1800,0.8\n", encoding="utf-8")
    hk_api._headers_for_file(path)
    assert lock.used == 0  # lock released


def test_etag_cache_eviction_limit(tmp_path: Path, monkeypatch) -> None:
    from historical_k import api as hk_api

    hk_api._ETAG_CACHE_LIMIT = 1
    hk_api._ETAG_CACHE.clear()
    hk_api._ETAG_CACHE_LOCK = hk_api.threading.Lock()

    path1 = tmp_path / "a.csv"
    path2 = tmp_path / "b.csv"
    path1.write_text("x\n1\n", encoding="utf-8")
    path2.write_text("x\n2\n", encoding="utf-8")

    hk_api._headers_for_file(path1)
    hk_api._headers_for_file(path2)
    assert len(hk_api._ETAG_CACHE) == 1
    assert next(iter(hk_api._ETAG_CACHE.keys())) == str(path2.resolve())
