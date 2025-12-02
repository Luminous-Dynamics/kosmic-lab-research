from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any, Dict
from urllib.parse import urlsplit

from fastapi.testclient import TestClient

from historical_k.client import KApiClient
import historical_k.api as api


class _RespShim:
    def __init__(self, resp) -> None:
        self._r = resp
        self.status_code = resp.status_code
        self.headers = resp.headers

    def json(self) -> Any:  # type: ignore[override]
        return self._r.json()

    @property
    def text(self) -> str:  # type: ignore[override]
        return self._r.text

    @property
    def content(self) -> bytes:  # type: ignore[override]
        return self._r.content


def _asgi_transport(client: TestClient):
    def _call(method: str, url: str, *, headers: Dict[str, str], params: Dict[str, Any]):
        us = urlsplit(url)
        path = us.path
        r = client.request(method, path, headers=headers, params=params)
        return _RespShim(r)

    return _call


def test_client_series_etag_roundtrip(tmp_path: Path, monkeypatch) -> None:
    # Prepare artifacts
    base = tmp_path / "logs" / "historical_k"
    base.mkdir(parents=True)
    (base / "k_t_series.csv").write_text("year,K\n1800,0.8\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    # Fresh import not required here; app picks cwd at runtime
    tc = TestClient(api.app)
    client = KApiClient("http://testserver", transport=_asgi_transport(tc))

    r1 = client.get_series(as_json=True)
    assert r1.status_code == 200
    assert r1.etag
    assert isinstance(r1.json_data, list)

    r2 = client.get_series(as_json=True, etag=r1.etag)
    assert r2.status_code == 304


def test_client_series_csv(tmp_path: Path, monkeypatch) -> None:
    base = tmp_path / "logs" / "historical_k"
    base.mkdir(parents=True)
    (base / "k_t_series.csv").write_text("year,K\n1800,0.8\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    tc = TestClient(api.app)
    client = KApiClient("http://testserver", transport=_asgi_transport(tc))
    r = client.get_series(as_json=False)
    assert r.status_code == 200
    assert r.text and r.text.startswith("year,K")

