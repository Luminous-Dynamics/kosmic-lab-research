"""
Polity5 Institutional Data Integration for Historical K(t) Index.

Integrates real institutional/governance data to replace synthetic institutional evolution proxy.

Data Source: Polity5 Project (Center for Systemic Peace)
Coverage: 1800-2020
Variables: Democracy scores, regime characteristics, durability
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd


def download_polity_data(output_dir: Path) -> Path:
    """
    Download Polity5 dataset.

    Args:
        output_dir: Directory to save downloaded data

    Returns:
        Path to downloaded file
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    instructions = """
    ============================================================
    Polity5 Institutional Data Download Instructions
    ============================================================

    Manual Download Required:

    1. Visit Polity5 Project Website:
       https://www.systemicpeace.org/inscrdata.html

    2. Download "Polity5 Annual Time-Series":
       - File: "p5v2018.xls" or "p5v2018.csv"
       - Coverage: 1800-2018 (167+ countries)
       - Variables: polity, democ, autoc, durable

    3. Save to: {output_dir}/p5v2018.xls

    Alternative Sources:

    1. Comparative Constitutions Project:
       https://comparativeconstitutionsproject.org/download-data/
       - Constitutional characteristics
       - Rights indices

    2. V-Dem (Varieties of Democracy):
       https://www.v-dem.net/data/dataset-archive/
       - More comprehensive democracy measures
       - Coverage: 1789-present

    ============================================================

    Once downloaded, run:
        python historical_k/polity_integration.py --process

    """.format(
        output_dir=output_dir
    )

    print(instructions)

    # Check if data already exists
    polity_file = output_dir / "p5v2018.xls"
    polity_csv = output_dir / "p5v2018.csv"

    if polity_file.exists():
        print(f"✓ Found Polity5 data: {polity_file}")
        return polity_file
    elif polity_csv.exists():
        print(f"✓ Found Polity5 data: {polity_csv}")
        return polity_csv
    else:
        print("⚠️  No Polity5 data found. Please download manually.")
        return None


def process_polity_data(input_file: Path, output_file: Path) -> pd.DataFrame:
    """
    Process Polity5 data into institutional evolution proxy.

    Args:
        input_file: Raw Polity5 data file
        output_file: Processed output file

    Returns:
        DataFrame with year and institutional_evolution columns
    """
    print(f"\n🏛️  Processing Polity5 institutional data from {input_file}")

    # Read data
    if input_file.suffix == ".csv":
        df = pd.read_csv(input_file)
    else:
        df = pd.read_excel(input_file)

    print(f"   Raw data: {len(df)} rows, {len(df.columns)} columns")

    # Polity5 dataset structure:
    # - country: Country name
    # - ccode: Country code
    # - scode: Short country code
    # - year: Year
    # - polity: Combined polity score (-10 to +10)
    # - polity2: Modified polity score (removes special codes)
    # - democ: Democracy score (0-10)
    # - autoc: Autocracy score (0-10)
    # - durable: Years of current regime
    # - xrreg, xrcomp, xropen: Executive recruitment variables
    # - xconst: Executive constraints (1-7)
    # - parreg, parcomp: Political participation variables

    # Normalize column names
    df.columns = df.columns.str.lower().str.strip()

    # Check for required columns
    required_cols = ["year", "polity2"]  # polity2 is preferred over polity
    alt_col = "polity" if "polity" in df.columns else None

    if "polity2" not in df.columns and alt_col is None:
        raise ValueError(
            f"Missing required column 'polity' or 'polity2'. Available: {df.columns.tolist()}"
        )

    polity_col = "polity2" if "polity2" in df.columns else "polity"
    print(f"   Using polity column: {polity_col}")

    # Filter out special codes (Polity uses -66, -77, -88 for various missing data codes)
    df = df[df[polity_col] >= -10]

    print(f"   Filtered valid polity scores: {len(df)} records")
    print(f"   Year range: {df['year'].min()}-{df['year'].max()}")
    print(
        f"   Countries: {df['country'].nunique() if 'country' in df.columns else 'N/A'}"
    )

    # Calculate additional metrics if available
    has_democ = "democ" in df.columns
    has_xconst = "xconst" in df.columns
    has_durable = "durable" in df.columns

    print(
        f"   Available metrics: democ={has_democ}, xconst={has_xconst}, durable={has_durable}"
    )

    # Aggregate to global level
    # Multiple approaches:
    # 1. Simple average of polity scores
    # 2. Population-weighted average (if population data available)
    # 3. Democracy prevalence (% countries with polity > 6)

    # Simple global average by year
    global_df = (
        df.groupby("year")
        .agg({polity_col: "mean", "country": "count"})  # Number of countries with data
        .reset_index()
    )
    global_df.columns = ["year", "polity_mean", "n_countries"]

    # Calculate democracy prevalence (% with polity > 6)
    democracy_count = df[df[polity_col] > 6].groupby("year").size()
    global_df["democracy_rate"] = (democracy_count / global_df["n_countries"]).fillna(0)

    # Add additional metrics if available
    if has_democ:
        democ_avg = df.groupby("year")["democ"].mean()
        global_df["democ_mean"] = democ_avg

    if has_xconst:
        xconst_avg = df.groupby("year")["xconst"].mean()
        global_df["xconst_mean"] = xconst_avg

    if has_durable:
        durable_avg = df.groupby("year")["durable"].mean()
        global_df["durable_mean"] = durable_avg

    print(f"\n   Global institutional metrics computed:")
    print(
        f"   Years: {len(global_df)} ({global_df['year'].min()}-{global_df['year'].max()})"
    )
    print(f"   Avg polity score: {global_df['polity_mean'].mean():.2f}")
    print(f"   Democracy rate: {global_df['democracy_rate'].mean():.1%}")

    # Interpolate to fill gaps (some years may have limited coverage)
    year_range = range(int(global_df["year"].min()), int(global_df["year"].max()) + 1)
    annual_df = pd.DataFrame({"year": list(year_range)})
    annual_df = annual_df.merge(global_df, on="year", how="left")

    # Interpolate polity score
    annual_df["polity_mean"] = annual_df["polity_mean"].interpolate(method="linear")
    annual_df["democracy_rate"] = annual_df["democracy_rate"].interpolate(
        method="linear"
    )

    # Compute institutional evolution proxy
    # Formula: combine polity score (transformed to [0,1]) and democracy prevalence
    # Polity ranges from -10 to +10, transform to [0, 1]
    annual_df["polity_norm"] = (annual_df["polity_mean"] + 10) / 20

    # Weight: 60% polity score, 40% democracy prevalence
    annual_df["institutional_evolution_raw"] = (
        0.6 * annual_df["polity_norm"] + 0.4 * annual_df["democracy_rate"]
    )

    # Add regime durability if available (indicates stability)
    if has_durable and "durable_mean" in annual_df.columns:
        annual_df["durable_mean"] = annual_df["durable_mean"].interpolate(
            method="linear"
        )
        # Normalize durability (cap at 100 years)
        annual_df["durable_norm"] = np.clip(annual_df["durable_mean"] / 100, 0, 1)

        # Incorporate durability: 50% polity/democracy, 50% stability
        annual_df["institutional_evolution_raw"] = (
            0.5 * annual_df["institutional_evolution_raw"]
            + 0.5 * annual_df["durable_norm"]
        )

    # Final normalization to [0, 1] within the time period
    min_val = annual_df["institutional_evolution_raw"].min()
    max_val = annual_df["institutional_evolution_raw"].max()
    annual_df["institutional_evolution"] = (
        annual_df["institutional_evolution_raw"] - min_val
    ) / (max_val - min_val)

    print(f"\n✅ Institutional evolution computed:")
    print(f"   Years: {len(annual_df)}")
    print(f"   Coverage: {annual_df['year'].min()}-{annual_df['year'].max()}")
    print(
        f"   Range: {annual_df['institutional_evolution'].min():.3f} - {annual_df['institutional_evolution'].max():.3f}"
    )
    print(f"   Mean: {annual_df['institutional_evolution'].mean():.3f}")
    if 2018 in annual_df["year"].values:
        print(
            f"   2018 value: {annual_df[annual_df['year'] == 2018]['institutional_evolution'].values[0]:.3f}"
        )

    # Save processed data
    output_file.parent.mkdir(parents=True, exist_ok=True)
    result_df = annual_df[["year", "institutional_evolution"]].copy()
    result_df.to_csv(output_file, index=False)
    print(f"   Saved to: {output_file}")

    # Summary statistics
    summary = {
        "source": "Polity5 Project",
        "coverage": f"{annual_df['year'].min()}-{annual_df['year'].max()}",
        "n_years": len(annual_df),
        "min_value": float(annual_df["institutional_evolution"].min()),
        "max_value": float(annual_df["institutional_evolution"].max()),
        "mean_value": float(annual_df["institutional_evolution"].mean()),
        "value_2018": (
            float(
                annual_df[annual_df["year"] == 2018]["institutional_evolution"].values[
                    0
                ]
            )
            if 2018 in annual_df["year"].values
            else None
        ),
        "avg_polity_2018": (
            float(annual_df[annual_df["year"] == 2018]["polity_mean"].values[0])
            if 2018 in annual_df["year"].values
            else None
        ),
        "democracy_rate_2018": (
            float(annual_df[annual_df["year"] == 2018]["democracy_rate"].values[0])
            if 2018 in annual_df["year"].values
            else None
        ),
        "has_durability_data": has_durable,
    }

    summary_file = output_file.parent / f"{output_file.stem}_summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"   Summary saved to: {summary_file}")

    return result_df


def validate_polity_data(processed_file: Path) -> bool:
    """
    Validate processed Polity5 data.

    Args:
        processed_file: Path to processed data file

    Returns:
        True if validation passes
    """
    print(f"\n🔬 Validating {processed_file}")

    if not processed_file.exists():
        print(f"   ❌ File not found: {processed_file}")
        return False

    df = pd.read_csv(processed_file)

    # Check required columns
    if "year" not in df.columns or "institutional_evolution" not in df.columns:
        print(f"   ❌ Missing required columns. Found: {df.columns.tolist()}")
        return False

    # Check year range
    if df["year"].min() > 1850 or df["year"].max() < 2010:
        print(f"   ⚠️  Limited year range: {df['year'].min()}-{df['year'].max()}")

    # Check value range
    if (
        df["institutional_evolution"].min() < 0
        or df["institutional_evolution"].max() > 1
    ):
        print(
            f"   ❌ Values outside [0,1]: {df['institutional_evolution'].min():.3f} - {df['institutional_evolution'].max():.3f}"
        )
        return False

    # Check for NaN values
    if df["institutional_evolution"].isna().any():
        n_nan = df["institutional_evolution"].isna().sum()
        print(f"   ⚠️  {n_nan} NaN values found")

    # Check general upward trend (democratization over time)
    # Use 20-year windows
    windows = [
        df.iloc[i : i + 20]["institutional_evolution"].mean()
        for i in range(0, len(df) - 20, 20)
    ]
    generally_increasing = (
        sum(windows[i] < windows[i + 1] for i in range(len(windows) - 1))
        / (len(windows) - 1)
        > 0.6
    )

    if not generally_increasing:
        print(f"   ⚠️  No clear upward trend detected (expected for democratization)")

    print(f"   ✅ Validation passed")
    print(f"   Years: {len(df)}")
    print(f"   Coverage: {df['year'].min()}-{df['year'].max()}")
    print(
        f"   Value range: {df['institutional_evolution'].min():.3f} - {df['institutional_evolution'].max():.3f}"
    )

    return True


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Polity5 Institutional Data Integration for Historical K(t)"
    )
    parser.add_argument(
        "--download", action="store_true", help="Show download instructions"
    )
    parser.add_argument(
        "--process", action="store_true", help="Process downloaded Polity5 data"
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate processed data"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/sources/polity/p5v2018.xls"),
        help="Input file path",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/institutional_evolution_1800_2018.csv"),
        help="Output file path",
    )

    args = parser.parse_args()

    if args.download or (not args.process and not args.validate):
        download_polity_data(Path("data/sources/polity"))

    if args.process:
        if args.input.exists():
            process_polity_data(args.input, args.output)
        else:
            print(f"❌ Input file not found: {args.input}")
            print("   Run with --download to see instructions")
            return 1

    if args.validate:
        validate_polity_data(args.output)

    return 0


if __name__ == "__main__":
    exit(main())
