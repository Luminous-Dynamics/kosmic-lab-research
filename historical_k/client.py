"""Minimal Python client for the Historical K API.

Features:
- Convenience helpers for common endpoints
- Optional ETag round-trips via `etag` parameter
- Content negotiation for `/k/series` (JSON or CSV)

Example:
    >>> from historical_k.client import KApiClient
    >>> api = KApiClient("http://localhost:8052")
    >>> resp = api.get_series(as_json=True)
    >>> resp.status_code, resp.etag, len(resp.json_data or [])
    (200, 'abc...', 22)
    >>> # Conditional GET using ETag (may return 304 with no body)
    >>> resp2 = api.get_series(as_json=True, etag=resp.etag)
    >>> resp2.status_code
    304
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlsplit

import requests
from requests.adapters import HTTPAdapter
try:
    # urllib3 Retry available via requests' vendored urllib3 in many environments
    from urllib3.util.retry import Retry  # type: ignore
except Exception:  # pragma: no cover - fallback minimal shim
    class Retry:  # type: ignore
        def __init__(self, total=0, backoff_factor=0.0, status_forcelist=None):
            self.total = total


@dataclass
class ApiResponse:
    status_code: int
    etag: str | None
    content_type: str | None
    json_data: Optional[List[Dict[str, Any]]] = None
    text: Optional[str] = None
    content: Optional[bytes] = None


class KApiClient:
    def __init__(
        self,
        base_url: str = "http://localhost:8052",
        *,
        session: Optional[requests.Session] = None,
        transport: Optional[callable] = None,
        retries: int = 0,
        backoff_factor: float = 0.2,
    ) -> None:
        """
        Initialize client.

        Args:
            base_url: Server base URL
            session: Optional requests.Session for connection pooling
            transport: Optional (method, url, **kwargs) -> Response shim for testing
        """
        self.base_url = base_url.rstrip("/") + "/"
        self._session = session or requests.Session()
        self._transport = transport
        if retries and self._transport is None:
            retry = Retry(
                total=retries,
                backoff_factor=backoff_factor,
                status_forcelist=(429, 500, 502, 503, 504),
            )
            adapter = HTTPAdapter(max_retries=retry)
            self._session.mount("http://", adapter)
            self._session.mount("https://", adapter)

    # ---------------
    # Low-level GET
    # ---------------
    def _get(self, path: str, *, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        url = urljoin(self.base_url, path.lstrip("/"))
        if self._transport is not None:
            # For tests: use provided transport callable
            return self._transport("GET", url, headers=headers or {}, params=params or {})
        return self._session.get(url, headers=headers, params=params, timeout=10)

    # ---------------
    # Public endpoints
    # ---------------
    def get_series(self, *, as_json: bool = True, etag: Optional[str] = None) -> ApiResponse:
        headers: Dict[str, str] = {}
        params: Dict[str, Any] = {}
        if as_json:
            # Default JSON
            pass
        else:
            headers["Accept"] = "text/csv"
            params["as_json"] = False  # explicit override to be safe
        if etag:
            headers["If-None-Match"] = etag
        r = self._get("/k/series", headers=headers, params=params)
        ctype = r.headers.get("Content-Type")
        et = r.headers.get("ETag")
        if r.status_code == 200:
            if as_json:
                return ApiResponse(r.status_code, et, ctype, json_data=r.json())
            return ApiResponse(r.status_code, et, ctype, text=r.text)
        return ApiResponse(r.status_code, et, ctype)

    def get_summary(self, *, etag: Optional[str] = None) -> ApiResponse:
        headers: Dict[str, str] = {}
        if etag:
            headers["If-None-Match"] = etag
        r = self._get("/k/summary", headers=headers)
        ctype = r.headers.get("Content-Type")
        et = r.headers.get("ETag")
        if r.status_code == 200:
            return ApiResponse(r.status_code, et, ctype, json_data=[r.json()])
        return ApiResponse(r.status_code, et, ctype)

    def get_regimes(self, *, etag: Optional[str] = None) -> ApiResponse:
        headers: Dict[str, str] = {}
        if etag:
            headers["If-None-Match"] = etag
        r = self._get("/regimes", headers=headers)
        ctype = r.headers.get("Content-Type")
        et = r.headers.get("ETag")
        if r.status_code == 200:
            return ApiResponse(r.status_code, et, ctype, text=r.text)
        return ApiResponse(r.status_code, et, ctype)

    def get_plot(self, *, etag: Optional[str] = None) -> ApiResponse:
        headers: Dict[str, str] = {}
        if etag:
            headers["If-None-Match"] = etag
        r = self._get("/k/plot", headers=headers)
        ctype = r.headers.get("Content-Type")
        et = r.headers.get("ETag")
        if r.status_code == 200:
            return ApiResponse(r.status_code, et, ctype, content=r.content)
        return ApiResponse(r.status_code, et, ctype)

    def get_forecast(self, *, format: str = "auto", etag: Optional[str] = None) -> ApiResponse:
        headers: Dict[str, str] = {}
        params: Dict[str, Any] = {"format": format}
        if etag:
            headers["If-None-Match"] = etag
        r = self._get("/forecast", headers=headers, params=params)
        ctype = r.headers.get("Content-Type")
        et = r.headers.get("ETag")
        if r.status_code == 200:
            if ctype and "application/json" in ctype:
                return ApiResponse(r.status_code, et, ctype, json_data=[r.json()])
            return ApiResponse(r.status_code, et, ctype, content=r.content)
        return ApiResponse(r.status_code, et, ctype)

    def get_meta(self) -> Dict[str, Any]:
        r = self._get("/meta")
        r.raise_for_status()
        return r.json()

    def get_info(self) -> Dict[str, Any]:
        r = self._get("/info")
        r.raise_for_status()
        return r.json()
