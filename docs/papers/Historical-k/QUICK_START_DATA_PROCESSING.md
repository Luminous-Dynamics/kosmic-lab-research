# Quick Start: Data Processing for A(t) Implementation

**Purpose**: Extract and inspect downloaded datasets to begin A₁ (Governance) prototype
**Time**: 30-60 minutes
**Prerequisites**: All Priority 1 datasets downloaded (✅ complete!)

---

## Step 1: Extract All ZIP Files (10 minutes)

```bash
cd /srv/luminous-dynamics/kosmic-lab/historical_k/data_sources/external

# Extract V-Dem (most critical - 15 MB)
mkdir -p vdem && unzip -q V-Dem-CY-Core-v15_csv.zip -d vdem/
echo "✅ V-Dem extracted"

# Extract World Values Survey (124 MB)
mkdir -p wvs && unzip -q F00011931-WVS_Time_Series_1981-2022_csv_v5_0.zip -d wvs/
echo "✅ WVS extracted"

# Extract Pew Global Attitudes
mkdir -p pew && unzip -q Pew-Research-Center-Global-Attitudes-Spring-2024-Survey-Public.zip -d pew/
echo "✅ Pew extracted"

# Extract Gini coefficients
mkdir -p gini && unzip -q API_SI.POV.GINI_DS2_en_csv_v2_252305.zip -d gini/
echo "✅ Gini extracted"

# Extract GPS (unknown contents)
mkdir -p gps && unzip -q GPS_Dataset.zip -d gps/
echo "✅ GPS extracted"

echo "=== All extractions complete! ==="
ls -lh */
```

---

## Step 2: Inspect V-Dem Data Structure (5 minutes)

V-Dem is the **GOLD STANDARD** for H1 (Governance). Let's understand its structure:

```bash
# List extracted files
ls -lh vdem/

# Check column names in main dataset
head -1 vdem/V-Dem-CY-Core-v15.csv | tr ',' '\n' | grep -E "(country|year|v2x_|COW)" | head -20

# Quick stats
wc -l vdem/*.csv
```

**Expected key variables**:
- `country_name`, `year` - identifiers
- `v2x_libdem` - Liberal democracy index [0-1]
- `v2x_polyarchy` - Electoral democracy index [0-1]
- `v2x_partipdem` - Participatory democracy index [0-1]
- `v2x_delibdem` - Deliberative democracy index [0-1]
- `v2x_egaldem` - Egalitarian democracy index [0-1]

**Quick verification**:
```bash
# Check year range
cut -d',' -f2 vdem/V-Dem-CY-Core-v15.csv | sort -n | uniq | head -5
cut -d',' -f2 vdem/V-Dem-CY-Core-v15.csv | sort -n | uniq | tail -5
# Should show: 1789 (or earlier) to 2023
```

---

## Step 3: Inspect WVS Data Structure (5 minutes)

WVS provides **trust and cooperation data** - critical for H1 and H3:

```bash
# List extracted files
ls -lh wvs/

# Find the main data file
find wvs/ -name "*.csv" -o -name "*.sav" | head -5

# If CSV exists, check structure
head -1 wvs/WVS_TimeSeries_1981_2022_csv_v5_0.csv | tr ';' '\n' | grep -E "(V24|V108|V109|country|year|wave)" | head -20
```

**Expected key variables**:
- `S003` - Country code
- `S020` - Year of survey
- `S002` - Wave number (1-7)
- `V24` - Most people can be trusted (1=Yes, 2=No)
- `V108-V123` - Confidence in institutions (1=Great deal ... 4=None at all)

**Quick verification**:
```bash
# Check waves available
cut -d';' -f? wvs/WVS_TimeSeries_*.csv | sort -u
# Should show waves 1-7 (1981-1984, 1989-1993, 1994-1998, 1999-2004, 2005-2009, 2010-2014, 2017-2022)
```

---

## Step 4: Create Processing Scripts Directory (2 minutes)

```bash
cd /srv/luminous-dynamics/kosmic-lab
mkdir -p historical_k/processing_scripts
cd historical_k/processing_scripts

# Create placeholder scripts
touch process_vdem.py
touch process_wvs.py
touch process_pew.py
touch process_gini.py
touch compute_a1_governance.py

echo "✅ Processing scripts directory created"
ls -lh
```

---

## Step 5: Build A₁ (Governance) Processing Script (20-30 minutes)

Create `process_vdem.py`:

```python
#!/usr/bin/env python3
"""
Process V-Dem data for A₁ (Governance Quality) proxy.

A₁ components:
- Policy Effectiveness: v2x_execorr (executive corruption inverse) + v2xlg_legcon (legislative constraints)
- Democratic Quality: v2x_libdem (liberal democracy) + v2x_delibdem (deliberative)
- Institutional Trust: (from WVS, merge later)

Output: governance_quality_vdem_1810_2023.csv
"""
import pandas as pd
import numpy as np

# Load V-Dem data
print("Loading V-Dem v15 data...")
vdem = pd.read_csv('../data_sources/external/vdem/V-Dem-CY-Core-v15.csv')

print(f"Loaded {len(vdem)} country-year observations")
print(f"Year range: {vdem['year'].min()} - {vdem['year'].max()}")
print(f"Countries: {vdem['country_name'].nunique()}")

# Select relevant columns for A₁
governance_vars = [
    'country_name',
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
print(f"\nFound {len(existing_cols)}/{len(governance_vars)} expected columns")

# Extract governance subset
gov_data = vdem[existing_cols].copy()

# Compute composite A₁ (Governance Quality)
# Formula: A₁ = 0.3×Democratic_Quality + 0.3×Effectiveness + 0.4×Trust (WVS, added later)
gov_data['democratic_quality'] = (
    gov_data['v2x_libdem'] * 0.4 +        # Liberal institutions
    gov_data['v2x_delibdem'] * 0.3 +      # Deliberative quality
    gov_data['v2x_egaldem'] * 0.3         # Egalitarian protection
)

gov_data['policy_effectiveness'] = (
    (1 - gov_data['v2x_execorr']) * 0.6 + # Corruption inverse
    gov_data['v2xlg_legcon'] * 0.4        # Legislative checks
)

# Compute preliminary A₁ (before adding WVS trust)
gov_data['a1_preliminary'] = (
    gov_data['democratic_quality'] * 0.5 +
    gov_data['policy_effectiveness'] * 0.5
)

# Save processed data
output_path = '../data_sources/processed/governance_quality_vdem_1810_2023.csv'
gov_data.to_csv(output_path, index=False)
print(f"\n✅ Saved to: {output_path}")

# Summary statistics
print("\n=== A₁ Preliminary Summary ===")
print(gov_data['a1_preliminary'].describe())
print(f"\nGlobal mean by decade:")
gov_data['decade'] = (gov_data['year'] // 10) * 10
decade_means = gov_data.groupby('decade')['a1_preliminary'].mean()
print(decade_means.tail(10))

# Compare to K₁ for 2020 (expected Gap₁ ≈ 0.27-0.33)
recent = gov_data[gov_data['year'] == 2020]
if len(recent) > 0:
    a1_2020 = recent['a1_preliminary'].mean()
    k1_2020 = 0.825  # From K(t) data
    gap = k1_2020 - a1_2020
    ratio = a1_2020 / k1_2020 if k1_2020 > 0 else 0

    print(f"\n=== 2020 Validation ===")
    print(f"K₁ (Capacity):  {k1_2020:.3f}")
    print(f"A₁ (Quality):   {a1_2020:.3f}")
    print(f"Gap₁:           {gap:.3f} ({'✅' if 0.20 < gap < 0.40 else '⚠️ outside expected range'})")
    print(f"Ratio (A/K):    {ratio:.1%}")
```

---

## Step 6: Run Initial Processing (5 minutes)

```bash
cd /srv/luminous-dynamics/kosmic-lab/historical_k/processing_scripts

# Make script executable
chmod +x process_vdem.py

# Run processing
python3 process_vdem.py

# Expected output:
# - Loaded ~30,000 country-year observations
# - Year range: 1789-2023
# - A₁ preliminary mean ≈ 0.45-0.55
# - Gap₁ ≈ 0.25-0.35 (validation range)
```

---

## Step 7: Verify Output (5 minutes)

```bash
# Check processed data
ls -lh ../data_sources/processed/

# Inspect first few rows
head -20 ../data_sources/processed/governance_quality_vdem_1810_2023.csv

# Quick stats with pandas
python3 -c "
import pandas as pd
df = pd.read_csv('../data_sources/processed/governance_quality_vdem_1810_2023.csv')
print('Shape:', df.shape)
print('\nColumns:', df.columns.tolist())
print('\nYear range:', df['year'].min(), '-', df['year'].max())
print('\nA₁ stats:\n', df['a1_preliminary'].describe())
"
```

---

## Next Steps After Extraction

### Immediate (today):
1. Run V-Dem processing script
2. Validate A₁ preliminary against K₁
3. Document any issues or surprises

### This Week:
1. Process WVS for trust data (H1 enhancement, H3 reciprocity)
2. Merge WVS trust into A₁ (final version)
3. Process Gini for A₄ (inclusion quality)
4. Compute provisional A(t) for 2000-2020

### Next Week:
1. Download missing datasets (WGI, WHR, CPI)
2. Complete A₂-A₇ quality proxies
3. Full A(t) computation and validation
4. Manuscript integration

---

## Troubleshooting

### If V-Dem extraction fails:
```bash
# Check ZIP integrity
unzip -t V-Dem-CY-Core-v15_csv.zip

# Manual extraction if needed
cd vdem
unzip ../V-Dem-CY-Core-v15_csv.zip
```

### If column names don't match:
```bash
# Dump all column names to inspect
head -1 vdem/V-Dem-CY-Core-v15.csv | tr ',' '\n' > vdem_columns.txt
cat vdem_columns.txt | grep v2x
```

### If years are missing:
```python
# Check year coverage
import pandas as pd
df = pd.read_csv('vdem/V-Dem-CY-Core-v15.csv')
print(df.groupby('year').size())
```

---

**Ready to proceed?** Run Step 1 to extract all datasets, then Step 6 to process V-Dem for A₁ prototype!
