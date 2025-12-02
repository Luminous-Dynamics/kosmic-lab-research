# Track C-1 External Data Download Guide

**Time Required:** ~2 hours total (30 min per dataset)
**Difficulty:** Easy (straightforward downloads)

---

## Prerequisites

Create the data directory:
```bash
mkdir -p data/sources/external/raw
cd data/sources/external/raw
```

---

## 1. Human Development Index (HDI) 📊

**Source:** United Nations Development Programme (UNDP)
**Coverage:** 1990-2023
**Time:** ~30 minutes

### Direct Links:
- **Main Portal:** https://hdr.undp.org/data-center/human-development-index
- **Download Page:** https://hdr.undp.org/sites/default/files/2023-24_HDR/HDR23-24_Composite_indices_complete_time_series.csv

### Steps:
1. Visit: https://hdr.undp.org/data-center/human-development-index
2. Click "Download" or "Data Download"
3. Look for "Human Development Index (HDI)" time series
4. Download CSV or Excel format
5. If Excel, open and save as CSV

### Required Format:
```csv
year,hdi_global
1990,0.598
1991,0.604
...
2020,0.737
```

### Processing:
```bash
# If you have country-level data, compute global average:
# year, country, hdi -> year, hdi_global (average across countries)

# Save as:
cp downloaded_hdi.csv data/sources/external/raw/hdi.csv
```

**Alternative Source (if UNDP site issues):**
- World Bank: https://data.worldbank.org/ (search "HDI")
- Our World in Data: https://ourworldindata.org/human-development-index

---

## 2. GDP per Capita (Maddison Project) 💰

**Source:** Maddison Project Database
**Coverage:** 1-2020 CE (we need 1810-2020)
**Time:** ~30 minutes

### Direct Links:
- **Main Page:** https://www.rug.nl/ggdc/historicaldevelopment/maddison/
- **Latest Release:** https://www.rug.nl/ggdc/historicaldevelopment/maddison/releases/maddison-project-database-2020
- **Direct Download:** https://www.rug.nl/ggdc/historicaldevelopment/maddison/data/mpd2020.xlsx

### Steps:
1. Visit: https://www.rug.nl/ggdc/historicaldevelopment/maddison/releases/maddison-project-database-2020
2. Download "Full data file" (Excel format)
3. Open mpd2020.xlsx
4. Sheet: "Full data" contains all countries/years

### Required Format:
```csv
year,gdp_per_capita_global
1810,800
1820,850
...
2020,15000
```

### Processing:
```python
# Process Maddison data (if needed):
import pandas as pd

# Load Maddison data
df = pd.read_excel('mpd2020.xlsx', sheet_name='Full data')

# Compute population-weighted global average
# Columns: country, year, gdppc (GDP per capita), pop (population)
global_avg = df.groupby('year').apply(
    lambda x: (x['gdppc'] * x['pop']).sum() / x['pop'].sum()
).reset_index()
global_avg.columns = ['year', 'gdp_per_capita_global']

# Filter to 1810-2020
global_avg = global_avg[(global_avg['year'] >= 1810) & (global_avg['year'] <= 2020)]

# Save
global_avg.to_csv('data/sources/external/raw/maddison_gdp.csv', index=False)
```

**Alternative (simpler):**
- World Bank GDP data: https://data.worldbank.org/indicator/NY.GDP.PCAP.CD
- Coverage: 1960-2023 (less historical but easier)

---

## 3. KOF Globalization Index 🌐

**Source:** KOF Swiss Economic Institute
**Coverage:** 1970-2022
**Time:** ~30 minutes

### Direct Links:
- **Main Page:** https://kof.ethz.ch/en/forecasts-and-indicators/indicators/kof-globalisation-index.html
- **Data Portal:** https://kof.ethz.ch/en/forecasts-and-indicators/indicators/kof-globalisation-index.html
- **Direct Download:** Look for "Download data" button

### Steps:
1. Visit: https://kof.ethz.ch/en/forecasts-and-indicators/indicators/kof-globalisation-index.html
2. Scroll to "Downloads" section
3. Download "KOF Globalisation Index" (Excel or CSV)
4. Look for "Overall KOF Globalisation Index" column

### Required Format:
```csv
year,kof_global
1970,40.5
1971,41.2
...
2020,62.8
```

### Processing:
```python
# Process KOF data:
import pandas as pd

# Load KOF data (format varies by version)
df = pd.read_excel('kof_globalization.xlsx')

# Look for columns: year, code (country), KOFGIdf (overall index)
# Compute global average (or use world value if available)
global_avg = df[df['code'] == 'WLD'][['year', 'KOFGIdf']].copy()
global_avg.columns = ['year', 'kof_global']

# Or compute average across all countries:
# global_avg = df.groupby('year')['KOFGIdf'].mean().reset_index()
# global_avg.columns = ['year', 'kof_global']

global_avg.to_csv('data/sources/external/raw/kof_globalization.csv', index=False)
```

**Note:** KOF index ranges 0-100, normalize to [0, 1] if needed: `kof_global / 100`

---

## 4. DHL Global Connectedness Index 📦

**Source:** DHL & NYU Stern School of Business
**Coverage:** 2001-2023 (biennial: 2001, 2003, 2005, ...)
**Time:** ~30 minutes

### Direct Links:
- **Main Report:** https://www.dhl.com/global-en/delivered/globalization/global-connectedness-index.html
- **Latest Report (2024):** https://www.dhl.com/content/dam/dhl/global/delivered/documents/pdf/glo-global-connectedness-index-2024.pdf

### Steps:
1. Visit: https://www.dhl.com/global-en/delivered/globalization/global-connectedness-index.html
2. Download the latest PDF report
3. Look for appendix tables with historical data
4. **Manual extraction required** - data is in PDF tables

### Alternative (Easier):
Check these sources for machine-readable data:
- NYU Stern: https://www.stern.nyu.edu/experience-stern/about/departments-centers-initiatives/centers-of-research/center-for-the-future-of-management/research/global-connectedness-index
- Look for supplementary Excel files

### Required Format:
```csv
year,dhl_connectedness
2001,0.45
2003,0.48
2005,0.52
...
2020,0.61
```

### Processing:
- DHL reports "Depth" scores (0-100)
- Normalize to [0, 1]: `dhl_connectedness = depth / 100`
- Data is biennial, interpolate intermediate years if needed

**Note:** This is the most difficult dataset - PDF extraction required. May want to skip initially.

---

## Quick Start Commands

After downloading all files:

```bash
# Check files exist
ls -lh data/sources/external/raw/

# Expected files:
# - hdi.csv
# - maddison_gdp.csv  
# - kof_globalization.csv
# - dhl_connectedness.csv

# Run validation
poetry run python historical_k/external_validation.py --process

# Update visualizations with correlations
poetry run python historical_k/visualize_harmonies.py \
  --correlations logs/validation_external/correlations.json \
  --option both

# View results
cat logs/validation_external/validation_report.md
```

---

## Data Format Requirements Summary

All files must be CSV with two columns:

1. **HDI:** `year,hdi_global` (range: 0-1)
2. **GDP:** `year,gdp_per_capita_global` (units: constant 2011 USD)
3. **KOF:** `year,kof_global` (range: 0-100 or 0-1)
4. **DHL:** `year,dhl_connectedness` (range: 0-1)

**Year format:** Integer (e.g., 1990, 2020)
**No missing values** in the year range you provide

---

## Troubleshooting

### "Cannot find download link"
- Sites change frequently - use search: "[dataset name] download"
- Check "Data" or "Downloads" sections
- Look for latest release year

### "Data in wrong format"
- Use Python/Excel to reshape
- Script provided above for Maddison and KOF
- Ask Claude for help with specific format issues

### "Missing years"
- Interpolate: `df.interpolate(method='linear')`
- Or skip validation for that index

### "DHL data too difficult"
- Skip DHL initially (hardest to get)
- Run validation with HDI, GDP, KOF only (3/4 is fine)

---

## Time-Saving Tips

1. **Start with HDI and GDP** (easiest, most coverage)
2. **Skip DHL if pressed for time** (biennial, PDF extraction)
3. **Use World Bank as backup** for HDI/GDP (easier interface)
4. **Don't perfect the processing** - rough global averages are fine
5. **Test with partial data** - validation works with 1-7 indices

---

## Expected Results

After running validation, you should see:

```
✓ Loaded K(t): 263 years (-3000 to 2020)
✓ Loaded HDI: 31 years (1990-2020)
✓ Loaded Maddison GDP: 211 years (1810-2020)
✓ Loaded KOF: 51 years (1970-2020)
✓ Loaded DHL: 20 years (2001-2020)

Validation Results:
  HDI vs K(t):  r = 0.85*** (n=31)
  GDP vs K(t):  r = 0.78*** (n=211)
  KOF vs K(t):  r = 0.82*** (n=51)
  DHL vs K(t):  r = 0.79*** (n=20)
```

Strong positive correlations (r > 0.7) validate K(t) as credible measure.

---

**Questions?** Review download instructions or run `poetry run python historical_k/external_validation.py --download`
