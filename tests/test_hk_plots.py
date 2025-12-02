from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import historical_k.compute_k as hk


def test_compute_k_plots_smoke(tmp_path: Path) -> None:
    # Minimal results frame with required columns
    years = np.array([1800, 1810, 1820, 1830])
    df = pd.DataFrame(
        {
            "year": years,
            "K": np.array([0.8, 0.9, 0.95, 1.0]),
            "resonant_coherence": np.linspace(0.5, 0.8, len(years)),
            "interconnection": np.linspace(0.4, 0.7, len(years)),
            "reciprocity": np.linspace(0.6, 0.9, len(years)),
            "play_entropy": np.linspace(0.3, 0.6, len(years)),
            "wisdom_accuracy": np.linspace(0.55, 0.75, len(years)),
            "flourishing": np.linspace(0.45, 0.65, len(years)),
        }
    )

    # Test series plot with scalar CI
    out_series = tmp_path / "k_t_plot.png"
    hk._plot_series(df, 0.75, 1.05, out_series, prereg_events=None, reference_line=0.5)
    assert out_series.exists()

    # Test harmonies plot
    out_harmonies = tmp_path / "k_t_harmonies.png"
    hk._plot_harmonies(df, out_harmonies)
    assert out_harmonies.exists()
