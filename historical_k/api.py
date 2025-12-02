"""
FastAPI service exposing Historical K(t) artifacts.

Endpoints provide access to the latest computed results under logs/.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional
import hashlib
from email.utils import format_datetime
from datetime import datetime, timezone
import os

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from uuid import uuid4
import logging
import time
from collections import defaultdict, deque, OrderedDict
import threading
from pydantic import BaseModel
import importlib.metadata as _meta

# Allow overriding logs directory via environment for flexible deployment/testing
LOGS = Path(os.environ.get("KOSMIC_LOGS_DIR", "logs")).resolve()
# ETag mode (strong: sha256 of file; weak: mtime/size)
ETAG_MODE = os.environ.get("KOSMIC_API_ETAG", "strong").lower()
CACHE_SECONDS = int(os.environ.get("KOSMIC_API_CACHE_SECONDS", "60"))
LOG_JSON = os.environ.get("KOSMIC_API_LOG_JSON", "1").lower() in {"1", "true", "yes"}
_RATE_LIMIT = int(os.environ.get("KOSMIC_API_RATE_LIMIT", "0") or 0)
_RATE_WINDOW = int(os.environ.get("KOSMIC_API_RATE_WINDOW", "60") or 60)
_PUBLIC_PATHS = set((os.environ.get("KOSMIC_API_PUBLIC_PATHS") or "/health,/ready,/meta,/info").split(","))
_API_TOKEN = os.environ.get("KOSMIC_API_TOKEN")
_ETAG_CACHE_LIMIT = max(1, int(os.environ.get("KOSMIC_API_ETAG_CACHE_LIMIT", "256") or 256))
_ETAG_CACHE: "OrderedDict[str, tuple[int, int, str]]" = OrderedDict()
_ETAG_CACHE_LOCK = threading.Lock()
_ETAG_CACHE_HITS = 0
_ETAG_CACHE_MISSES = 0
_ETAG_CACHE_EVICTIONS = 0

class HealthModel(BaseModel):
    status: str


class ForecastModel(BaseModel):
    method: str
    years: List[int]
    forecast: List[float]
    ci_lower: List[float]
    ci_upper: List[float]


class SummaryModel(BaseModel):
    mean_K: float
    ci_low: float
    ci_high: float
    years: List[int]
    bootstrap_samples: int
    per_year: bool
    normalization: str
    feature_aggregation: str
    weights: Dict[str, float] = {}
    ci_low_yearly: Optional[List[float]] = None
    ci_high_yearly: Optional[List[float]] = None
    
class ReadyModel(BaseModel):
    ok: bool
    missing: List[str]
    notes: Optional[str] = None


class ErrorPayload(BaseModel):
    status_code: int
    detail: str
    request_id: Optional[str] = None


class ErrorModel(BaseModel):
    error: ErrorPayload


class FileInfo(BaseModel):
    exists: bool
    path: str
    etag: str
    last_modified: str
    size: int


class MetaConfig(BaseModel):
    logs_dir: str
    etag_mode: str
    cache_seconds: int
    cors_enabled: bool
    cors_origins: List[str]
    git_commit: str


class MetaModel(BaseModel):
    version: str
    config: MetaConfig
    artifacts: Dict[str, FileInfo]

tags_metadata = [
    {"name": "health", "description": "Basic health/readiness info"},
    {"name": "artifacts", "description": "Historical K artifacts and forecasts"},
    {"name": "meta", "description": "Service configuration and artifact inventory"},
]

_PKG_VERSION = "0.1.0"
try:
    _PKG_VERSION = _meta.version("kosmic-lab")
except Exception:
    pass

app = FastAPI(
    title="Kosmic Lab Historical K API",
    description="Serve Historical K(t) series, summaries, plots, regimes, and forecasts",
    version=_PKG_VERSION,
    contact={
        "name": "Kosmic Lab Team",
        "email": "kosmic-lab@example.org",
        "url": "https://github.com/Luminous-Dynamics/kosmic-lab",
    },
    openapi_tags=tags_metadata,
)

# Enable gzip compression for larger responses (configurable)
_GZIP_MIN = int(os.environ.get("KOSMIC_API_GZIP_MIN_SIZE", "512") or 512)
app.add_middleware(GZipMiddleware, minimum_size=_GZIP_MIN)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach an X-Request-ID header to every response.

    - If the client supplies X-Request-ID, we forward it back.
    - Otherwise, we generate a UUIDv4.
    """

    async def dispatch(self, request, call_next):  # type: ignore[override]
        req_id = request.headers.get("X-Request-ID") or str(uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        return response


app.add_middleware(RequestIDMiddleware)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):  # type: ignore[override]
        response = await call_next(request)
        # Minimal safe defaults
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("X-XSS-Protection", "0")  # modern browsers disable XSS auditor
        return response


app.add_middleware(SecurityHeadersMiddleware)


_logger = logging.getLogger("historical_k.api")
if not _logger.handlers:
    logging.basicConfig(level=logging.INFO)

_START_TIME = time.time()


class AccessLogMiddleware(BaseHTTPMiddleware):
    # Simple in-process counters for Prometheus-style metrics
    HTTP_REQUESTS: dict[tuple[str, str, int], int] = defaultdict(int)
    _LOCK = threading.Lock()
    # Duration histogram (milliseconds)
    DURATION_BUCKETS = [5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000]
    DURATION_COUNTS: dict[int, int] = defaultdict(int)  # keyed by bucket upper bound
    DURATION_SUM: float = 0.0
    DURATION_COUNT: int = 0

    async def dispatch(self, request, call_next):  # type: ignore[override]
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = int((time.perf_counter() - start) * 1000)
        rid = response.headers.get("X-Request-ID") or ""
        record = {
            "event": "http_access",
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": duration_ms,
            "request_id": rid,
            "etag": response.headers.get("ETag", ""),
        }
        # Add Server-Timing for client-side diagnostics
        response.headers["Server-Timing"] = f"app;dur={duration_ms}"
        # Increment request counters
        try:
            key = (request.method, request.url.path, response.status_code)
            with self._LOCK:
                self.HTTP_REQUESTS[key] += 1
                # Update histogram
                # Find first bucket >= duration
                b = None
                for ub in self.DURATION_BUCKETS:
                    if duration_ms <= ub:
                        b = ub
                        break
                if b is None:
                    # overflow bucket represented by -1
                    b = -1
                self.DURATION_COUNTS[b] += 1
                self.DURATION_SUM += float(duration_ms)
                self.DURATION_COUNT += 1
        except Exception:
            pass
        if LOG_JSON:
            try:
                _logger.info(json.dumps(record, sort_keys=True))
            except Exception:
                _logger.info("http_access %s", record)
        else:
            _logger.info(
                "%s %s -> %s (%d ms) rid=%s",
                record["method"],
                record["path"],
                record["status"],
                record["duration_ms"],
                record["request_id"],
            )
        return response


app.add_middleware(AccessLogMiddleware)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    req_id = request.headers.get("X-Request-ID") or ""
    payload = ErrorModel(error=ErrorPayload(status_code=exc.status_code, detail=str(exc.detail), request_id=req_id))
    resp = JSONResponse(status_code=exc.status_code, content=payload.model_dump())
    if req_id:
        resp.headers["X-Request-ID"] = req_id
    return resp


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    req_id = request.headers.get("X-Request-ID") or ""
    payload = ErrorModel(error=ErrorPayload(status_code=500, detail="Internal Server Error", request_id=req_id))
    resp = JSONResponse(status_code=500, content=payload.model_dump())
    if req_id:
        resp.headers["X-Request-ID"] = req_id
    return resp


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):  # type: ignore[override]
        # Skip auth if no token configured or path is public
        if not _API_TOKEN:
            return await call_next(request)
        path = request.url.path
        if any(path.startswith(p) for p in _PUBLIC_PATHS):
            return await call_next(request)
        # Accept either Authorization: Bearer <token> or X-API-Key: <token>
        auth = request.headers.get("authorization", "")
        api_key = request.headers.get("x-api-key")
        ok = False
        if auth.lower().startswith("bearer ") and auth.split(" ", 1)[1] == _API_TOKEN:
            ok = True
        if api_key == _API_TOKEN:
            ok = True
        if not ok:
            payload = ErrorModel(
                error=ErrorPayload(status_code=401, detail="Unauthorized", request_id=request.headers.get("X-Request-ID") or "")
            )
            resp = JSONResponse(status_code=401, content=payload.model_dump())
            resp.headers["WWW-Authenticate"] = "Bearer"
            return resp
        return await call_next(request)


app.add_middleware(AuthMiddleware)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):  # type: ignore[override]
        super().__init__(app)
        self.buckets: dict[str, deque[float]] = defaultdict(deque)

    def _is_public(self, path: str) -> bool:
        return any(path.startswith(p) for p in _PUBLIC_PATHS)

    async def dispatch(self, request, call_next):  # type: ignore[override]
        if _RATE_LIMIT <= 0:
            return await call_next(request)
        path = request.url.path
        if self._is_public(path):
            return await call_next(request)
        # Identify client (X-Forwarded-For first IP fallback to peer)
        fwd = request.headers.get("x-forwarded-for")
        key = (fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else "unknown"))
        now = time.time()
        bucket = self.buckets[key]
        # prune
        while bucket and now - bucket[0] > _RATE_WINDOW:
            bucket.popleft()
        if len(bucket) >= _RATE_LIMIT:
            retry_after = max(1, _RATE_WINDOW - int(now - bucket[0]))
            payload = ErrorModel(
                error=ErrorPayload(status_code=429, detail="Too Many Requests", request_id=request.headers.get("X-Request-ID") or "")
            )
            resp = JSONResponse(status_code=429, content=payload.model_dump())
            resp.headers["Retry-After"] = str(retry_after)
            resp.headers["X-RateLimit-Limit"] = str(_RATE_LIMIT)
            resp.headers["X-RateLimit-Remaining"] = "0"
            return resp
        bucket.append(now)
        resp = await call_next(request)
        resp.headers["X-RateLimit-Limit"] = str(_RATE_LIMIT)
        resp.headers["X-RateLimit-Remaining"] = str(max(0, _RATE_LIMIT - len(bucket)))
        return resp


app.add_middleware(RateLimitMiddleware)


def _customize_openapi_security(schema: dict) -> dict:
    # Inject securitySchemes and per-operation security requirements if token configured
    components = schema.setdefault("components", {})
    sec = components.setdefault("securitySchemes", {})
    sec.setdefault(
        "HTTPBearer",
        {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
    )
    sec.setdefault(
        "ApiKeyAuth",
        {"type": "apiKey", "in": "header", "name": "X-API-Key"},
    )
    # Apply operation-level security when token configured; keep public paths open
    if _API_TOKEN:
        for path, ops in schema.get("paths", {}).items():
            for method, op in ops.items():
                if not isinstance(op, dict):
                    continue
                if any(path.startswith(p) for p in _PUBLIC_PATHS):
                    op["security"] = []
                else:
                    op["security"] = [{"HTTPBearer": []}, {"ApiKeyAuth": []}]
    return schema


_OPENAPI_CACHE: dict | None = None


def custom_openapi():
    global _OPENAPI_CACHE
    if _OPENAPI_CACHE is not None:
        return _OPENAPI_CACHE
    from fastapi.openapi.utils import get_openapi

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
    )
    schema = _customize_openapi_security(schema)
    app.openapi_schema = schema
    _OPENAPI_CACHE = schema
    return schema


# Override FastAPI openapi generator
app.openapi = custom_openapi  # type: ignore[assignment]


@app.get("/", tags=["meta"])  # root convenience
def index() -> JSONResponse:
    """Return version and top-level links for quick discovery."""
    base = ""
    links = {
        "health": "/health",
        "ready": "/ready",
        "meta": "/meta",
        "info": "/info",
        "docs": "/docs",
        "redoc": "/redoc",
        "series": "/k/series",
        "summary": "/k/summary",
        "plot": "/k/plot",
        "regimes": "/regimes",
        "forecast": "/forecast",
    }
    payload = {"version": app.version, "_links": links}
    resp = JSONResponse(payload)
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.get("/metrics", tags=["meta"])  # Prometheus exposition (best-effort)
def metrics() -> PlainTextResponse:
    """Return simple Prometheus-style metrics for HTTP requests.

    Format:
      # TYPE http_requests_total counter
      http_requests_total{path="/health",method="GET",status="200"} 3
    """
    lines = ["# TYPE http_requests_total counter"]
    with AccessLogMiddleware._LOCK:
        snapshot = dict(AccessLogMiddleware.HTTP_REQUESTS)
        counts = dict(AccessLogMiddleware.DURATION_COUNTS)
        sum_ms = AccessLogMiddleware.DURATION_SUM
        total = AccessLogMiddleware.DURATION_COUNT
    with _ETAG_CACHE_LOCK:
        cache_hits = _ETAG_CACHE_HITS
        cache_misses = _ETAG_CACHE_MISSES
        cache_evictions = _ETAG_CACHE_EVICTIONS
        cache_size = len(_ETAG_CACHE)
    for (method, path, status), count in sorted(snapshot.items()):
        # Sanitize quotes in path if any
        p = path.replace("\\", "\\\\").replace("\"", "\\\"")
        lines.append(
            f'http_requests_total{{path="{p}",method="{method}",status="{status}"}} {count}'
        )
    # Service info (version + git commit)
    lines.append(
        f'kosmic_app_info{{version="{app.version}",git_commit="{_infer_git_sha()}"}} 1'
    )
    # Uptime in seconds
    uptime = int(max(0, time.time() - _START_TIME))
    lines.append(f"kosmic_uptime_seconds {uptime}")

    # Duration histogram (global)
    lines.append("# TYPE http_request_duration_ms histogram")
    # Build cumulative counts
    cumulative = 0
    for ub in AccessLogMiddleware.DURATION_BUCKETS:
        cumulative += counts.get(ub, 0)
        lines.append(
            f'http_request_duration_ms_bucket{{le="{ub}"}} {cumulative}'
        )
    # +Inf bucket includes overflow counts
    cumulative += counts.get(-1, 0)
    lines.append('http_request_duration_ms_bucket{le="+Inf"} ' + str(cumulative))
    lines.append(f"http_request_duration_ms_sum {sum_ms}")
    lines.append(f"http_request_duration_ms_count {total}")
    # Cache stats
    lines.append(f"kosmic_etag_cache_hits_total {cache_hits}")
    lines.append(f"kosmic_etag_cache_misses_total {cache_misses}")
    lines.append(f"kosmic_etag_cache_evictions_total {cache_evictions}")
    lines.append(f"kosmic_etag_cache_size {cache_size}")
    lines.append(f"kosmic_etag_cache_limit {_ETAG_CACHE_LIMIT}")
    text = "\n".join(lines) + "\n"
    # Return as plain text
    resp = PlainTextResponse(content=text, media_type="text/plain; version=0.0.4")
    resp.headers["Cache-Control"] = "no-store"
    return resp


def _head_only_response(request: Request, headers: Dict[str, str]) -> JSONResponse | None:
    """If the request method is HEAD, return an empty 200 with provided headers."""
    if request.method == "HEAD":
        return JSONResponse(status_code=200, content=None, headers=headers)
    return None

# Optional CORS support (comma-separated origins)
_cors_env = os.environ.get("KOSMIC_API_CORS_ORIGINS")
_CORS_ORIGINS: list[str] = []
if _cors_env:
    _CORS_ORIGINS = [o.strip() for o in _cors_env.split(",") if o.strip()]
    if _CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=_CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=[
                "ETag",
                "Last-Modified",
                "X-Request-ID",
                "X-RateLimit-Limit",
                "X-RateLimit-Remaining",
                "Retry-After",
            ],
        )


@app.get("/health", response_model=HealthModel, tags=["health"]) 
def health() -> JSONResponse:
    payload = HealthModel(status="ok").model_dump()
    resp = JSONResponse(payload)
    resp.headers["Cache-Control"] = "no-store"
    return resp


_ERR = {
    401: {"model": ErrorModel, "description": "Unauthorized"},
    404: {"model": ErrorModel, "description": "Artifact not found"},
    429: {"model": ErrorModel, "description": "Too Many Requests"},
}


@app.get("/k/series", tags=["artifacts"], responses=_ERR) 
def get_k_series(
    request: Request, as_json: Optional[bool] = None, download: bool = False
) -> JSONResponse | FileResponse:
    path = LOGS / "historical_k" / "k_t_series.csv"
    if not path.exists():
        raise HTTPException(
            status_code=404, detail="k_t_series.csv not found; run historical-run"
        )
    headers = _headers_for_file(path)
    # Content negotiation depends on Accept header; advertise for caches
    headers["Vary"] = "Accept"
    nm = _not_modified_response(request, headers)
    if nm is not None:
        return nm
    head_resp = _head_only_response(request, headers)
    if head_resp is not None:
        return head_resp
    # Content negotiation: explicit query param wins; else honor Accept header
    accept = (request.headers.get("accept") or "").lower()
    if as_json is True or (as_json is None and "text/csv" not in accept):
        df = pd.read_csv(path)
        return JSONResponse(df.to_dict(orient="records"), headers=headers)
    resp = FileResponse(path, headers=headers, media_type="text/csv")
    if download:
        resp.headers["Content-Disposition"] = f"attachment; filename={path.name}"
    return resp


@app.get("/k/summary", response_model=SummaryModel, tags=["artifacts"], responses=_ERR) 
def get_k_summary(request: Request) -> SummaryModel | JSONResponse:
    path = LOGS / "historical_k" / "k_t_summary.json"
    if not path.exists():
        raise HTTPException(
            status_code=404, detail="k_t_summary.json not found; run historical-run"
        )
    headers = _headers_for_file(path)
    nm = _not_modified_response(request, headers)
    if nm is not None:
        return nm
    head_resp = _head_only_response(request, headers)
    if head_resp is not None:
        return head_resp
    data = json.loads(path.read_text(encoding="utf-8"))
    try:
        return SummaryModel(**data)
    except Exception:
        # Fallback to raw JSON if fields don't match expected schema
        return JSONResponse(data, headers=headers)


@app.get("/k/plot", tags=["artifacts"], responses=_ERR) 
def get_k_plot(request: Request, download: bool = False) -> FileResponse | JSONResponse:
    path = LOGS / "historical_k" / "k_t_plot.png"
    if not path.exists():
        raise HTTPException(
            status_code=404, detail="k_t_plot.png not found; run historical-run"
        )
    headers = _headers_for_file(path)
    nm = _not_modified_response(request, headers)
    if nm is not None:
        return nm
    head_resp = _head_only_response(request, headers)
    if head_resp is not None:
        return head_resp
    resp = FileResponse(path, headers=headers, media_type="image/png")
    if download:
        resp.headers["Content-Disposition"] = f"attachment; filename={path.name}"
    return resp


@app.get("/regimes", tags=["artifacts"], responses=_ERR) 
def get_regimes(request: Request, download: bool = False) -> FileResponse | JSONResponse:
    path = LOGS / "regimes" / "regimes.csv"
    if not path.exists():
        raise HTTPException(
            status_code=404, detail="regimes.csv not found; run historical-regimes"
        )
    headers = _headers_for_file(path)
    nm = _not_modified_response(request, headers)
    if nm is not None:
        return nm
    head_resp = _head_only_response(request, headers)
    if head_resp is not None:
        return head_resp
    resp = FileResponse(path, headers=headers, media_type="text/csv")
    if download:
        resp.headers["Content-Disposition"] = f"attachment; filename={path.name}"
    return resp


@app.get("/forecast", response_model=ForecastModel, tags=["artifacts"], responses=_ERR) 
def get_forecast(
    request: Request, format: str = "auto", download: bool = False
) -> ForecastModel | JSONResponse | FileResponse:
    json_path = LOGS / "forecasting" / "forecast.json"
    fmt = (format or "auto").lower()
    if json_path.exists() and fmt in {"auto", "json"}:
        headers = _headers_for_file(json_path)
        nm = _not_modified_response(request, headers)
        if nm is not None:
            return nm
        head_resp = _head_only_response(request, headers)
        if head_resp is not None:
            return head_resp
        data = json.loads(json_path.read_text(encoding="utf-8"))
        try:
            return ForecastModel(**data)
        except Exception:
            return JSONResponse(data, headers=headers)
    plot_path = LOGS / "forecasting" / "forecast_plot.png"
    if plot_path.exists() and fmt in {"auto", "plot"}:
        headers = _headers_for_file(plot_path)
        nm = _not_modified_response(request, headers)
        if nm is not None:
            return nm
        head_resp = _head_only_response(request, headers)
        if head_resp is not None:
            return head_resp
        resp = FileResponse(plot_path, headers=headers, media_type="image/png")
        if download:
            resp.headers["Content-Disposition"] = f"attachment; filename={plot_path.name}"
        return resp
    raise HTTPException(
        status_code=404, detail="forecast artifacts not found; run historical-forecast"
    )


@app.get("/meta", response_model=MetaModel, tags=["meta"]) 
def get_meta() -> MetaModel:
    """Return API version and artifact availability with ETag/Last-Modified info."""
    def _describe(path: Path) -> FileInfo:
        if not path.exists():
            return FileInfo(
                exists=False, path=str(path), etag="", last_modified="", size=0
            )
        headers = _headers_for_file(path)
        return FileInfo(
            exists=True,
            path=str(path),
            etag=headers.get("ETag", ""),
            last_modified=headers.get("Last-Modified", ""),
            size=path.stat().st_size,
        )

    # Prefer FastAPI app.version if set, fallback to static
    version = getattr(app, "version", None) or "0.1.0"
    artifacts = {
        "k_series": _describe(LOGS / "historical_k" / "k_t_series.csv"),
        "k_summary": _describe(LOGS / "historical_k" / "k_t_summary.json"),
        "k_plot": _describe(LOGS / "historical_k" / "k_t_plot.png"),
        "regimes": _describe(LOGS / "regimes" / "regimes.csv"),
        "forecast_json": _describe(LOGS / "forecasting" / "forecast.json"),
        "forecast_plot": _describe(LOGS / "forecasting" / "forecast_plot.png"),
    }
    config = MetaConfig(
        logs_dir=str(LOGS),
        etag_mode=ETAG_MODE,
        cache_seconds=CACHE_SECONDS,
        cors_enabled=bool(_CORS_ORIGINS),
        cors_origins=_CORS_ORIGINS,
        git_commit=_infer_git_sha(),
    )
    return MetaModel(version=version, config=config, artifacts=artifacts)


@app.get("/info", response_model=MetaModel, tags=["meta"]) 
def get_info() -> MetaModel:
    """Alias of /meta for convenience."""
    return get_meta()


@app.get("/ready", response_model=ReadyModel, responses={503: {"model": ErrorModel, "description": "Not Ready"}})
def ready() -> JSONResponse:
    """Readiness check with artifact presence report.

    ok is True when the server is up; missing lists any expected optional artifacts
    that are not present. Callers can decide policy based on missing list.
    """
    expected = [
        LOGS / "historical_k" / "k_t_series.csv",
        LOGS / "historical_k" / "k_t_summary.json",
        LOGS / "historical_k" / "k_t_plot.png",
        LOGS / "regimes" / "regimes.csv",
        LOGS / "forecasting" / "forecast.json",
        LOGS / "forecasting" / "forecast_plot.png",
    ]
    missing = [str(p) for p in expected if not p.exists()]
    # Strict readiness mode: treat core artifacts as required and return 503 if missing
    strict = os.environ.get("KOSMIC_API_STRICT_READY", "0").lower() in {"1", "true", "yes"}
    if strict:
        required = [
            LOGS / "historical_k" / "k_t_series.csv",
            LOGS / "historical_k" / "k_t_summary.json",
        ]
        req_missing = [str(p) for p in required if not p.exists()]
        if req_missing:
            payload = ReadyModel(ok=False, missing=req_missing, notes=("Strict mode: missing required artifacts"))
            resp = JSONResponse(status_code=503, content=payload.model_dump())
            resp.headers["Cache-Control"] = "no-store"
            return resp
    ok_payload = ReadyModel(ok=True, missing=missing, notes=("Artifacts optional; see /meta")).model_dump()
    resp = JSONResponse(ok_payload)
    resp.headers["Cache-Control"] = "no-store"
    return resp


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8052)


def _headers_for_file(path: Path) -> Dict[str, str]:
    """Return ETag and Last-Modified headers for a file, plus short Cache-Control.

    Uses a strong ETag (sha256 of file contents) for correctness. If performance
    becomes a concern for large files, consider switching to a weak ETag based on
    size/mtime (e.g., W/"{mtime_ns}-{size}").
    """
    stat = path.stat()
    cache_key = str(path.resolve())
    if ETAG_MODE == "weak":
        etag = f'W/"{stat.st_mtime_ns}-{stat.st_size}"'
    else:
        with _ETAG_CACHE_LOCK:
            cached = _ETAG_CACHE.get(cache_key)
            if cached and cached[0] == stat.st_mtime_ns and cached[1] == stat.st_size:
                etag = cached[2]
                _ETAG_CACHE.move_to_end(cache_key, last=True)
                globals()["_ETAG_CACHE_HITS"] += 1
            else:
                etag = hashlib.sha256(path.read_bytes()).hexdigest()
                _ETAG_CACHE[cache_key] = (stat.st_mtime_ns, stat.st_size, etag)
                globals()["_ETAG_CACHE_MISSES"] += 1
                if len(_ETAG_CACHE) > _ETAG_CACHE_LIMIT:
                    _ETAG_CACHE.popitem(last=False)
                    globals()["_ETAG_CACHE_EVICTIONS"] += 1
    last_mod = format_datetime(datetime.fromtimestamp(stat.st_mtime, timezone.utc))
    return {
        "ETag": etag,
        "Last-Modified": last_mod,
        "Cache-Control": f"public, max-age={CACHE_SECONDS}",
    }


def _parsed_http_date(value: str) -> datetime | None:
    try:
        from email.utils import parsedate_to_datetime

        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def _not_modified_response(request: Request, headers: Dict[str, str]) -> JSONResponse | None:
    # ETag precondition
    inm = request.headers.get("if-none-match")
    if inm and inm == headers.get("ETag"):
        return JSONResponse(status_code=304, content=None, headers=headers)
    # If-Modified-Since precondition
    ims = request.headers.get("if-modified-since")
    last = headers.get("Last-Modified")
    if ims and last:
        ims_dt = _parsed_http_date(ims)
        last_dt = _parsed_http_date(last)
        if ims_dt and last_dt and ims_dt >= last_dt:
            return JSONResponse(status_code=304, content=None, headers=headers)
    return None


def _infer_git_sha() -> str:
    """Best-effort HEAD commit hash for reproducibility tracking."""
    head = Path(".git/HEAD")
    if not head.exists():
        return "UNKNOWN"
    try:
        ref = head.read_text(encoding="utf-8").strip()
        if ref.startswith("ref:"):
            ref_path = Path(".git") / ref.split(" ", 1)[1]
            if ref_path.exists():
                return ref_path.read_text(encoding="utf-8").strip()
        elif len(ref) == 40:
            return ref
    except Exception:
        return "UNKNOWN"
    return "UNKNOWN"


if __name__ == "__main__":
    main()
