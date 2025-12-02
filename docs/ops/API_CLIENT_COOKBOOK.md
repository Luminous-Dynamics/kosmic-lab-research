# Historical K API Client Cookbook

Practical recipes for consuming the API from Python and JavaScript with HTTP caching and content negotiation.

## Python (requests)

```python
from historical_k.client import KApiClient

api = KApiClient("http://localhost:8052")

# 1) Fetch series as JSON
resp = api.get_series(as_json=True)
print(resp.status_code, resp.etag, len(resp.json_data or []))

# 2) Conditional GET using ETag (fast 304 when unchanged)
resp2 = api.get_series(as_json=True, etag=resp.etag)
print(resp2.status_code)  # 304 if unchanged

# 3) Fetch CSV via Accept header
csv_resp = api.get_series(as_json=False)
print(csv_resp.text.splitlines()[:2])
```

## JavaScript (Fetch API)

```js
// Simple JSON fetch with ETag caching
const BASE = 'http://localhost:8052';
let etag = null;

async function fetchSeriesJson() {
  const headers = new Headers();
  if (etag) headers.set('If-None-Match', etag);
  const res = await fetch(`${BASE}/k/series`, { headers, cache: 'no-store' });
  if (res.status === 304) {
    console.log('Not modified, skip parsing');
    return null;
  }
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  etag = res.headers.get('ETag');
  const data = await res.json();
  console.log('Records:', data.length);
  return data;
}

// Request CSV via Accept header
async function fetchSeriesCsv() {
  const res = await fetch(`${BASE}/k/series`, {
    headers: { Accept: 'text/csv' },
    cache: 'no-store',
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const csvText = await res.text();
  console.log('CSV sample:', csvText.split('\n').slice(0, 2));
  return csvText;
}
```

## Python (async, aiohttp)

```python
import asyncio
from historical_k.async_client import AsyncKApiClient

async def main():
    client = AsyncKApiClient("http://localhost:8052")
    # Series as JSON
    r1 = await client.get_series(as_json=True)
    print(r1.status, r1.etag, len(r1.json_data or []))
    # Conditional GET
    r2 = await client.get_series(as_json=True, etag=r1.etag)
    print(r2.status)  # 304 if unchanged
    # Forecast as plot
    rp = await client.get_forecast(format="plot")
    print(rp.status, rp.content_type, len(rp.content or b""))
    # Regimes as CSV
    rr = await client.get_regimes()
    print(rr.status, rr.content_type, (rr.text or "").splitlines()[:1])
    await client.close()

asyncio.run(main())
```

## Browser CORS

Set on the server: `KOSMIC_API_CORS_ORIGINS="http://localhost:8050,https://your.app"`.

Exposed headers include: `ETag`, `Last-Modified`, `X-Request-ID`.
