from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import historical_k.forecasting as hk_forecast
import historical_k.regimes as hk_regimes
from historical_k.performance_optimized import PerformanceOptimizer


def _compute_k_top(data: pd.DataFrame):
    return data["K"].values


def test_regimes_detect_minimal(monkeypatch) -> None:
    if not getattr(hk_regimes, "HAS_RUPTURES", False):
        pytest.skip("ruptures not installed")

    years = list(range(1800, 1860, 10))
    # Simple series with a change around mid-point
    values = [0.8, 0.82, 0.81, 0.83, 0.85, 1.1]
    series = pd.Series(values, index=years)
    regimes_df, breaks = hk_regimes.detect_regime_changes(series, penalty=2.0)
    assert not regimes_df.empty
    assert len(breaks) >= 1


def test_forecast_minimal() -> None:
    if not getattr(hk_forecast, "HAS_STATSMODELS", False):
        pytest.skip("statsmodels not installed")

    years = list(range(1800, 1900, 10))
    series = pd.Series(np.linspace(0.8, 1.0, len(years)), index=years)
    result = hk_forecast.forecast_k_trajectory(
        series, horizon_years=20, method="ensemble"
    )
    assert "years" in result and "forecast" in result
    assert len(result["years"]) == 2


def test_performance_optimizer_small() -> None:
    df = pd.DataFrame({"year": range(2000, 2010), "K": np.random.rand(10)})
    opt = PerformanceOptimizer(n_cores=1)
    arr = opt.bootstrap_parallel(df, _compute_k_top, n_samples=10)
    assert arr.shape[0] == 10
