# Historical K API – JavaScript Helper

Small, dependency‑free utilities to consume the API with HTTP caching and content negotiation.

## Minimal ETag Cache Wrapper

```js
// Basic cache using ETag + If-None-Match in localStorage (or any KV store)
const API = (base = 'http://localhost:8052') => {
  const key = (p) => `hk:etag:${p}`;
  const get = async (path, opts = {}) => {
    const url = new URL(path, base);
    const headers = new Headers(opts.headers || {});
    const etag = localStorage.getItem(key(path));
    if (etag) headers.set('If-None-Match', etag);
    const res = await fetch(url, { ...opts, headers, cache: 'no-store' });
    if (res.status === 304) return { status: 304, etag, data: null };
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    const newTag = res.headers.get('ETag') || '';
    if (newTag) localStorage.setItem(key(path), newTag);
    const ctype = res.headers.get('Content-Type') || '';
    if (ctype.includes('application/json')) return { status: res.status, etag: newTag, data: await res.json() };
    if (ctype.includes('text/csv')) return { status: res.status, etag: newTag, data: await res.text() };
    return { status: res.status, etag: newTag, data: await res.arrayBuffer() };
  };
  return {
    seriesJson: () => get('/k/series'),
    seriesCsv: () => get('/k/series?as_json=false', { headers: { Accept: 'text/csv' } }),
    summary:  () => get('/k/summary'),
    meta:     () => get('/meta'),
    metrics:  () => get('/metrics'),
  };
};

// Usage:
// const api = API('http://localhost:8052');
// const s = await api.seriesJson();
// const csv = await api.seriesCsv();
```

## CSV to Array Helper

```js
export function parseCsv(text) {
  const [head, ...rows] = text.trim().split(/\r?\n/);
  const cols = head.split(',');
  return rows.map((r) => Object.fromEntries(r.split(',').map((v, i) => [cols[i], v])));
}
```

## Auth and CORS

If `KOSMIC_API_TOKEN` is set on the server, pass either header:

```
Authorization: Bearer <token>
X-API-Key: <token>
```

Expose headers include `ETag`, `Last-Modified`, `X-Request-ID`, and rate‑limit headers.

## Downloads

To force downloads, append `download=true` to CSV/PNG endpoints (e.g., `/regimes?download=true`).
