from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from historical_k.etl import build_harmony_frame, compute_k_series


def test_mini_k_pipeline_with_fallbacks(tmp_path: Path) -> None:
    years = [2000, 2010, 2020]
    # Use features that don't exist on disk to trigger deterministic zero fallbacks
    proxies = {
        "resonant_coherence": ["nonexistent_feature_a"],
        "interconnection": ["nonexistent_feature_b"],
    }
    frame = build_harmony_frame(proxies, years, normalization="minmax_global")
    assert set(frame.columns) == {"resonant_coherence", "interconnection"}
    k = compute_k_series(frame)
    assert isinstance(k, pd.Series)
    assert list(k.index) == years
    # Fallback zeros become well-defined series; mean across zeros is zero
    assert float(k.mean()) == 0.0

