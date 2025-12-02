"""Async Python client for the Historical K API (optional aiohttp).

This client mirrors a subset of the sync KApiClient, but uses aiohttp
when available. For testing, an `transport` coroutine may be provided to
route calls to an in-memory transport (e.g., FastAPI TestClient wrapper).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Callable, Awaitable
from urllib.parse import urljoin, urlsplit


try:  # pragma: no cover - covered via transport in tests
    import aiohttp
except Exception:  # pragma: no cover
    aiohttp = None  # type: ignore


@dataclass
class AsyncApiResponse:
    status: int
    etag: str | None
    content_type: str | None
    json_data: Optional[List[Dict[str, Any]]] = None
    text: Optional[str] = None
    content: Optional[bytes] = None


class AsyncKApiClient:
    def __init__(
        self,
        base_url: str = "http://localhost:8052",
        *,
        session: Optional["aiohttp.ClientSession"] = None,
        transport: Optional[Callable[[str, str, Dict[str, str], Dict[str, Any]], Awaitable[Any]]] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self._session = session
        self._transport = transport

    async def _ensure_session(self) -> "aiohttp.ClientSession":  # type: ignore
        if self._transport is not None:
            raise RuntimeError("Transport provided; no session required")
        if aiohttp is None:
            raise ImportError("aiohttp not installed")
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _get(self, path: str, *, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None):
        url = urljoin(self.base_url, path.lstrip("/"))
        if self._transport is not None:
            return await self._transport("GET", url, headers or {}, params or {})
        sess = await self._ensure_session()
        return await sess.get(url, headers=headers, params=params)

    async def get_series(self, *, as_json: bool = True, etag: Optional[str] = None) -> AsyncApiResponse:
        headers: Dict[str, str] = {}
        params: Dict[str, Any] = {}
        if not as_json:
            headers["Accept"] = "text/csv"
            params["as_json"] = False
        if etag:
            headers["If-None-Match"] = etag
        r = await self._get("/k/series", headers=headers, params=params)
        # Handle both aiohttp response and custom transport shim
        status = getattr(r, "status", getattr(r, "status_code", None))
        hdrs = getattr(r, "headers", {})
        ctype = hdrs.get("Content-Type") if isinstance(hdrs, dict) else r.headers.get("Content-Type")
        tag = hdrs.get("ETag") if isinstance(hdrs, dict) else r.headers.get("ETag")
        if status == 200:
            if as_json:
                data = await r.json() if hasattr(r, "json") else r.json()
                return AsyncApiResponse(status, tag, ctype, json_data=data)
            text = await r.text() if hasattr(r, "text") else r.text
            return AsyncApiResponse(status, tag, ctype, text=text)
        return AsyncApiResponse(status, tag, ctype)

    async def get_summary(self, *, etag: Optional[str] = None) -> AsyncApiResponse:
        headers: Dict[str, str] = {}
        if etag:
            headers["If-None-Match"] = etag
        r = await self._get("/k/summary", headers=headers)
        status = getattr(r, "status", getattr(r, "status_code", None))
        hdrs = getattr(r, "headers", {})
        ctype = hdrs.get("Content-Type") if isinstance(hdrs, dict) else r.headers.get("Content-Type")
        tag = hdrs.get("ETag") if isinstance(hdrs, dict) else r.headers.get("ETag")
        if status == 200:
            data = await r.json() if hasattr(r, "json") else r.json()
            # normalize into list like sync client
            payload = data if isinstance(data, list) else [data]
            return AsyncApiResponse(status, tag, ctype, json_data=payload)
        return AsyncApiResponse(status, tag, ctype)

    async def get_forecast(self, *, format: str = "auto", etag: Optional[str] = None) -> AsyncApiResponse:
        headers: Dict[str, str] = {}
        params: Dict[str, Any] = {"format": format}
        if etag:
            headers["If-None-Match"] = etag
        r = await self._get("/forecast", headers=headers, params=params)
        status = getattr(r, "status", getattr(r, "status_code", None))
        hdrs = getattr(r, "headers", {})
        ctype = hdrs.get("Content-Type") if isinstance(hdrs, dict) else r.headers.get("Content-Type")
        tag = hdrs.get("ETag") if isinstance(hdrs, dict) else r.headers.get("ETag")
        if status == 200:
            if ctype and "application/json" in ctype:
                data = await r.json() if hasattr(r, "json") else r.json()
                payload = data if isinstance(data, list) else [data]
                return AsyncApiResponse(status, tag, ctype, json_data=payload)
            content = await r.read() if hasattr(r, "read") else r.content
            return AsyncApiResponse(status, tag, ctype, content=content)
        return AsyncApiResponse(status, tag, ctype)

    async def get_regimes(self, *, etag: Optional[str] = None) -> AsyncApiResponse:
        headers: Dict[str, str] = {}
        if etag:
            headers["If-None-Match"] = etag
        r = await self._get("/regimes", headers=headers)
        status = getattr(r, "status", getattr(r, "status_code", None))
        hdrs = getattr(r, "headers", {})
        ctype = hdrs.get("Content-Type") if isinstance(hdrs, dict) else r.headers.get("Content-Type")
        tag = hdrs.get("ETag") if isinstance(hdrs, dict) else r.headers.get("ETag")
        if status == 200:
            text = await r.text() if hasattr(r, "text") else r.text
            return AsyncApiResponse(status, tag, ctype, text=text)
        return AsyncApiResponse(status, tag, ctype)

    async def get_plot(self, *, etag: Optional[str] = None) -> AsyncApiResponse:
        headers: Dict[str, str] = {}
        if etag:
            headers["If-None-Match"] = etag
        r = await self._get("/k/plot", headers=headers)
        status = getattr(r, "status", getattr(r, "status_code", None))
        hdrs = getattr(r, "headers", {})
        ctype = hdrs.get("Content-Type") if isinstance(hdrs, dict) else r.headers.get("Content-Type")
        tag = hdrs.get("ETag") if isinstance(hdrs, dict) else r.headers.get("ETag")
        if status == 200:
            content = await r.read() if hasattr(r, "read") else r.content
            return AsyncApiResponse(status, tag, ctype, content=content)
        return AsyncApiResponse(status, tag, ctype)

    async def close(self) -> None:
        if self._session is not None:
            await self._session.close()
