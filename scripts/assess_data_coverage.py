#!/usr/bin/env python3
"""
Assess temporal coverage of all external datasets for K(t) computation.

This script checks the actual year range in each dataset to determine:
1. Which datasets have data through 2020
2. Which datasets have data through 2023+
3. Specific gaps that need to be addressed
4. Feasibility of extending to 2025
"""

import sys
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")


def check_excel_coverage(file_path):
    """Check temporal coverage of Excel files."""
    try:
        # Try reading without specifying sheet (uses first sheet)
        df_sample = pd.read_excel(file_path, nrows=10)

        # Find year column
        year_cols = [
            col
            for col in df_sample.columns
            if any(term in str(col).lower() for term in ["year", "date", "time"])
        ]

        if not year_cols:
            return None, None, "No year column found"

        year_col = year_cols[0]

        # Read full file
        df_full = pd.read_excel(file_path, usecols=[year_col])
        years = pd.to_numeric(df_full[year_col], errors="coerce").dropna()

        if len(years) == 0:
            return None, None, "No valid years"

        return int(years.min()), int(years.max()), None
    except Exception as e:
        return None, None, str(e)[:100]


def check_dataset_coverage(data_dir="data/sources/external/raw"):
    """Check temporal coverage for each dataset."""
    print("\n" + "=" * 80)
    print("📊 Historical K(t) Data Coverage Assessment")
    print("=" * 80 + "\n")

    data_path = Path(data_dir)
    if not data_path.exists():
        print(f"❌ Data directory not found: {data_dir}")
        return

    results = []
    csv_files = list(data_path.glob("*.csv"))
    excel_files = list(data_path.glob("*.xls")) + list(data_path.glob("*.xlsx"))

    print(
        f"Found {len(csv_files)} CSV files and {len(excel_files)} Excel files to analyze...\n"
    )

    for csv_file in csv_files:
        try:
            # First check structure with small sample
            df_sample = pd.read_csv(csv_file, nrows=10)

            # Find year column (case-insensitive)
            year_cols = [
                col
                for col in df_sample.columns
                if any(term in col.lower() for term in ["year", "date", "time"])
            ]

            if not year_cols:
                results.append(
                    {
                        "file": csv_file.name,
                        "min_year": "N/A",
                        "max_year": "N/A",
                        "coverage": "No year column found",
                        "status": "⚠️",
                    }
                )
                continue

            # Use first year column found
            year_col = year_cols[0]

            # Read full dataset (just the year column)
            df_full = pd.read_csv(csv_file, usecols=[year_col])

            # Convert to numeric, handling various formats
            years = pd.to_numeric(df_full[year_col], errors="coerce")
            years = years.dropna()

            if len(years) == 0:
                results.append(
                    {
                        "file": csv_file.name,
                        "min_year": "N/A",
                        "max_year": "N/A",
                        "coverage": "No valid years",
                        "status": "⚠️",
                    }
                )
                continue

            min_year = int(years.min())
            max_year = int(years.max())

            # Determine status
            if max_year >= 2023:
                status = "✅"
            elif max_year >= 2020:
                status = "🟡"
            else:
                status = "🔴"

            results.append(
                {
                    "file": csv_file.name,
                    "min_year": min_year,
                    "max_year": max_year,
                    "coverage": f"{min_year} to {max_year}",
                    "status": status,
                }
            )

        except Exception as e:
            results.append(
                {
                    "file": csv_file.name,
                    "min_year": "Error",
                    "max_year": "Error",
                    "coverage": str(e)[:50],
                    "status": "❌",
                }
            )

    # Process Excel files
    for excel_file in excel_files:
        min_year, max_year, error = check_excel_coverage(excel_file)

        if error:
            results.append(
                {
                    "file": excel_file.name,
                    "min_year": "Error",
                    "max_year": "Error",
                    "coverage": error,
                    "status": "❌",
                }
            )
        elif min_year and max_year:
            # Determine status
            if max_year >= 2023:
                status = "✅"
            elif max_year >= 2020:
                status = "🟡"
            else:
                status = "🔴"

            results.append(
                {
                    "file": excel_file.name,
                    "min_year": min_year,
                    "max_year": max_year,
                    "coverage": f"{min_year} to {max_year}",
                    "status": status,
                }
            )

    # Print detailed results
    print("📋 Dataset Coverage Report:")
    print("-" * 80)
    print(f"{'Status':<8} {'Dataset':<40} {'Coverage':<30}")
    print("-" * 80)

    for r in sorted(
        results,
        key=lambda x: x["max_year"] if isinstance(x["max_year"], int) else 0,
        reverse=True,
    ):
        file_short = r["file"][:38] if len(r["file"]) > 38 else r["file"]
        print(f"{r['status']:<8} {file_short:<40} {r['coverage']:<30}")

    # Summary statistics
    print("\n" + "=" * 80)
    print("📊 Summary Statistics:")
    print("=" * 80)

    valid_results = [r for r in results if isinstance(r["max_year"], int)]

    if valid_results:
        complete_2020 = [r for r in valid_results if r["max_year"] >= 2020]
        complete_2023 = [r for r in valid_results if r["max_year"] >= 2023]
        needs_update = [r for r in valid_results if r["max_year"] < 2020]

        print(f"\n📦 Total datasets analyzed: {len(results)}")
        print(f"✅ Valid temporal data: {len(valid_results)}")
        print(
            f"🟡 Coverage through 2020+: {len(complete_2020)} ({len(complete_2020)/len(valid_results)*100:.1f}%)"
        )
        print(
            f"✅ Coverage through 2023+: {len(complete_2023)} ({len(complete_2023)/len(valid_results)*100:.1f}%)"
        )
        print(f"🔴 Needs updates (<2020): {len(needs_update)}")

        if complete_2023:
            print("\n🎯 Datasets with 2023+ data (ready for extension):")
            for r in sorted(complete_2023, key=lambda x: x["max_year"], reverse=True)[
                :10
            ]:
                print(f"   • {r['file']:<40} → {r['max_year']}")

        if needs_update:
            print("\n⚠️  Datasets needing updates:")
            for r in sorted(needs_update, key=lambda x: x["max_year"], reverse=True):
                print(f"   • {r['file']:<40} → Last year: {r['max_year']}")

        # Recommendation
        print("\n" + "=" * 80)
        print("💡 Recommendations:")
        print("=" * 80)

        pct_2023 = len(complete_2023) / len(valid_results) * 100
        pct_2020 = len(complete_2020) / len(valid_results) * 100

        if pct_2023 >= 70:
            print("\n✅ EXCELLENT: Majority of datasets have 2023+ coverage")
            print("   → Extending to 2025 is highly feasible")
            print("   → Recommendation: Proceed with extension now")
        elif pct_2020 >= 70:
            print("\n🟡 GOOD: Majority of datasets have 2020+ coverage")
            print("   → Extension possible but may need some updates")
            print("   → Recommendation: Update key datasets, then extend")
        else:
            print("\n🔴 NEEDS WORK: Many datasets lack modern coverage")
            print("   → Significant updates required before extension")
            print("   → Recommendation: Update datasets first, validate, then extend")

        print("\n📅 Next Steps:")
        print("   1. Review datasets needing updates")
        print("   2. Download latest versions from sources")
        print("   3. Re-run K(t) computation with updated data")
        print("   4. Extend temporal range to 2025")

    else:
        print("\n⚠️  No valid temporal data found in datasets")
        print("   → Check data directory structure and file formats")

    print("\n" + "=" * 80)

    return results


if __name__ == "__main__":
    data_dir = "data/sources/external/raw"

    # Allow custom directory from command line
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]

    results = check_dataset_coverage(data_dir)
