#!/usr/bin/env python3
"""
Process Polity V Institutional Data for H7 Institutions Component

Extracts global institutional quality from Polity V dataset,
creates annual time series for 1800-2018, and normalizes to 0-1 scale.

Input: data_sources/h7_institutions/polity5_2018.xls (4.5 MB)
Output: data_sources/processed/h7_institutions_1800_2018.csv
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

def process_institutions_data():
    """Process Polity V data to normalized annual time series."""

    # Define paths (relative to historical_k directory)
    script_dir = Path(__file__).parent
    input_path = script_dir / 'data_sources/h7_institutions/polity5_2018.xls'
    output_path = script_dir / 'data_sources/processed/h7_institutions_1800_2018.csv'

    print("=" * 60)
    print("H7 Institutions Component Processing")
    print("=" * 60)
    print()

    # Check input file exists
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        sys.exit(1)

    print(f"Loading Polity V data from {input_path}...")

    # Try reading Excel file
    try:
        # Try with openpyxl first (for .xlsx)
        polity = pd.read_excel(input_path, engine='openpyxl')
        print(f"  Loaded with openpyxl engine")
    except:
        try:
            # Fall back to xlrd for old .xls format
            polity = pd.read_excel(input_path, engine='xlrd')
            print(f"  Loaded with xlrd engine")
        except Exception as e:
            print(f"ERROR: Could not read Excel file: {e}")
            print("Trying default engine...")
            try:
                polity = pd.read_excel(input_path)
                print(f"  Loaded with default engine")
            except Exception as e2:
                print(f"ERROR: All engines failed: {e2}")
                sys.exit(1)

    print(f"  Total rows: {len(polity):,}")
    print(f"  Columns: {list(polity.columns)[:10]}...")  # Show first 10 columns
    print()

    # Check for required columns
    if 'year' not in polity.columns:
        # Try to find year column (might be 'Year' or 'YEAR')
        year_cols = [c for c in polity.columns if 'year' in c.lower()]
        if year_cols:
            polity.rename(columns={year_cols[0]: 'year'}, inplace=True)
            print(f"  Renamed '{year_cols[0]}' to 'year'")
        else:
            print(f"ERROR: No year column found!")
            print(f"Available columns: {list(polity.columns)}")
            sys.exit(1)

    if 'polity2' not in polity.columns:
        # Try to find polity2 column
        polity_cols = [c for c in polity.columns if 'polity' in c.lower()]
        print(f"Available polity columns: {polity_cols}")
        if polity_cols:
            polity.rename(columns={polity_cols[0]: 'polity2'}, inplace=True)
            print(f"  Renamed '{polity_cols[0]}' to 'polity2'")
        else:
            print(f"ERROR: No polity column found!")
            sys.exit(1)

    print(f"Year range: {polity['year'].min()} - {polity['year'].max()}")
    print(f"Unique countries: {polity['country'].nunique() if 'country' in polity.columns else 'N/A'}")
    print()

    # Filter to valid polity2 scores (-10 to +10)
    print("Filtering valid polity2 scores...")
    valid_polity = polity[
        (polity['polity2'].notna()) &
        (polity['polity2'] >= -10) &
        (polity['polity2'] <= 10)
    ].copy()

    print(f"  Valid observations: {len(valid_polity):,} (of {len(polity):,})")
    print(f"  Removed: {len(polity) - len(valid_polity):,} invalid/missing")
    print()

    # Compute global institutional quality
    print("Computing global institutional quality...")
    print("  Method: Simple mean across countries per year")
    print("  (Alternative: population-weighted mean would require population data)")

    # Group by year and compute mean polity2 score
    global_inst = valid_polity.groupby('year').agg({
        'polity2': ['mean', 'median', 'std', 'count']
    }).reset_index()

    global_inst.columns = ['year', 'polity2_mean', 'polity2_median', 'polity2_std', 'country_count']

    print(f"  Time series length: {len(global_inst)} years")
    print(f"  Year range: {global_inst['year'].min()} - {global_inst['year'].max()}")
    print()

    # Display sample statistics
    print("Sample statistics by year:")
    print(global_inst.head(10).to_string(index=False))
    print()

    # Normalize polity2 scores from (-10, +10) to (0, 1)
    print("Normalizing to 0-1 scale...")
    print(f"  Polity2 range: {global_inst['polity2_mean'].min():.3f} to {global_inst['polity2_mean'].max():.3f}")

    # Normalize: (polity2 + 10) / 20 maps (-10, +10) → (0, 1)
    global_inst['institutions_normalized'] = (global_inst['polity2_mean'] + 10) / 20

    # Verify normalization
    norm_min = global_inst['institutions_normalized'].min()
    norm_max = global_inst['institutions_normalized'].max()
    print(f"  Normalized min: {norm_min:.6f}")
    print(f"  Normalized max: {norm_max:.6f}")
    print()

    # Create output dataframe
    output_df = global_inst[['year', 'polity2_mean', 'country_count', 'institutions_normalized']].copy()
    output_df = output_df.rename(columns={
        'polity2_mean': 'polity2_score',
        'institutions_normalized': 'h7_institutions_component'
    })

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save processed data
    print(f"Saving processed data to {output_path}...")
    output_df.to_csv(output_path, index=False)
    print(f"  File size: {output_path.stat().st_size / 1024:.1f} KB")
    print()

    # Display sample data
    print("Sample of processed data:")
    print("=" * 60)

    # Show first 5 rows
    print("\nFirst 5 years:")
    print(output_df.head().to_string(index=False))

    # Show last 5 rows
    print("\nLast 5 years:")
    print(output_df.tail().to_string(index=False))

    # Show some key years
    key_years = [1800, 1850, 1900, 1950, 2000, 2018]
    print("\nKey years:")
    for year in key_years:
        row = output_df[output_df['year'] == year]
        if not row.empty:
            score = row['polity2_score'].values[0]
            norm = row['h7_institutions_component'].values[0]
            count = row['country_count'].values[0]
            print(f"  {year}: Polity2={score:+.2f} → {norm:.6f} ({count} countries)")

    print()
    print("=" * 60)
    print("✅ Institutions data processing COMPLETE")
    print(f"✅ Output: {output_path}")
    print(f"✅ Coverage: {len(output_df)} years ({output_df['year'].min()}-{output_df['year'].max()})")
    print("=" * 60)

    return output_df

if __name__ == '__main__':
    try:
        result = process_institutions_data()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
