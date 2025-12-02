#!/usr/bin/env python3
"""
Process data for A₃ (Reciprocity Quality) - Generative Exchange & Trust.

A₃ components:
- Civil Society Participation: v2x_cspart (collective action capacity)
- Equal Distribution of Resources: v2xeg_eqdr (economic reciprocity proxy)
- [Economic Equality: To be added from Gini coefficient data]
- [Generalized Trust: To be added from WVS data]

Output: reciprocity_quality_vdem_1789_2024.csv
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

# Select relevant columns for A₃
reciprocity_vars = [
    'country_name',
    'country_text_id',
    'year',
    'v2x_cspart',        # Civil society participation index
    'v2xeg_eqdr',        # Equal distribution of resources
    'v2x_egal',          # Egalitarian component (backup)
]

# Check which columns exist
existing_cols = [col for col in reciprocity_vars if col in vdem.columns]
missing_cols = [col for col in reciprocity_vars if col not in vdem.columns]

print(f"\nFound {len(existing_cols)}/{len(reciprocity_vars)} expected columns")
if missing_cols:
    print(f"⚠️  Missing columns: {missing_cols}")

# Extract reciprocity subset
recip_data = vdem[existing_cols].copy()

# Compute composite A₃ (Reciprocity Quality)
# Formula: A₃ = 0.50×civil_society + 0.50×resource_equality
# (Economic equality via Gini and trust via WVS to be added later)

print("\n=== Computing A₃ components ===")

# Component 1: Civil Society Participation (50% weight)
# v2x_cspart measures engagement in collective organizations
recip_data['civil_society'] = recip_data['v2x_cspart']

# Component 2: Resource Equality (50% weight)
# v2xeg_eqdr measures equal distribution of resources
recip_data['resource_equality'] = recip_data['v2xeg_eqdr']

# Compute preliminary A₃ (before adding Gini and trust data)
recip_data['a3_preliminary'] = (
    recip_data['civil_society'] * 0.50 +
    recip_data['resource_equality'] * 0.50
)

# Create output directory
output_dir = '/srv/luminous-dynamics/kosmic-lab/historical_k/data_sources/processed'
os.makedirs(output_dir, exist_ok=True)

# Save processed data
output_path = os.path.join(output_dir, 'reciprocity_quality_vdem_1789_2024.csv')
recip_data.to_csv(output_path, index=False)
print(f"\n✅ Saved to: {output_path}")

# Summary statistics
print("\n=== A₃ Preliminary Summary ===")
print(recip_data['a3_preliminary'].describe())

print(f"\nGlobal mean by decade:")
recip_data['decade'] = (recip_data['year'] // 10) * 10
decade_means = recip_data.groupby('decade')['a3_preliminary'].mean()
print(decade_means.tail(15))

# Compare to K₃ for 2020 (expected Gap₃ ≈ 0.40-0.45)
recent = recip_data[recip_data['year'] == 2020]
if len(recent) > 0:
    a3_2020 = recent['a3_preliminary'].mean()
    k3_2020 = 0.892  # From K(t) data (H3 Reciprocity capacity)
    gap = k3_2020 - a3_2020
    ratio = a3_2020 / k3_2020 if k3_2020 > 0 else 0

    print(f"\n=== 2020 Validation ===")
    print(f"K₃ (Capacity):  {k3_2020:.3f}")
    print(f"A₃ (Quality):   {a3_2020:.3f}")
    print(f"Gap₃:           {gap:.3f} ({'✅ within expected range' if 0.35 < gap < 0.50 else '⚠️  outside expected 0.35-0.50'})")
    print(f"Ratio (A/K):    {ratio:.1%}")

    print(f"\n=== Interpretation ===")
    if 0.35 < gap < 0.50:
        print(f"✅ Gap₃ = {gap:.1%} suggests moderate quality gap in reciprocity")
        print(f"   - We have capacity for exchange (K₃ = {k3_2020:.2f})")
        print(f"   - But reciprocity quality lags (A₃ = {a3_2020:.2f})")
        print(f"   - {gap:.0%} of reciprocity capacity unutilized!")
    else:
        print(f"⚠️  Gap₃ = {gap:.1%} outside expected range - review formula or data")

# Distribution analysis
print(f"\n=== Distribution Analysis ===")
print(f"Countries with A₃ > 0.7 in 2020: {len(recent[recent['a3_preliminary'] > 0.7])}")
print(f"Countries with A₃ < 0.3 in 2020: {len(recent[recent['a3_preliminary'] < 0.3])}")

# Top 10 and bottom 10 in 2020
if len(recent) > 0:
    top10 = recent.nlargest(10, 'a3_preliminary')[['country_name', 'a3_preliminary', 'civil_society', 'resource_equality']]
    bottom10 = recent.nsmallest(10, 'a3_preliminary')[['country_name', 'a3_preliminary', 'civil_society', 'resource_equality']]

    print("\nTop 10 countries (2020):")
    for idx, row in top10.iterrows():
        print(f"  {row['country_name']}: {row['a3_preliminary']:.3f} (civil_soc: {row['civil_society']:.2f}, res_eq: {row['resource_equality']:.2f})")

    print("\nBottom 10 countries (2020):")
    for idx, row in bottom10.iterrows():
        print(f"  {row['country_name']}: {row['a3_preliminary']:.3f} (civil_soc: {row['civil_society']:.2f}, res_eq: {row['resource_equality']:.2f})")

# Historical trend analysis
print("\n=== Historical Trend Analysis ===")
historical_years = [1810, 1850, 1900, 1950, 1980, 2000, 2020]
for year in historical_years:
    year_data = recip_data[recip_data['year'] == year]
    if len(year_data) > 0:
        mean_val = year_data['a3_preliminary'].mean()
        n_countries = len(year_data)
        print(f"{year}: A₃ = {mean_val:.3f} (n={n_countries} countries)")

print("\n" + "="*60)
print("✅ A₃ (Reciprocity Quality) processing complete!")
print("\nNext steps:")
print("1. Add Gini coefficient data for economic equality (1960-2023)")
print("2. Add WVS trust data for generalized trust (1981-2022)")
print("3. Compare A₃ vs K₃ trends over time")
print("4. Proceed to A₅ (Knowledge Quality)")
print("="*60)
