# Minimal Plotly Dashboard for Historical K API

Quick example to visualize K(t) from the API with ETag caching.

## index.html

```html
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Historical K Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
  </head>
  <body>
    <h2>Historical K(t)</h2>
    <div id="plot" style="width:800px;height:400px;"></div>
    <script type="module">
      const BASE = 'http://localhost:8052';
      async function fetchWithETag(path) {
        const key = `hk:etag:${path}`;
        const etag = localStorage.getItem(key);
        const headers = new Headers();
        if (etag) headers.set('If-None-Match', etag);
        const res = await fetch(`${BASE}${path}`, { headers, cache: 'no-store' });
        if (res.status === 304) return null;
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const newTag = res.headers.get('ETag');
        if (newTag) localStorage.setItem(key, newTag);
        return await res.json();
      }

      async function main() {
        const data = await fetchWithETag('/k/series');
        if (!data) return; // unchanged
        const years = data.map((d) => d.year);
        const K = data.map((d) => d.K);
        const trace = { x: years, y: K, mode: 'lines+markers', name: 'K(t)' };
        const layout = { xaxis: { title: 'Year' }, yaxis: { title: 'K-index' } };
        Plotly.newPlot('plot', [trace], layout);
      }
      main();
    </script>
  </body>
  </html>
```

Serve locally (any static server) and point to your API base URL.

For CORS, set `KOSMIC_API_CORS_ORIGINS="http://localhost:PORT"` on the server.

