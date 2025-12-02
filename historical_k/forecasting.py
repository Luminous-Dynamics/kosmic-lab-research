"""
Forecasting tools for Historical K(t).

Projects K(t) forward using time series models.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.holtwinters import ExponentialSmoothing

    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False
    print("Warning: statsmodels not installed. Install with: pip install statsmodels")


def forecast_k_trajectory(
    k_series: pd.Series, horizon_years: int = 30, method: str = "arima"
) -> Dict:
    """Project K(t) forward using time series model.

    Args:
        k_series: Historical K(t) series
        horizon_years: Years to forecast
        method: 'arima', 'holtwinters', or 'ensemble'

    Returns:
        Dict with forecast data
    """
    if not HAS_STATSMODELS:
        raise ImportError("statsmodels required. Install with: pip install statsmodels")

    # Determine forecast periods
    last_year = k_series.index[-1]
    granularity = (
        int(k_series.index[1] - k_series.index[0]) if len(k_series) > 1 else 10
    )
    n_periods = horizon_years // granularity
    future_years = [int(last_year + (i + 1) * granularity) for i in range(n_periods)]

    if method == "arima":
        # Fit ARIMA model
        try:
            model = ARIMA(k_series, order=(2, 1, 2))
            fitted = model.fit()

            # Generate forecast
            forecast_result = fitted.get_forecast(steps=n_periods)
            forecast = forecast_result.predicted_mean
            conf_int = forecast_result.conf_int(alpha=0.05)

            return {
                "method": "ARIMA(2,1,2)",
                "years": future_years,
                "forecast": forecast.values.tolist(),
                "ci_lower": conf_int.iloc[:, 0].values.tolist(),
                "ci_upper": conf_int.iloc[:, 1].values.tolist(),
                "aic": float(fitted.aic),
                "bic": float(fitted.bic),
            }
        except Exception as e:
            print(f"ARIMA failed: {e}, falling back to simple linear extrapolation")
            return _linear_forecast(k_series, future_years)

    elif method == "holtwinters":
        try:
            model = ExponentialSmoothing(k_series, trend="add", seasonal=None)
            fitted = model.fit()

            forecast = fitted.forecast(steps=n_periods)

            # Simple prediction intervals
            residuals = k_series - fitted.fittedvalues
            std_resid = residuals.std()
            ci_lower = forecast - 1.96 * std_resid
            ci_upper = forecast + 1.96 * std_resid

            return {
                "method": "Holt-Winters",
                "years": future_years,
                "forecast": forecast.values.tolist(),
                "ci_lower": ci_lower.values.tolist(),
                "ci_upper": ci_upper.values.tolist(),
            }
        except Exception as e:
            print(f"Holt-Winters failed: {e}, falling back to linear")
            return _linear_forecast(k_series, future_years)

    elif method == "ensemble":
        arima_result = forecast_k_trajectory(k_series, horizon_years, method="arima")
        hw_result = forecast_k_trajectory(k_series, horizon_years, method="holtwinters")

        ensemble_forecast = [
            (a + h) / 2 for a, h in zip(arima_result["forecast"], hw_result["forecast"])
        ]
        ensemble_lower = [
            (a + h) / 2 for a, h in zip(arima_result["ci_lower"], hw_result["ci_lower"])
        ]
        ensemble_upper = [
            (a + h) / 2 for a, h in zip(arima_result["ci_upper"], hw_result["ci_upper"])
        ]

        return {
            "method": "Ensemble (ARIMA + Holt-Winters)",
            "years": future_years,
            "forecast": ensemble_forecast,
            "ci_lower": ensemble_lower,
            "ci_upper": ensemble_upper,
        }
    else:
        raise ValueError(f"Unknown method: {method}")


def _linear_forecast(k_series: pd.Series, future_years: list) -> Dict:
    """Simple linear extrapolation fallback."""
    years = k_series.index.values
    slope, intercept = np.polyfit(years, k_series.values, 1)

    forecast = [slope * y + intercept for y in future_years]
    residual_std = np.std(k_series.values - (slope * years + intercept))

    ci_lower = [f - 1.96 * residual_std for f in forecast]
    ci_upper = [f + 1.96 * residual_std for f in forecast]

    return {
        "method": "Linear Extrapolation",
        "years": future_years,
        "forecast": forecast,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
    }


def plot_forecast(
    k_series: pd.Series, forecast_result: Dict, output_path: str | Path
) -> None:
    """Visualize forecast."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(14, 7))

    # Historical
    hist_years = k_series.index
    ax.plot(
        hist_years,
        k_series.values,
        "b-",
        linewidth=2,
        label="Historical K(t)",
        marker="o",
    )

    # Forecast
    forecast_years = forecast_result["years"]
    forecast = forecast_result["forecast"]
    ci_lower = forecast_result["ci_lower"]
    ci_upper = forecast_result["ci_upper"]

    ax.plot(
        forecast_years,
        forecast,
        "r--",
        linewidth=2,
        label=f'Forecast ({forecast_result["method"]})',
        marker="s",
    )
    ax.fill_between(
        forecast_years, ci_lower, ci_upper, color="red", alpha=0.2, label="95% CI"
    )

    # Mark present
    ax.axvline(
        hist_years[-1],
        color="green",
        linestyle=":",
        alpha=0.7,
        label="Present",
        linewidth=2,
    )

    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("K-index", fontsize=12)
    ax.set_title(
        f"Historical K(t) and Forecast to {forecast_years[-1]}",
        fontsize=14,
        fontweight="bold",
    )
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Summary text
    final_forecast = forecast[-1]
    current_k = k_series.iloc[-1]
    change = ((final_forecast - current_k) / current_k) * 100

    summary_text = (
        f"Current K ({int(hist_years[-1])}): {current_k:.3f}\n"
        f"Forecast K ({forecast_years[-1]}): {final_forecast:.3f}\n"
        f"Projected change: {change:+.1f}%\n"
        f"CI: [{ci_lower[-1]:.3f}, {ci_upper[-1]:.3f}]"
    )
    ax.text(
        0.02,
        0.98,
        summary_text,
        transform=ax.transAxes,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.7),
        fontsize=10,
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✅ Forecast plot saved to {output_path}")


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Forecast Historical K(t)")
    parser.add_argument("--data", type=Path, default="logs/historical_k/k_t_series.csv")
    parser.add_argument("--output", type=Path, default="logs/forecasting")
    parser.add_argument("--horizon", type=int, default=30, help="Years to forecast")
    parser.add_argument(
        "--method", choices=["arima", "holtwinters", "ensemble"], default="ensemble"
    )

    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    # Load data
    df = pd.read_csv(args.data)
    k_series = pd.Series(df["K"].values, index=df["year"].values)

    print(f"🔮 Forecasting K(t) with {args.method} for {args.horizon} years...")

    # Forecast
    result = forecast_k_trajectory(
        k_series, horizon_years=args.horizon, method=args.method
    )

    # Save results
    with open(args.output / "forecast.json", "w") as f:
        json.dump(result, f, indent=2)

    # Plot
    plot_forecast(k_series, result, args.output / "forecast_plot.png")

    print(f"\n🎉 Forecast complete!")
    print(f"   Final forecast ({result['years'][-1]}): {result['forecast'][-1]:.3f}")
    print(f"   95% CI: [{result['ci_lower'][-1]:.3f}, {result['ci_upper'][-1]:.3f}]")
