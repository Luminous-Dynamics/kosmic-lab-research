"""
HYDE-Based Evolutionary Progression Proxy for Historical K(t) Index.

Fallback implementation using HYDE 3.2 demographic data to create proxies for:
- Technological sophistication
- Cognitive complexity
- Institutional evolution

Data Source: HYDE 3.2 Historical Demographics (already processed)
Coverage: 3000 BCE - 2020 CE
Quality: Better than pure synthetic, not as good as WIPO/Barro-Lee/Polity5

Note: This is a fallback approach. Real data sources (WIPO, Barro-Lee, Polity5)
      provide higher quality proxies when available.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd


def load_hyde_data(hyde_file: Path) -> pd.DataFrame:
    """
    Load processed HYDE demographic data.

    Args:
        hyde_file: Path to processed HYDE aggregated data

    Returns:
        DataFrame with HYDE demographic indicators
    """
    print(f"📥 Loading HYDE demographic data from {hyde_file}")

    if not hyde_file.exists():
        raise FileNotFoundError(f"HYDE data not found: {hyde_file}")

    df = pd.read_csv(hyde_file)

    print(f"   Loaded {len(df)} years of HYDE data")
    print(f"   Coverage: {df['year'].min()} to {df['year'].max()}")
    print(f"   Columns: {df.columns.tolist()}")

    return df


def compute_tech_sophistication_proxy(df: pd.DataFrame) -> pd.Series:
    """
    Compute technological sophistication proxy from HYDE data.

    Proxy formula:
    - Population size (log scale) → More people = more innovation
    - Agricultural land use → Agricultural revolution
    - Urbanization potential → Cities = technology hubs

    Args:
        df: HYDE demographic DataFrame

    Returns:
        Series with tech_sophistication values
    """
    print("\n🔧 Computing technological sophistication proxy...")

    # Use pre-computed log population
    log_pop = df["log_population"]

    # Use pre-computed agricultural fraction
    ag_fraction = df["agricultural_fraction"]

    # Urbanization potential (population density approximation)
    # Use total land = cropland + grazing as rough proxy
    total_land = df["cropland"] + df["grazing"]
    # Avoid division by zero
    pop_density = df["population"] / (total_land + 1e-10)
    log_density = np.log1p(pop_density)

    # Normalize components to [0, 1]
    log_pop_norm = (log_pop - log_pop.min()) / (log_pop.max() - log_pop.min())
    ag_norm = (ag_fraction - ag_fraction.min()) / (
        ag_fraction.max() - ag_fraction.min()
    )
    density_norm = (log_density - log_density.min()) / (
        log_density.max() - log_density.min()
    )

    # Weighted combination
    # 50% population, 30% agriculture, 20% density
    tech_proxy = 0.5 * log_pop_norm + 0.3 * ag_norm + 0.2 * density_norm

    print(
        f"   Tech sophistication range: {tech_proxy.min():.3f} - {tech_proxy.max():.3f}"
    )
    print(f"   Tech sophistication mean: {tech_proxy.mean():.3f}")

    return tech_proxy


def compute_cognitive_complexity_proxy(df: pd.DataFrame) -> pd.Series:
    """
    Compute cognitive complexity proxy from HYDE data.

    Proxy formula:
    - Population density → Urban centers = education hubs
    - Agricultural development → Surplus = time for learning
    - Population growth rate → Innovation pressure

    Args:
        df: HYDE demographic DataFrame

    Returns:
        Series with cognitive_complexity values
    """
    print("\n🧠 Computing cognitive complexity proxy...")

    # Population density as urbanization/education proxy
    total_land = df["cropland"] + df["grazing"]
    pop_density = df["population"] / (total_land + 1e-10)
    log_density = np.log1p(pop_density)

    # Agricultural surplus (cropland per capita)
    cropland_per_capita = df["cropland"] / (df["population"] + 1e-10)

    # Population growth rate (innovation pressure)
    pop_growth = df["population"].pct_change().fillna(0)
    pop_growth_smooth = pop_growth.rolling(window=5, center=True, min_periods=1).mean()

    # Normalize components
    density_norm = (log_density - log_density.min()) / (
        log_density.max() - log_density.min()
    )
    surplus_norm = (cropland_per_capita - cropland_per_capita.min()) / (
        cropland_per_capita.max() - cropland_per_capita.min()
    )

    # Handle growth rate normalization (can be negative)
    growth_min = pop_growth_smooth.min()
    growth_max = pop_growth_smooth.max()
    if growth_max - growth_min < 1e-10:
        growth_norm = pd.Series(0.5, index=pop_growth_smooth.index)
    else:
        growth_norm = (pop_growth_smooth - growth_min) / (growth_max - growth_min)

    # Weighted combination
    # 40% density, 30% surplus, 30% growth
    cognitive_proxy = 0.4 * density_norm + 0.3 * surplus_norm + 0.3 * growth_norm

    print(
        f"   Cognitive complexity range: {cognitive_proxy.min():.3f} - {cognitive_proxy.max():.3f}"
    )
    print(f"   Cognitive complexity mean: {cognitive_proxy.mean():.3f}")

    return cognitive_proxy


def compute_institutional_evolution_proxy(df: pd.DataFrame) -> pd.Series:
    """
    Compute institutional evolution proxy from HYDE data.

    Proxy formula:
    - Population size (log) → Larger populations need institutions
    - Population density → Governance complexity
    - Population stability → Institutional durability

    Args:
        df: HYDE demographic DataFrame

    Returns:
        Series with institutional_evolution values
    """
    print("\n🏛️  Computing institutional evolution proxy...")

    # Population size as state capacity proxy (use pre-computed log)
    log_pop = df["log_population"]

    # Population density as governance complexity
    total_land = df["cropland"] + df["grazing"]
    pop_density = df["population"] / (total_land + 1e-10)
    log_density = np.log1p(pop_density)

    # Population stability (inverse of volatility)
    pop_growth = df["population"].pct_change().fillna(0)
    pop_volatility = pop_growth.rolling(window=5, center=True, min_periods=1).std()
    pop_stability = 1 - (pop_volatility - pop_volatility.min()) / (
        pop_volatility.max() - pop_volatility.min()
    )
    pop_stability = pop_stability.fillna(0.5)

    # Normalize components
    pop_norm = (log_pop - log_pop.min()) / (log_pop.max() - log_pop.min())
    density_norm = (log_density - log_density.min()) / (
        log_density.max() - log_density.min()
    )

    # Weighted combination
    # 40% population, 30% density, 30% stability
    institutional_proxy = 0.4 * pop_norm + 0.3 * density_norm + 0.3 * pop_stability

    print(
        f"   Institutional evolution range: {institutional_proxy.min():.3f} - {institutional_proxy.max():.3f}"
    )
    print(f"   Institutional evolution mean: {institutional_proxy.mean():.3f}")

    return institutional_proxy


def create_evolutionary_progression(
    tech_proxy: pd.Series,
    cognitive_proxy: pd.Series,
    institutional_proxy: pd.Series,
    weights: Dict[str, float] = None,
) -> pd.Series:
    """
    Combine three proxies into unified evolutionary_progression.

    Args:
        tech_proxy: Technological sophistication proxy
        cognitive_proxy: Cognitive complexity proxy
        institutional_proxy: Institutional evolution proxy
        weights: Component weights (default: 40% tech, 30% cognitive, 30% institutional)

    Returns:
        Series with evolutionary_progression values
    """
    print("\n🔀 Merging proxies into evolutionary progression...")

    if weights is None:
        weights = {"tech": 0.4, "cognitive": 0.3, "institutional": 0.3}

    print(
        f"   Weights: tech={weights['tech']}, cognitive={weights['cognitive']}, institutional={weights['institutional']}"
    )

    # Weighted average
    evolutionary_progression = (
        weights["tech"] * tech_proxy
        + weights["cognitive"] * cognitive_proxy
        + weights["institutional"] * institutional_proxy
    )

    # Final normalization to [0, 1]
    min_val = evolutionary_progression.min()
    max_val = evolutionary_progression.max()
    evolutionary_progression_norm = (evolutionary_progression - min_val) / (
        max_val - min_val
    )

    print(f"\n✅ Evolutionary progression computed:")
    print(
        f"   Range: {evolutionary_progression_norm.min():.3f} - {evolutionary_progression_norm.max():.3f}"
    )
    print(f"   Mean: {evolutionary_progression_norm.mean():.3f}")

    return evolutionary_progression_norm


def save_evolutionary_progression(
    years: pd.Series,
    evolutionary_progression: pd.Series,
    tech_proxy: pd.Series,
    cognitive_proxy: pd.Series,
    institutional_proxy: pd.Series,
    output_file: Path,
):
    """
    Save evolutionary progression data to CSV.

    Args:
        years: Year values
        evolutionary_progression: Final evolutionary progression values
        tech_proxy: Technological sophistication component
        cognitive_proxy: Cognitive complexity component
        institutional_proxy: Institutional evolution component
        output_file: Output file path
    """
    print(f"\n💾 Saving evolutionary progression to {output_file}")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Create DataFrame with all components
    df = pd.DataFrame(
        {
            "year": years,
            "evolutionary_progression": evolutionary_progression,
            "tech_sophistication": tech_proxy,
            "cognitive_complexity": cognitive_proxy,
            "institutional_evolution": institutional_proxy,
        }
    )

    # Save main data
    df[["year", "evolutionary_progression"]].to_csv(output_file, index=False)
    print(f"   ✓ Saved evolutionary progression")

    # Save detailed version with components
    detailed_file = output_file.parent / f"{output_file.stem}_detailed.csv"
    df.to_csv(detailed_file, index=False)
    print(f"   ✓ Saved detailed version: {detailed_file}")

    # Summary statistics
    summary = {
        "source": "HYDE 3.2 demographic data (proxy approach)",
        "note": "Fallback implementation - real data sources preferred",
        "coverage": f"{years.min()}-{years.max()}",
        "n_years": len(df),
        "min_value": float(evolutionary_progression.min()),
        "max_value": float(evolutionary_progression.max()),
        "mean_value": float(evolutionary_progression.mean()),
        "value_2020": (
            float(df[df["year"] == 2020]["evolutionary_progression"].values[0])
            if 2020 in years.values
            else None
        ),
        "components": {
            "tech_mean": float(tech_proxy.mean()),
            "cognitive_mean": float(cognitive_proxy.mean()),
            "institutional_mean": float(institutional_proxy.mean()),
        },
        "weights": {"tech": 0.4, "cognitive": 0.3, "institutional": 0.3},
    }

    summary_file = output_file.parent / f"{output_file.stem}_summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"   ✓ Summary saved: {summary_file}")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Create HYDE-based Evolutionary Progression Proxy"
    )
    parser.add_argument(
        "--hyde-data",
        type=Path,
        default=Path("data/sources/hyde/processed/hyde_aggregated_-3000_2020.csv"),
        help="Path to processed HYDE data",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/evolutionary_progression_hyde_-3000_2020.csv"),
        help="Output file path",
    )
    parser.add_argument(
        "--year-start",
        type=int,
        default=-3000,
        help="Start year (default: -3000 for 3000 BCE)",
    )
    parser.add_argument(
        "--year-end", type=int, default=2020, help="End year (default: 2020)"
    )

    args = parser.parse_args()

    print("=" * 80)
    print("HYDE-Based Evolutionary Progression Proxy Generator")
    print("=" * 80)
    print("\n⚠️  NOTE: This is a fallback approach using demographic data")
    print(
        "   Real data sources (WIPO/Barro-Lee/Polity5) provide higher quality proxies"
    )
    print("   However, this approach is better than pure synthetic data\n")

    # Load HYDE data
    hyde_df = load_hyde_data(args.hyde_data)

    # Filter to year range
    hyde_df = hyde_df[
        (hyde_df["year"] >= args.year_start) & (hyde_df["year"] <= args.year_end)
    ].reset_index(drop=True)

    print(f"\n   Filtered to {len(hyde_df)} years ({args.year_start}-{args.year_end})")

    # Compute three proxies
    tech_proxy = compute_tech_sophistication_proxy(hyde_df)
    cognitive_proxy = compute_cognitive_complexity_proxy(hyde_df)
    institutional_proxy = compute_institutional_evolution_proxy(hyde_df)

    # Combine into evolutionary progression
    evolutionary_progression = create_evolutionary_progression(
        tech_proxy, cognitive_proxy, institutional_proxy
    )

    # Save results
    save_evolutionary_progression(
        hyde_df["year"],
        evolutionary_progression,
        tech_proxy,
        cognitive_proxy,
        institutional_proxy,
        args.output,
    )

    print(f"\n🎉 HYDE-based evolutionary progression created!")
    print(f"\n   Output: {args.output}")
    print(f"   Coverage: {args.year_start} to {args.year_end}")
    print(f"   Quality: Better than synthetic, but real data sources preferred")

    return 0


if __name__ == "__main__":
    exit(main())
