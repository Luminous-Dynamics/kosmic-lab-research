#!/usr/bin/env python3
"""
Extended Historical K(t) Computation (3000 BCE - 2020 CE)

Integrates ancient data sources (Seshat, HYDE 3.2) with modern data
and computes K-index across all seven harmonies including the new
Evolutionary Progression harmony.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from historical_k import compute_k, etl
from historical_k.ancient_data import (
    fetch_hyde_demographics,
    fetch_seshat_data,
    merge_ancient_modern,
)
from historical_k.evolutionary_progression import compute_evolutionary_progression


def compute_k_extended(
    config_path: str | Path,
    output_dir: str | Path = "logs/historical_k_extended",
    hyde_proxy_path: str | Path = None,
) -> pd.DataFrame:
    """Compute extended K(t) from 3000 BCE to 2020 CE.

    Args:
        config_path: Path to extended configuration YAML
        output_dir: Directory for output files
        hyde_proxy_path: Path to HYDE-based evolutionary progression proxy CSV
                         (if provided, uses real proxy instead of synthetic)

    Returns:
        DataFrame with K(t), harmonies, and bands over 5000 years
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("🌊 Extended Historical K(t) Computation")
    print("   Temporal Coverage: 3000 BCE - 2020 CE")
    print("   Seven Harmonies including Evolutionary Progression")
    print("=" * 80)
    print()

    # Load configuration
    with open(config_path) as f:
        config = yaml.safe_load(f)

    start_year = config["temporal_coverage"]["start_year"]
    end_year = config["temporal_coverage"]["end_year"]

    print(
        f"📅 Computing K(t) from {start_year} to {end_year} ({end_year - start_year} years)"
    )
    print()

    # Step 1: Fetch ancient data sources
    print("Step 1: Fetching ancient data sources...")
    print("-" * 80)

    ancient_data = {}

    if config["data_sources"]["ancient"]["seshat"]["enabled"]:
        print("📜 Fetching Seshat Global History Databank...")
        seshat_df = fetch_seshat_data(
            start_year=start_year,
            end_year=500,
            output_dir=output_dir / "data" / "seshat",
        )
        ancient_data["seshat"] = seshat_df
        print(
            f"   ✅ Seshat: {len(seshat_df)} records ({seshat_df['year'].min()} to {seshat_df['year'].max()})"
        )

    if config["data_sources"]["ancient"]["hyde"]["enabled"]:
        print("🌍 Fetching HYDE 3.2 demographic reconstruction...")
        hyde_df = fetch_hyde_demographics(
            start_year=start_year,
            end_year=end_year,
            output_dir=output_dir / "data" / "hyde",
        )
        ancient_data["hyde"] = hyde_df
        print(
            f"   ✅ HYDE: {len(hyde_df)} records ({hyde_df['year'].min()} to {hyde_df['year'].max()})"
        )

    print()

    # Step 2: Load modern data (if exists)
    print("Step 2: Loading modern data...")
    print("-" * 80)

    modern_df = None
    modern_data_path = Path("logs/historical_k/k_t_series.csv")

    if modern_data_path.exists():
        print(f"📊 Loading existing modern K(t) from {modern_data_path}")
        modern_df = pd.read_csv(modern_data_path)
        print(
            f"   ✅ Modern data: {len(modern_df)} records ({modern_df['year'].min()} to {modern_df['year'].max()})"
        )
    else:
        print(
            "   ⚠️  No modern data found. Run standard compute_k.py first, or proceed with ancient-only."
        )

    print()

    # Step 3: Merge ancient and modern datasets
    print("Step 3: Integrating data sources...")
    print("-" * 80)

    # Combine all ancient sources
    if len(ancient_data) > 0:
        print("🔗 Merging ancient data sources...")

        # Start with Seshat as base
        if "seshat" in ancient_data:
            combined_ancient = ancient_data["seshat"].copy()

            # Merge in HYDE data
            if "hyde" in ancient_data:
                hyde = ancient_data["hyde"]
                # Align years and merge
                combined_ancient = pd.merge(
                    combined_ancient,
                    hyde,
                    on="year",
                    how="outer",
                    suffixes=("", "_hyde"),
                )
        elif "hyde" in ancient_data:
            combined_ancient = ancient_data["hyde"].copy()
        else:
            raise ValueError("No ancient data sources enabled")

        combined_ancient = combined_ancient.sort_values("year").reset_index(drop=True)
        print(f"   ✅ Combined ancient data: {len(combined_ancient)} records")

        # Merge with modern data if available
        if modern_df is not None:
            print("🔗 Merging ancient and modern datasets...")
            full_data = merge_ancient_modern(
                combined_ancient,
                modern_df,
                overlap_years=config["integration"]["overlap_window"],
            )
        else:
            full_data = combined_ancient

    else:
        if modern_df is not None:
            full_data = modern_df.copy()
        else:
            raise ValueError("No data sources available")

    print(f"   ✅ Full integrated dataset: {len(full_data)} records")
    print(f"   Coverage: {full_data['year'].min()} to {full_data['year'].max()}")
    print()

    # Step 4: Compute seventh harmony (Evolutionary Progression)
    print("Step 4: Computing seventh harmony (Evolutionary Progression)...")
    print("-" * 80)

    if hyde_proxy_path:
        # Load HYDE-based real proxy data
        print(f"   📥 Loading HYDE-based proxy from {hyde_proxy_path}")
        hyde_proxy_df = pd.read_csv(hyde_proxy_path)
        print(f"   ✅ Loaded {len(hyde_proxy_df)} years of HYDE proxy data")
        print(
            f"   Coverage: {hyde_proxy_df['year'].min()} to {hyde_proxy_df['year'].max()}"
        )

        # Merge with full_data
        full_data = full_data.merge(
            hyde_proxy_df[["year", "evolutionary_progression"]], on="year", how="left"
        )

        # Fill any missing years with interpolation
        full_data["evolutionary_progression"] = (
            full_data["evolutionary_progression"]
            .interpolate(method="linear")
            .fillna(method="bfill")
            .fillna(method="ffill")
        )

        print(f"   🔄 Merged HYDE proxy with full dataset")
        print(
            f"   Range: {full_data['evolutionary_progression'].min():.3f} - {full_data['evolutionary_progression'].max():.3f}"
        )
    else:
        # Use synthetic computation (original approach)
        print("   🔄 Computing synthetic evolutionary progression")
        progression = compute_evolutionary_progression(full_data, config)
        full_data["evolutionary_progression"] = progression

    print()

    # Step 5: Compute K-index with all seven harmonies
    print("Step 5: Computing extended K-index...")
    print("-" * 80)

    # List all harmony columns
    harmony_cols = [
        "resonant_coherence",
        "interconnection",
        "reciprocity",
        "play_entropy",
        "wisdom_accuracy",
        "flourishing",
        "evolutionary_progression",
    ]

    # For simplicity, if harmonies don't exist, compute from proxies
    # In production, would use full etl.py logic
    available_harmonies = [col for col in harmony_cols if col in full_data.columns]

    if len(available_harmonies) < 7:
        print("   ⚠️  Not all harmonies available in data. Computing from proxies...")

        # Generate placeholder harmonies (in production, use actual proxy data)
        for harmony in harmony_cols:
            if harmony not in full_data.columns:
                if harmony == "evolutionary_progression":
                    # Already computed
                    continue
                else:
                    # Placeholder: random walk around historical mean
                    print(f"   🔄 Generating synthetic {harmony}...")
                    base = 0.5
                    noise = np.random.normal(0, 0.1, len(full_data))
                    trend = 0.0001 * (full_data["year"] - full_data["year"].min())
                    full_data[harmony] = np.clip(base + trend + noise, 0, 1)

    # Normalize all harmonies to [0, 1] epoch-aware if configured
    if config["windows"]["normalization"] == "minmax_by_epoch":
        print("   🔄 Applying epoch-aware normalization...")
        epochs = config["integration"]["normalization"]["epochs"]

        for harmony in harmony_cols:
            if harmony in full_data.columns:
                for epoch in epochs:
                    mask = (full_data["year"] >= epoch["start"]) & (
                        full_data["year"] <= epoch["end"]
                    )
                    if mask.any():
                        epoch_data = full_data.loc[mask, harmony]
                        min_val = epoch_data.min()
                        max_val = epoch_data.max()
                        if max_val > min_val:
                            full_data.loc[mask, harmony] = (epoch_data - min_val) / (
                                max_val - min_val
                            )

    # Compute K as weighted average of harmonies
    weights = config["harmony_weights"]
    k_values = np.zeros(len(full_data))

    for harmony in harmony_cols:
        if harmony in full_data.columns:
            k_values += full_data[harmony].values * weights[harmony]

    full_data["K"] = k_values
    print(
        f"   ✅ K-index computed (mean: {k_values.mean():.3f}, std: {k_values.std():.3f})"
    )
    print()

    # Step 6: Uncertainty quantification
    print("Step 6: Uncertainty quantification...")
    print("-" * 80)

    if config["uncertainty"]["bootstrap_samples"] > 0:
        print(
            f"   🎲 Running {config['uncertainty']['bootstrap_samples']} bootstrap samples..."
        )

        # Simplified bootstrap: resample harmonies and recompute K
        n_samples = config["uncertainty"]["bootstrap_samples"]
        n_records = len(full_data)

        bootstrap_k = np.zeros((n_records, n_samples))

        np.random.seed(config["uncertainty"]["seed"])

        for i in range(n_samples):
            if (i + 1) % 500 == 0:
                print(f"      Progress: {i+1}/{n_samples}")

            # Resample with replacement
            indices = np.random.choice(n_records, size=n_records, replace=True)
            resampled = full_data.iloc[indices]

            # Recompute K
            k_boot = np.zeros(n_records)
            for harmony in harmony_cols:
                if harmony in resampled.columns:
                    # Re-aggregate back to original years
                    for idx, year in enumerate(full_data["year"]):
                        year_mask = resampled["year"] == year
                        if year_mask.any():
                            k_boot[idx] += (
                                resampled.loc[year_mask, harmony].mean()
                                * weights[harmony]
                            )

            bootstrap_k[:, i] = k_boot

        # Compute confidence intervals
        ci_level = config["uncertainty"]["ci"]
        alpha = 1 - ci_level

        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100

        full_data["K_lower"] = np.percentile(bootstrap_k, lower_percentile, axis=1)
        full_data["K_upper"] = np.percentile(bootstrap_k, upper_percentile, axis=1)

        print(
            f"   ✅ Bootstrap complete. {ci_level*100:.0f}% confidence intervals computed."
        )
    else:
        print("   ⏭️  Bootstrap disabled.")
        full_data["K_lower"] = full_data["K"]
        full_data["K_upper"] = full_data["K"]

    print()

    # Step 7: Save results
    print("Step 7: Saving results...")
    print("-" * 80)

    # Primary K(t) series
    output_cols = ["year", "K", "K_lower", "K_upper"] + harmony_cols
    available_output_cols = [col for col in output_cols if col in full_data.columns]

    k_series_path = Path(config["output"]["k_series"]["path"])
    k_series_path.parent.mkdir(parents=True, exist_ok=True)

    full_data[available_output_cols].to_csv(k_series_path, index=False)
    print(f"   ✅ K(t) series saved: {k_series_path}")

    # Detailed results
    if config["output"]["detailed"]["path"]:
        detailed_path = Path(config["output"]["detailed"]["path"])
        detailed_path.parent.mkdir(parents=True, exist_ok=True)
        full_data.to_csv(detailed_path, index=False)
        print(f"   ✅ Detailed results saved: {detailed_path}")

    print()

    # Step 8: Summary statistics
    print("=" * 80)
    print("📊 EXTENDED K(T) SUMMARY")
    print("=" * 80)
    print(
        f"Temporal Coverage: {full_data['year'].min()} to {full_data['year'].max()} ({len(full_data)} records)"
    )
    print(f"\nK-index Statistics:")
    print(f"  Mean: {full_data['K'].mean():.4f}")
    print(f"  Std:  {full_data['K'].std():.4f}")
    print(
        f"  Min:  {full_data['K'].min():.4f} (year {full_data.loc[full_data['K'].idxmin(), 'year']:.0f})"
    )
    print(
        f"  Max:  {full_data['K'].max():.4f} (year {full_data.loc[full_data['K'].idxmax(), 'year']:.0f})"
    )
    print(f"\nSeven Harmonies (mean scores):")
    for harmony in harmony_cols:
        if harmony in full_data.columns:
            print(f"  {harmony:30s}: {full_data[harmony].mean():.4f}")
    print("=" * 80)
    print()

    return full_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compute extended Historical K(t) from 3000 BCE to 2020 CE"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default="historical_k/k_config_extended.yaml",
        help="Path to extended configuration YAML",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default="logs/historical_k_extended",
        help="Output directory",
    )
    parser.add_argument(
        "--hyde-proxy",
        type=Path,
        default=None,
        help="Path to HYDE-based evolutionary progression proxy CSV (optional)",
    )

    args = parser.parse_args()

    result_df = compute_k_extended(args.config, args.output, args.hyde_proxy)

    print("✅ Extended Historical K(t) computation complete!")
    print(f"📁 Results saved to: {args.output}")
