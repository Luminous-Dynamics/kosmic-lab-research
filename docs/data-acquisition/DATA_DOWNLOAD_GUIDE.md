# Complete Data Download Guide
**Historical K(t): 5000-Year Civilizational Coherence Analysis**

This guide provides step-by-step instructions for obtaining all required datasets for publication-ready K(t) computation.

---

## Overview

Three categories of data needed:
1. **Ancient Data** (3000 BCE - 500 CE): Seshat + HYDE 3.2
2. **Modern Data** (1800 - 2020): Already integrated (V-Dem, World Bank)
3. **Validation Data**: HDI, GDP, Polity, battle deaths

**Total Download Size**: ~2.5 GB
**Estimated Time**: 2-4 hours (depending on connection speed)

---

## Part 1: Seshat Global History Databank

### Option 1: Dataverse Repository (Recommended)

**URL**: https://dataverse.harvard.edu/dataverse/seshat

**Steps**:
1. Visit the Harvard Dataverse Seshat collection
2. Download datasets for these variables:
   - Social Complexity Variables
   - Polity Metadata
   - Warfare Variables
   - Religion Variables

3. Place downloaded files in:
   ```
   data/sources/seshat/raw/
   ```

**Expected Files**:
- `social_complexity.csv` or similar
- `polities.csv` or `polity_metadata.csv`
- `warfare.csv`
- `religion.csv`

### Option 2: Direct Contact

If Dataverse unavailable:
1. Email: submissions@seshatdatabank.info
2. Subject: "Research Data Request - Civilizational Coherence Study"
3. Request: Social complexity, polity, warfare, and religion variables for 3000 BCE - 500 CE

### Option 3: GitHub Repository

**URL**: https://github.com/seshat-ga/seshat

**Note**: File structure may vary. Look for:
- CSV exports in `/data/` directory
- Database dumps
- Processed datasets

### Verification

After download:
```bash
cd /srv/luminous-dynamics/kosmic-lab
ls -lh data/sources/seshat/raw/

# Should show:
# polities.csv (or similar)
# social_complexity.csv
# warfare.csv
# religion.csv
```

Test integration:
```bash
poetry run python -c "from historical_k.seshat_integration import fetch_seshat_data; data = fetch_seshat_data(); print(f'Loaded {len(data)} records')"
```

---

## Part 2: HYDE 3.2 Historical Demographics

### Download Instructions

**Size**: ~2 GB compressed
**URL**: https://doi.org/10.17026/dans-25g-gez3

**Steps**:
1. Visit DANS EASY archive: https://easy.dans.knaw.nl/ui/datasets/id/easy-dataset:74466

2. Click "Download" to get complete HYDE 3.2 baseline dataset

3. Extract the ZIP file:
   ```bash
   cd ~/Downloads
   unzip HYDE3.2_baseline.zip
   ```

4. Move to project directory:
   ```bash
   mv HYDE3.2/baseline/* /srv/luminous-dynamics/kosmic-lab/data/sources/hyde/raw/
   ```

**Expected Directory Structure**:
```
data/sources/hyde/raw/
├── population/
│   ├── popc_-10000BC.nc
│   ├── popc_-9000BC.nc
│   ├── ...
│   └── popc_2020AD.nc
├── cropland/
│   ├── cropland_-10000BC.nc
│   └── ...
├── grazing/
│   ├── grazing_-10000BC.nc
│   └── ...
└── urban/
    ├── urban_-10000BC.nc
    └── ...
```

### Alternative: PBL Netherlands

If DANS is unavailable:
**URL**: https://themasites.pbl.nl/tridion/en/themasites/hyde/

Download individual variable datasets and place in same structure.

### Verification

```bash
# Check files exist
ls data/sources/hyde/raw/population/ | wc -l
# Should show 100+ NetCDF files

# Test integration
poetry run python -m historical_k.hyde_integration --check
```

---

## Part 3: External Validation Datasets

### 3.1 Human Development Index (HDI)

**Source**: United Nations Development Programme
**URL**: http://hdr.undp.org/en/data

**Steps**:
1. Navigate to "Download Data" section
2. Select "Human Development Index (HDI)" time series
3. Download as CSV: 1990-2023 (all countries)
4. Place in: `data/sources/external/raw/hdi.csv`

**Size**: ~5 MB

### 3.2 Maddison Project GDP per Capita

**Source**: Groningen Growth and Development Centre
**URL**: https://www.rug.nl/ggdc/historicaldevelopment/maddison/releases/maddison-project-database-2020

**Steps**:
1. Download "Full dataset" (Excel or CSV version)
2. If Excel, export to CSV
3. Place in: `data/sources/external/raw/maddison_gdp.csv`

**Coverage**: 1 CE - 2018
**Size**: ~10 MB

### 3.3 Polity V Democracy Scores

**Source**: Center for Systemic Peace
**URL**: https://www.systemicpeace.org/inscrdata.html

**Steps**:
1. Download "Polity5 Annual Time-Series, 1946-2018"
2. Extract from XLS to CSV
3. Place in: `data/sources/external/raw/polity5.csv`

**Size**: ~2 MB

### 3.4 V-Dem Democracy Index

**Source**: Varieties of Democracy Institute
**URL**: https://www.v-dem.net/data/the-v-dem-dataset/

**Steps**:
1. Navigate to "Download" section
2. Select "Country-Year: V-Dem Full+Others" (CSV format)
3. **Note**: Large file (~500 MB)
4. Place in: `data/sources/external/raw/vdem.csv`

**Coverage**: 1789-2023
**Size**: ~500 MB

### 3.5 UCDP Battle Deaths

**Source**: Uppsala Conflict Data Program
**URL**: https://ucdp.uu.se/downloads/

**Steps**:
1. Navigate to datasets section
2. Download "UCDP Battle-Related Deaths Dataset"
3. Place in: `data/sources/external/raw/ucdp_battle_deaths.csv`

**Coverage**: 1989-present
**Size**: ~1 MB

### 3.6 Correlates of War (Optional)

**Source**: Correlates of War Project
**URL**: https://correlatesofwar.org/data-sets/

**Steps**:
1. Download "Inter-State War Data, v4.0"
2. Download "Intra-State War Data, v5.1"
3. Place in:
   - `data/sources/external/raw/cow_inter_state.csv`
   - `data/sources/external/raw/cow_intra_state.csv`

**Coverage**: 1816-2007
**Size**: ~500 KB each

### Verification

```bash
# Check all external files
ls -lh data/sources/external/raw/

# Should show:
# hdi.csv
# maddison_gdp.csv
# polity5.csv
# vdem.csv (large)
# ucdp_battle_deaths.csv
# cow_*.csv (optional)

# Test validation module
poetry run python -m historical_k.external_validation --download
```

---

## Complete Verification

After downloading all data:

```bash
# Run comprehensive check
make data-fetch-all

# Expected output:
# ✓ Seshat: 4 files found
# ✓ HYDE: 100+ files found
# ✓ External: 5-7 files found
```

---

## Quick Start After Download

Once all data is downloaded:

```bash
# 1. Re-compute extended K(t) with real data
make extended-compute
# Output: logs/historical_k_extended/k_t_series_5000y.csv

# 2. Run external validation
make external-validate
# Output: logs/validation_external/validation_report.md

# 3. Run robustness tests
make robustness-test
# Output: logs/robustness/robustness_report.md

# 4. Check publication readiness
make publication-ready
```

---

## Troubleshooting

### Seshat Data Not Loading

**Problem**: "FileNotFoundError: polities.csv not found"

**Solutions**:
1. Verify files are in `data/sources/seshat/raw/`
2. Check file names match expected (may need renaming)
3. Ensure CSV format (not Excel/XLS)
4. Try: `poetry run python -m historical_k.seshat_integration --check`

### HYDE NetCDF Import Error

**Problem**: "ImportError: No module named 'netCDF4'"

**Solution**:
```bash
poetry add netCDF4
# Or if that fails:
pip install netCDF4==1.6.4
```

### External Validation Files Not Found

**Problem**: "Could not find HDI columns"

**Solutions**:
1. Verify CSV format (not Excel)
2. Check first few rows have correct structure
3. Column names may vary - module auto-detects common patterns

### Large File Downloads Failing

**Problem**: Download interrupted / times out

**Solutions**:
1. Use a download manager (wget, curl with resume)
2. Download during off-peak hours
3. For HYDE: Download via institutional access if available
4. For V-Dem: Use their API for partial downloads if needed

---

## Data Quality Checklist

Before proceeding to analysis:

### Seshat
- [ ] At least 50 records for 3000 BCE - 500 CE period
- [ ] Social complexity variables present
- [ ] No more than 20% missing data

### HYDE 3.2
- [ ] NetCDF files for all four variables (population, cropland, grazing, urban)
- [ ] Coverage from at least 1000 BCE to 2020 CE
- [ ] Files can be opened with netCDF4 library

### External Indices
- [ ] HDI: At least 30 years of data (1990-2020)
- [ ] Maddison GDP: At least 100 years overlapping with K(t)
- [ ] Polity or V-Dem: At least 50 years of democracy scores
- [ ] Battle deaths: Any coverage overlapping with K(t)

---

## Data Citations

### Seshat
Turchin, P., et al. (2018). Seshat: The Global History Databank. *Cliodynamics*, 9(1), 99-134. https://doi.org/10.21237/C7clio9137696

### HYDE 3.2
Klein Goldewijk, K., Beusen, A., Doelman, J., & Stehfest, E. (2017). Anthropogenic land use estimates for the Holocene – HYDE 3.2. *Earth System Science Data*, 9(2), 927-953. https://doi.org/10.5194/essd-9-927-2017

### HDI
United Nations Development Programme. (2023). Human Development Index. Retrieved from http://hdr.undp.org/

### Maddison GDP
Bolt, J., & van Zanden, J. L. (2020). Maddison style estimates of the evolution of the world economy. A new 2020 update. *Maddison Project Database*, version 2020.

### Polity V
Marshall, M. G., & Gurr, T. R. (2020). Polity5: Political Regime Characteristics and Transitions, 1800-2018. Center for Systemic Peace.

### V-Dem
Coppedge, M., et al. (2023). V-Dem Dataset v13. Varieties of Democracy (V-Dem) Project. https://doi.org/10.23696/vdemds23

### UCDP
Pettersson, T., et al. (2023). UCDP Battle-Related Deaths Dataset. Uppsala Conflict Data Program. https://ucdp.uu.se/

---

## Timeline Estimate

| Phase | Task | Time | Cumulative |
|-------|------|------|------------|
| 1 | Download Seshat | 30 min | 30 min |
| 2 | Download HYDE (~2 GB) | 1-2 hours | 2.5 hours |
| 3 | Download external indices | 30 min | 3 hours |
| 4 | Verify all data | 15 min | 3.25 hours |
| 5 | Re-compute K(t) | 5 min | 3.5 hours |
| 6 | Run validation | 10 min | 3.75 hours |
| 7 | Run robustness | 15 min | 4 hours |

**Total**: ~4 hours (assuming good internet connection)

---

## Support

For data download issues:
- **Seshat**: submissions@seshatdatabank.info
- **HYDE**: Ask via PBL Netherlands website
- **V-Dem**: support@v-dem.net
- **Project Issues**: GitHub Issues

For analysis issues after download:
```bash
make publication-ready  # Shows what's missing
```

---

*This guide ensures complete, reproducible data acquisition for the Historical K(t) project.*
