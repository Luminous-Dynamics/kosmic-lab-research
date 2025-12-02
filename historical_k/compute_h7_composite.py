#!/usr/bin/env python3
"""
Compute H7 Composite Index from Four Components

Merges all processed H7 components and computes weighted composite.

Inputs:
  - data_sources/processed/h7_energy_1810_2020.csv
  - data_sources/processed/h7_tech_1963_2023.csv
  - data_sources/processed/h7_institutions_1800_2018.csv
  - data_sources/processed/h7_computation_1850_2020.csv

Output:
  - data_sources/processed/h7_composite_1810_2020.csv
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

def compute_h7_composite():
    """Compute H7 composite from all four normalized components."""

    # Define paths (relative to historical_k directory)
    script_dir = Path(__file__).parent
    processed_dir = script_dir / 'data_sources/processed'

    energy_path = processed_dir / 'h7_energy_1810_2020.csv'
    tech_path = processed_dir / 'h7_tech_1963_2023.csv'
    institutions_path = processed_dir / 'h7_institutions_1800_2018.csv'
    computation_path = processed_dir / 'h7_computation_1850_2020.csv'
    output_path = processed_dir / 'h7_composite_1810_2020.csv'

    print("=" * 70)
    print("H7 Composite Index Construction")
    print("=" * 70)
    print()

    # Load all components
    print("Loading processed components...")

    try:
        energy = pd.read_csv(energy_path)
        print(f"  ✅ Energy: {len(energy)} years ({energy['year'].min()}-{energy['year'].max()})")
    except:
        print(f"  ❌ Energy: File not found or error")
        sys.exit(1)

    try:
        tech = pd.read_csv(tech_path)
        print(f"  ✅ Technology: {len(tech)} years ({tech['year'].min()}-{tech['year'].max()})")
    except:
        print(f"  ❌ Technology: File not found or error")
        sys.exit(1)

    try:
        institutions = pd.read_csv(institutions_path)
        print(f"  ✅ Institutions: {len(institutions)} years ({institutions['year'].min()}-{institutions['year'].max()})")
    except:
        print(f"  ❌ Institutions: File not found or error")
        sys.exit(1)

    try:
        computation = pd.read_csv(computation_path)
        print(f"  ✅ Computation: {len(computation)} years ({computation['year'].min()}-{computation['year'].max()})")
    except:
        print(f"  ❌ Computation: File not found or error")
        sys.exit(1)

    print()

    # Define component weights (without Knowledge component)
    weights = {
        'energy': 0.37,        # 37% (was 35%)
        'tech': 0.32,          # 32% (was 30%)
        'institutions': 0.21,  # 21% (was 20%)
        'computation': 0.10    # 10% (unchanged)
    }

    print("Component weights:")
    for component, weight in weights.items():
        print(f"  {component.capitalize()}: {weight*100:.0f}%")
    print(f"  Total: {sum(weights.values())*100:.0f}%")
    print()

    # Prepare dataframes with consistent column names
    energy_df = energy[['year', 'h7_energy_component']].copy()
    tech_df = tech[['year', 'h7_tech_component']].copy()
    institutions_df = institutions[['year', 'h7_institutions_component']].copy()
    computation_df = computation[['year', 'h7_computation_component']].copy()

    # Merge all components (outer join to preserve all years)
    print("Merging components...")
    h7_df = energy_df.merge(tech_df, on='year', how='outer')
    h7_df = h7_df.merge(institutions_df, on='year', how='outer')
    h7_df = h7_df.merge(computation_df, on='year', how='outer')

    h7_df = h7_df.sort_values('year').reset_index(drop=True)

    print(f"  Merged dataframe: {len(h7_df)} years ({h7_df['year'].min():.0f}-{h7_df['year'].max():.0f})")
    print()

    # Check data coverage
    print("Data coverage by component:")
    print(f"  Energy: {energy_df['h7_energy_component'].notna().sum()} years")
    print(f"  Technology: {tech_df['h7_tech_component'].notna().sum()} years")
    print(f"  Institutions: {institutions_df['h7_institutions_component'].notna().sum()} years")
    print(f"  Computation: {computation_df['h7_computation_component'].notna().sum()} years")
    print()

    # Handle missing data
    print("Handling missing data...")
    original_na_count = h7_df.isna().sum().sum()

    # Strategy: Linear interpolation, then forward-fill, then backward-fill
    for col in ['h7_energy_component', 'h7_tech_component',
                'h7_institutions_component', 'h7_computation_component']:
        na_before = h7_df[col].isna().sum()
        if na_before > 0:
            # First try interpolation
            h7_df[col] = h7_df[col].interpolate(method='linear', limit_direction='both')
            # Then forward-fill
            h7_df[col] = h7_df[col].fillna(method='ffill')
            # Then backward-fill
            h7_df[col] = h7_df[col].fillna(method='bfill')

            na_after = h7_df[col].isna().sum()
            print(f"  {col}: {na_before} missing → {na_after} missing (filled {na_before - na_after})")

    remaining_na = h7_df.isna().sum().sum()
    print(f"  Total NaN values: {original_na_count} → {remaining_na}")
    print()

    # Compute weighted H7 composite
    print("Computing weighted H7 composite...")
    h7_df['h7_composite'] = (
        weights['energy'] * h7_df['h7_energy_component'] +
        weights['tech'] * h7_df['h7_tech_component'] +
        weights['institutions'] * h7_df['h7_institutions_component'] +
        weights['computation'] * h7_df['h7_computation_component']
    )

    # Check for any remaining NaN in composite
    composite_na = h7_df['h7_composite'].isna().sum()
    if composite_na > 0:
        print(f"  ⚠️  Warning: {composite_na} NaN values in composite!")
    else:
        print(f"  ✅ No NaN values in composite")

    # Verify normalization (composite should be 0-1)
    comp_min = h7_df['h7_composite'].min()
    comp_max = h7_df['h7_composite'].max()
    print(f"  Composite range: {comp_min:.6f} to {comp_max:.6f}")

    if comp_min < 0 or comp_max > 1:
        print(f"  ⚠️  Warning: Composite outside [0, 1] range!")
    else:
        print(f"  ✅ Composite within [0, 1] range")
    print()

    # Filter to target period (1810-2020)
    print("Filtering to 1810-2020 period...")
    h7_final = h7_df[(h7_df['year'] >= 1810) & (h7_df['year'] <= 2020)].copy()
    print(f"  Final dataset: {len(h7_final)} years")
    print()

    # Save composite
    print(f"Saving H7 composite to {output_path}...")
    h7_final.to_csv(output_path, index=False)
    print(f"  File size: {output_path.stat().st_size / 1024:.1f} KB")
    print()

    # Display summary statistics
    print("H7 Composite Summary Statistics:")
    print("=" * 70)
    print(h7_final['h7_composite'].describe())
    print()

    # Display sample data
    print("Sample of H7 composite data:")
    print("=" * 70)

    # Show first 5 years
    print("\nFirst 5 years:")
    display_cols = ['year', 'h7_energy_component', 'h7_tech_component',
                    'h7_institutions_component', 'h7_computation_component', 'h7_composite']
    print(h7_final[display_cols].head().to_string(index=False))

    # Show last 5 years
    print("\nLast 5 years:")
    print(h7_final[display_cols].tail().to_string(index=False))

    # Show key historical years
    key_years = [1810, 1850, 1900, 1950, 2000, 2020]
    print("\nKey historical years:")
    for year in key_years:
        row = h7_final[h7_final['year'] == year]
        if not row.empty:
            h7_val = row['h7_composite'].values[0]
            print(f"  {year}: H7 = {h7_val:.6f}")

    # Calculate growth rates
    print("\nGrowth analysis:")
    h7_1810 = h7_final[h7_final['year'] == 1810]['h7_composite'].values[0]
    h7_2020 = h7_final[h7_final['year'] == 2020]['h7_composite'].values[0]
    h7_growth = h7_2020 / h7_1810 if h7_1810 > 0 else float('inf')
    years_span = 2020 - 1810

    print(f"  1810 baseline: {h7_1810:.6f}")
    print(f"  2020 final: {h7_2020:.6f}")
    print(f"  Total growth: {h7_growth:.2f}x over {years_span} years")
    if h7_1810 > 0:
        cagr = ((h7_2020 / h7_1810) ** (1 / years_span) - 1) * 100
        print(f"  CAGR: {cagr:.3f}% per year")

    print()
    print("=" * 70)
    print("✅ H7 COMPOSITE CONSTRUCTION COMPLETE")
    print(f"✅ Output: {output_path}")
    print(f"✅ Coverage: {len(h7_final)} years (1810-2020)")
    print(f"✅ All 4 components integrated with weights:")
    print(f"   Energy (37%) + Tech (32%) + Institutions (21%) + Computation (10%)")
    print("=" * 70)

    return h7_final

if __name__ == '__main__':
    try:
        result = compute_h7_composite()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
