#!/usr/bin/env python3
"""
Process OWID Energy Data for H7 Energy Component

Extracts global primary energy consumption from OWID dataset,
creates annual time series for 1810-2020, and normalizes to 0-1 scale.

Input: data_sources/h7_energy/owid_energy_data.csv (9.2 MB)
Output: data_sources/processed/h7_energy_1810_2020.csv
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

def process_energy_data():
    """Process OWID energy data to normalized annual time series."""

    # Define paths (relative to historical_k directory)
    script_dir = Path(__file__).parent
    input_path = script_dir / 'data_sources/h7_energy/owid_energy_data.csv'
    output_path = script_dir / 'data_sources/processed/h7_energy_1810_2020.csv'

    print("=" * 60)
    print("H7 Energy Component Processing")
    print("=" * 60)
    print()

    # Check input file exists
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        sys.exit(1)

    print(f"Loading OWID energy data from {input_path}...")
    df = pd.read_csv(input_path)
    print(f"  Total rows: {len(df):,}")
    print(f"  Columns: {list(df.columns)[:10]}...")  # Show first 10 columns
    print()

    # Filter to World entity
    print("Filtering to 'World' entity...")
    world = df[df['country'] == 'World'].copy()
    print(f"  World rows: {len(world):,}")
    print(f"  Year range: {world['year'].min()} - {world['year'].max()}")
    print()

    # Check primary_energy_consumption column
    if 'primary_energy_consumption' not in world.columns:
        print("ERROR: 'primary_energy_consumption' column not found!")
        print(f"Available columns: {list(world.columns)}")
        sys.exit(1)

    # Extract 1810-2020 time series
    print("Extracting 1810-2020 period...")
    energy_ts = world[(world['year'] >= 1810) & (world['year'] <= 2020)].copy()
    print(f"  Rows in period: {len(energy_ts)}")

    # Check for missing data
    missing = energy_ts['primary_energy_consumption'].isna().sum()
    print(f"  Missing values: {missing}")

    if missing > 0:
        print("  Handling missing values via interpolation...")
        energy_ts['primary_energy_consumption'] = energy_ts['primary_energy_consumption'].interpolate(method='linear')
        remaining_missing = energy_ts['primary_energy_consumption'].isna().sum()
        print(f"  Remaining missing: {remaining_missing}")

    print()

    # Normalize to 0-1 scale
    print("Normalizing to 0-1 scale...")
    energy_values = energy_ts['primary_energy_consumption'].values
    min_val = np.nanmin(energy_values)
    max_val = np.nanmax(energy_values)

    print(f"  Min value: {min_val:.2f} TWh")
    print(f"  Max value: {max_val:.2f} TWh")
    print(f"  Range: {max_val - min_val:.2f} TWh")

    energy_ts['energy_normalized'] = (energy_values - min_val) / (max_val - min_val)

    # Verify normalization
    norm_min = energy_ts['energy_normalized'].min()
    norm_max = energy_ts['energy_normalized'].max()
    print(f"  Normalized min: {norm_min:.6f}")
    print(f"  Normalized max: {norm_max:.6f}")
    print()

    # Create output dataframe
    output_df = energy_ts[['year', 'primary_energy_consumption', 'energy_normalized']].copy()
    output_df = output_df.rename(columns={
        'primary_energy_consumption': 'energy_twh',
        'energy_normalized': 'h7_energy_component'
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
    key_years = [1850, 1900, 1950, 2000]
    print("\nKey years:")
    for year in key_years:
        row = output_df[output_df['year'] == year]
        if not row.empty:
            print(f"  {year}: {row['energy_twh'].values[0]:.2f} TWh → {row['h7_energy_component'].values[0]:.6f}")

    print()
    print("=" * 60)
    print("✅ Energy data processing COMPLETE")
    print(f"✅ Output: {output_path}")
    print(f"✅ Coverage: {len(output_df)} years (1810-2020)")
    print("=" * 60)

    return output_df

if __name__ == '__main__':
    try:
        result = process_energy_data()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
