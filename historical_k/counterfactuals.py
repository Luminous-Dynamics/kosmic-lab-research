"""
Counterfactual Scenario Analysis for Historical K(t).

Simulates "what if" scenarios by altering historical events
and measuring impact on civilizational coherence.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import interpolate

# Predefined historical interventions
HISTORICAL_INTERVENTIONS = {
    "no_bronze_collapse": {
        "description": "What if the Bronze Age Collapse (-1200 BCE) never occurred?",
        "year": -1200,
        "type": "prevent_shock",
        "magnitude": 0.15,  # Prevented K drop
        "duration": 100,
    },
    "no_black_death": {
        "description": "What if the Black Death (1348) never occurred?",
        "year": 1348,
        "type": "prevent_shock",
        "magnitude": 0.12,
        "duration": 50,
    },
    "no_ww1": {
        "description": "What if World War I never occurred?",
        "year": 1914,
        "type": "prevent_shock",
        "magnitude": 0.10,
        "duration": 30,
    },
    "no_ww2": {
        "description": "What if World War II never occurred?",
        "year": 1939,
        "type": "prevent_shock",
        "magnitude": 0.15,
        "duration": 20,
    },
    "early_industrial": {
        "description": "What if the Industrial Revolution started 100 years earlier (1660)?",
        "year": 1660,
        "type": "accelerate_progress",
        "magnitude": 0.20,
        "duration": 200,
    },
    "early_democracy": {
        "description": "What if democracy spread 50 years earlier (1726)?",
        "year": 1726,
        "type": "accelerate_progress",
        "magnitude": 0.10,
        "duration": 150,
    },
    "no_fall_rome": {
        "description": "What if Rome never fell (476)?",
        "year": 476,
        "type": "prevent_shock",
        "magnitude": 0.18,
        "duration": 200,
    },
}


def simulate_counterfactual(k_data: pd.DataFrame, intervention: Dict) -> pd.DataFrame:
    """Simulate counterfactual K(t) with a historical intervention.

    Args:
        k_data: Original K(t) series
        intervention: Dict with intervention parameters

    Returns:
        DataFrame with counterfactual K(t)
    """
    print(f"🔮 Simulating: {intervention['description']}")

    counterfactual = k_data.copy()
    year_col = "year"
    k_col = "K"

    intervention_year = intervention["year"]
    intervention_type = intervention["type"]
    magnitude = intervention["magnitude"]
    duration = intervention["duration"]

    # Find intervention point
    if (
        intervention_year < k_data[year_col].min()
        or intervention_year > k_data[year_col].max()
    ):
        print(f"   ⚠️  Intervention year {intervention_year} outside data range")
        return counterfactual

    # Get index closest to intervention year
    idx = (k_data[year_col] - intervention_year).abs().idxmin()
    intervention_idx = k_data.index.get_loc(idx)

    if intervention_type == "prevent_shock":
        # Prevent a historical decline
        # Add magnitude to K for duration years

        for i in range(intervention_idx, min(intervention_idx + duration, len(k_data))):
            # Decay effect over time
            years_since = i - intervention_idx
            decay = np.exp(-years_since / (duration / 3))  # Exponential decay
            counterfactual.loc[k_data.index[i], k_col] += magnitude * decay

    elif intervention_type == "accelerate_progress":
        # Accelerate advancement
        # Add increasing magnitude over duration

        for i in range(intervention_idx, min(intervention_idx + duration, len(k_data))):
            years_since = i - intervention_idx
            # S-curve adoption
            progress = 1 / (1 + np.exp(-(years_since - duration / 2) / (duration / 10)))
            counterfactual.loc[k_data.index[i], k_col] += magnitude * progress

    elif intervention_type == "catastrophic_event":
        # Add a new catastrophic event
        # Decrease K sharply then recover

        for i in range(intervention_idx, min(intervention_idx + duration, len(k_data))):
            years_since = i - intervention_idx
            # Sharp drop then recovery
            impact = -magnitude * np.exp(-years_since / (duration / 4))
            counterfactual.loc[k_data.index[i], k_col] += impact

    # Clip to valid range
    counterfactual[k_col] = np.clip(counterfactual[k_col], 0, 1)

    print(f"   ✅ Counterfactual simulated")
    print(
        f"   Average impact: {(counterfactual[k_col].mean() - k_data[k_col].mean()):.4f}"
    )

    return counterfactual


def compare_scenarios(
    original: pd.DataFrame, counterfactuals: Dict[str, pd.DataFrame]
) -> pd.DataFrame:
    """Compare multiple counterfactual scenarios.

    Args:
        original: Original K(t) data
        counterfactuals: Dict mapping scenario names to counterfactual data

    Returns:
        DataFrame with comparison metrics
    """
    print(f"📊 Comparing {len(counterfactuals)} counterfactual scenarios...")

    metrics = []

    for scenario_name, cf_data in counterfactuals.items():
        # Compute impact metrics
        k_diff = cf_data["K"] - original["K"]

        metrics.append(
            {
                "scenario": scenario_name,
                "mean_impact": k_diff.mean(),
                "max_impact": k_diff.max(),
                "min_impact": k_diff.min(),
                "total_impact": k_diff.sum(),
                "affected_years": (k_diff.abs() > 0.01).sum(),
            }
        )

    comparison = pd.DataFrame(metrics)
    comparison = comparison.sort_values("mean_impact", ascending=False)

    print(f"   ✅ Scenario comparison complete")

    return comparison


def plot_counterfactual(
    original: pd.DataFrame,
    counterfactuals: Dict[str, pd.DataFrame],
    output_path: str | Path,
    highlight_scenario: Optional[str] = None,
) -> None:
    """Visualize counterfactual scenarios.

    Args:
        original: Original K(t) data
        counterfactuals: Dict of counterfactual scenarios
        output_path: Where to save plot
        highlight_scenario: Which scenario to highlight (if any)
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))

    # Plot 1: Absolute K(t) values
    ax1.plot(
        original["year"],
        original["K"],
        "k-",
        linewidth=3,
        label="Actual History",
        alpha=0.8,
    )

    colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"]
    for i, (scenario_name, cf_data) in enumerate(counterfactuals.items()):
        color = colors[i % len(colors)]
        alpha = 0.9 if scenario_name == highlight_scenario else 0.5
        linewidth = 2.5 if scenario_name == highlight_scenario else 1.5

        ax1.plot(
            cf_data["year"],
            cf_data["K"],
            color=color,
            linewidth=linewidth,
            alpha=alpha,
            label=scenario_name,
        )

    ax1.set_xlabel("Year", fontsize=12, fontweight="bold")
    ax1.set_ylabel("K-index", fontsize=12, fontweight="bold")
    ax1.set_title("Counterfactual K(t) Scenarios", fontsize=14, fontweight="bold")
    ax1.legend(loc="best", fontsize=9)
    ax1.grid(True, alpha=0.3)

    # Plot 2: Impact (difference from actual)
    for i, (scenario_name, cf_data) in enumerate(counterfactuals.items()):
        color = colors[i % len(colors)]
        alpha = 0.9 if scenario_name == highlight_scenario else 0.5
        linewidth = 2.5 if scenario_name == highlight_scenario else 1.5

        impact = cf_data["K"] - original["K"]
        ax2.plot(
            cf_data["year"],
            impact,
            color=color,
            linewidth=linewidth,
            alpha=alpha,
            label=scenario_name,
        )

    ax2.axhline(0, color="black", linestyle="--", linewidth=1, alpha=0.5)
    ax2.set_xlabel("Year", fontsize=12, fontweight="bold")
    ax2.set_ylabel("ΔK (Counterfactual - Actual)", fontsize=12, fontweight="bold")
    ax2.set_title("Counterfactual Impact on K-index", fontsize=14, fontweight="bold")
    ax2.legend(loc="best", fontsize=9)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✅ Counterfactual plot saved to {output_path}")


def generate_counterfactual_report(
    comparison: pd.DataFrame, interventions: Dict, output_path: str | Path
) -> None:
    """Generate markdown report of counterfactual analysis."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    report = "# Counterfactual Scenario Analysis\n\n"
    report += "## Scenarios Tested\n\n"

    for scenario_name, intervention in interventions.items():
        report += f"### {scenario_name}\n\n"
        report += f"**Description**: {intervention['description']}\n\n"
        report += f"- **Year**: {intervention['year']}\n"
        report += f"- **Type**: {intervention['type']}\n"
        report += f"- **Magnitude**: {intervention['magnitude']:.2f}\n"
        report += f"- **Duration**: {intervention['duration']} years\n\n"

    report += "## Impact Comparison\n\n"
    report += "Scenarios ranked by mean impact on K-index:\n\n"
    report += "| Rank | Scenario | Mean ΔK | Max ΔK | Affected Years |\n"
    report += "|------|----------|---------|--------|----------------|\n"

    for i, row in comparison.iterrows():
        rank = comparison.index.get_loc(i) + 1
        report += f"| {rank} | {row['scenario']} | {row['mean_impact']:+.4f} | "
        report += f"{row['max_impact']:+.4f} | {int(row['affected_years'])} |\n"

    report += "\n## Key Insights\n\n"

    # Identify most impactful scenarios
    top_positive = comparison.nlargest(1, "mean_impact").iloc[0]
    top_negative = comparison.nsmallest(1, "mean_impact").iloc[0]

    report += f"**Most Positive Impact**: {top_positive['scenario']} "
    report += f"(ΔK = +{top_positive['mean_impact']:.4f})\n\n"

    if top_negative["mean_impact"] < 0:
        report += f"**Most Negative Impact**: {top_negative['scenario']} "
        report += f"(ΔK = {top_negative['mean_impact']:.4f})\n\n"

    report += "## Interpretation\n\n"
    report += "**Mean ΔK**: Average change in K-index over all time\n\n"
    report += "**Max ΔK**: Maximum instantaneous impact\n\n"
    report += "**Affected Years**: Number of years with |ΔK| > 0.01\n\n"

    report += "## Methodology\n\n"
    report += "Counterfactual scenarios simulate alternative histories by:\n\n"
    report += "1. **Preventing Shocks**: Remove historical declines (wars, collapses)\n"
    report += (
        "2. **Accelerating Progress**: Speed up technological/social advancement\n"
    )
    report += "3. **Adding Events**: Introduce hypothetical catastrophes\n\n"

    report += (
        "Impact propagates forward with exponential decay or S-curve adoption.\n\n"
    )

    output_path.write_text(report)
    print(f"✅ Counterfactual report saved to {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Counterfactual scenario analysis for K(t)"
    )
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, default="logs/counterfactuals")
    parser.add_argument(
        "--scenarios",
        nargs="+",
        choices=list(HISTORICAL_INTERVENTIONS.keys()) + ["all"],
        default=["all"],
    )

    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    # Load data
    df = pd.read_csv(args.data)
    print(f"📊 Loaded data: {df.shape}")

    # Select scenarios
    if "all" in args.scenarios:
        scenarios_to_run = HISTORICAL_INTERVENTIONS
    else:
        scenarios_to_run = {
            k: v for k, v in HISTORICAL_INTERVENTIONS.items() if k in args.scenarios
        }

    print(f"🔮 Running {len(scenarios_to_run)} counterfactual scenarios...")
    print()

    # Simulate counterfactuals
    counterfactuals = {}
    for scenario_name, intervention in scenarios_to_run.items():
        cf_data = simulate_counterfactual(df, intervention)
        counterfactuals[scenario_name] = cf_data

        # Save individual scenario
        cf_data.to_csv(args.output / f"{scenario_name}.csv", index=False)
        print()

    # Compare scenarios
    comparison = compare_scenarios(df, counterfactuals)
    comparison.to_csv(args.output / "scenario_comparison.csv", index=False)
    print(f"✅ Comparison saved to {args.output / 'scenario_comparison.csv'}")
    print()

    # Plot results
    plot_counterfactual(df, counterfactuals, args.output / "counterfactuals.png")

    # Generate report
    generate_counterfactual_report(
        comparison, scenarios_to_run, args.output / "counterfactual_report.md"
    )

    print(f"\n✅ Counterfactual analysis complete!")
    print(f"📁 Results saved to: {args.output}")
    print()
    print("Top 3 Most Impactful Scenarios:")
    for i, row in comparison.head(3).iterrows():
        rank = comparison.index.get_loc(i) + 1
        print(f"  {rank}. {row['scenario']}: ΔK = {row['mean_impact']:+.4f}")
