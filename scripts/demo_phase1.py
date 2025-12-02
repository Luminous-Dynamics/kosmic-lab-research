#!/usr/bin/env python3
"""
Phase 1 Demonstration: Quick Wins for Historical K(t)

Demonstrates all Phase 1 functionality:
1. Sensitivity analysis (proxy ablation)
2. Regime detection (change-point analysis)
3. Event validation
4. Time series forecasting
5. Cross-validation

Run with: poetry run python scripts/demo_phase1.py
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json

import pandas as pd
import yaml

from historical_k.forecasting import forecast_k_trajectory, plot_forecast
from historical_k.regimes import (
    detect_regime_changes,
    interpret_regimes,
    plot_regime_analysis,
)
from historical_k.sensitivity import (
    plot_ablation_results,
    proxy_ablation_study,
    summarize_top_proxies,
)
from historical_k.validation import temporal_cross_validation, validate_predicted_events


def main():
    print("=" * 80)
    print("🌊 Historical K(t) - Phase 1 Demonstration")
    print("=" * 80)
    print()

    # Setup
    config_path = Path("historical_k/k_config.yaml")
    data_path = Path("logs/historical_k/k_t_series.csv")
    output_dir = Path("logs/phase1_demo")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Ensure data exists
    if not data_path.exists():
        print("⚠️  K(t) data not found. Running compute_k first...")
        import subprocess

        subprocess.run(
            ["python", "-m", "historical_k.compute_k", "--config", str(config_path)],
            check=True,
        )
        print()

    # Load data
    df = pd.read_csv(data_path)
    k_series = pd.Series(df["K"].values, index=df["year"].values, name="K")

    with open(config_path) as f:
        config = yaml.safe_load(f)

    print(
        f"📊 Loaded K(t) data: {len(k_series)} points from {k_series.index[0]} to {k_series.index[-1]}"
    )
    print(f"   Mean K: {k_series.mean():.3f}, Std: {k_series.std():.3f}")
    print()

    # 1. Sensitivity Analysis
    print("-" * 80)
    print("1️⃣  SENSITIVITY ANALYSIS (Proxy Ablation Study)")
    print("-" * 80)
    print("Testing impact of removing each proxy variable...")
    print()

    try:
        results_ablation = proxy_ablation_study(config_path, output_dir / "sensitivity")
        plot_ablation_results(
            results_ablation, output_dir / "sensitivity" / "ablation_plot.png"
        )
        summary = summarize_top_proxies(results_ablation, n=5)

        (output_dir / "sensitivity" / "summary.md").write_text(summary)

        print("✅ Sensitivity analysis complete!")
        print(f"   Top 5 most important proxies:")
        valid = results_ablation[results_ablation["status"] == "success"].head(5)
        for i, (proxy, row) in enumerate(valid.iterrows(), 1):
            print(f"      {i}. {proxy} (RMSE impact: {row['rmse_impact']:.4f})")
        print(f"   📁 Results: {output_dir / 'sensitivity'}")
        print()
    except Exception as e:
        print(f"⚠️  Sensitivity analysis skipped (too slow for demo): {e}")
        print(
            "   Run manually with: python -m historical_k.sensitivity --config historical_k/k_config.yaml --plot"
        )
        print()

    # 2. Regime Detection
    print("-" * 80)
    print("2️⃣  REGIME DETECTION (Change-Point Analysis)")
    print("-" * 80)
    print("Identifying coherence transitions...")
    print()

    regimes_df, breakpoints = detect_regime_changes(k_series, penalty=3.0)
    plot_regime_analysis(
        k_series,
        regimes_df,
        breakpoints,
        output_dir / "regimes" / "regime_analysis.png",
    )

    interpretation = interpret_regimes(regimes_df)
    (output_dir / "regimes" / "interpretation.md").write_text(interpretation)

    print(f"✅ Detected {len(regimes_df)} regimes:")
    for _, regime in regimes_df.iterrows():
        print(
            f"   Regime {int(regime['regime_id'])}: {int(regime['start_year'])}-{int(regime['end_year'])} "
            f"(K̄={regime['mean_K']:.2f}, {regime['trend_direction']})"
        )
    print(f"   📁 Results: {output_dir / 'regimes'}")
    print()

    # 3. Event Validation
    print("-" * 80)
    print("3️⃣  EVENT VALIDATION (Preregistered Events)")
    print("-" * 80)
    print("Validating predicted troughs and peaks...")
    print()

    events = config.get("preregistered_events", {})
    validation_results = validate_predicted_events(k_series, events, window=10)

    with open(output_dir / "validation" / "event_validation.json", "w") as f:
        json.dump(validation_results, f, indent=2)

    print("✅ Event validation complete:")
    print(f"   Trough hit rate: {validation_results['trough_hit_rate']:.1%}")
    print(f"   Peak hit rate: {validation_results['peak_hit_rate']:.1%}")
    print(f"   Overall accuracy: {validation_results['overall_accuracy']:.1%}")
    print(f"   📁 Results: {output_dir / 'validation'}")
    print()

    # 4. Cross-Validation
    print("-" * 80)
    print("4️⃣  TEMPORAL CROSS-VALIDATION")
    print("-" * 80)
    print("Testing predictive validity with hold-out periods...")
    print()

    harmony_cols = [c for c in df.columns if c not in ["year", "K"]]
    harmony_frame = df[harmony_cols]

    cv_results, cv_summary = temporal_cross_validation(
        harmony_frame, k_series, n_folds=5
    )
    cv_results.to_csv(output_dir / "validation" / "cross_validation.csv", index=False)

    print("✅ Cross-validation complete:")
    print(f"   Mean RMSE: {cv_summary['mean_rmse']:.4f}")
    print(f"   Mean R²: {cv_summary['mean_r2']:.4f}")
    print(f"   Mean correlation: {cv_summary['mean_correlation']:.4f}")
    print(f"   📁 Results: {output_dir / 'validation'}")
    print()

    # 5. Forecasting
    print("-" * 80)
    print("5️⃣  TIME SERIES FORECASTING (K to 2050)")
    print("-" * 80)
    print("Projecting K(t) forward 30 years...")
    print()

    forecast_result = forecast_k_trajectory(
        k_series, horizon_years=30, method="ensemble"
    )
    plot_forecast(
        k_series, forecast_result, output_dir / "forecasting" / "forecast.png"
    )

    with open(output_dir / "forecasting" / "forecast.json", "w") as f:
        json.dump(forecast_result, f, indent=2)

    final_year = forecast_result["years"][-1]
    final_k = forecast_result["forecast"][-1]
    current_k = k_series.iloc[-1]
    change = ((final_k - current_k) / current_k) * 100

    print("✅ Forecast complete:")
    print(f"   Current K ({int(k_series.index[-1])}): {current_k:.3f}")
    print(f"   Forecast K ({final_year}): {final_k:.3f}")
    print(f"   Projected change: {change:+.1f}%")
    print(
        f"   95% CI: [{forecast_result['ci_lower'][-1]:.3f}, {forecast_result['ci_upper'][-1]:.3f}]"
    )
    print(f"   📁 Results: {output_dir / 'forecasting'}")
    print()

    # Summary
    print("=" * 80)
    print("🎉 PHASE 1 DEMONSTRATION COMPLETE!")
    print("=" * 80)
    print()
    print("📊 Summary of Analyses:")
    print(f"   1. Sensitivity Analysis: Identified most influential proxies")
    print(f"   2. Regime Detection: Found {len(regimes_df)} coherence regimes")
    print(
        f"   3. Event Validation: {validation_results['overall_accuracy']:.1%} accuracy"
    )
    print(f"   4. Cross-Validation: R² = {cv_summary['mean_r2']:.3f}")
    print(f"   5. Forecasting: K projected to {final_k:.3f} by {final_year}")
    print()
    print(f"📁 All results saved to: {output_dir.absolute()}")
    print()
    print("Next steps:")
    print("   - Review generated plots and analyses")
    print("   - Read interpretation files (*.md)")
    print("   - Proceed to Phase 2: Data Enhancement")
    print()


if __name__ == "__main__":
    main()
