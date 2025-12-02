"""
Barro-Lee Education Data Integration for Historical K(t) Index.

Integrates real education attainment data to replace synthetic cognitive complexity proxy.

Data Source: Barro-Lee Educational Attainment Dataset
Coverage: 1950-2015 (5-year intervals)
Variables: Years of schooling, educational attainment distribution
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd


def download_barro_lee_data(output_dir: Path) -> Path:
    """
    Download Barro-Lee educational attainment data.

    Args:
        output_dir: Directory to save downloaded data

    Returns:
        Path to downloaded file
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    instructions = """
    ============================================================
    Barro-Lee Education Data Download Instructions
    ============================================================

    Manual Download Required:

    1. Visit Barro-Lee Dataset Website:
       http://www.barrolee.com/

    2. Navigate to "Data" section

    3. Download:
       - "BL2013_MF1599_v2.2.xlsx" (Most comprehensive)
       - Coverage: 1950-2015, 5-year intervals
       - Variables: Educational attainment by age group

    4. Save to: {output_dir}/BL2013_MF1599_v2.2.xlsx

    Alternative (CSV format):
       - http://www.barrolee.com/data/BL_v2.2/BL2013_MF1599_v2.2.csv

    UNESCO Supplementary Data:

    1. Visit UNESCO Institute for Statistics:
       http://data.uis.unesco.org/

    2. Download:
       - Literacy rates (1970-present)
       - Enrollment ratios (1970-present)

    3. Save to: {output_dir}/unesco_literacy.csv

    ============================================================

    Once downloaded, run:
        python historical_k/barro_lee_integration.py --process

    """.format(
        output_dir=output_dir
    )

    print(instructions)

    # Check if data already exists
    bl_file = output_dir / "BL2013_MF1599_v2.2.xlsx"
    bl_csv = output_dir / "BL2013_MF1599_v2.2.csv"

    if bl_file.exists():
        print(f"✓ Found Barro-Lee data: {bl_file}")
        return bl_file
    elif bl_csv.exists():
        print(f"✓ Found Barro-Lee data: {bl_csv}")
        return bl_csv
    else:
        print("⚠️  No Barro-Lee data found. Please download manually.")
        return None


def process_barro_lee_data(input_file: Path, output_file: Path) -> pd.DataFrame:
    """
    Process Barro-Lee education data into cognitive complexity proxy.

    Args:
        input_file: Raw Barro-Lee data file
        output_file: Processed output file

    Returns:
        DataFrame with year and cognitive_complexity columns
    """
    print(f"\n📚 Processing Barro-Lee education data from {input_file}")

    # Read data
    if input_file.suffix == ".csv":
        df = pd.read_csv(input_file)
    else:
        df = pd.read_excel(input_file)

    print(f"   Raw data: {len(df)} rows, {len(df.columns)} columns")

    # Barro-Lee dataset structure:
    # - Country code (BLcode, WBcode)
    # - Year (year)
    # - Age group (AG15, AG25, etc.)
    # - Educational attainment variables:
    #   * yr_sch: Average years of schooling
    #   * lu: % no education
    #   * lp: % primary
    #   * ls: % secondary
    #   * lh: % tertiary (higher)

    # Normalize column names
    df.columns = df.columns.str.lower().str.strip()

    # Check for required columns
    required_cols = ["year", "yr_sch"]  # Minimum requirements
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(
                f"Missing required column '{col}'. Available: {df.columns.tolist()}"
            )

    print(f"   Found required columns: {required_cols}")

    # Filter to age group 15+ (most comprehensive coverage)
    # Some datasets use different age group codes
    if "agefrom" in df.columns and "ageto" in df.columns:
        df = df[(df["agefrom"] == 15) & (df["ageto"] == 99)]
    elif "age_group" in df.columns:
        df = df[df["age_group"].isin(["15+", "15-99", "AG15"])]

    print(f"   Filtered to age 15+: {len(df)} records")

    # Aggregate to global level (population-weighted if population data available)
    if "pop" in df.columns or "population" in df.columns:
        pop_col = "pop" if "pop" in df.columns else "population"
        print(f"   Using population weights: {pop_col}")

        # Calculate global weighted average
        global_df = (
            df.groupby("year")
            .apply(
                lambda x: pd.Series(
                    {
                        "yr_sch_weighted": (x["yr_sch"] * x[pop_col]).sum()
                        / x[pop_col].sum(),
                        "total_population": x[pop_col].sum(),
                        "n_countries": len(x),
                    }
                )
            )
            .reset_index()
        )
    else:
        print("   No population weights - using simple average")
        global_df = df.groupby("year").agg({"yr_sch": "mean"}).reset_index()
        global_df.rename(columns={"yr_sch": "yr_sch_weighted"}, inplace=True)
        global_df["n_countries"] = df.groupby("year").size().values

    # Calculate tertiary education rate if available
    if "lh" in df.columns:
        tertiary = df.groupby("year")["lh"].mean().reset_index()
        tertiary.columns = ["year", "tertiary_rate"]
        global_df = global_df.merge(tertiary, on="year", how="left")
        print("   Calculated tertiary education rate")
    else:
        global_df["tertiary_rate"] = np.nan

    print(f"\n   Global education metrics computed:")
    print(
        f"   Years: {len(global_df)} ({global_df['year'].min()}-{global_df['year'].max()})"
    )
    print(f"   Avg years of schooling: {global_df['yr_sch_weighted'].mean():.2f}")

    # Interpolate to annual resolution (Barro-Lee is 5-year intervals)
    print("\n   Interpolating to annual resolution...")
    year_range = range(int(global_df["year"].min()), int(global_df["year"].max()) + 1)
    annual_df = pd.DataFrame({"year": list(year_range)})

    # Merge and interpolate
    annual_df = annual_df.merge(global_df, on="year", how="left")
    annual_df["yr_sch"] = annual_df["yr_sch_weighted"].interpolate(method="linear")

    if (
        "tertiary_rate" in annual_df.columns
        and not annual_df["tertiary_rate"].isna().all()
    ):
        annual_df["tertiary_rate"] = annual_df["tertiary_rate"].interpolate(
            method="linear"
        )
        has_tertiary = True
    else:
        annual_df["tertiary_rate"] = 0.1  # Reasonable default
        has_tertiary = False

    # Compute cognitive complexity proxy
    # Formula: weighted combination of schooling years and tertiary attainment
    # Normalize each component to [0, 1]
    annual_df["yr_sch_norm"] = (annual_df["yr_sch"] - annual_df["yr_sch"].min()) / (
        annual_df["yr_sch"].max() - annual_df["yr_sch"].min()
    )

    if has_tertiary:
        annual_df["tertiary_norm"] = (
            annual_df["tertiary_rate"] / 100
        )  # Already in percentage
        annual_df["cognitive_complexity"] = (
            0.7 * annual_df["yr_sch_norm"] + 0.3 * annual_df["tertiary_norm"]
        )
    else:
        # If no tertiary data, use only years of schooling
        annual_df["cognitive_complexity"] = annual_df["yr_sch_norm"]

    # Final normalization to [0, 1]
    min_val = annual_df["cognitive_complexity"].min()
    max_val = annual_df["cognitive_complexity"].max()
    annual_df["cognitive_complexity"] = (
        annual_df["cognitive_complexity"] - min_val
    ) / (max_val - min_val)

    print(f"\n✅ Cognitive complexity computed:")
    print(f"   Years: {len(annual_df)}")
    print(f"   Coverage: {annual_df['year'].min()}-{annual_df['year'].max()}")
    print(
        f"   Range: {annual_df['cognitive_complexity'].min():.3f} - {annual_df['cognitive_complexity'].max():.3f}"
    )
    print(f"   Mean: {annual_df['cognitive_complexity'].mean():.3f}")
    if 2015 in annual_df["year"].values:
        print(
            f"   2015 value: {annual_df[annual_df['year'] == 2015]['cognitive_complexity'].values[0]:.3f}"
        )

    # Save processed data
    output_file.parent.mkdir(parents=True, exist_ok=True)
    result_df = annual_df[["year", "cognitive_complexity"]].copy()
    result_df.to_csv(output_file, index=False)
    print(f"   Saved to: {output_file}")

    # Summary statistics
    summary = {
        "source": "Barro-Lee Educational Attainment Dataset",
        "coverage": f"{annual_df['year'].min()}-{annual_df['year'].max()}",
        "n_years": len(annual_df),
        "min_value": float(annual_df["cognitive_complexity"].min()),
        "max_value": float(annual_df["cognitive_complexity"].max()),
        "mean_value": float(annual_df["cognitive_complexity"].mean()),
        "value_2015": (
            float(
                annual_df[annual_df["year"] == 2015]["cognitive_complexity"].values[0]
            )
            if 2015 in annual_df["year"].values
            else None
        ),
        "has_tertiary_data": has_tertiary,
        "avg_years_schooling_2015": (
            float(annual_df[annual_df["year"] == 2015]["yr_sch"].values[0])
            if 2015 in annual_df["year"].values
            else None
        ),
    }

    summary_file = output_file.parent / f"{output_file.stem}_summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"   Summary saved to: {summary_file}")

    return result_df


def validate_barro_lee_data(processed_file: Path) -> bool:
    """
    Validate processed Barro-Lee data.

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
    if "year" not in df.columns or "cognitive_complexity" not in df.columns:
        print(f"   ❌ Missing required columns. Found: {df.columns.tolist()}")
        return False

    # Check year range
    if df["year"].min() > 1960 or df["year"].max() < 2010:
        print(f"   ⚠️  Limited year range: {df['year'].min()}-{df['year'].max()}")

    # Check value range
    if df["cognitive_complexity"].min() < 0 or df["cognitive_complexity"].max() > 1:
        print(
            f"   ❌ Values outside [0,1]: {df['cognitive_complexity'].min():.3f} - {df['cognitive_complexity'].max():.3f}"
        )
        return False

    # Check for NaN values
    if df["cognitive_complexity"].isna().any():
        n_nan = df["cognitive_complexity"].isna().sum()
        print(f"   ⚠️  {n_nan} NaN values found")

    # Check monotonic trend (education should generally increase)
    is_monotonic = df["cognitive_complexity"].is_monotonic_increasing
    if not is_monotonic:
        print(
            f"   ⚠️  Non-monotonic trend detected (some expected due to interpolation)"
        )

    print(f"   ✅ Validation passed")
    print(f"   Years: {len(df)}")
    print(f"   Coverage: {df['year'].min()}-{df['year'].max()}")
    print(
        f"   Value range: {df['cognitive_complexity'].min():.3f} - {df['cognitive_complexity'].max():.3f}"
    )

    return True


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Barro-Lee Education Data Integration for Historical K(t)"
    )
    parser.add_argument(
        "--download", action="store_true", help="Show download instructions"
    )
    parser.add_argument(
        "--process", action="store_true", help="Process downloaded Barro-Lee data"
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate processed data"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/sources/barro_lee/BL2013_MF1599_v2.2.xlsx"),
        help="Input file path",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/cognitive_complexity_1950_2015.csv"),
        help="Output file path",
    )

    args = parser.parse_args()

    if args.download or (not args.process and not args.validate):
        download_barro_lee_data(Path("data/sources/barro_lee"))

    if args.process:
        if args.input.exists():
            process_barro_lee_data(args.input, args.output)
        else:
            print(f"❌ Input file not found: {args.input}")
            print("   Run with --download to see instructions")
            return 1

    if args.validate:
        validate_barro_lee_data(args.output)

    return 0


if __name__ == "__main__":
    exit(main())
