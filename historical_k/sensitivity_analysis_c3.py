#!/usr/bin/env python3
"""
Track C-3: Sensitivity Analysis for Historical K(t)

Tests robustness of K₂₀₂₀ = 0.9144 finding to:
1. Alternative proxy component weights (5 schemes)
2. Alternative normalization methods (4 approaches)

Quantifies sensitivity: ΔK₂₀₂₀ / Δparameters
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Set publication-quality style
sns.set_context("paper", font_scale=1.2)
sns.set_style("whitegrid")
plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["font.family"] = "serif"


def load_hyde_proxy_data(hyde_file: Path) -> pd.DataFrame:
    """Load HYDE evolutionary progression proxy data."""
    print(f"📥 Loading HYDE proxy data from {hyde_file}")
    df = pd.read_csv(hyde_file)
    print(
        f"   ✅ Loaded {len(df)} years ({df['year'].min():.0f} to {df['year'].max():.0f})"
    )
    return df


def load_k_series(k_file: Path) -> pd.DataFrame:
    """Load K(t) time series."""
    print(f"📥 Loading K(t) series from {k_file}")
    df = pd.read_csv(k_file)
    print(
        f"   ✅ Loaded {len(df)} years ({df['year'].min():.0f} to {df['year'].max():.0f})"
    )
    return df


def normalize_minmax(data: pd.Series) -> pd.Series:
    """Min-max normalization: [0, 1]."""
    return (data - data.min()) / (data.max() - data.min())


def normalize_zscore(data: pd.Series) -> pd.Series:
    """Z-score standardization: mean=0, std=1, then rescale to [0, 1]."""
    z = (data - data.mean()) / data.std()
    # Rescale to [0, 1]
    return (z - z.min()) / (z.max() - z.min())


def normalize_rank(data: pd.Series) -> pd.Series:
    """Rank-based normalization: ranks divided by max rank."""
    ranks = data.rank(method="average")
    return (ranks - 1) / (len(ranks) - 1)


def normalize_quantile(data: pd.Series) -> pd.Series:
    """Quantile (uniform) transformation."""
    ranks = data.rank(method="average")
    return (ranks - 0.5) / len(ranks)


NORMALIZATION_METHODS = {
    "minmax": ("Min-Max", normalize_minmax),
    "zscore": ("Z-Score", normalize_zscore),
    "rank": ("Rank-Based", normalize_rank),
    "quantile": ("Quantile", normalize_quantile),
}


def compute_evolutionary_proxy_with_weights(
    hyde_data: pd.DataFrame,
    tech_weight: float,
    cognitive_weight: float,
    institutional_weight: float,
    normalization: str = "minmax",
) -> pd.Series:
    """
    Compute evolutionary progression with custom weights.

    Args:
        hyde_data: HYDE demographic DataFrame with component columns
        tech_weight: Weight for tech_sophistication
        cognitive_weight: Weight for cognitive_complexity
        institutional_weight: Weight for institutional_evolution
        normalization: Normalization method ('minmax', 'zscore', 'rank', 'quantile')

    Returns:
        Series with evolutionary_progression values
    """
    # Get normalization function
    norm_func = NORMALIZATION_METHODS[normalization][1]

    # Normalize components
    tech_norm = norm_func(hyde_data["tech_sophistication"])
    cognitive_norm = norm_func(hyde_data["cognitive_complexity"])
    institutional_norm = norm_func(hyde_data["institutional_evolution"])

    # Weighted combination
    evolutionary_proxy = (
        tech_weight * tech_norm
        + cognitive_weight * cognitive_norm
        + institutional_weight * institutional_norm
    )

    return evolutionary_proxy


def recompute_k_with_new_proxy(
    k_series: pd.DataFrame, new_proxy: pd.Series, years: pd.Series
) -> pd.DataFrame:
    """
    Recompute K-index with new evolutionary progression proxy.

    Args:
        k_series: Original K(t) series
        new_proxy: New evolutionary progression values
        years: Corresponding years

    Returns:
        Modified K(t) series with new proxy
    """
    # Create new proxy dataframe
    proxy_df = pd.DataFrame({"year": years, "evolutionary_progression_new": new_proxy})

    # Merge with K series
    merged = k_series.merge(proxy_df, on="year", how="left")

    # Fill missing years with interpolation
    merged["evolutionary_progression_new"] = (
        merged["evolutionary_progression_new"]
        .interpolate(method="linear")
        .fillna(method="bfill")
        .fillna(method="ffill")
    )

    # Recompute K-index
    # K = mean of seven harmonies
    harmonies = [
        "resonant_coherence",
        "interconnection",
        "reciprocity",
        "play_entropy",
        "wisdom_accuracy",
        "flourishing",
        "evolutionary_progression_new",  # Use new proxy
    ]

    # Check all harmonies exist
    for h in harmonies[:-1]:  # Exclude last (we just added it)
        if h not in merged.columns:
            raise ValueError(f"Harmony {h} not found in K series")

    merged["K_new"] = merged[harmonies].mean(axis=1)

    return merged


def test_weight_sensitivity(
    hyde_data: pd.DataFrame, k_series: pd.DataFrame, normalization: str = "minmax"
) -> Dict:
    """
    Test sensitivity to alternative weight schemes.

    Tests 5 schemes:
    1. Baseline: 40/30/30 (tech/cognitive/institutional)
    2. Equal: 33/33/33
    3. Tech-heavy: 50/25/25
    4. Cognitive-heavy: 25/50/25
    5. Institutional-heavy: 25/25/50

    Returns:
        Dictionary with results for each scheme
    """
    print(f"\n🔬 Testing Weight Sensitivity (normalization={normalization})...")

    weight_schemes = {
        "baseline": (0.40, 0.30, 0.30),
        "equal": (0.333, 0.333, 0.333),
        "tech_heavy": (0.50, 0.25, 0.25),
        "cognitive_heavy": (0.25, 0.50, 0.25),
        "institutional_heavy": (0.25, 0.25, 0.50),
    }

    results = {}

    for scheme_name, (tech_w, cog_w, inst_w) in weight_schemes.items():
        print(
            f"   Testing {scheme_name}: tech={tech_w:.2f}, cog={cog_w:.2f}, inst={inst_w:.2f}"
        )

        # Compute new proxy
        new_proxy = compute_evolutionary_proxy_with_weights(
            hyde_data, tech_w, cog_w, inst_w, normalization
        )

        # Recompute K(t)
        k_new = recompute_k_with_new_proxy(k_series, new_proxy, hyde_data["year"])

        # Get K₂₀₂₀
        k_2020 = (
            k_new.loc[k_new["year"] == 2020, "K_new"].values[0]
            if len(k_new[k_new["year"] == 2020]) > 0
            else np.nan
        )

        results[scheme_name] = {
            "weights": {"tech": tech_w, "cognitive": cog_w, "institutional": inst_w},
            "K_2020": float(k_2020),
            "K_mean": float(k_new["K_new"].mean()),
            "K_std": float(k_new["K_new"].std()),
        }

        print(f"      K₂₀₂₀ = {k_2020:.4f}")

    # Compute sensitivity metrics
    baseline_k = results["baseline"]["K_2020"]
    max_k = max(r["K_2020"] for r in results.values())
    min_k = min(r["K_2020"] for r in results.values())
    delta_k = max_k - min_k
    relative_sensitivity = delta_k / baseline_k if baseline_k > 0 else 0

    results["summary"] = {
        "baseline_K_2020": baseline_k,
        "max_K_2020": max_k,
        "min_K_2020": min_k,
        "delta_K_2020": delta_k,
        "relative_sensitivity": relative_sensitivity,
        "relative_sensitivity_pct": relative_sensitivity * 100,
    }

    print(f"\n   📊 Weight Sensitivity Summary:")
    print(f"      Baseline K₂₀₂₀: {baseline_k:.4f}")
    print(f"      Range: [{min_k:.4f}, {max_k:.4f}]")
    print(f"      Δ: {delta_k:.4f} ({relative_sensitivity*100:.2f}%)")

    return results


def test_normalization_sensitivity(
    hyde_data: pd.DataFrame, k_series: pd.DataFrame
) -> Dict:
    """
    Test sensitivity to alternative normalization methods.

    Tests 4 methods:
    1. Min-max (baseline)
    2. Z-score standardization
    3. Rank-based
    4. Quantile transformation

    Returns:
        Dictionary with results for each method
    """
    print(f"\n🔬 Testing Normalization Sensitivity...")

    # Use baseline weights
    tech_w, cog_w, inst_w = 0.40, 0.30, 0.30

    results = {}

    for norm_key, (norm_name, _) in NORMALIZATION_METHODS.items():
        print(f"   Testing {norm_name}...")

        # Compute new proxy with this normalization
        new_proxy = compute_evolutionary_proxy_with_weights(
            hyde_data, tech_w, cog_w, inst_w, norm_key
        )

        # Recompute K(t)
        k_new = recompute_k_with_new_proxy(k_series, new_proxy, hyde_data["year"])

        # Get K₂₀₂₀
        k_2020 = (
            k_new.loc[k_new["year"] == 2020, "K_new"].values[0]
            if len(k_new[k_new["year"] == 2020]) > 0
            else np.nan
        )

        results[norm_key] = {
            "name": norm_name,
            "K_2020": float(k_2020),
            "K_mean": float(k_new["K_new"].mean()),
            "K_std": float(k_new["K_new"].std()),
        }

        print(f"      K₂₀₂₀ = {k_2020:.4f}")

    # Compute sensitivity metrics
    baseline_k = results["minmax"]["K_2020"]
    max_k = max(r["K_2020"] for r in results.values())
    min_k = min(r["K_2020"] for r in results.values())
    delta_k = max_k - min_k
    relative_sensitivity = delta_k / baseline_k if baseline_k > 0 else 0

    results["summary"] = {
        "baseline_K_2020": baseline_k,
        "max_K_2020": max_k,
        "min_K_2020": min_k,
        "delta_K_2020": delta_k,
        "relative_sensitivity": relative_sensitivity,
        "relative_sensitivity_pct": relative_sensitivity * 100,
    }

    print(f"\n   📊 Normalization Sensitivity Summary:")
    print(f"      Baseline K₂₀₂₀: {baseline_k:.4f}")
    print(f"      Range: [{min_k:.4f}, {max_k:.4f}]")
    print(f"      Δ: {delta_k:.4f} ({relative_sensitivity*100:.2f}%)")

    return results


def plot_weight_sensitivity(results: Dict, output_file: Path):
    """Create visualization of weight sensitivity results."""
    print(f"\n📊 Creating weight sensitivity visualization...")

    # Extract data
    schemes = [
        "baseline",
        "equal",
        "tech_heavy",
        "cognitive_heavy",
        "institutional_heavy",
    ]
    scheme_names = [
        "Baseline\n(40/30/30)",
        "Equal\n(33/33/33)",
        "Tech-Heavy\n(50/25/25)",
        "Cognitive-Heavy\n(25/50/25)",
        "Institutional-Heavy\n(25/25/50)",
    ]
    k_values = [results[s]["K_2020"] for s in schemes]

    baseline_k = results["baseline"]["K_2020"]

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Bar plot
    bars = ax.bar(range(len(schemes)), k_values, color="steelblue", alpha=0.7)

    # Highlight baseline
    bars[0].set_color("darkblue")
    bars[0].set_alpha(1.0)

    # Baseline reference line
    ax.axhline(
        baseline_k,
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Baseline: {baseline_k:.4f}",
    )

    # Labels
    ax.set_xticks(range(len(schemes)))
    ax.set_xticklabels(scheme_names, fontsize=10)
    ax.set_ylabel("K₂₀₂₀", fontsize=12, fontweight="bold")
    ax.set_title(
        "Weight Sensitivity Analysis\nK₂₀₂₀ Across Alternative Weight Schemes",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )

    # Value labels on bars
    for i, (bar, val) in enumerate(zip(bars, k_values)):
        height = bar.get_height()
        delta = val - baseline_k
        delta_pct = (delta / baseline_k) * 100
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{val:.4f}\n({delta_pct:+.1f}%)",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    output_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"   ✅ Saved to {output_file}")
    plt.close()


def plot_normalization_sensitivity(results: Dict, output_file: Path):
    """Create visualization of normalization sensitivity results."""
    print(f"\n📊 Creating normalization sensitivity visualization...")

    # Extract data
    norm_keys = ["minmax", "zscore", "rank", "quantile"]
    norm_names = [results[k]["name"] for k in norm_keys]
    k_values = [results[k]["K_2020"] for k in norm_keys]

    baseline_k = results["minmax"]["K_2020"]

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Bar plot
    bars = ax.bar(range(len(norm_keys)), k_values, color="forestgreen", alpha=0.7)

    # Highlight baseline
    bars[0].set_color("darkgreen")
    bars[0].set_alpha(1.0)

    # Baseline reference line
    ax.axhline(
        baseline_k,
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Baseline: {baseline_k:.4f}",
    )

    # Labels
    ax.set_xticks(range(len(norm_keys)))
    ax.set_xticklabels(norm_names, fontsize=11)
    ax.set_ylabel("K₂₀₂₀", fontsize=12, fontweight="bold")
    ax.set_title(
        "Normalization Sensitivity Analysis\nK₂₀₂₀ Across Alternative Normalization Methods",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )

    # Value labels on bars
    for i, (bar, val) in enumerate(zip(bars, k_values)):
        height = bar.get_height()
        delta = val - baseline_k
        delta_pct = (delta / baseline_k) * 100
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{val:.4f}\n({delta_pct:+.1f}%)",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    output_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"   ✅ Saved to {output_file}")
    plt.close()


def generate_sensitivity_report(
    weight_results: Dict, norm_results: Dict, output_file: Path
):
    """Generate markdown report of sensitivity analysis."""
    print(f"\n📝 Generating sensitivity report...")

    lines = []
    lines.append("# Track C-3: Sensitivity Analysis Report")
    lines.append("")
    lines.append(f"**Generated**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # Weight sensitivity
    lines.append("## 1. Weight Sensitivity Analysis")
    lines.append("")
    lines.append(
        "**Objective**: Test robustness of K₂₀₂₀ to alternative weight schemes for combining three evolutionary progression components (tech, cognitive, institutional)."
    )
    lines.append("")

    ws = weight_results["summary"]
    lines.append(f"**Baseline K₂₀₂₀**: {ws['baseline_K_2020']:.4f}")
    lines.append(f"**K₂₀₂₀ Range**: [{ws['min_K_2020']:.4f}, {ws['max_K_2020']:.4f}]")
    lines.append(
        f"**ΔK₂₀₂₀**: {ws['delta_K_2020']:.4f} ({ws['relative_sensitivity_pct']:.2f}% relative)"
    )
    lines.append("")

    lines.append("### Weight Schemes Tested")
    lines.append("")
    lines.append(
        "| Scheme | Tech | Cognitive | Institutional | K₂₀₂₀ | Δ from Baseline | % Change |"
    )
    lines.append(
        "|--------|------|-----------|---------------|-------|-----------------|----------|"
    )

    baseline_k = ws["baseline_K_2020"]
    for scheme in [
        "baseline",
        "equal",
        "tech_heavy",
        "cognitive_heavy",
        "institutional_heavy",
    ]:
        r = weight_results[scheme]
        w = r["weights"]
        k = r["K_2020"]
        delta = k - baseline_k
        pct = (delta / baseline_k) * 100
        lines.append(
            f"| {scheme.replace('_', ' ').title()} | {w['tech']:.2f} | {w['cognitive']:.2f} | {w['institutional']:.2f} | {k:.4f} | {delta:+.4f} | {pct:+.2f}% |"
        )

    lines.append("")
    lines.append(
        "**Interpretation**: "
        + (
            "Highly robust - K₂₀₂₀ varies by less than 5%"
            if ws["relative_sensitivity_pct"] < 5
            else (
                "Moderately robust - K₂₀₂₀ varies by 5-15%"
                if ws["relative_sensitivity_pct"] < 15
                else "Sensitive - K₂₀₂₀ varies by more than 15%"
            )
        )
    )
    lines.append("")

    # Normalization sensitivity
    lines.append("## 2. Normalization Sensitivity Analysis")
    lines.append("")
    lines.append(
        "**Objective**: Test robustness of K₂₀₂₀ to alternative normalization methods for rescaling proxy components."
    )
    lines.append("")

    ns = norm_results["summary"]
    lines.append(f"**Baseline K₂₀₂₀**: {ns['baseline_K_2020']:.4f}")
    lines.append(f"**K₂₀₂₀ Range**: [{ns['min_K_2020']:.4f}, {ns['max_K_2020']:.4f}]")
    lines.append(
        f"**ΔK₂₀₂₀**: {ns['delta_K_2020']:.4f} ({ns['relative_sensitivity_pct']:.2f}% relative)"
    )
    lines.append("")

    lines.append("### Normalization Methods Tested")
    lines.append("")
    lines.append("| Method | Description | K₂₀₂₀ | Δ from Baseline | % Change |")
    lines.append("|--------|-------------|-------|-----------------|----------|")

    baseline_k = ns["baseline_K_2020"]
    for norm_key in ["minmax", "zscore", "rank", "quantile"]:
        r = norm_results[norm_key]
        k = r["K_2020"]
        delta = k - baseline_k
        pct = (delta / baseline_k) * 100
        desc = NORMALIZATION_METHODS[norm_key][0]
        lines.append(f"| {r['name']} | {desc} | {k:.4f} | {delta:+.4f} | {pct:+.2f}% |")

    lines.append("")
    lines.append(
        "**Interpretation**: "
        + (
            "Highly robust - K₂₀₂₀ varies by less than 5%"
            if ns["relative_sensitivity_pct"] < 5
            else (
                "Moderately robust - K₂₀₂₀ varies by 5-15%"
                if ns["relative_sensitivity_pct"] < 15
                else "Sensitive - K₂₀₂₀ varies by more than 15%"
            )
        )
    )
    lines.append("")

    # Overall conclusions
    lines.append("## 3. Overall Robustness Assessment")
    lines.append("")

    total_range = max(ws["max_K_2020"], ns["max_K_2020"]) - min(
        ws["min_K_2020"], ns["min_K_2020"]
    )
    avg_baseline = (ws["baseline_K_2020"] + ns["baseline_K_2020"]) / 2
    total_sensitivity = (total_range / avg_baseline) * 100

    lines.append(f"**Combined Sensitivity**: {total_sensitivity:.2f}%")
    lines.append("")

    if total_sensitivity < 5:
        lines.append(
            "✅ **HIGHLY ROBUST**: K₂₀₂₀ = 0.9144 finding is highly robust to methodological choices. Peak civilizational coherence in 2020 is a reliable result."
        )
    elif total_sensitivity < 15:
        lines.append(
            "⚠️ **MODERATELY ROBUST**: K₂₀₂₀ finding shows moderate sensitivity to methodological choices. 2020 peak is likely but requires careful interpretation."
        )
    else:
        lines.append(
            "🚨 **SENSITIVE**: K₂₀₂₀ finding shows high sensitivity to methodological choices. Results require cautious interpretation and additional validation."
        )

    lines.append("")
    lines.append("### Recommendations")
    lines.append("")
    lines.append(
        "1. **Report Baseline**: Use baseline weights (40/30/30) and min-max normalization as primary result"
    )
    lines.append(
        "2. **Report Range**: Include sensitivity range in manuscript as robustness check"
    )
    lines.append(
        "3. **Sensitivity Analysis**: Reference this analysis in methods/supplementary materials"
    )
    lines.append(
        "4. **Future Work**: Consider Bayesian approach with weight uncertainty propagation"
    )

    # Write report
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(lines))
    print(f"   ✅ Report saved to {output_file}")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Track C-3: Sensitivity Analysis for Historical K(t)"
    )
    parser.add_argument(
        "--hyde-proxy",
        type=Path,
        default="data/processed/evolutionary_progression_hyde_-3000_2020.csv",
        help="HYDE proxy data with components",
    )
    parser.add_argument(
        "--k-series",
        type=Path,
        default="logs/historical_k_extended/k_t_series_5000y.csv",
        help="K(t) time series",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default="logs/sensitivity_c3",
        help="Output directory for results",
    )

    args = parser.parse_args()

    print("=" * 80)
    print("🔬 Track C-3: Sensitivity Analysis for Historical K(t)")
    print("=" * 80)
    print()

    # Load data
    hyde_data = load_hyde_proxy_data(args.hyde_proxy)
    k_series = load_k_series(args.k_series)

    # Test weight sensitivity
    weight_results = test_weight_sensitivity(
        hyde_data, k_series, normalization="minmax"
    )

    # Test normalization sensitivity
    norm_results = test_normalization_sensitivity(hyde_data, k_series)

    # Save results
    print("\n" + "=" * 80)
    print("💾 Saving Results")
    print("=" * 80)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    # JSON outputs
    with open(args.output_dir / "weight_sensitivity.json", "w") as f:
        json.dump(weight_results, f, indent=2)
    print(
        f"✅ Weight sensitivity results: {args.output_dir / 'weight_sensitivity.json'}"
    )

    with open(args.output_dir / "normalization_sensitivity.json", "w") as f:
        json.dump(norm_results, f, indent=2)
    print(
        f"✅ Normalization sensitivity results: {args.output_dir / 'normalization_sensitivity.json'}"
    )

    # Visualizations
    plot_weight_sensitivity(weight_results, args.output_dir / "weight_sensitivity.png")
    plot_normalization_sensitivity(
        norm_results, args.output_dir / "normalization_sensitivity.png"
    )

    # Report
    generate_sensitivity_report(
        weight_results, norm_results, args.output_dir / "sensitivity_report.md"
    )

    print("\n" + "=" * 80)
    print("✅ Sensitivity Analysis Complete!")
    print(f"📁 Results saved to: {args.output_dir}")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    exit(main())
