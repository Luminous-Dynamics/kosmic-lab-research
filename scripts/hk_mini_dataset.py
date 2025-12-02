#!/usr/bin/env python3
"""
Generate a minimal Historical K(t) dataset from small real proxy CSVs.

Uses:
  - historical_k/data/network_modularity_inverse.csv
  - historical_k/data/trade_network_degree.csv

Outputs under logs/historical_k:
  - k_t_series.csv
  - k_t_summary.json
  - k_t_plot.png
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from historical_k.etl import build_harmony_frame, compute_k_series
from historical_k.compute_k import _plot_series


def main() -> None:
    years = [2000, 2010, 2020]
    proxies = {
        "resonant_coherence": ["network_modularity_inverse"],
        "interconnection": [
            "trade_network_degree",
            "renewable_energy_share",
            "trade_openness_index",
        ],
        "reciprocity": ["alliance_reciprocity_ratio"],
        "wisdom_accuracy": ["forecast_skill_index"],
    }
    frame = build_harmony_frame(proxies, years, normalization="minmax_global")
    k = compute_k_series(frame)
    results = pd.DataFrame({"year": years, "K": k.to_numpy()})

    out_dir = Path("logs/historical_k")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "k_t_series.csv").write_text(
        results.to_csv(index=False), encoding="utf-8"
    )
    summary = {"mean_K": float(k.mean())}
    (out_dir / "k_t_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _plot_series(results, summary["mean_K"], summary["mean_K"], out_dir / "k_t_plot.png")
    print(f"✅ Wrote mini dataset artifacts to {out_dir}")


if __name__ == "__main__":
    main()
