from __future__ import annotations

from pathlib import Path

import pandas as pd

from historical_k.etl import build_harmony_frame, compute_k_series


def test_hk_frame_with_real_features() -> None:
    years = [2000, 2010, 2020]
    proxies = {
        "resonant_coherence": ["network_modularity_inverse"],
        "interconnection": ["trade_network_degree"],
    }
    frame = build_harmony_frame(proxies, years, normalization="minmax_global")
    assert set(frame.columns) == {"resonant_coherence", "interconnection"}
    k = compute_k_series(frame)
    assert isinstance(k, pd.Series)
    assert list(k.index) == years
    # Values are scaled between 0 and 1; mean should be > 0
    assert float(k.mean()) > 0.0

