# Historical K API Operations Guide

This guide summarizes common operations for running, testing, and integrating the Historical K API.

## Run Locally (Poetry)

- Generate fixtures and start server
  - `make api-fixtures`
  - `make api` (http://localhost:8052)
- Weak ETag + longer cache TTL
  - `make api-weak` (env: `KOSMIC_API_ETAG=weak`, `KOSMIC_API_CACHE_SECONDS=300`)
- Quick smoke run
  - `make api-smoke` (starts uvicorn, polls `/ready`, exercises ETag/304)

## Run via Docker Compose

- One-time setup
  - `cp -n .env.example .env` (customize `API_PORT`, `KOSMIC_*`)
- Start
  - `docker-compose up compute` (produce artifacts into `./logs`)
  - `docker-compose up -d api` (serve API)
- Protect API with a token (optional)
  - In `.env`: `KOSMIC_API_TOKEN=secret`
  - Then call with `Authorization: Bearer secret` or `X-API-Key: secret`
- Rate limit (optional)
  - In `.env`: `KOSMIC_API_RATE_LIMIT=60`, `KOSMIC_API_RATE_WINDOW=60`
- ETag/cache tuning
  - Strong vs weak ETag: `KOSMIC_API_ETAG=strong|weak` (strong hashes contents; weak uses mtime/size)
  - Cache TTL: `KOSMIC_API_CACHE_SECONDS=60`
  - In-memory ETag cache (strong mode): `KOSMIC_API_ETAG_CACHE_LIMIT=256` (LRU; prevents re-hashing large files)
- Logs and health
  - `make docker-api-logs`
  - `docker inspect --format='{{json .State.Health}}' historical-k-api | jq`
- Stop
  - `make docker-api-stop`

## Endpoints

- Health: `/health` (200 OK)
- Readiness: `/ready`
  - Strict mode (503 on missing required artifacts): `KOSMIC_API_STRICT_READY=1`
- Metadata: `/meta` (includes `config.git_commit`, CORS, cache/etag)
- Info: `/info` (alias of `/meta`)
- Artifacts:
  - `/k/series` (JSON default; CSV when `Accept: text/csv` or `?as_json=false`)
  - `/k/summary`
  - `/k/plot` (PNG)
  - `/regimes` (CSV)
  - `/forecast?format=auto|json|plot`
  - Error shape: `{ "error": { "status_code", "detail", "request_id" } }`
- HEAD optimization: all artifact endpoints short-circuit on HEAD (no body parsing), returning only headers/ETag/Last-Modified for fast cache validation.
- Metrics: `/metrics` exposes HTTP counters, duration histogram, uptime, app info, and ETag cache stats (`kosmic_etag_cache_hits_total`, `kosmic_etag_cache_misses_total`, `kosmic_etag_cache_evictions_total`, `kosmic_etag_cache_size`, `kosmic_etag_cache_limit`).

## Behavior & Security

- Request correlation
  - Echo/generate `X-Request-ID` on all responses
- Security headers
  - `X-Content-Type-Options=nosniff`, `X-Frame-Options=DENY`, `Referrer-Policy=no-referrer`, `X-XSS-Protection=0`
- Compression
  - GZip enabled for responses > 512 bytes

## Logging

- Structured access logs (default JSON)
  - Toggle: `KOSMIC_API_LOG_JSON=1|0`
  - Fields: `event=http_access`, `method`, `path`, `status`, `duration_ms`, `request_id`, `etag`

## OpenAPI / Docs

- Dump OpenAPI spec
  - `make openapi-spec` → `logs/openapi.json`
- Interactive docs
  - Swagger UI: `/docs`
  - ReDoc: `/redoc`

## CI overview

- API unit tests subset: `api-tests` workflow
- API smoke run: `api-smoke` workflow (launches uvicorn, probes endpoints)
- Nox sessions: tests, lint, format check
- Nix flake check: nix-based validation
