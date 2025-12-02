"""
Validation tools for Historical K(t).

Includes event validation and temporal cross-validation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def validate_predicted_events(
    k_series: pd.Series, preregistered_events: Dict, window: int = 10
) -> Dict:
    """Validate preregistered event predictions against actual K(t).

    Args:
        k_series: K(t) time series
        preregistered_events: Dict with 'troughs' and 'peaks' lists (or nested lists)
        window: Years tolerance for matching

    Returns:
        Dict with validation metrics
    """
    # Collect all troughs and peaks from nested structure
    troughs_pred = []
    peaks_pred = []

    # Handle both flat and nested event structures
    if "troughs" in preregistered_events:
        troughs_pred = preregistered_events["troughs"]
    else:
        # Combine ancient_troughs, modern_troughs, etc.
        for key, value in preregistered_events.items():
            if "trough" in key.lower() and isinstance(value, list):
                troughs_pred.extend(value)

    if "peaks" in preregistered_events:
        peaks_pred = preregistered_events["peaks"]
    else:
        # Combine ancient_peaks, modern_peaks, etc.
        for key, value in preregistered_events.items():
            if "peak" in key.lower() and isinstance(value, list):
                peaks_pred.extend(value)

    # Find actual extrema
    k_smoothed = k_series.rolling(window=3, center=True).mean().fillna(k_series)
    troughs_actual = (
        k_smoothed.nsmallest(len(troughs_pred)).index.tolist() if troughs_pred else []
    )
    peaks_actual = (
        k_smoothed.nlargest(len(peaks_pred)).index.tolist() if peaks_pred else []
    )

    # Compute hit rates
    def hit_rate(predicted, actual, window):
        if not predicted:
            return 0.0
        hits = sum(1 for p in predicted if any(abs(p - a) <= window for a in actual))
        return hits / len(predicted)

    trough_hit = hit_rate(troughs_pred, troughs_actual, window)
    peak_hit = hit_rate(peaks_pred, peaks_actual, window)

    return {
        "trough_hit_rate": trough_hit,
        "peak_hit_rate": peak_hit,
        "overall_accuracy": (
            (trough_hit + peak_hit) / 2 if (troughs_pred or peaks_pred) else 0.0
        ),
        "window_tolerance": window,
        "troughs_predicted": len(troughs_pred),
        "peaks_predicted": len(peaks_pred),
        "troughs_matched": [
            p for p in troughs_pred if any(abs(p - a) <= window for a in troughs_actual)
        ],
        "peaks_matched": [
            p for p in peaks_pred if any(abs(p - a) <= window for a in peaks_actual)
        ],
    }


def temporal_cross_validation(
    harmony_frame: pd.DataFrame, k_series: pd.Series, n_folds: int = 5
) -> Tuple[pd.DataFrame, Dict]:
    """Perform temporal cross-validation on K(t) computation.

    Args:
        harmony_frame: DataFrame of harmony values
        k_series: True K(t) values
        n_folds: Number of validation folds

    Returns:
        Tuple of (fold_results_df, summary_dict)
    """
    # Filter out rows with NaN K values (ancient data without all harmonies)
    valid_mask = ~k_series.isna().values
    harmony_frame_valid = harmony_frame[valid_mask].reset_index(drop=True)
    k_series_valid = k_series[valid_mask].reset_index(drop=True)

    n_years = len(k_series_valid)
    fold_size = n_years // n_folds

    results = []
    for i in range(n_folds):
        # Hold out fold i
        test_indices = list(range(i * fold_size, min((i + 1) * fold_size, n_years)))
        test_mask = np.zeros(n_years, dtype=bool)
        test_mask[test_indices] = True
        train_mask = ~test_mask

        # Split data
        train_frame = harmony_frame_valid[train_mask]
        test_frame = harmony_frame_valid[test_mask]
        k_train = k_series_valid[train_mask]
        k_test = k_series_valid[test_mask]

        if len(k_test) == 0:
            continue

        # Simple equal weighting (could use Bayesian learning here)
        k_pred = test_frame.mean(axis=1)

        # Evaluate with safety checks for zero variance
        rmse = float(np.sqrt(((k_pred - k_test) ** 2).mean()))
        mae = float(abs(k_pred - k_test).mean())

        # R² with safety check for zero variance
        ss_tot = ((k_test - k_test.mean()) ** 2).sum()
        if ss_tot < 1e-10:
            r2 = np.nan  # Undefined when test set has zero variance
        else:
            ss_res = ((k_pred - k_test) ** 2).sum()
            r2 = float(1 - ss_res / ss_tot)

        # Correlation with safety check
        if k_pred.std() < 1e-10 or k_test.std() < 1e-10:
            corr = np.nan  # Undefined when either series has zero variance
        else:
            corr = float(k_pred.corr(k_test))

        results.append(
            {
                "fold": i + 1,
                "n_train": train_mask.sum(),
                "n_test": test_mask.sum(),
                "rmse": rmse,
                "mae": mae,
                "r2": r2,
                "correlation": corr,
            }
        )

    results_df = pd.DataFrame(results)

    summary = {
        "mean_rmse": float(results_df["rmse"].mean()),
        "mean_mae": float(results_df["mae"].mean()),
        "mean_r2": float(results_df["r2"].mean()),
        "mean_correlation": float(results_df["correlation"].mean()),
        "std_rmse": float(results_df["rmse"].std()),
    }

    return results_df, summary


if __name__ == "__main__":
    import argparse

    import yaml

    parser = argparse.ArgumentParser(description="Validation tools for Historical K(t)")
    parser.add_argument("--data", type=Path, default="logs/historical_k/k_t_series.csv")
    parser.add_argument("--config", type=Path, default="historical_k/k_config.yaml")
    parser.add_argument("--output", type=Path, default="logs/validation")
    parser.add_argument("--event-validation", action="store_true")
    parser.add_argument("--cross-validation", action="store_true")

    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    # Load data
    df = pd.read_csv(args.data)
    k_series = pd.Series(df["K"].values, index=df["year"].values)

    if args.event_validation:
        # Load preregistered events from config
        with open(args.config) as f:
            config = yaml.safe_load(f)
        events = config.get("preregistered_events", {})

        print("🔬 Validating preregistered events...")
        results = validate_predicted_events(k_series, events)

        print(f"✅ Event validation complete:")
        print(f"   Trough hit rate: {results['trough_hit_rate']:.1%}")
        print(f"   Peak hit rate: {results['peak_hit_rate']:.1%}")
        print(f"   Overall accuracy: {results['overall_accuracy']:.1%}")

        # Save results
        with open(args.output / "event_validation.json", "w") as f:
            import json

            json.dump(results, f, indent=2)

    if args.cross_validation:
        print("🔬 Running temporal cross-validation...")
        harmony_cols = [c for c in df.columns if c not in ["year", "K"]]
        harmony_frame = df[harmony_cols]

        cv_results, summary = temporal_cross_validation(harmony_frame, k_series)

        print(f"✅ Cross-validation complete:")
        print(f"   Mean RMSE: {summary['mean_rmse']:.4f}")
        print(f"   Mean R²: {summary['mean_r2']:.4f}")
        print(f"   Mean correlation: {summary['mean_correlation']:.4f}")

        cv_results.to_csv(args.output / "cross_validation.csv", index=False)
        with open(args.output / "cv_summary.json", "w") as f:
            import json

            json.dump(summary, f, indent=2)

    print(f"\n🎉 Validation complete! Results in {args.output}")
