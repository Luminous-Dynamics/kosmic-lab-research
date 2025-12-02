from __future__ import annotations

import importlib.util as _util
from typing import Any, Dict
from urllib.parse import urlsplit

import pytest
from fastapi.testclient import TestClient

from historical_k.api import app
from historical_k.async_client import AsyncKApiClient, AsyncApiResponse


def _build_async_transport(tc: TestClient):
    class _Shim:
        def __init__(self, r):
            self._r = r
            self.status = r.status_code
            self.headers = r.headers
        def json(self):
            return self._r.json()
        def text(self):
            return self._r.text

    async def _call(method: str, url: str, headers: Dict[str, str], params: Dict[str, Any]):
        us = urlsplit(url)
        path = us.path
        r = tc.request(method, path, headers=headers, params=params)
        return _Shim(r)

    return _call


@pytest.mark.asyncio
async def test_async_client_series(tmp_path, monkeypatch):
    # Prepare series file
    base = tmp_path / "logs" / "historical_k"
    base.mkdir(parents=True)
    (base / "k_t_series.csv").write_text("year,K\n1800,0.8\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    tc = TestClient(app)
    client = AsyncKApiClient("http://testserver", transport=_build_async_transport(tc))
    r1 = await client.get_series(as_json=True)
    assert isinstance(r1, AsyncApiResponse)
    assert r1.status == 200 and r1.etag
    r2 = await client.get_series(as_json=True, etag=r1.etag)
    assert r2.status == 304


@pytest.mark.asyncio
async def test_async_client_summary(tmp_path, monkeypatch):
    base = tmp_path / "logs" / "historical_k"
    base.mkdir(parents=True)
    (base / "k_t_summary.json").write_text('{"mean_K": 0.9}', encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    tc = TestClient(app)
    client = AsyncKApiClient("http://testserver", transport=_build_async_transport(tc))
    r1 = await client.get_summary()
    assert r1.status == 200 and r1.etag
    r2 = await client.get_summary(etag=r1.etag)
    assert r2.status == 304


@pytest.mark.asyncio
async def test_async_client_regimes_and_plot(tmp_path, monkeypatch):
    # Prepare regimes and plot
    (tmp_path / "logs" / "regimes").mkdir(parents=True)
    (tmp_path / "logs" / "historical_k").mkdir(parents=True)
    (tmp_path / "logs" / "regimes" / "regimes.csv").write_text("regime_id,start_year,end_year\n1,1800,1830\n", encoding="utf-8")
    (tmp_path / "logs" / "historical_k" / "k_t_plot.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    monkeypatch.chdir(tmp_path)
    tc = TestClient(app)
    client = AsyncKApiClient("http://testserver", transport=_build_async_transport(tc))
    rr = await client.get_regimes()
    assert rr.status == 200 and rr.text and "regime_id" in rr.text
    rp = await client.get_plot()
    assert rp.status == 200 and rp.content and len(rp.content) > 0
