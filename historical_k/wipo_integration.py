"""
WIPO Patent Data Integration for Historical K(t) Index.

Integrates real patent data to replace synthetic technological sophistication proxy.

Data Source: WIPO IP Statistics Data Center
Coverage: 1883-present
Variables: Patent applications, grants, technology field diversity
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
from scipy.stats import entropy


def download_wipo_data(output_dir: Path) -> Path:
    """
    Download WIPO patent statistics.

    Args:
        output_dir: Directory to save downloaded data

    Returns:
        Path to downloaded file

    Note:
        WIPO data is available from multiple sources:
        1. WIPO IP Statistics: https://www3.wipo.int/ipstats/
        2. OECD Patent Database: https://stats.oecd.org/
        3. EPO PATSTAT: https://www.epo.org/searching-for-patents/business/patstat.html

        For now, we'll use a manual download approach and provide instructions.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    instructions = """
    ============================================================
    WIPO Patent Data Download Instructions
    ============================================================

    Manual Download Required:

    1. Visit WIPO IP Statistics Data Center:
       https://www3.wipo.int/ipstats/

    2. Navigate to:
       Statistics > Patents > Applications > Time Series

    3. Download:
       - "Patent applications by year (1883-present)"
       - Select: All countries, All technologies
       - Format: CSV or Excel

    4. Save to: {output_dir}/wipo_patent_applications.csv

    Alternative Source (OECD):

    1. Visit OECD Patent Database:
       https://stats.oecd.org/Index.aspx?DataSetCode=PATS_IPC

    2. Download:
       - Patent applications by IPC technology area
       - Time period: 1883-2023
       - Format: CSV

    3. Save to: {output_dir}/oecd_patent_applications.csv

    ============================================================

    Once downloaded, run:
        python historical_k/wipo_integration.py --process

    """.format(
        output_dir=output_dir
    )

    print(instructions)

    # Check if data already exists
    wipo_file = output_dir / "wipo_patent_applications.csv"
    oecd_file = output_dir / "oecd_patent_applications.csv"

    if wipo_file.exists():
        print(f"✓ Found WIPO data: {wipo_file}")
        return wipo_file
    elif oecd_file.exists():
        print(f"✓ Found OECD data: {oecd_file}")
        return oecd_file
    else:
        print("⚠️  No patent data found. Please download manually.")
        return None


def process_wipo_data(input_file: Path, output_file: Path) -> pd.DataFrame:
    """
    Process WIPO patent data into technological sophistication proxy.

    Args:
        input_file: Raw WIPO data file
        output_file: Processed output file

    Returns:
        DataFrame with year and tech_sophistication columns
    """
    print(f"\n📊 Processing WIPO patent data from {input_file}")

    # Read data (handle both CSV and Excel)
    if input_file.suffix == ".csv":
        df = pd.read_csv(input_file)
    else:
        df = pd.read_excel(input_file)

    print(f"   Raw data: {len(df)} rows, columns: {df.columns.tolist()}")

    # Expected columns (flexible naming):
    # - Year / year / YEAR
    # - Applications / Patent Applications / applications
    # - Grants / Patent Grants / grants (optional)
    # - Technology / IPC / Field (for diversity calculation)

    # Normalize column names
    df.columns = df.columns.str.lower().str.strip()

    # Find year column
    year_col = None
    for col in ["year", "priority_year", "application_year", "filing_year"]:
        if col in df.columns:
            year_col = col
            break

    if year_col is None:
        raise ValueError(
            f"Could not find year column. Available: {df.columns.tolist()}"
        )

    # Find applications column
    apps_col = None
    for col in ["applications", "patent_applications", "total_applications", "count"]:
        if col in df.columns:
            apps_col = col
            break

    if apps_col is None:
        raise ValueError(
            f"Could not find applications column. Available: {df.columns.tolist()}"
        )

    print(f"   Using columns: year={year_col}, applications={apps_col}")

    # Aggregate by year (if data is country-level or tech-field-level)
    agg_df = df.groupby(year_col)[apps_col].sum().reset_index()
    agg_df.columns = ["year", "applications"]

    # Sort by year
    agg_df = agg_df.sort_values("year").reset_index(drop=True)

    # Filter to 1883-2023 range
    agg_df = agg_df[(agg_df["year"] >= 1883) & (agg_df["year"] <= 2023)]

    print(
        f"   Aggregated: {len(agg_df)} years ({agg_df['year'].min()}-{agg_df['year'].max()})"
    )
    print(
        f"   Patent applications range: {agg_df['applications'].min():,.0f} - {agg_df['applications'].max():,.0f}"
    )

    # Compute technological sophistication proxy
    # Formula: log(applications) normalized to [0, 1]
    agg_df["log_applications"] = np.log1p(
        agg_df["applications"]
    )  # log(1 + x) to handle zeros

    # Calculate 5-year moving average to smooth year-to-year noise
    agg_df["applications_smooth"] = (
        agg_df["applications"].rolling(window=5, center=True, min_periods=1).mean()
    )
    agg_df["log_applications_smooth"] = np.log1p(agg_df["applications_smooth"])

    # Compute technology diversity if field data available
    tech_col = None
    for col in ["technology", "ipc", "field", "tech_field", "ipc_section"]:
        if col in df.columns:
            tech_col = col
            break

    if tech_col is not None:
        print(f"   Computing technology diversity using column: {tech_col}")

        # Calculate Shannon entropy of technology field distribution by year
        diversity = []
        for year in agg_df["year"]:
            year_data = df[df[year_col] == year]
            if len(year_data) > 0:
                field_counts = year_data.groupby(tech_col)[apps_col].sum()
                if len(field_counts) > 0:
                    # Shannon entropy normalized by log(number of categories)
                    ent = entropy(field_counts.values, base=2)
                    max_ent = np.log2(len(field_counts))
                    diversity.append(ent / max_ent if max_ent > 0 else 0)
                else:
                    diversity.append(np.nan)
            else:
                diversity.append(np.nan)

        agg_df["tech_diversity"] = diversity
        print(f"   Technology diversity computed: mean={np.nanmean(diversity):.3f}")
    else:
        print("   ⚠️  No technology field data - diversity not computed")
        agg_df["tech_diversity"] = 0.5  # Neutral value

    # Final technological sophistication formula
    # Combines volume (log patents) and diversity
    if "tech_diversity" in agg_df.columns and not agg_df["tech_diversity"].isna().all():
        agg_df["tech_sophistication_raw"] = (
            0.7
            * agg_df["log_applications_smooth"]
            / agg_df["log_applications_smooth"].max()
            + 0.3 * agg_df["tech_diversity"]
        )
    else:
        # If no diversity data, use only patent volume
        agg_df["tech_sophistication_raw"] = (
            agg_df["log_applications_smooth"] / agg_df["log_applications_smooth"].max()
        )

    # Normalize to [0, 1] within modern epoch (1883-2023)
    min_val = agg_df["tech_sophistication_raw"].min()
    max_val = agg_df["tech_sophistication_raw"].max()
    agg_df["tech_sophistication"] = (agg_df["tech_sophistication_raw"] - min_val) / (
        max_val - min_val
    )

    print(f"\n✅ Technological sophistication computed:")
    print(f"   Years: {len(agg_df)}")
    print(
        f"   Range: {agg_df['tech_sophistication'].min():.3f} - {agg_df['tech_sophistication'].max():.3f}"
    )
    print(f"   Mean: {agg_df['tech_sophistication'].mean():.3f}")
    print(
        f"   2020 value: {agg_df[agg_df['year'] == 2020]['tech_sophistication'].values[0]:.3f}"
    )

    # Save processed data
    output_file.parent.mkdir(parents=True, exist_ok=True)
    agg_df.to_csv(output_file, index=False)
    print(f"   Saved to: {output_file}")

    # Summary statistics
    summary = {
        "source": "WIPO IP Statistics",
        "coverage": f"{agg_df['year'].min()}-{agg_df['year'].max()}",
        "n_years": len(agg_df),
        "min_value": float(agg_df["tech_sophistication"].min()),
        "max_value": float(agg_df["tech_sophistication"].max()),
        "mean_value": float(agg_df["tech_sophistication"].mean()),
        "value_2020": (
            float(agg_df[agg_df["year"] == 2020]["tech_sophistication"].values[0])
            if 2020 in agg_df["year"].values
            else None
        ),
        "has_diversity": "tech_diversity" in agg_df.columns
        and not agg_df["tech_diversity"].isna().all(),
    }

    summary_file = output_file.parent / f"{output_file.stem}_summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"   Summary saved to: {summary_file}")

    return agg_df[["year", "tech_sophistication"]]


def validate_wipo_data(processed_file: Path) -> bool:
    """
    Validate processed WIPO data.

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
    if "year" not in df.columns or "tech_sophistication" not in df.columns:
        print(f"   ❌ Missing required columns. Found: {df.columns.tolist()}")
        return False

    # Check year range
    if df["year"].min() > 1900 or df["year"].max() < 2020:
        print(f"   ⚠️  Limited year range: {df['year'].min()}-{df['year'].max()}")

    # Check value range
    if df["tech_sophistication"].min() < 0 or df["tech_sophistication"].max() > 1:
        print(
            f"   ❌ Values outside [0,1]: {df['tech_sophistication'].min():.3f} - {df['tech_sophistication'].max():.3f}"
        )
        return False

    # Check for NaN values
    if df["tech_sophistication"].isna().any():
        n_nan = df["tech_sophistication"].isna().sum()
        print(f"   ⚠️  {n_nan} NaN values found")

    # Check monotonic trend (should generally increase)
    # Use 10-year windows
    windows = [
        df.iloc[i : i + 10]["tech_sophistication"].mean()
        for i in range(0, len(df) - 10, 10)
    ]
    monotonic = all(windows[i] <= windows[i + 1] for i in range(len(windows) - 1))

    if not monotonic:
        print(
            f"   ⚠️  Non-monotonic trend detected (expected for technological progress)"
        )

    print(f"   ✅ Validation passed")
    print(f"   Years: {len(df)}")
    print(f"   Coverage: {df['year'].min()}-{df['year'].max()}")
    print(
        f"   Value range: {df['tech_sophistication'].min():.3f} - {df['tech_sophistication'].max():.3f}"
    )

    return True


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="WIPO Patent Data Integration for Historical K(t)"
    )
    parser.add_argument(
        "--download", action="store_true", help="Show download instructions"
    )
    parser.add_argument(
        "--process", action="store_true", help="Process downloaded WIPO data"
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate processed data"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/sources/wipo/wipo_patent_applications.csv"),
        help="Input file path",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/tech_sophistication_1883_2023.csv"),
        help="Output file path",
    )

    args = parser.parse_args()

    if args.download or (not args.process and not args.validate):
        download_wipo_data(Path("data/sources/wipo"))

    if args.process:
        if args.input.exists():
            process_wipo_data(args.input, args.output)
        else:
            print(f"❌ Input file not found: {args.input}")
            print("   Run with --download to see instructions")
            return 1

    if args.validate:
        validate_wipo_data(args.output)

    return 0


if __name__ == "__main__":
    exit(main())
