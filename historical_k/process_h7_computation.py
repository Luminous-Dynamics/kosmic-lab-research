#!/usr/bin/env python3
"""
Process Nordhaus Computing Power Data for H7 Computation Component

Normalizes Nordhaus computing power data to 0-1 scale.

Input: data_sources/h7_computation/nordhaus_2007_computing.csv (1.2 KB)
Output: data_sources/processed/h7_computation_1850_2020.csv
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

def process_computation_data():
    """Process Nordhaus computing power data to normalized annual time series."""

    # Define paths (relative to historical_k directory)
    script_dir = Path(__file__).parent
    input_path = script_dir / 'data_sources/h7_computation/nordhaus_2007_computing.csv'
    output_path = script_dir / 'data_sources/processed/h7_computation_1850_2020.csv'

    print("=" * 60)
    print("H7 Computing Power Component Processing")
    print("=" * 60)
    print()

    # Check input file exists
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        sys.exit(1)

    print(f"Loading Nordhaus computing data from {input_path}...")
    computing = pd.read_csv(input_path)

    print(f"  Total rows: {len(computing)}")
    print(f"  Columns: {list(computing.columns)}")
    print()

    # Display raw data
    print("Raw data sample:")
    print(computing.head(10).to_string(index=False))
    print()

    # Check year range
    year_min = computing['year'].min()
    year_max = computing['year'].max()
    print(f"Year range: {year_min} - {year_max}")
    print()

    # Normalize log_performance to 0-1 scale
    print("Normalizing log performance to 0-1 scale...")

    # Log performance ranges from -13 (manual calculation) to +13 (AI/ML acceleration)
    log_min = computing['log_performance'].min()
    log_max = computing['log_performance'].max()

    print(f"  Log performance range: {log_min:.1f} to {log_max:.1f}")
    print(f"  Span: {log_max - log_min:.1f} orders of magnitude")

    # Normalize: (log_performance - min) / (max - min)
    computing['computation_normalized'] = (computing['log_performance'] - log_min) / (log_max - log_min)

    # Verify normalization
    norm_min = computing['computation_normalized'].min()
    norm_max = computing['computation_normalized'].max()
    print(f"  Normalized min: {norm_min:.6f}")
    print(f"  Normalized max: {norm_max:.6f}")
    print()

    # Create output dataframe
    output_df = computing[['year', 'relative_performance', 'log_performance', 'computation_normalized', 'notes']].copy()
    output_df = output_df.rename(columns={
        'computation_normalized': 'h7_computation_component'
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

    # Show some key technological eras
    key_years = [1850, 1900, 1946, 1970, 1990, 2000, 2020]
    print("\nKey technological eras:")
    for year in key_years:
        row = output_df[output_df['year'] == year]
        if not row.empty:
            log_perf = row['log_performance'].values[0]
            norm = row['h7_computation_component'].values[0]
            note = row['notes'].values[0]
            print(f"  {year}: Log={log_perf:+5.1f} → {norm:.6f} ({note})")

    # Calculate doubling time
    print("\nGrowth analysis:")
    years_span = year_max - year_min
    log_span = log_max - log_min
    doublings = log_span / np.log10(2)  # log10(2) ≈ 0.301
    print(f"  Total span: {years_span} years")
    print(f"  Performance improvement: {10**log_span:.2e}x ({log_span:.1f} orders of magnitude)")
    print(f"  Number of doublings: {doublings:.1f}")
    print(f"  Average doubling time: {years_span / doublings:.1f} years")

    print()
    print("=" * 60)
    print("✅ Computing power data processing COMPLETE")
    print(f"✅ Output: {output_path}")
    print(f"✅ Coverage: {len(output_df)} years ({year_min}-{year_max})")
    print("=" * 60)

    return output_df

if __name__ == '__main__':
    try:
        result = process_computation_data()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
