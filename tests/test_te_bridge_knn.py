from __future__ import annotations

import numpy as np

from core.te_bridge import knn_transfer_entropy


def test_knn_te_directionality() -> None:
    rng = np.random.default_rng(42)
    n = 600
    x = np.zeros(n)
    y = np.zeros(n)
    for t in range(1, n):
        x[t] = 0.9 * x[t - 1] + rng.normal(scale=0.2)
        # y depends on its past and x's past (causal influence x -> y)
        y[t] = 0.6 * y[t - 1] + 0.5 * x[t - 1] + rng.normal(scale=0.2)

    # Past/present alignment for TE(x->y): x[:-1], y[:-1], y[1:]
    te_xy = knn_transfer_entropy(x[:-1], y[:-1], y[1:], k=4, standardize=True)
    te_yx = knn_transfer_entropy(y[:-1], x[:-1], x[1:], k=4, standardize=True)
    assert te_xy >= 0.0 and te_yx >= 0.0
    assert te_xy > te_yx

