#!/usr/bin/env python3
"""
Compute Final K(t) Index - Collective Human Capital 1810-2020

Merges all 7 harmonies of the K-Index:
H1: Resonant Coherence (Governance)
H2: Universal Interconnectedness (Financial Integration)
H3: Sacred Reciprocity (Cooperation)
H4: Infinite Play (Economic Complexity)
H5: Integral Wisdom (Education)
H6: Pan-Sentient Flourishing (Wellbeing)
H7: Evolutionary Progression (Technology)

**Path C Update (2025-11-27)**: Default changed to geometric mean aggregation
to enforce non-substitutability across harmonies (weakest link coordination).

Output: data_sources/processed/k_index_final_1810_2020.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
from aggregation_methods import compute_k_geometric, compute_k_arithmetic

def load_harmony_datasets():
    """Load all 7 harmony component datasets."""

    print("=" * 70)
    print("Loading All 7 Harmony Components")
    print("=" * 70)
    print()

    script_dir = Path(__file__).parent
    data_dir = script_dir / 'data_sources'

    # Define harmony paths (using actual filenames and locations)
    harmonies = {
        'h1': data_dir / 'h1_governance' / 'governance_coherence_1810_2020.csv',
        'h2': data_dir / 'h2_interconnection' / 'financial_integration_1810_2020.csv',
        'h3': data_dir / 'h3_reciprocity' / 'reciprocity_1810_2020.csv',
        'h4': data_dir / 'h4_complexity' / 'economic_complexity_1810_2020.csv',
        'h5': data_dir / 'h5_knowledge' / 'barro_lee_custom_1810_2020.csv',
        'h6': data_dir / 'h6_wellbeing' / 'wellbeing_1810_2020.csv',
        'h7': data_dir / 'processed' / 'h7_composite_1810_2020.csv',
    }

    # Expected component column names for each harmony
    harmony_columns = {
        'h1': 'h1_governance_component',
        'h2': 'h2_interconnection_component',
        'h3': 'h3_reciprocity_component',
        'h4': 'h4_complexity_component',
        'h5': 'h5_knowledge_component',
        'h6': 'h6_wellbeing_component',
        'h7': 'h7_composite',
    }

    # Load each harmony
    harmony_data = {}

    for h_name, h_path in harmonies.items():
        print(f"Loading {h_name.upper()}: {h_path.name}")

        if not h_path.exists():
            raise FileNotFoundError(f"Missing harmony dataset: {h_path}")

        df = pd.read_csv(h_path)

        # Get expected component column name
        expected_col = harmony_columns[h_name]

        # Verify the column exists
        if expected_col not in df.columns:
            raise ValueError(f"{h_name} missing expected column '{expected_col}'. Available columns: {list(df.columns)}")

        # Extract year and component
        harmony_data[h_name] = df[['year', expected_col]].rename(columns={expected_col: h_name})

        # Validate year range
        years = harmony_data[h_name]['year']
        if years.min() != 1810 or years.max() != 2020 or len(years) != 211:
            raise ValueError(f"{h_name} has unexpected year range: {years.min()}-{years.max()}, {len(years)} years")

        # Validate normalization
        component_values = harmony_data[h_name][h_name]
        if component_values.min() < 0 or component_values.max() > 1:
            raise ValueError(f"{h_name} not normalized: range [{component_values.min():.4f}, {component_values.max():.4f}]")

        print(f"  ✅ Loaded: {len(years)} years, range [{component_values.min():.4f}, {component_values.max():.4f}]")

    print()
    return harmony_data

def merge_harmonies(harmony_data):
    """Merge all harmonies into single dataframe."""

    print("=" * 70)
    print("Merging All Harmonies")
    print("=" * 70)
    print()

    # Start with H1
    df = harmony_data['h1'].copy()

    # Merge remaining harmonies
    for h_name in ['h2', 'h3', 'h4', 'h5', 'h6', 'h7']:
        df = df.merge(harmony_data[h_name], on='year', how='outer', validate='one_to_one')

    # Verify no missing data
    if df.isnull().any().any():
        print("⚠️  WARNING: Missing data detected!")
        print(df.isnull().sum())
        raise ValueError("Merged data contains NaN values")

    print(f"✅ Merged dataframe: {len(df)} years × {len(df.columns)} columns")
    print(f"   Columns: {list(df.columns)}")
    print()

    return df

def compute_k_index(df, weights=None, method='geometric'):
    """
    Compute K(t) index from all 7 harmonies using specified aggregation method.

    **Path C Update (2025-11-27)**: Default changed to geometric mean to enforce
    non-substitutability across harmonies (weakest link coordination).

    Args:
        df: DataFrame with harmony columns (h1-h7)
        weights: Optional dict of harmony weights (must sum to 1.0)
        method: 'geometric' (default, Path C) or 'arithmetic' (original)

    Returns:
        DataFrame with added 'k_index' column
    """

    print("=" * 70)
    print("Computing K(t) Index")
    print("=" * 70)
    print()

    # Equal weights by default
    if weights is None:
        weights = {
            'h1': 1/7,  # Resonant Coherence
            'h2': 1/7,  # Universal Interconnectedness
            'h3': 1/7,  # Sacred Reciprocity
            'h4': 1/7,  # Infinite Play
            'h5': 1/7,  # Integral Wisdom
            'h6': 1/7,  # Pan-Sentient Flourishing
            'h7': 1/7,  # Evolutionary Progression
        }

    # Verify weights sum to 1
    total_weight = sum(weights.values())
    if not np.isclose(total_weight, 1.0):
        raise ValueError(f"Weights must sum to 1.0, got {total_weight}")

    print("Harmony Weights:")
    for h_name, weight in weights.items():
        print(f"  {h_name.upper()}: {weight:.4f} ({weight*100:.2f}%)")
    print()

    print(f"Aggregation Method: {method.upper()}")
    print()

    # Extract harmony columns for aggregation
    harmony_cols = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7']
    harmony_frame = df[harmony_cols].copy()

    # Compute K(t) using specified method
    if method.lower() == 'geometric':
        k_series = compute_k_geometric(harmony_frame, weights)
        print("  ✓ Using geometric mean (enforces non-substitutability)")
    elif method.lower() == 'arithmetic':
        k_series = compute_k_arithmetic(harmony_frame, weights)
        print("  ✓ Using arithmetic mean (original method)")
    else:
        raise ValueError(f"Unknown method '{method}'. Use 'geometric' or 'arithmetic'.")

    df['k_index'] = k_series.values

    # Validate K(t) normalization
    k_min = df['k_index'].min()
    k_max = df['k_index'].max()

    print(f"K(t) Index Range: [{k_min:.6f}, {k_max:.6f}]")

    if k_min < 0 or k_max > 1:
        print(f"  ⚠️  WARNING: K(t) outside [0, 1] range!")
    else:
        print(f"  ✅ K(t) properly normalized to [0, 1]")

    print()

    return df

def generate_statistics(df):
    """Generate comprehensive statistics for K(t) and all harmonies."""

    print("=" * 70)
    print("K(t) Index Statistics (1810-2020)")
    print("=" * 70)
    print()

    # Overall K(t) statistics
    k_1810 = df[df['year'] == 1810]['k_index'].values[0]
    k_2020 = df[df['year'] == 2020]['k_index'].values[0]
    k_growth = k_2020 / k_1810
    k_change = k_2020 - k_1810

    print(f"K(t) Summary:")
    print(f"  1810 baseline: {k_1810:.6f}")
    print(f"  2020 final:    {k_2020:.6f}")
    print(f"  Absolute gain: {k_change:.6f} (+{k_change/k_1810*100:.1f}%)")
    print(f"  Growth factor: {k_growth:.2f}x")
    print()

    # Compute CAGR
    years_span = 210  # 1810 to 2020
    cagr = (k_2020 / k_1810) ** (1 / years_span) - 1
    print(f"  CAGR (1810-2020): {cagr*100:.3f}% per year")
    print()

    # Individual harmony growth
    print("Individual Harmony Growth (1810-2020):")
    print("-" * 70)

    harmonies = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7']
    harmony_names = {
        'h1': 'Resonant Coherence',
        'h2': 'Universal Interconnectedness',
        'h3': 'Sacred Reciprocity',
        'h4': 'Infinite Play',
        'h5': 'Integral Wisdom',
        'h6': 'Pan-Sentient Flourishing',
        'h7': 'Evolutionary Progression',
    }

    growth_data = []

    for h in harmonies:
        h_1810 = df[df['year'] == 1810][h].values[0]
        h_2020 = df[df['year'] == 2020][h].values[0]
        h_growth = h_2020 / h_1810
        h_change = h_2020 - h_1810

        print(f"{h.upper()} ({harmony_names[h]}):")
        print(f"  {h_1810:.4f} → {h_2020:.4f} = {h_growth:.2f}x growth")

        growth_data.append({
            'harmony': h.upper(),
            'name': harmony_names[h],
            'growth': h_growth,
            'value_1810': h_1810,
            'value_2020': h_2020,
        })

    print()

    # Rank harmonies by growth
    growth_df = pd.DataFrame(growth_data).sort_values('growth', ascending=False)

    print("Harmonies Ranked by Growth:")
    print("-" * 70)
    for idx, row in growth_df.iterrows():
        print(f"  {row['harmony']}: {row['growth']:.2f}x - {row['name']}")

    print()

    # Historical periods
    print("K(t) by Historical Period:")
    print("-" * 70)

    periods = [
        (1810, 1870, "Pre-industrial era"),
        (1870, 1914, "First globalization"),
        (1914, 1945, "World wars / deglobalization"),
        (1945, 1980, "Post-war golden age"),
        (1980, 2000, "Late 20th century"),
        (2000, 2020, "21st century"),
    ]

    for start, end, label in periods:
        period_df = df[(df['year'] >= start) & (df['year'] <= end)]
        k_start = period_df[period_df['year'] == start]['k_index'].values[0]
        k_end = period_df[period_df['year'] == end]['k_index'].values[0]
        k_gain = k_end - k_start
        years = end - start
        annual_gain = (k_gain / years) * 100

        print(f"{label} ({start}-{end}):")
        print(f"  K(t): {k_start:.4f} → {k_end:.4f}")
        print(f"  Gain: +{k_gain:.4f} ({annual_gain:.3f}% per year)")
        print()

    return growth_df

def save_final_dataset(df):
    """Save final K(t) index dataset."""

    print("=" * 70)
    print("Saving Final K(t) Dataset")
    print("=" * 70)
    print()

    script_dir = Path(__file__).parent
    output_dir = script_dir / 'data_sources/processed'
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / 'k_index_final_1810_2020.csv'

    # Select columns to save
    output_df = df[[
        'year',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7',
        'k_index'
    ]].copy()

    # Save
    print(f"Saving to {output_path}...")
    output_df.to_csv(output_path, index=False, float_format='%.6f')

    file_size_kb = output_path.stat().st_size / 1024
    print(f"  ✅ Saved: {len(output_df)} rows × {len(output_df.columns)} columns")
    print(f"  File size: {file_size_kb:.1f} KB")
    print()

    # Display sample
    print("Sample of final K(t) dataset:")
    print("=" * 70)
    print()

    print("First 5 years:")
    print(output_df.head().to_string(index=False))
    print()

    print("Last 5 years:")
    print(output_df.tail().to_string(index=False))
    print()

    return output_path

def main():
    """Main computation pipeline."""

    print()
    print("=" * 70)
    print("FINAL K(t) INDEX COMPUTATION")
    print("Collective Human Capital Index (1810-2020)")
    print("=" * 70)
    print()

    try:
        # Step 1: Load all harmonies
        harmony_data = load_harmony_datasets()

        # Step 2: Merge into single dataframe
        df = merge_harmonies(harmony_data)

        # Step 3: Compute K(t) index
        df = compute_k_index(df)

        # Step 4: Generate statistics
        growth_df = generate_statistics(df)

        # Step 5: Save final dataset
        output_path = save_final_dataset(df)

        # Final summary
        print("=" * 70)
        print("✅ K(t) INDEX COMPUTATION COMPLETE!")
        print("=" * 70)
        print()
        print(f"📊 Output: {output_path}")
        print(f"📈 Coverage: {len(df)} years (1810-2020)")
        print(f"🎯 K(t) Range: [{df['k_index'].min():.6f}, {df['k_index'].max():.6f}]")

        k_1810 = df[df['year'] == 1810]['k_index'].values[0]
        k_2020 = df[df['year'] == 2020]['k_index'].values[0]
        k_growth = k_2020 / k_1810

        print(f"🚀 Total Growth: {k_growth:.2f}x (1810-2020)")
        print()
        print("Next steps:")
        print("  1. Create visualizations (K(t) trajectory + harmonies)")
        print("  2. Update manuscript Methods section")
        print("  3. Draft manuscript Results section")
        print()
        print("=" * 70)

        return df

    except Exception as e:
        print()
        print("=" * 70)
        print("❌ ERROR DURING K(t) COMPUTATION")
        print("=" * 70)
        print()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)

if __name__ == '__main__':
    result = main()
    import sys
    sys.exit(0)
