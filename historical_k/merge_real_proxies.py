"""
Merge Real Data Proxies into Evolutionary Progression Harmony.

Combines:
- Technological sophistication (WIPO patents)
- Cognitive complexity (Barro-Lee education)
- Institutional evolution (Polity5)

Into unified evolutionary_progression harmony for Historical K(t).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd


def load_proxy_data(data_dir: Path) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load all three processed proxy datasets.

    Args:
        data_dir: Directory containing processed data files

    Returns:
        Tuple of (tech_df, cognitive_df, institutional_df)
    """
    print("📥 Loading processed proxy data...")

    tech_file = data_dir / "tech_sophistication_1883_2023.csv"
    cognitive_file = data_dir / "cognitive_complexity_1950_2015.csv"
    institutional_file = data_dir / "institutional_evolution_1800_2018.csv"

    # Load technological sophistication
    if tech_file.exists():
        tech_df = pd.read_csv(tech_file)
        print(
            f"   ✓ Tech sophistication: {len(tech_df)} years ({tech_df['year'].min()}-{tech_df['year'].max()})"
        )
    else:
        print(f"   ⚠️  Tech sophistication file not found: {tech_file}")
        tech_df = None

    # Load cognitive complexity
    if cognitive_file.exists():
        cognitive_df = pd.read_csv(cognitive_file)
        print(
            f"   ✓ Cognitive complexity: {len(cognitive_df)} years ({cognitive_df['year'].min()}-{cognitive_df['year'].max()})"
        )
    else:
        print(f"   ⚠️  Cognitive complexity file not found: {cognitive_file}")
        cognitive_df = None

    # Load institutional evolution
    if institutional_file.exists():
        institutional_df = pd.read_csv(institutional_file)
        print(
            f"   ✓ Institutional evolution: {len(institutional_df)} years ({institutional_df['year'].min()}-{institutional_df['year'].max()})"
        )
    else:
        print(f"   ⚠️  Institutional evolution file not found: {institutional_file}")
        institutional_df = None

    return tech_df, cognitive_df, institutional_df


def merge_proxies(
    tech_df: pd.DataFrame,
    cognitive_df: pd.DataFrame,
    institutional_df: pd.DataFrame,
    weights: Dict[str, float] = None,
    year_range: Tuple[int, int] = (1800, 2020),
) -> pd.DataFrame:
    """
    Merge three proxy datasets into single evolutionary_progression harmony.

    Args:
        tech_df: Technological sophistication data
        cognitive_df: Cognitive complexity data
        institutional_df: Institutional evolution data
        weights: Dictionary with keys 'tech', 'cognitive', 'institutional'
        year_range: Tuple of (start_year, end_year)

    Returns:
        DataFrame with year and evolutionary_progression columns
    """
    print(f"\n🔀 Merging proxies for year range {year_range[0]}-{year_range[1]}...")

    # Default weights (from Track B plan)
    if weights is None:
        weights = {"tech": 0.4, "cognitive": 0.3, "institutional": 0.3}

    print(
        f"   Weights: tech={weights['tech']}, cognitive={weights['cognitive']}, institutional={weights['institutional']}"
    )

    # Create full year range
    years = list(range(year_range[0], year_range[1] + 1))
    merged_df = pd.DataFrame({"year": years})

    # Merge technological sophistication
    if tech_df is not None:
        merged_df = merged_df.merge(
            tech_df[["year", "tech_sophistication"]], on="year", how="left"
        )
        n_tech = merged_df["tech_sophistication"].notna().sum()
        print(f"   Tech sophistication: {n_tech}/{len(merged_df)} years with data")
    else:
        merged_df["tech_sophistication"] = np.nan
        print(f"   Tech sophistication: No data available")

    # Merge cognitive complexity
    if cognitive_df is not None:
        merged_df = merged_df.merge(
            cognitive_df[["year", "cognitive_complexity"]], on="year", how="left"
        )
        n_cognitive = merged_df["cognitive_complexity"].notna().sum()
        print(
            f"   Cognitive complexity: {n_cognitive}/{len(merged_df)} years with data"
        )
    else:
        merged_df["cognitive_complexity"] = np.nan
        print(f"   Cognitive complexity: No data available")

    # Merge institutional evolution
    if institutional_df is not None:
        merged_df = merged_df.merge(
            institutional_df[["year", "institutional_evolution"]], on="year", how="left"
        )
        n_institutional = merged_df["institutional_evolution"].notna().sum()
        print(
            f"   Institutional evolution: {n_institutional}/{len(merged_df)} years with data"
        )
    else:
        merged_df["institutional_evolution"] = np.nan
        print(f"   Institutional evolution: No data available")

    # Interpolate missing values (forward and backward fill for edges)
    print("\n   Interpolating missing values...")
    merged_df["tech_sophistication"] = (
        merged_df["tech_sophistication"]
        .interpolate(method="linear")
        .fillna(method="bfill")
        .fillna(method="ffill")
    )
    merged_df["cognitive_complexity"] = (
        merged_df["cognitive_complexity"]
        .interpolate(method="linear")
        .fillna(method="bfill")
        .fillna(method="ffill")
    )
    merged_df["institutional_evolution"] = (
        merged_df["institutional_evolution"]
        .interpolate(method="linear")
        .fillna(method="bfill")
        .fillna(method="ffill")
    )

    # Check remaining NaN values
    nan_tech = merged_df["tech_sophistication"].isna().sum()
    nan_cognitive = merged_df["cognitive_complexity"].isna().sum()
    nan_institutional = merged_df["institutional_evolution"].isna().sum()

    if nan_tech > 0 or nan_cognitive > 0 or nan_institutional > 0:
        print(f"   ⚠️  Remaining NaN after interpolation:")
        print(
            f"      Tech: {nan_tech}, Cognitive: {nan_cognitive}, Institutional: {nan_institutional}"
        )

    # Compute evolutionary progression as weighted average
    merged_df["evolutionary_progression"] = (
        weights["tech"] * merged_df["tech_sophistication"]
        + weights["cognitive"] * merged_df["cognitive_complexity"]
        + weights["institutional"] * merged_df["institutional_evolution"]
    )

    # Normalize to [0, 1]
    min_val = merged_df["evolutionary_progression"].min()
    max_val = merged_df["evolutionary_progression"].max()
    merged_df["evolutionary_progression"] = (
        merged_df["evolutionary_progression"] - min_val
    ) / (max_val - min_val)

    print(f"\n✅ Evolutionary progression computed:")
    print(f"   Years: {len(merged_df)}")
    print(
        f"   Range: {merged_df['evolutionary_progression'].min():.3f} - {merged_df['evolutionary_progression'].max():.3f}"
    )
    print(f"   Mean: {merged_df['evolutionary_progression'].mean():.3f}")
    if 2020 in merged_df["year"].values:
        print(
            f"   2020 value: {merged_df[merged_df['year'] == 2020]['evolutionary_progression'].values[0]:.3f}"
        )

    return merged_df


def save_merged_data(merged_df: pd.DataFrame, output_file: Path):
    """
    Save merged evolutionary progression data.

    Args:
        merged_df: Merged DataFrame
        output_file: Output file path
    """
    print(f"\n💾 Saving merged data to {output_file}")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Save main data
    result_df = merged_df[["year", "evolutionary_progression"]].copy()
    result_df.to_csv(output_file, index=False)
    print(f"   ✓ Saved evolutionary progression")

    # Save detailed version with all components
    detailed_file = output_file.parent / f"{output_file.stem}_detailed.csv"
    merged_df.to_csv(detailed_file, index=False)
    print(f"   ✓ Saved detailed version: {detailed_file}")

    # Summary statistics
    summary = {
        "source": "Merged real data (WIPO + Barro-Lee + Polity5)",
        "coverage": f"{merged_df['year'].min()}-{merged_df['year'].max()}",
        "n_years": len(merged_df),
        "min_value": float(merged_df["evolutionary_progression"].min()),
        "max_value": float(merged_df["evolutionary_progression"].max()),
        "mean_value": float(merged_df["evolutionary_progression"].mean()),
        "value_2020": (
            float(
                merged_df[merged_df["year"] == 2020]["evolutionary_progression"].values[
                    0
                ]
            )
            if 2020 in merged_df["year"].values
            else None
        ),
        "components": {
            "tech_mean": float(merged_df["tech_sophistication"].mean()),
            "cognitive_mean": float(merged_df["cognitive_complexity"].mean()),
            "institutional_mean": float(merged_df["institutional_evolution"].mean()),
        },
    }

    summary_file = output_file.parent / f"{output_file.stem}_summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"   ✓ Summary saved: {summary_file}")


def compare_with_synthetic(merged_df: pd.DataFrame, synthetic_file: Path = None):
    """
    Compare merged real data with original synthetic proxy.

    Args:
        merged_df: Merged DataFrame with real data
        synthetic_file: Path to original K(t) file with synthetic evolutionary progression
    """
    if synthetic_file is None or not synthetic_file.exists():
        print("\n⚠️  No synthetic data file provided for comparison")
        return

    print(f"\n📊 Comparing with synthetic data from {synthetic_file}")

    # Load original data
    orig_df = pd.read_csv(synthetic_file)

    if "evolutionary_progression" not in orig_df.columns:
        print("   ⚠️  No evolutionary_progression column found in synthetic file")
        return

    # Merge for comparison
    comparison = merged_df[["year", "evolutionary_progression"]].merge(
        orig_df[["year", "evolutionary_progression"]],
        on="year",
        how="inner",
        suffixes=("_real", "_synthetic"),
    )

    # Compute correlation
    corr = comparison["evolutionary_progression_real"].corr(
        comparison["evolutionary_progression_synthetic"]
    )
    print(f"   Correlation (real vs synthetic): r = {corr:.3f}")

    # Compute RMSE
    rmse = np.sqrt(
        (
            (
                comparison["evolutionary_progression_real"]
                - comparison["evolutionary_progression_synthetic"]
            )
            ** 2
        ).mean()
    )
    print(f"   RMSE (real vs synthetic): {rmse:.3f}")

    # Compare 2020 values
    if 2020 in comparison["year"].values:
        real_2020 = comparison[comparison["year"] == 2020][
            "evolutionary_progression_real"
        ].values[0]
        synth_2020 = comparison[comparison["year"] == 2020][
            "evolutionary_progression_synthetic"
        ].values[0]
        diff = real_2020 - synth_2020
        print(
            f"   2020 value: Real={real_2020:.3f}, Synthetic={synth_2020:.3f}, Diff={diff:+.3f}"
        )


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Merge Real Data Proxies into Evolutionary Progression"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data/processed"),
        help="Directory with processed proxy files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/evolutionary_progression_1800_2020.csv"),
        help="Output file path",
    )
    parser.add_argument(
        "--compare",
        type=Path,
        default=None,
        help="Compare with synthetic data file (original K(t) series)",
    )
    parser.add_argument("--year-start", type=int, default=1800, help="Start year")
    parser.add_argument("--year-end", type=int, default=2020, help="End year")

    args = parser.parse_args()

    # Load data
    tech_df, cognitive_df, institutional_df = load_proxy_data(args.data_dir)

    # Check if at least one dataset available
    if tech_df is None and cognitive_df is None and institutional_df is None:
        print("\n❌ No proxy data files found!")
        print("   Please run:")
        print("     python historical_k/wipo_integration.py --process")
        print("     python historical_k/barro_lee_integration.py --process")
        print("     python historical_k/polity_integration.py --process")
        return 1

    # Merge proxies
    merged_df = merge_proxies(
        tech_df,
        cognitive_df,
        institutional_df,
        year_range=(args.year_start, args.year_end),
    )

    # Save merged data
    save_merged_data(merged_df, args.output)

    # Compare with synthetic if provided
    if args.compare:
        compare_with_synthetic(merged_df, args.compare)

    print(f"\n🎉 Merge complete!")

    return 0


if __name__ == "__main__":
    exit(main())
