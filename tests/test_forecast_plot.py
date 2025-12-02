from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from historical_k.forecasting import forecast_k_trajectory, plot_forecast
import importlib.util as _util


@pytest.mark.skipif(_util.find_spec("statsmodels") is None, reason="statsmodels not installed")
def test_forecast_plot_smoke(tmp_path: Path) -> None:
    years = list(range(1900, 1960, 10))
    series = pd.Series(np.linspace(0.8, 1.0, len(years)), index=years)
    # Try ensemble; if statsmodels missing, test is skipped
    result = forecast_k_trajectory(series, horizon_years=20, method="ensemble")
    out = tmp_path / "forecast.png"
    plot_forecast(series, result, out)
    assert out.exists()
