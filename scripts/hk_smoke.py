#!/usr/bin/env python3
"""
Quick Historical K(t) smoke generator using deterministic fallbacks.

Produces minimal artifacts under logs/historical_k suitable for API smoke tests:
  - k_t_series.csv
  - k_t_summary.json
  - k_t_plot.png
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from historical_k.etl import build_harmony_frame, compute_k_series
from historical_k.compute_k import _plot_series


def main() -> None:
    years = [2000, 2010, 2020]
    proxies = {
        # Nonexistent features trigger deterministic zero fallbacks in ETL
        "resonant_coherence": ["nonexistent_a"],
        "interconnection": ["nonexistent_b"],
    }
    frame = build_harmony_frame(proxies, years, normalization="minmax_global")
    k = compute_k_series(frame)
    results = pd.DataFrame({"year": years, "K": k.to_numpy()})

    out_dir = Path("logs/historical_k")
    out_dir.mkdir(parents=True, exist_ok=True)
    # Save CSV
    (out_dir / "k_t_series.csv").write_text(
        results.to_csv(index=False), encoding="utf-8"
    )
    # Summary JSON
    summary = {"mean_K": float(k.mean())}
    (out_dir / "k_t_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    # Plot
    _plot_series(results, summary["mean_K"], summary["mean_K"], out_dir / "k_t_plot.png")
    # Minimal regimes CSV
    reg_dir = Path("logs/regimes")
    reg_dir.mkdir(parents=True, exist_ok=True)
    (reg_dir / "regimes.csv").write_text(
        "regime_id,start_year,end_year\n1,2000,2010\n2,2010,2020\n", encoding="utf-8"
    )
    # Minimal forecast JSON
    f_dir = Path("logs/forecasting")
    f_dir.mkdir(parents=True, exist_ok=True)
    forecast = {
        "years": [2030, 2040],
        "forecast": [float(summary["mean_K"]), float(summary["mean_K"])],
        "ci_lower": [float(summary["mean_K"]), float(summary["mean_K"])],
        "ci_upper": [float(summary["mean_K"]), float(summary["mean_K"])],
    }
    (f_dir / "forecast.json").write_text(
        json.dumps(forecast, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"✅ Wrote smoke artifacts to {out_dir}, {reg_dir}, and {f_dir}")


if __name__ == "__main__":
    main()
