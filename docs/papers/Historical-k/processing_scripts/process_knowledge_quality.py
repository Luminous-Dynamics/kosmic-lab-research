#!/usr/bin/env python3
"""
Process data for A₅ (Knowledge Quality) - Epistemic Infrastructure.

A₅ components:
- Rule of Law: v2xcl_rol (institutional knowledge reliability)
- Legislative Constraints: v2xlg_legcon (checks on power = knowledge integrity)
- Judicial Independence: v2x_jucon (fair knowledge adjudication)
- [Education Quality: To be added from UNESCO data]
- [Research Capacity: To be added from patent/R&D data]

Output: knowledge_quality_vdem_1789_2024.csv
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

# Select relevant columns for A₅
knowledge_vars = [
    'country_name',
    'country_text_id',
    'year',
    'v2xcl_rol',         # Rule of law index
    'v2xlg_legcon',      # Legislative constraints on executive
    'v2x_jucon',         # Judicial constraints on executive
    'v2x_liberal',       # Liberal component (backup)
]

# Check which columns exist
existing_cols = [col for col in knowledge_vars if col in vdem.columns]
missing_cols = [col for col in knowledge_vars if col not in vdem.columns]

print(f"\nFound {len(existing_cols)}/{len(knowledge_vars)} expected columns")
if missing_cols:
    print(f"⚠️  Missing columns: {missing_cols}")

# Extract knowledge subset
knowledge_data = vdem[existing_cols].copy()

# Compute composite A₅ (Knowledge Quality)
# Formula: A₅ = 0.40×rule_of_law + 0.35×legislative_checks + 0.25×judicial_independence
# (Education quality and R&D capacity to be added later)

print("\n=== Computing A₅ components ===")

# Component 1: Rule of Law (40% weight)
# v2xcl_rol measures transparent laws, impartial enforcement (knowledge reliability)
knowledge_data['rule_of_law'] = knowledge_data['v2xcl_rol']

# Component 2: Legislative Constraints (35% weight)
# v2xlg_legcon measures institutional checks (prevents knowledge corruption)
knowledge_data['legislative_checks'] = knowledge_data['v2xlg_legcon']

# Component 3: Judicial Independence (25% weight)
# v2x_jucon measures independent judiciary (fair knowledge adjudication)
knowledge_data['judicial_independence'] = knowledge_data['v2x_jucon']

# Compute preliminary A₅ (before adding education and R&D data)
knowledge_data['a5_preliminary'] = (
    knowledge_data['rule_of_law'] * 0.40 +
    knowledge_data['legislative_checks'] * 0.35 +
    knowledge_data['judicial_independence'] * 0.25
)

# Create output directory
output_dir = '/srv/luminous-dynamics/kosmic-lab/historical_k/data_sources/processed'
os.makedirs(output_dir, exist_ok=True)

# Save processed data
output_path = os.path.join(output_dir, 'knowledge_quality_vdem_1789_2024.csv')
knowledge_data.to_csv(output_path, index=False)
print(f"\n✅ Saved to: {output_path}")

# Summary statistics
print("\n=== A₅ Preliminary Summary ===")
print(knowledge_data['a5_preliminary'].describe())

print(f"\nGlobal mean by decade:")
knowledge_data['decade'] = (knowledge_data['year'] // 10) * 10
decade_means = knowledge_data.groupby('decade')['a5_preliminary'].mean()
print(decade_means.tail(15))

# Compare to K₅ for 2020 (expected Gap₅ ≈ 0.30-0.35)
recent = knowledge_data[knowledge_data['year'] == 2020]
if len(recent) > 0:
    a5_2020 = recent['a5_preliminary'].mean()
    k5_2020 = 0.923  # From K(t) data (H5 Knowledge capacity)
    gap = k5_2020 - a5_2020
    ratio = a5_2020 / k5_2020 if k5_2020 > 0 else 0

    print(f"\n=== 2020 Validation ===")
    print(f"K₅ (Capacity):  {k5_2020:.3f}")
    print(f"A₅ (Quality):   {a5_2020:.3f}")
    print(f"Gap₅:           {gap:.3f} ({'✅ within expected range' if 0.25 < gap < 0.40 else '⚠️  outside expected 0.25-0.40'})")
    print(f"Ratio (A/K):    {ratio:.1%}")

    print(f"\n=== Interpretation ===")
    if 0.25 < gap < 0.40:
        print(f"✅ Gap₅ = {gap:.1%} suggests moderate quality gap in knowledge systems")
        print(f"   - We have knowledge capacity (K₅ = {k5_2020:.2f})")
        print(f"   - But knowledge quality lags (A₅ = {a5_2020:.2f})")
        print(f"   - {gap:.0%} of knowledge capacity unutilized!")
    else:
        print(f"⚠️  Gap₅ = {gap:.1%} outside expected range - review formula or data")

# Distribution analysis
print(f"\n=== Distribution Analysis ===")
print(f"Countries with A₅ > 0.8 in 2020: {len(recent[recent['a5_preliminary'] > 0.8])}")
print(f"Countries with A₅ < 0.3 in 2020: {len(recent[recent['a5_preliminary'] < 0.3])}")

# Top 10 and bottom 10 in 2020
if len(recent) > 0:
    top10 = recent.nlargest(10, 'a5_preliminary')[['country_name', 'a5_preliminary', 'rule_of_law', 'legislative_checks', 'judicial_independence']]
    bottom10 = recent.nsmallest(10, 'a5_preliminary')[['country_name', 'a5_preliminary', 'rule_of_law', 'legislative_checks', 'judicial_independence']]

    print("\nTop 10 countries (2020):")
    for idx, row in top10.iterrows():
        print(f"  {row['country_name']}: {row['a5_preliminary']:.3f} (rol: {row['rule_of_law']:.2f}, leg: {row['legislative_checks']:.2f}, jud: {row['judicial_independence']:.2f})")

    print("\nBottom 10 countries (2020):")
    for idx, row in bottom10.iterrows():
        print(f"  {row['country_name']}: {row['a5_preliminary']:.3f} (rol: {row['rule_of_law']:.2f}, leg: {row['legislative_checks']:.2f}, jud: {row['judicial_independence']:.2f})")

# Historical trend analysis
print("\n=== Historical Trend Analysis ===")
historical_years = [1810, 1850, 1900, 1950, 1980, 2000, 2020]
for year in historical_years:
    year_data = knowledge_data[knowledge_data['year'] == year]
    if len(year_data) > 0:
        mean_val = year_data['a5_preliminary'].mean()
        n_countries = len(year_data)
        print(f"{year}: A₅ = {mean_val:.3f} (n={n_countries} countries)")

print("\n" + "="*60)
print("✅ A₅ (Knowledge Quality) processing complete!")
print("\nNext steps:")
print("1. Add UNESCO education quality data (1970-2024)")
print("2. Add patent/R&D data for research capacity (1960-2024)")
print("3. Compare A₅ vs K₅ trends over time")
print("4. Compute provisional A(t) = geometric_mean(A₁, A₂, A₃, A₅)")
print("="*60)
