from __future__ import annotations

import numpy as np
import pytest

from core.te_bridge import knn_transfer_entropy


@pytest.mark.parametrize("k", [2, 3, 4, 5])
def test_knn_te_directionality_across_k(k: int) -> None:
    rng = np.random.default_rng(123)
    n = 700
    x = np.zeros(n)
    y = np.zeros(n)
    for t in range(1, n):
        x[t] = 0.9 * x[t - 1] + rng.normal(scale=0.2)
        y[t] = 0.6 * y[t - 1] + 0.4 * x[t - 1] + rng.normal(scale=0.2)

    te_xy = knn_transfer_entropy(x[:-1], y[:-1], y[1:], k=k, standardize=True)
    te_yx = knn_transfer_entropy(y[:-1], x[:-1], x[1:], k=k, standardize=True)
    assert te_xy >= 0.0 and te_yx >= 0.0
    assert te_xy > te_yx

