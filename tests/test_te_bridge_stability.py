from __future__ import annotations

import numpy as np
import pytest

from core.te_bridge import knn_transfer_entropy, gaussian_transfer_entropy


def test_knn_te_raises_when_n_le_k() -> None:
    x = np.arange(5)
    y = np.arange(5)
    yp = y.copy()
    with pytest.raises(ValueError):
        _ = knn_transfer_entropy(x, y, yp, k=5)


def test_gaussian_te_non_negative_on_constants() -> None:
    x = np.ones(10)
    y = np.ones(10)
    yp = np.ones(10)
    te = gaussian_transfer_entropy(x[:-1], y[:-1], yp[1:])
    assert te >= 0.0

