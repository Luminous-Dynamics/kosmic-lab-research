#!/usr/bin/env python3
from __future__ import annotations

"""Micro-benchmark for KSG TE to observe impact of BallTree reuse.

Generates a simple causal process x -> y and measures knn_transfer_entropy runtime.
"""
import time
import numpy as np

from core.te_bridge import knn_transfer_entropy


def gen_xy(n: int, seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    x = np.zeros(n)
    y = np.zeros(n)
    for t in range(1, n):
        x[t] = 0.9 * x[t - 1] + rng.normal(scale=0.2)
        y[t] = 0.6 * y[t - 1] + 0.4 * x[t - 1] + rng.normal(scale=0.2)
    return x, y


def bench(n: int = 5000, k: int = 5, iters: int = 5) -> None:
    x, y = gen_xy(n)
    x_past, y_past, y_present = x[:-1], y[:-1], y[1:]
    # Warmup
    _ = knn_transfer_entropy(x_past, y_past, y_present, k=k)
    t0 = time.perf_counter()
    vals = []
    for _ in range(iters):
        vals.append(knn_transfer_entropy(x_past, y_past, y_present, k=k))
    dt = (time.perf_counter() - t0) * 1000 / iters
    print(f"n={n} k={k} TE={np.mean(vals):.4f} avg_ms={dt:.2f}")


if __name__ == "__main__":
    bench()

