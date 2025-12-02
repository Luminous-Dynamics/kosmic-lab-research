#!/usr/bin/env python3
"""
Process data for A₂ (Interconnection Quality) - Information Networks.

A₂ components:
- Media Freedom: v2x_freexp_altinf (freedom of expression + alternative info)
- Information Pluralism: v2xme_altinf (alternative information sources)
- Educational Equality: v2peedueq (equal access to education = information literacy)
- [Internet Equality: To be added from ITU data]

Output: interconnection_quality_vdem_1789_2024.csv
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

# Select relevant columns for A₂
interconnection_vars = [
    'country_name',
    'country_text_id',
    'year',
    'v2x_freexp_altinf',   # Freedom of expression + alternative sources index
    'v2x_freexp',          # Freedom of expression index (backup)
    'v2xme_altinf',        # Alternative information index (media pluralism)
    'v2peedueq',           # Educational equality (information literacy proxy)
]

# Check which columns exist
existing_cols = [col for col in interconnection_vars if col in vdem.columns]
missing_cols = [col for col in interconnection_vars if col not in vdem.columns]

print(f"\nFound {len(existing_cols)}/{len(interconnection_vars)} expected columns")
if missing_cols:
    print(f"⚠️  Missing columns: {missing_cols}")

# Extract interconnection subset
interconn_data = vdem[existing_cols].copy()

# Compute composite A₂ (Interconnection Quality)
# Formula: A₂ = 0.40×media_freedom + 0.30×information_pluralism + 0.30×educational_equality
# (Internet equality to be added later from ITU data for 2000-2024 period)

print("\n=== Computing A₂ components ===")

# Component 1: Media Freedom (40% weight)
# v2x_freexp_altinf combines freedom of expression + alternative information
interconn_data['media_freedom'] = interconn_data['v2x_freexp_altinf']

# Component 2: Information Pluralism (30% weight)
# v2xme_altinf measures diversity of information sources
interconn_data['information_pluralism'] = interconn_data['v2xme_altinf']

# Component 3: Educational Equality (30% weight)
# v2peedueq measures equal access to education (proxy for information literacy)
interconn_data['educational_equality'] = interconn_data['v2peedueq']

# Compute preliminary A₂ (before adding ITU internet equality data)
interconn_data['a2_preliminary'] = (
    interconn_data['media_freedom'] * 0.40 +
    interconn_data['information_pluralism'] * 0.30 +
    interconn_data['educational_equality'] * 0.30
)

# Create output directory
output_dir = '/srv/luminous-dynamics/kosmic-lab/historical_k/data_sources/processed'
os.makedirs(output_dir, exist_ok=True)

# Save processed data
output_path = os.path.join(output_dir, 'interconnection_quality_vdem_1789_2024.csv')
interconn_data.to_csv(output_path, index=False)
print(f"\n✅ Saved to: {output_path}")

# Summary statistics
print("\n=== A₂ Preliminary Summary ===")
print(interconn_data['a2_preliminary'].describe())

print(f"\nGlobal mean by decade:")
interconn_data['decade'] = (interconn_data['year'] // 10) * 10
decade_means = interconn_data.groupby('decade')['a2_preliminary'].mean()
print(decade_means.tail(15))

# Compare to K₂ for 2020 (expected Gap₂ ≈ 0.35-0.39)
recent = interconn_data[interconn_data['year'] == 2020]
if len(recent) > 0:
    a2_2020 = recent['a2_preliminary'].mean()
    k2_2020 = 0.917  # From K(t) data (H2 Interconnection capacity)
    gap = k2_2020 - a2_2020
    ratio = a2_2020 / k2_2020 if k2_2020 > 0 else 0

    print(f"\n=== 2020 Validation ===")
    print(f"K₂ (Capacity):  {k2_2020:.3f}")
    print(f"A₂ (Quality):   {a2_2020:.3f}")
    print(f"Gap₂:           {gap:.3f} ({'✅ within expected range' if 0.30 < gap < 0.45 else '⚠️  outside expected 0.30-0.45'})")
    print(f"Ratio (A/K):    {ratio:.1%}")

    print(f"\n=== Interpretation ===")
    if 0.30 < gap < 0.45:
        print(f"✅ Gap₂ = {gap:.1%} suggests moderate quality gap in information networks")
        print(f"   - We have infrastructure (K₂ = {k2_2020:.2f})")
        print(f"   - But information quality lags (A₂ = {a2_2020:.2f})")
        print(f"   - {gap:.0%} of interconnection capacity unutilized!")
    else:
        print(f"⚠️  Gap₂ = {gap:.1%} outside expected range - review formula or data")

# Distribution analysis
print(f"\n=== Distribution Analysis ===")
print(f"Countries with A₂ > 0.7 in 2020: {len(recent[recent['a2_preliminary'] > 0.7])}")
print(f"Countries with A₂ < 0.3 in 2020: {len(recent[recent['a2_preliminary'] < 0.3])}")

# Top 10 and bottom 10 in 2020
if len(recent) > 0:
    top10 = recent.nlargest(10, 'a2_preliminary')[['country_name', 'a2_preliminary', 'media_freedom', 'information_pluralism', 'educational_equality']]
    bottom10 = recent.nsmallest(10, 'a2_preliminary')[['country_name', 'a2_preliminary', 'media_freedom', 'information_pluralism', 'educational_equality']]

    print("\nTop 10 countries (2020):")
    for idx, row in top10.iterrows():
        print(f"  {row['country_name']}: {row['a2_preliminary']:.3f} (media: {row['media_freedom']:.2f}, plural: {row['information_pluralism']:.2f}, edu_eq: {row['educational_equality']:.2f})")

    print("\nBottom 10 countries (2020):")
    for idx, row in bottom10.iterrows():
        print(f"  {row['country_name']}: {row['a2_preliminary']:.3f} (media: {row['media_freedom']:.2f}, plural: {row['information_pluralism']:.2f}, edu_eq: {row['educational_equality']:.2f})")

# Historical trend analysis
print("\n=== Historical Trend Analysis ===")
historical_years = [1810, 1850, 1900, 1950, 1980, 2000, 2020]
for year in historical_years:
    year_data = interconn_data[interconn_data['year'] == year]
    if len(year_data) > 0:
        mean_val = year_data['a2_preliminary'].mean()
        n_countries = len(year_data)
        print(f"{year}: A₂ = {mean_val:.3f} (n={n_countries} countries)")

print("\n" + "="*60)
print("✅ A₂ (Interconnection Quality) processing complete!")
print("\nNext steps:")
print("1. Add ITU internet equality data for 2000-2024 period")
print("2. Compare A₂ vs K₂ trends over time")
print("3. Proceed to A₃ (Reciprocity Quality)")
print("="*60)
