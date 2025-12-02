#!/usr/bin/env python3
"""
Process V-Dem data for A₁ (Governance Quality) proxy.

A₁ components:
- Policy Effectiveness: v2x_execorr (executive corruption inverse) + v2xlg_legcon (legislative constraints)
- Democratic Quality: v2x_libdem (liberal democracy) + v2x_delibdem (deliberative)
- Institutional Trust: (from WVS, merge later)

Output: governance_quality_vdem_1789_2024.csv
"""
import pandas as pd
import numpy as np
import os

# Load V-Dem data
print("Loading V-Dem v15 data...")
data_path = '/srv/luminous-dynamics/kosmic-lab/historical_k/data_sources/external/vdem/V-Dem-CY-Core-v15.csv'
vdem = pd.read_csv(data_path)

print(f"Loaded {len(vdem):,} country-year observations")
print(f"Year range: {vdem['year'].min()} - {vdem['year'].max()}")
print(f"Countries: {vdem['country_name'].nunique()}")

# Select relevant columns for A₁
governance_vars = [
    'country_name',
    'country_text_id',
    'year',
    'v2x_libdem',      # Liberal democracy (institutions + rights)
    'v2x_polyarchy',   # Electoral democracy
    'v2x_partipdem',   # Participatory democracy
    'v2x_delibdem',    # Deliberative democracy (quality of process)
    'v2x_egaldem',     # Egalitarian democracy (equal protection)
    'v2x_execorr',     # Executive corruption (inverse for quality)
    'v2xlg_legcon'     # Legislative constraints on executive
]

# Check which columns exist
existing_cols = [col for col in governance_vars if col in vdem.columns]
missing_cols = [col for col in governance_vars if col not in vdem.columns]

print(f"\nFound {len(existing_cols)}/{len(governance_vars)} expected columns")
if missing_cols:
    print(f"⚠️  Missing columns: {missing_cols}")

# Extract governance subset
gov_data = vdem[existing_cols].copy()

# Compute composite A₁ (Governance Quality)
# Formula: A₁ = 0.3×Democratic_Quality + 0.3×Effectiveness + 0.4×Trust (WVS, added later)

print("\n=== Computing A₁ components ===")

# Component 1: Democratic Quality (40% liberal + 30% deliberative + 30% egalitarian)
gov_data['democratic_quality'] = (
    gov_data['v2x_libdem'] * 0.4 +        # Liberal institutions
    gov_data['v2x_delibdem'] * 0.3 +      # Deliberative quality
    gov_data['v2x_egaldem'] * 0.3         # Egalitarian protection
)

# Component 2: Policy Effectiveness (60% anti-corruption + 40% legislative checks)
gov_data['policy_effectiveness'] = (
    (1 - gov_data['v2x_execorr']) * 0.6 + # Corruption inverse
    gov_data['v2xlg_legcon'] * 0.4        # Legislative checks
)

# Compute preliminary A₁ (before adding WVS trust)
gov_data['a1_preliminary'] = (
    gov_data['democratic_quality'] * 0.5 +
    gov_data['policy_effectiveness'] * 0.5
)

# Create output directory
output_dir = '/srv/luminous-dynamics/kosmic-lab/historical_k/data_sources/processed'
os.makedirs(output_dir, exist_ok=True)

# Save processed data
output_path = os.path.join(output_dir, 'governance_quality_vdem_1789_2024.csv')
gov_data.to_csv(output_path, index=False)
print(f"\n✅ Saved to: {output_path}")

# Summary statistics
print("\n=== A₁ Preliminary Summary ===")
print(gov_data['a1_preliminary'].describe())

print(f"\nGlobal mean by decade:")
gov_data['decade'] = (gov_data['year'] // 10) * 10
decade_means = gov_data.groupby('decade')['a1_preliminary'].mean()
print(decade_means.tail(15))

# Compare to K₁ for 2020 (expected Gap₁ ≈ 0.27-0.33)
recent = gov_data[gov_data['year'] == 2020]
if len(recent) > 0:
    a1_2020 = recent['a1_preliminary'].mean()
    k1_2020 = 0.825  # From K(t) data (H1 Governance capacity)
    gap = k1_2020 - a1_2020
    ratio = a1_2020 / k1_2020 if k1_2020 > 0 else 0

    print(f"\n=== 2020 Validation ===")
    print(f"K₁ (Capacity):  {k1_2020:.3f}")
    print(f"A₁ (Quality):   {a1_2020:.3f}")
    print(f"Gap₁:           {gap:.3f} ({'✅ within expected range' if 0.20 < gap < 0.40 else '⚠️  outside expected 0.20-0.40'})")
    print(f"Ratio (A/K):    {ratio:.1%}")

# Distribution analysis
print(f"\n=== Distribution Analysis ===")
print(f"Countries with A₁ > 0.7 in 2020: {len(recent[recent['a1_preliminary'] > 0.7])}")
print(f"Countries with A₁ < 0.3 in 2020: {len(recent[recent['a1_preliminary'] < 0.3])}")

# Top 10 and bottom 10 in 2020
if len(recent) > 0:
    top10 = recent.nlargest(10, 'a1_preliminary')[['country_name', 'a1_preliminary']]
    bottom10 = recent.nsmallest(10, 'a1_preliminary')[['country_name', 'a1_preliminary']]

    print("\nTop 10 countries (2020):")
    for idx, row in top10.iterrows():
        print(f"  {row['country_name']}: {row['a1_preliminary']:.3f}")

    print("\nBottom 10 countries (2020):")
    for idx, row in bottom10.iterrows():
        print(f"  {row['country_name']}: {row['a1_preliminary']:.3f}")

print("\n" + "="*60)
print("✅ V-Dem processing complete!")
print("Next step: Process WVS for trust data (process_wvs.py)")
print("="*60)
