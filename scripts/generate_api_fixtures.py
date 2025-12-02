#!/usr/bin/env python3
"""
Generate minimal artifact files for the Historical K API endpoints.

Creates small placeholder files under logs/ so you can quickly validate
the FastAPI service without running the full pipelines.

Artifacts created:
  - logs/historical_k/k_t_series.csv
  - logs/historical_k/k_t_summary.json
  - logs/historical_k/k_t_plot.png (empty placeholder)
  - logs/regimes/regimes.csv
  - logs/forecasting/forecast.json

Usage:
  poetry run python scripts/generate_api_fixtures.py --out logs

Or via poetry script (after pyproject registration):
  poetry run kosmic-api-fixtures
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def generate(out_dir: Path) -> None:
    # Historical series CSV
    series = "year,K\n1800,0.80\n1810,0.90\n1820,0.95\n1830,1.00\n"
    _write(out_dir / "historical_k" / "k_t_series.csv", series)

    # Summary JSON (minimal fields; API falls back to raw JSON if schema differs)
    summary = {"mean_K": 0.91}
    _write(out_dir / "historical_k" / "k_t_summary.json", json.dumps(summary, indent=2) + "\n")

    # Plot placeholder (zero-byte valid file)
    _write_bytes(out_dir / "historical_k" / "k_t_plot.png", b"")

    # Regimes CSV
    regimes = "regime_id,start_year,end_year\n1,1800,1830\n2,1830,1860\n"
    _write(out_dir / "regimes" / "regimes.csv", regimes)

    # Forecast JSON
    forecast = {
        "years": [1840, 1850],
        "forecast": [1.02, 1.08],
        "ci_lower": [0.95, 1.00],
        "ci_upper": [1.10, 1.15],
    }
    _write(out_dir / "forecasting" / "forecast.json", json.dumps(forecast, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate API fixture artifacts under logs/")
    parser.add_argument("--out", type=Path, default=Path("logs"), help="Output base directory")
    args = parser.parse_args()
    generate(args.out)
    print(f"✅ Fixtures written under {args.out}/")


if __name__ == "__main__":
    main()

