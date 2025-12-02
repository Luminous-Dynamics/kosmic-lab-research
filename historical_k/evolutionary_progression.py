"""
Seventh Harmony: Evolutionary Progression

Measures civilizational advancement toward greater complexity,
consciousness, and capability over time.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

# Evolutionary Progression proxy variables
PROGRESSION_PROXIES = {
    "technological_sophistication": {
        "description": "Level of technological development",
        "sources": ["energy_per_capita", "innovation_rate", "patents"],
        "weight": 0.25,
    },
    "cognitive_complexity": {
        "description": "Collective information processing capacity",
        "sources": ["education_years", "literacy_rate", "researchers_per_capita"],
        "weight": 0.20,
    },
    "institutional_evolution": {
        "description": "Sophistication of governance and social institutions",
        "sources": ["democracy_index", "rule_of_law", "institutional_quality"],
        "weight": 0.20,
    },
    "adaptive_capacity": {
        "description": "Ability to respond to challenges and change",
        "sources": ["resilience_index", "innovation_speed", "crisis_recovery"],
        "weight": 0.15,
    },
    "long_term_orientation": {
        "description": "Planning horizon and future consideration",
        "sources": [
            "investment_rate",
            "environmental_protection",
            "education_spending",
        ],
        "weight": 0.20,
    },
}


def compute_evolutionary_progression(data_df: pd.DataFrame, config: Dict) -> pd.Series:
    """Compute Evolutionary Progression harmony score.

    Args:
        data_df: DataFrame with proxy variables by year
        config: Configuration dict with proxy mappings

    Returns:
        Series with progression scores by year
    """
    print("🧬 Computing Evolutionary Progression scores...")

    # Extract relevant columns
    progression_data = {}

    for proxy_name, proxy_info in PROGRESSION_PROXIES.items():
        # Try to find matching columns in data
        matching_cols = [
            col
            for col in data_df.columns
            if any(source in col.lower() for source in proxy_info["sources"])
        ]

        if matching_cols:
            # Average matching columns
            progression_data[proxy_name] = data_df[matching_cols].mean(axis=1)
        else:
            # Generate synthetic proxy based on historical patterns
            print(f"  ⚠️  No data for {proxy_name}, using synthetic estimate")
            progression_data[proxy_name] = _generate_progression_proxy(
                data_df["year"], proxy_name, proxy_info
            )

    # Combine into DataFrame
    prog_df = pd.DataFrame(progression_data, index=data_df.index)

    # Normalize each proxy to [0, 1]
    for col in prog_df.columns:
        min_val = prog_df[col].min()
        max_val = prog_df[col].max()
        if max_val > min_val:
            prog_df[col] = (prog_df[col] - min_val) / (max_val - min_val)

    # Weighted average
    scores = pd.Series(0.0, index=data_df.index)
    for proxy_name, proxy_info in PROGRESSION_PROXIES.items():
        if proxy_name in prog_df.columns:
            scores += prog_df[proxy_name] * proxy_info["weight"]

    print(f"✅ Evolutionary Progression computed (mean: {scores.mean():.3f})")

    return scores


def _generate_progression_proxy(
    years: pd.Series, proxy_name: str, proxy_info: Dict
) -> pd.Series:
    """Generate synthetic progression proxy based on historical patterns."""
    years_array = years.values

    if proxy_name == "technological_sophistication":
        # Exponential growth, especially post-1800
        values = np.zeros(len(years_array))
        for i, year in enumerate(years_array):
            if year < 0:
                values[i] = 0.05 + 0.10 * (year + 3000) / 3000  # Slow ancient progress
            elif year < 1800:
                values[i] = 0.15 + 0.15 * year / 1800  # Gradual medieval/renaissance
            else:
                values[i] = 0.30 * np.exp(0.006 * (year - 1800))  # Exponential modern
        values = np.clip(values, 0, 1)

    elif proxy_name == "cognitive_complexity":
        # S-curve: literacy -> mass education -> digital literacy
        midpoint = 1900
        values = 0.05 + 0.90 / (1 + np.exp(-0.005 * (years_array - midpoint)))

    elif proxy_name == "institutional_evolution":
        # Step function: empires -> nation states -> international institutions
        values = np.zeros(len(years_array))
        for i, year in enumerate(years_array):
            if year < -1000:
                values[i] = 0.10  # Early states
            elif year < 1648:
                values[i] = 0.20  # Classical empires
            elif year < 1945:
                values[i] = 0.35  # Westphalian system
            else:
                values[i] = 0.50 + 0.40 * (year - 1945) / (years_array.max() - 1945)

    elif proxy_name == "adaptive_capacity":
        # Grows with technology and institutions
        tech = _generate_progression_proxy(years, "technological_sophistication", {})
        inst = _generate_progression_proxy(years, "institutional_evolution", {})
        values = (tech + inst) / 2

    elif proxy_name == "long_term_orientation":
        # Complex pattern: high in early (survival), low in middle (expansion), high again (sustainability)
        phase1 = 0.30 * np.exp(
            -0.0008 * (years_array + 3000)
        )  # Decline from survival mode
        phase2 = 0.40 / (
            1 + np.exp(-0.008 * (years_array - 1970))
        )  # Rise of sustainability
        values = 0.15 + phase1 + phase2

    else:
        # Default: gradual linear increase
        values = (years_array - years_array.min()) / (
            years_array.max() - years_array.min()
        )

    # Add moderate noise
    noise = np.random.normal(0, 0.02, len(values))
    values = np.clip(values + noise, 0, 1)

    return pd.Series(values, index=years.index)


def validate_progression_against_events(
    progression_series: pd.Series, historical_events: Dict[str, List[int]]
) -> Dict:
    """Validate progression scores against known historical progression events.

    Args:
        progression_series: Computed progression scores
        historical_events: Dict mapping event types to years

    Returns:
        Validation metrics
    """
    print("🔬 Validating Evolutionary Progression against historical events...")

    expected_increases = historical_events.get(
        "progressions",
        [
            -3000,  # Mesopotamian civilization
            -2500,  # Egyptian pyramids
            -500,  # Axial Age
            1450,  # Printing press
            1776,  # Enlightenment/American Revolution
            1945,  # UN founding
            1969,  # Moon landing
            1991,  # World Wide Web
        ],
    )

    expected_setbacks = historical_events.get(
        "regressions",
        [
            -1200,  # Bronze Age Collapse
            476,  # Fall of Rome
            1348,  # Black Death
            1914,  # WWI
            1939,  # WWII
        ],
    )

    results = {
        "progression_hits": 0,
        "progression_total": len(expected_increases),
        "setback_hits": 0,
        "setback_total": len(expected_setbacks),
    }

    window = 50  # Year tolerance

    # Check for increases around progression events
    for event_year in expected_increases:
        available_years = progression_series.index
        nearby_years = available_years[abs(available_years - event_year) <= window]

        if len(nearby_years) > 1:
            # Check if trend is upward
            nearby_values = progression_series.loc[nearby_years].sort_index()
            if len(nearby_values) >= 2:
                trend = nearby_values.iloc[-1] - nearby_values.iloc[0]
                if trend > 0:
                    results["progression_hits"] += 1

    # Check for decreases around setback events
    for event_year in expected_setbacks:
        available_years = progression_series.index
        nearby_years = available_years[abs(available_years - event_year) <= window]

        if len(nearby_years) > 1:
            nearby_values = progression_series.loc[nearby_years].sort_index()
            if len(nearby_values) >= 2:
                # Look for local minimum or downward trend
                is_minimum = all(
                    nearby_values.iloc[len(nearby_values) // 2] <= nearby_values
                )
                downward = nearby_values.iloc[-1] < nearby_values.iloc[0]
                if is_minimum or downward:
                    results["setback_hits"] += 1

    # Compute hit rates
    results["progression_rate"] = (
        results["progression_hits"] / results["progression_total"]
        if results["progression_total"] > 0
        else 0
    )
    results["setback_rate"] = (
        results["setback_hits"] / results["setback_total"]
        if results["setback_total"] > 0
        else 0
    )
    results["overall_accuracy"] = (
        results["progression_hits"] + results["setback_hits"]
    ) / (results["progression_total"] + results["setback_total"])

    print(f"  ✅ Progression event detection: {results['progression_rate']:.1%}")
    print(f"  ✅ Setback event detection: {results['setback_rate']:.1%}")
    print(f"  ✅ Overall accuracy: {results['overall_accuracy']:.1%}")

    return results


def plot_evolutionary_progression(
    years: pd.Series, progression: pd.Series, output_path: str | Path
) -> None:
    """Visualize evolutionary progression over time with key events."""
    import matplotlib.pyplot as plt

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(16, 8))

    # Plot progression curve
    ax.plot(
        years,
        progression,
        linewidth=2.5,
        color="#2E86AB",
        label="Evolutionary Progression",
    )

    # Add key progression events
    progression_events = [
        (-3000, "Mesopotamian\nCivilization", 0.15),
        (-2500, "Egyptian\nPyramids", 0.20),
        (-500, "Axial Age", 0.30),
        (1450, "Printing\nPress", 0.40),
        (1776, "Enlightenment", 0.50),
        (1945, "UN Founding", 0.60),
        (1969, "Moon\nLanding", 0.70),
        (1991, "World Wide\nWeb", 0.80),
    ]

    for year, label, y_pos in progression_events:
        if years.min() <= year <= years.max():
            ax.axvline(year, color="green", linestyle=":", alpha=0.5, linewidth=1.5)
            ax.text(
                year,
                y_pos,
                label,
                rotation=0,
                fontsize=8,
                ha="center",
                bbox=dict(boxstyle="round", facecolor="lightgreen", alpha=0.7),
            )

    # Add setback events
    setback_events = [
        (-1200, "Bronze Age\nCollapse", 0.25),
        (476, "Fall of\nRome", 0.28),
        (1348, "Black\nDeath", 0.35),
        (1914, "WWI", 0.45),
        (1939, "WWII", 0.48),
    ]

    for year, label, y_pos in setback_events:
        if years.min() <= year <= years.max():
            ax.axvline(year, color="red", linestyle="--", alpha=0.5, linewidth=1.5)
            ax.text(
                year,
                y_pos,
                label,
                rotation=0,
                fontsize=8,
                ha="center",
                bbox=dict(boxstyle="round", facecolor="lightcoral", alpha=0.7),
            )

    ax.set_xlabel("Year", fontsize=14, fontweight="bold")
    ax.set_ylabel("Evolutionary Progression Score", fontsize=14, fontweight="bold")
    ax.set_title(
        "Civilizational Evolutionary Progression: 3000 BCE - 2020 CE",
        fontsize=16,
        fontweight="bold",
    )
    ax.legend(loc="upper left", fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1.05)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✅ Evolutionary Progression plot saved to {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Compute Evolutionary Progression harmony"
    )
    parser.add_argument("--data", type=Path, required=True, help="Input data CSV")
    parser.add_argument("--output", type=Path, default="logs/progression")
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)

    # Load data
    df = pd.read_csv(args.data)
    print(f"📊 Loaded data: {df.shape}")

    # Compute progression
    progression = compute_evolutionary_progression(df, {})

    # Validate
    events = {}  # Would load from config
    validation = validate_progression_against_events(progression, events)

    # Plot
    plot_evolutionary_progression(
        df["year"], progression, args.output / "progression.png"
    )

    # Save
    result_df = pd.DataFrame(
        {"year": df["year"], "evolutionary_progression": progression}
    )
    result_df.to_csv(args.output / "progression.csv", index=False)

    print(f"\n✅ Evolutionary Progression analysis complete!")
    print(f"   Mean score: {progression.mean():.3f}")
    print(f"   Std dev: {progression.std():.3f}")
    print(
        f"   Min: {progression.min():.3f} (year {df.loc[progression.idxmin(), 'year']})"
    )
    print(
        f"   Max: {progression.max():.3f} (year {df.loc[progression.idxmax(), 'year']})"
    )
