from __future__ import annotations

import numpy as np
import pandas as pd

from historical_k.forecasting import _linear_forecast


def test_linear_forecast_shape_and_keys() -> None:
    years = np.array([2000, 2010, 2020])
    series = pd.Series([0.9, 1.0, 1.1], index=years)
    future = [2030, 2040]
    result = _linear_forecast(series, future)
    assert set(result.keys()) >= {"method", "years", "forecast", "ci_lower", "ci_upper"}
    assert result["years"] == future
    assert len(result["forecast"]) == len(future)
    assert len(result["ci_lower"]) == len(future)
    assert len(result["ci_upper"]) == len(future)
