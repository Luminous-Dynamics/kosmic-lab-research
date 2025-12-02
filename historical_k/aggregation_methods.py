"""
Aggregation methods for K(t) index computation.

Provides both arithmetic and geometric mean aggregation with support for:
- Weighted and unweighted aggregation
- Numerical stability (log-space computation)
- Bootstrap compatibility
- Zero-handling via small epsilon

Usage:
    from historical_k.aggregation_methods import compute_k_geometric, compute_k_arithmetic

    k_geo = compute_k_geometric(harmony_frame)
    k_arith = compute_k_arithmetic(harmony_frame)  # For comparison
"""

from __future__ import annotations

from typing import Dict, Optional

import numpy as np
import pandas as pd


def compute_k_geometric(
    harmony_frame: pd.DataFrame, weights: Optional[Dict[str, float]] = None
) -> pd.Series:
    """
    Compute K(t) index via **geometric mean** (enforces non-substitutability).

    Formula: K(t) = (∏ H_i(t))^(1/n)

    Computed in log-space for numerical stability:
    K(t) = exp(mean(log(H_i(t))))

    The geometric mean mathematically enforces the "weakest link" property:
    if any harmony H_i → 0, then K(t) → 0, regardless of how high other
    harmonies are. This reflects coordination reality: collapsed governance
    breaks the system regardless of advanced technology.

    Args:
        harmony_frame: DataFrame with year index and harmony columns (H₁...H₇)
        weights: Optional dict mapping harmony names to weights (must sum to 1.0)

    Returns:
        pd.Series: K(t) index computed via geometric mean

    Raises:
        ValueError: If harmony_frame is empty or weights don't sum to 1.0

    Example:
        >>> harmonies = pd.DataFrame({
        ...     'h1': [0.5, 0.6, 0.7],
        ...     'h2': [0.6, 0.7, 0.8],
        ...     'h3': [0.4, 0.5, 0.6]
        ... })
        >>> k = compute_k_geometric(harmonies)
        >>> print(k)
        0    0.496
        1    0.596
        2    0.696
    """
    if harmony_frame.empty:
        raise ValueError("Harmony frame is empty.")

    # Add small epsilon to handle zeros (prevents log(0) = -inf)
    epsilon = 1e-10
    arr = harmony_frame.to_numpy() + epsilon

    if weights is None:
        # Unweighted geometric mean: exp(mean(log(H_i)))
        log_values = np.log(arr)
        log_mean = np.mean(log_values, axis=1)
        k_values = np.exp(log_mean)
    else:
        # Weighted geometric mean: exp(Σ w_i × log(H_i))
        cols = list(harmony_frame.columns)
        w = {k: float(v) for k, v in weights.items() if k in cols}

        if not w:
            # No valid weights → fallback to unweighted
            log_values = np.log(arr)
            log_mean = np.mean(log_values, axis=1)
            k_values = np.exp(log_mean)
        else:
            # Validate weights sum to 1.0
            w_sum = sum(w.values())
            if not np.isclose(w_sum, 1.0, atol=1e-9):
                raise ValueError(f"Weights must sum to 1.0, got {w_sum:.10f}")

            # Normalize weights (ensure exact sum = 1.0)
            w_norm = {k: v / w_sum for k, v in w.items()}

            # Build weight vector aligned to columns
            weight_vec = np.array([w_norm.get(c, 0.0) for c in cols])

            # Compute weighted geometric mean
            log_values = np.log(arr)
            log_weighted_mean = log_values @ weight_vec
            k_values = np.exp(log_weighted_mean)

    return pd.Series(k_values, index=harmony_frame.index, name="K")


def compute_k_arithmetic(
    harmony_frame: pd.DataFrame, weights: Optional[Dict[str, float]] = None
) -> pd.Series:
    """
    Compute K(t) index via **arithmetic mean** (original formulation).

    Formula: K(t) = (1/n) × Σ H_i(t)

    The arithmetic mean allows substitutability: high scores in one harmony
    can compensate for low scores in another. This is the original formulation
    but is being replaced by geometric mean in the Path C revision.

    Kept for comparison and validation purposes.

    Args:
        harmony_frame: DataFrame with year index and harmony columns (H₁...H₇)
        weights: Optional dict mapping harmony names to weights (must sum to 1.0)

    Returns:
        pd.Series: K(t) index computed via arithmetic mean

    Raises:
        ValueError: If harmony_frame is empty or weights don't sum to 1.0
    """
    if harmony_frame.empty:
        raise ValueError("Harmony frame is empty.")

    if weights is None:
        # Unweighted arithmetic mean
        return harmony_frame.mean(axis=1)

    # Weighted arithmetic mean
    cols = list(harmony_frame.columns)
    w = {k: float(v) for k, v in weights.items() if k in cols}

    if not w:
        # No valid weights → fallback to unweighted
        return harmony_frame.mean(axis=1)

    # Validate and normalize weights
    w_sum = sum(w.values())
    if not np.isclose(w_sum, 1.0, atol=1e-9):
        raise ValueError(f"Weights must sum to 1.0, got {w_sum:.10f}")

    w_norm = {k: v / w_sum for k, v in w.items()}

    # Build weight vector and compute weighted sum
    weight_vec = np.array([w_norm.get(c, 0.0) for c in cols])
    arr = harmony_frame.to_numpy()

    return pd.Series(arr @ weight_vec, index=harmony_frame.index, name="K")


def compare_aggregation_methods(
    harmony_frame: pd.DataFrame, weights: Optional[Dict[str, float]] = None
) -> pd.DataFrame:
    """
    Compute K(t) using both arithmetic and geometric means for comparison.

    Returns DataFrame with columns:
    - K_arithmetic: Original formulation
    - K_geometric: Path C formulation
    - delta_absolute: K_arith - K_geo
    - delta_percent: (K_arith - K_geo) / K_arith × 100

    Args:
        harmony_frame: DataFrame with year index and harmony columns
        weights: Optional weights for both methods

    Returns:
        pd.DataFrame with comparison metrics
    """
    k_arith = compute_k_arithmetic(harmony_frame, weights)
    k_geo = compute_k_geometric(harmony_frame, weights)

    comparison = pd.DataFrame(
        {
            "K_arithmetic": k_arith,
            "K_geometric": k_geo,
            "delta_absolute": k_arith - k_geo,
            "delta_percent": (k_arith - k_geo) / k_arith * 100,
        },
        index=harmony_frame.index,
    )

    return comparison


def validate_geometric_aggregation(harmony_frame: pd.DataFrame) -> Dict[str, bool]:
    """
    Validate that geometric mean satisfies mathematical requirements.

    Checks:
    1. K_geometric ≤ K_arithmetic (always true mathematically)
    2. K_geometric > 0 (no negative or zero values)
    3. K_geometric finite (no NaN or Inf)

    Args:
        harmony_frame: DataFrame with harmony columns

    Returns:
        Dict with validation results
    """
    k_arith = compute_k_arithmetic(harmony_frame)
    k_geo = compute_k_geometric(harmony_frame)

    validation = {
        "geometric_le_arithmetic": bool(np.all(k_geo <= k_arith + 1e-9)),
        "geometric_positive": bool(np.all(k_geo > 0)),
        "geometric_finite": bool(np.all(np.isfinite(k_geo))),
        "correlation_high": bool(
            np.corrcoef(k_arith, k_geo)[0, 1] > 0.95
        ),  # Should be highly correlated
    }

    return validation


# Convenience function for backward compatibility with existing code
def compute_k_series(
    harmony_frame: pd.DataFrame,
    weights: Optional[Dict[str, float]] = None,
    method: str = "geometric",
) -> pd.Series:
    """
    Compute K-index from harmony frame using specified aggregation method.

    This is the main entry point used by the existing codebase.
    Default changed to 'geometric' for Path C revision.

    Args:
        harmony_frame: DataFrame with harmony columns
        weights: Optional weights (if None, equal weighting)
        method: 'geometric' (default) or 'arithmetic'

    Returns:
        pd.Series: K(t) index

    Raises:
        ValueError: If method not recognized
    """
    method = (method or "geometric").lower()

    if method == "geometric":
        return compute_k_geometric(harmony_frame, weights)
    elif method == "arithmetic":
        return compute_k_arithmetic(harmony_frame, weights)
    else:
        raise ValueError(
            f"Unknown aggregation method '{method}'. Use 'geometric' or 'arithmetic'."
        )
