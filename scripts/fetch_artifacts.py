#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

from historical_k.client import KApiClient


def _load_etags(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_etags(path: Path, data: Dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fetch_all(base_url: str, out_dir: Path) -> None:
    client = KApiClient(base_url)
    out_dir.mkdir(parents=True, exist_ok=True)
    etag_path = out_dir / "etags.json"
    etags = _load_etags(etag_path)

    # Series (JSON)
    r = client.get_series(as_json=True, etag=etags.get("k_series_json"))
    if r.status_code == 200 and r.json_data is not None:
        (out_dir / "k_t_series.json").write_text(
            json.dumps(r.json_data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        if r.etag:
            etags["k_series_json"] = r.etag

    # Series (CSV)
    r = client.get_series(as_json=False, etag=etags.get("k_series_csv"))
    if r.status_code == 200 and r.text is not None:
        (out_dir / "k_t_series.csv").write_text(r.text, encoding="utf-8")
        if r.etag:
            etags["k_series_csv"] = r.etag

    # Summary JSON
    r = client.get_summary(etag=etags.get("k_summary"))
    if r.status_code == 200 and r.json_data:
        (out_dir / "k_t_summary.json").write_text(
            json.dumps(r.json_data[0], indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        if r.etag:
            etags["k_summary"] = r.etag

    # Regimes
    r = client.get_regimes(etag=etags.get("regimes"))
    if r.status_code == 200 and r.text is not None:
        (out_dir / "regimes.csv").write_text(r.text, encoding="utf-8")
        if r.etag:
            etags["regimes"] = r.etag

    # Forecast (prefer JSON)
    r = client.get_forecast(format="auto", etag=etags.get("forecast"))
    if r.status_code == 200:
        if r.content_type and "application/json" in r.content_type and r.json_data:
            (out_dir / "forecast.json").write_text(
                json.dumps(r.json_data[0], indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        elif r.content_type and "image/png" in r.content_type and r.content is not None:
            (out_dir / "forecast_plot.png").write_bytes(r.content)
        if r.etag:
            etags["forecast"] = r.etag

    _save_etags(etag_path, etags)


def main() -> None:
    p = argparse.ArgumentParser(description="Fetch Historical K API artifacts with ETag caching")
    p.add_argument("--base", default="http://localhost:8052", help="Base URL of API")
    p.add_argument("--out", type=Path, default=Path("artifacts"), help="Output directory")
    args = p.parse_args()
    fetch_all(args.base, args.out)
    print(f"✅ Artifacts downloaded to {args.out}")


if __name__ == "__main__":
    main()

