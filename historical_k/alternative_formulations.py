"""
Alternative K-Index Formulations.

Tests different methods of aggregating harmonies into a single K-index
to assess robustness and identify optimal formulation.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Callable, Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

HARMONY_COLUMNS = [
    "resonant_coherence",
    "interconnection",
    "reciprocity",
    "play_entropy",
    "wisdom_accuracy",
    "flourishing",
    "evolutionary_progression",
]


def compute_k_arithmetic(
    harmonies: pd.DataFrame, weights: np.ndarray = None
) -> pd.Series:
    """Standard arithmetic mean (current method)."""
    if weights is None:
        weights = np.ones(len(harmonies.columns)) / len(harmonies.columns)

    return (harmonies * weights).sum(axis=1)


def compute_k_geometric(
    harmonies: pd.DataFrame, weights: np.ndarray = None
) -> pd.Series:
    """Geometric mean - penalizes extreme imbalances."""
    if weights is None:
        weights = np.ones(len(harmonies.columns)) / len(harmonies.columns)

    # Avoid log(0)
    harmonies_safe = harmonies.clip(lower=1e-6)

    # Weighted geometric mean: exp(Σ w_i * log(x_i))
    log_weighted = np.log(harmonies_safe) * weights
    return np.exp(log_weighted.sum(axis=1))


def compute_k_harmonic(
    harmonies: pd.DataFrame, weights: np.ndarray = None
) -> pd.Series:
    """Harmonic mean - heavily penalizes low values."""
    if weights is None:
        weights = np.ones(len(harmonies.columns)) / len(harmonies.columns)

    # Avoid division by zero
    harmonies_safe = harmonies.clip(lower=1e-6)

    # Weighted harmonic mean: 1 / Σ(w_i / x_i)
    reciprocals_weighted = weights / harmonies_safe
    return 1 / reciprocals_weighted.sum(axis=1)


def compute_k_minimum(harmonies: pd.DataFrame, weights: np.ndarray = None) -> pd.Series:
    """Minimum (weakest link) - K limited by lowest harmony."""
    return harmonies.min(axis=1)


def compute_k_multiplicative(
    harmonies: pd.DataFrame, weights: np.ndarray = None
) -> pd.Series:
    """Pure multiplicative - product of all harmonies."""
    if weights is None:
        return harmonies.prod(axis=1)
    else:
        # Weighted product: Π x_i^w_i
        return (harmonies**weights).prod(axis=1)


def compute_k_quadratic(
    harmonies: pd.DataFrame, weights: np.ndarray = None
) -> pd.Series:
    """Quadratic mean (RMS) - emphasizes high values."""
    if weights is None:
        weights = np.ones(len(harmonies.columns)) / len(harmonies.columns)

    squared_weighted = (harmonies**2) * weights
    return np.sqrt(squared_weighted.sum(axis=1))


def compute_k_exponential(harmonies: pd.DataFrame, alpha: float = 2.0) -> pd.Series:
    """Exponential weighting - emphasizes differences."""
    # K = Σ exp(α * x_i) / n
    exp_weighted = np.exp(alpha * harmonies).mean(axis=1)
    # Normalize back to [0, 1]
    return (exp_weighted - np.exp(0)) / (np.exp(alpha) - np.exp(0))


# Registry of all formulations
FORMULATIONS = {
    "arithmetic": {
        "func": compute_k_arithmetic,
        "name": "Arithmetic Mean (Standard)",
        "description": "Simple weighted average of harmonies",
    },
    "geometric": {
        "func": compute_k_geometric,
        "name": "Geometric Mean",
        "description": "Penalizes imbalances between harmonies",
    },
    "harmonic": {
        "func": compute_k_harmonic,
        "name": "Harmonic Mean",
        "description": "Heavily penalizes low harmonies (weakest link sensitive)",
    },
    "minimum": {
        "func": compute_k_minimum,
        "name": "Minimum (Weakest Link)",
        "description": "K determined entirely by lowest harmony",
    },
    "multiplicative": {
        "func": compute_k_multiplicative,
        "name": "Multiplicative",
        "description": "Product of all harmonies",
    },
    "quadratic": {
        "func": compute_k_quadratic,
        "name": "Quadratic Mean (RMS)",
        "description": "Emphasizes high harmony values",
    },
    "exponential": {
        "func": compute_k_exponential,
        "name": "Exponential Weighting",
        "description": "Amplifies differences between harmonies",
    },
}


def compare_formulations(
    harmony_data: pd.DataFrame, formulations: List[str] = None
) -> pd.DataFrame:
    """Compute K using multiple formulations and compare.

    Args:
        harmony_data: DataFrame with harmony columns
        formulations: List of formulation names (or None for all)

    Returns:
        DataFrame with K values for each formulation
    """
    if formulations is None:
        formulations = list(FORMULATIONS.keys())

    print(f"🔬 Computing K using {len(formulations)} alternative formulations...")

    # Extract harmony columns
    harmony_cols = [col for col in HARMONY_COLUMNS if col in harmony_data.columns]
    harmonies = harmony_data[harmony_cols].copy()

    print(f"   Using {len(harmony_cols)} harmonies: {', '.join(harmony_cols)}")

    results = pd.DataFrame({"year": harmony_data["year"]})

    for form_name in formulations:
        if form_name not in FORMULATIONS:
            print(f"   ⚠️  Unknown formulation: {form_name}")
            continue

        print(f"   Computing: {FORMULATIONS[form_name]['name']}")
        func = FORMULATIONS[form_name]["func"]

        try:
            k_values = func(harmonies)
            results[form_name] = k_values
        except Exception as e:
            print(f"   ⚠️  Error in {form_name}: {e}")
            results[form_name] = np.nan

    print(f"   ✅ Formulations computed")

    return results


def analyze_formulation_differences(
    comparison: pd.DataFrame, baseline: str = "arithmetic"
) -> pd.DataFrame:
    """Analyze differences between formulations.

    Args:
        comparison: DataFrame from compare_formulations
        baseline: Which formulation to use as baseline

    Returns:
        DataFrame with difference statistics
    """
    print(f"📊 Analyzing differences (baseline: {baseline})...")

    formulations = [col for col in comparison.columns if col != "year"]

    if baseline not in formulations:
        print(f"   ⚠️  Baseline {baseline} not found, using first formulation")
        baseline = formulations[0]

    baseline_values = comparison[baseline]

    stats_list = []

    for form in formulations:
        if form == baseline:
            continue

        diff = comparison[form] - baseline_values

        stats_list.append(
            {
                "formulation": form,
                "mean_diff": diff.mean(),
                "std_diff": diff.std(),
                "max_diff": diff.max(),
                "min_diff": diff.min(),
                "correlation": comparison[form].corr(baseline_values),
                "rmse": np.sqrt((diff**2).mean()),
            }
        )

    stats_df = pd.DataFrame(stats_list)
    stats_df = stats_df.sort_values("rmse")

    print(f"   ✅ Difference analysis complete")

    return stats_df


def plot_formulation_comparison(
    comparison: pd.DataFrame, output_path: str | Path, highlight: List[str] = None
) -> None:
    """Visualize different K formulations.

    Args:
        comparison: DataFrame from compare_formulations
        output_path: Where to save plot
        highlight: Which formulations to highlight
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    formulations = [col for col in comparison.columns if col != "year"]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))

    colors = [
        "#000000",
        "#e74c3c",
        "#3498db",
        "#2ecc71",
        "#f39c12",
        "#9b59b6",
        "#1abc9c",
    ]

    # Plot 1: Absolute values
    for i, form in enumerate(formulations):
        color = colors[i % len(colors)]
        alpha = 0.9 if (highlight and form in highlight) else 0.6
        linewidth = 2.5 if (highlight and form in highlight) else 1.5

        label = FORMULATIONS.get(form, {}).get("name", form)
        ax1.plot(
            comparison["year"],
            comparison[form],
            color=color,
            linewidth=linewidth,
            alpha=alpha,
            label=label,
        )

    ax1.set_xlabel("Year", fontsize=12, fontweight="bold")
    ax1.set_ylabel("K-index", fontsize=12, fontweight="bold")
    ax1.set_title("K-Index: Alternative Formulations", fontsize=14, fontweight="bold")
    ax1.legend(loc="best", fontsize=9)
    ax1.grid(True, alpha=0.3)

    # Plot 2: Differences from arithmetic mean
    baseline = "arithmetic" if "arithmetic" in formulations else formulations[0]
    baseline_values = comparison[baseline]

    for i, form in enumerate(formulations):
        if form == baseline:
            continue

        color = colors[i % len(colors)]
        alpha = 0.9 if (highlight and form in highlight) else 0.6
        linewidth = 2.5 if (highlight and form in highlight) else 1.5

        diff = comparison[form] - baseline_values
        label = FORMULATIONS.get(form, {}).get("name", form)
        ax2.plot(
            comparison["year"],
            diff,
            color=color,
            linewidth=linewidth,
            alpha=alpha,
            label=label,
        )

    ax2.axhline(0, color="black", linestyle="--", linewidth=1, alpha=0.5)
    ax2.set_xlabel("Year", fontsize=12, fontweight="bold")
    ax2.set_ylabel(
        f'ΔK (vs. {FORMULATIONS[baseline]["name"]})', fontsize=12, fontweight="bold"
    )
    ax2.set_title(
        "Deviations from Baseline Formulation", fontsize=14, fontweight="bold"
    )
    ax2.legend(loc="best", fontsize=9)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✅ Formulation comparison plot saved to {output_path}")


def generate_formulation_report(
    comparison: pd.DataFrame, stats: pd.DataFrame, output_path: str | Path
) -> None:
    """Generate markdown report of alternative formulations."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    report = "# Alternative K-Index Formulations Analysis\n\n"
    report += "## Formulations Tested\n\n"

    for form_name, form_info in FORMULATIONS.items():
        report += f"### {form_info['name']}\n\n"
        report += f"{form_info['description']}\n\n"

    report += "## Comparison Statistics\n\n"
    report += "Differences from baseline (Arithmetic Mean):\n\n"
    report += "| Formulation | Mean Δ | Std Δ | RMSE | Correlation |\n"
    report += "|-------------|--------|-------|------|-------------|\n"

    for _, row in stats.iterrows():
        form_name = FORMULATIONS.get(row["formulation"], {}).get(
            "name", row["formulation"]
        )
        report += f"| {form_name} | {row['mean_diff']:+.4f} | "
        report += (
            f"{row['std_diff']:.4f} | {row['rmse']:.4f} | {row['correlation']:.4f} |\n"
        )

    report += "\n## Summary Statistics\n\n"

    formulations = [col for col in comparison.columns if col != "year"]
    for form in formulations:
        form_name = FORMULATIONS.get(form, {}).get("name", form)
        values = comparison[form]

        report += f"### {form_name}\n\n"
        report += f"- **Mean**: {values.mean():.4f}\n"
        report += f"- **Std**: {values.std():.4f}\n"
        report += f"- **Min**: {values.min():.4f}\n"
        report += f"- **Max**: {values.max():.4f}\n\n"

    report += "## Key Insights\n\n"

    # Most similar to baseline
    most_similar = stats.nsmallest(1, "rmse").iloc[0]
    report += f"**Most Similar to Baseline**: {most_similar['formulation']} "
    report += f"(RMSE = {most_similar['rmse']:.4f})\n\n"

    # Most different from baseline
    most_different = stats.nlargest(1, "rmse").iloc[0]
    report += f"**Most Different from Baseline**: {most_different['formulation']} "
    report += f"(RMSE = {most_different['rmse']:.4f})\n\n"

    report += "## Recommendation\n\n"
    report += "The **Arithmetic Mean** remains the recommended formulation for its:\n\n"
    report += "1. **Interpretability**: Simple weighted average is easy to understand\n"
    report += "2. **Stability**: Not overly sensitive to individual harmonies\n"
    report += "3. **Convention**: Standard practice in composite indices\n\n"

    report += "However, **Geometric Mean** and **Harmonic Mean** offer valuable sensitivity analysis:\n\n"
    report += "- **Geometric**: Penalizes imbalances, rewards balanced development\n"
    report += "- **Harmonic**: Identifies weakest links in civilizational coherence\n\n"

    output_path.write_text(report)
    print(f"✅ Formulation report saved to {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Test alternative K-index formulations"
    )
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, default="logs/formulations")
    parser.add_argument(
        "--formulations",
        nargs="+",
        choices=list(FORMULATIONS.keys()) + ["all"],
        default=["all"],
    )

    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    # Load data
    df = pd.read_csv(args.data)
    print(f"📊 Loaded data: {df.shape}")

    # Select formulations
    if "all" in args.formulations:
        formulations_to_test = list(FORMULATIONS.keys())
    else:
        formulations_to_test = args.formulations

    # Compute all formulations
    comparison = compare_formulations(df, formulations_to_test)
    comparison.to_csv(args.output / "formulation_comparison.csv", index=False)
    print(f"✅ Comparison saved to {args.output / 'formulation_comparison.csv'}")
    print()

    # Analyze differences
    stats = analyze_formulation_differences(comparison)
    stats.to_csv(args.output / "formulation_stats.csv", index=False)
    print(f"✅ Stats saved to {args.output / 'formulation_stats.csv'}")
    print()

    # Plot comparison
    plot_formulation_comparison(comparison, args.output / "formulations.png")

    # Generate report
    generate_formulation_report(
        comparison, stats, args.output / "formulation_report.md"
    )

    print(f"\n✅ Alternative formulations analysis complete!")
    print(f"📁 Results saved to: {args.output}")
    print()
    print("Formulations ranked by similarity to arithmetic mean:")
    for _, row in stats.head(5).iterrows():
        print(
            f"  {row['formulation']}: RMSE = {row['rmse']:.4f}, r = {row['correlation']:.4f}"
        )
