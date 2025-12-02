# Data Acquisition Status Report

**Generated**: 2025-11-21
**Status**: Partial Success - 3/8 datasets acquired automatically

---

## Executive Summary

**Automated Downloads**: ✅ 3/8 datasets (3.4 MB)
**Manual Downloads Required**: 🔶 5/8 datasets (~2.5 GB)
**Overall Completeness**: 37.5% by count, <1% by size

The external validation datasets were successfully downloaded programmatically. However, the two largest and most critical datasets (Seshat and HYDE 3.2) require manual download due to repository structure and file size constraints.

---

## ✅ Successfully Downloaded (Automated)

### 1. HDI - Human Development Index (UNDP)
- **Status**: ✅ **DOWNLOADED**
- **File**: `data/sources/external/raw/hdi.csv`
- **Size**: 1.70 MB
- **Source**: UN Development Programme
- **URL**: https://hdr.undp.org/sites/default/files/2021-22_HDR/HDR21-22_Composite_indices_complete_time_series.csv
- **Coverage**: 1990-2022, 193 countries
- **Variables**: HDI, life expectancy, education index, GNI per capita
- **Next Step**: Extract and process for validation (automated)

### 2. Maddison Project GDP per Capita
- **Status**: ✅ **DOWNLOADED**
- **File**: `data/sources/external/raw/maddison_gdp.xlsx`
- **Size**: 1.68 MB
- **Source**: Groningen Growth and Development Centre
- **URL**: https://www.rug.nl/ggdc/historicaldevelopment/maddison/data/mpd2020.xlsx
- **Coverage**: 1 CE - 2018, global
- **Variables**: GDP per capita (multiple estimates)
- **Next Step**: Convert Excel to CSV, extract time series (automated)

### 3. UCDP Battle-Related Deaths
- **Status**: ✅ **DOWNLOADED**
- **File**: `data/sources/external/raw/ucdp_battle_deaths.zip`
- **Size**: 36 KB (compressed)
- **Source**: Uppsala Conflict Data Program
- **URL**: https://ucdp.uu.se/downloads/brd/ucdp-brd-conf-221-csv.zip
- **Coverage**: 1989-2021
- **Variables**: Battle deaths by conflict
- **Next Step**: Extract ZIP, aggregate globally (automated)

---

## 🔶 Manual Download Required

### 4. Seshat Global History Databank ⚠️ CRITICAL
- **Status**: 🔶 **MANUAL REQUIRED**
- **Target**: `data/sources/seshat/raw/`
- **Size**: ~10-50 MB (estimated)
- **Reason**: GitHub URLs returned 404 errors; repository structure unclear
- **Source Options**:
  1. **Harvard Dataverse** (RECOMMENDED): https://dataverse.harvard.edu/dataverse/seshat
  2. **Direct Contact**: submissions@seshatdatabank.info
  3. **GitHub** (if structure identified): https://github.com/seshat-ga/seshat

**Files Needed**:
- `polities.csv` - Polity metadata (regions, dates)
- `social_complexity.csv` - Social complexity variables
- `warfare.csv` - Conflict and military data
- `religion.csv` - Religious system data

**Coverage**: 3000 BCE - 500 CE (30 polities)
**Importance**: **CRITICAL** - Provides all ancient period data (3000 BCE - 500 CE)
**Time Estimate**: 30-60 minutes (includes registration, download, extraction)

**Download Instructions**:
```bash
# Option 1: Harvard Dataverse
# 1. Visit https://dataverse.harvard.edu/dataverse/seshat
# 2. Download CSV datasets
# 3. Place in data/sources/seshat/raw/
# 4. Verify: make data-fetch-seshat

# Option 2: Direct contact if Dataverse unavailable
# Email: submissions@seshatdatabank.info
# Subject: "Research Data Request - Civilizational Coherence Study"
# Request: Social complexity, polity, warfare, religion variables (CSV format)
```

### 5. HYDE 3.2 - Historical Demographics ⚠️ CRITICAL
- **Status**: 🔶 **MANUAL REQUIRED**
- **Target**: `data/sources/hyde/raw/`
- **Size**: ~2.0 GB compressed, ~8 GB uncompressed
- **Reason**: Large NetCDF dataset requires manual download and extraction
- **Source**: DANS EASY Archive
- **URL**: https://doi.org/10.17026/dans-25g-gez3
- **Direct Link**: https://easy.dans.knaw.nl/ui/datasets/id/easy-dataset:74466

**Dataset Structure**:
```
HYDE3.2/baseline/
├── population/
│   ├── popc_-10000BC.nc
│   ├── popc_-9000BC.nc
│   └── ... (100+ files, 10000 BCE - 2020 CE)
├── cropland/
│   └── ... (land use history)
├── grazing/
│   └── ... (pastoral land use)
└── urban/
    └── ... (urbanization)
```

**Coverage**: 10,000 BCE - 2020 CE, global, 5 arc-minute resolution
**Importance**: **CRITICAL** - Provides demographic foundation across all periods
**Time Estimate**: 1-2 hours (large download)

**Download Instructions**:
```bash
# 1. Visit https://easy.dans.knaw.nl/ui/datasets/id/easy-dataset:74466
# 2. Click "Download" (may require DANS account)
# 3. Download HYDE3.2_baseline.zip (~2 GB)
# 4. Extract:
cd ~/Downloads
unzip HYDE3.2_baseline.zip

# 5. Move to project:
mv HYDE3.2/baseline/* /srv/luminous-dynamics/kosmic-lab/data/sources/hyde/raw/

# 6. Verify:
ls data/sources/hyde/raw/population/ | wc -l  # Should show 100+ files
make data-fetch-hyde  # Should show files detected
```

**Alternative**: PBL Netherlands direct download: https://themasites.pbl.nl/tridion/en/themasites/hyde/

### 6. Polity V Democracy Scores
- **Status**: 🔶 **MANUAL REQUIRED**
- **Target**: `data/sources/external/raw/polity5.csv`
- **Size**: ~2 MB
- **Reason**: HTTP 406 error (Not Acceptable) - server may require browser headers
- **Source**: Center for Systemic Peace
- **URL**: http://www.systemicpeace.org/inscrdata.html
- **Direct Link**: http://www.systemicpeace.org/inscr/p5v2018.xls

**Download Instructions**:
```bash
# Download manually in browser:
# 1. Visit http://www.systemicpeace.org/inscrdata.html
# 2. Download "Polity5 Annual Time-Series, 1946-2018"
# 3. Convert XLS to CSV
# 4. Place in data/sources/external/raw/polity5.csv
```

**Coverage**: 1800-2018 (167 countries)
**Importance**: MEDIUM - Can use V-Dem as alternative
**Time Estimate**: 10-15 minutes

### 7. V-Dem Democracy Index
- **Status**: 🔶 **MANUAL REQUIRED**
- **Target**: `data/sources/external/raw/vdem.csv`
- **Size**: ~500 MB
- **Reason**: Requires registration and login
- **Source**: Varieties of Democracy Institute
- **URL**: https://www.v-dem.net/data/the-v-dem-dataset/

**Download Instructions**:
```bash
# 1. Visit https://www.v-dem.net/data/the-v-dem-dataset/
# 2. Register for free account (if needed)
# 3. Download "Country-Year: V-Dem Full+Others" (CSV format)
# 4. Place in data/sources/external/raw/vdem.csv
```

**Coverage**: 1789-2023 (202 countries)
**Importance**: MEDIUM - Provides democracy dimension for validation
**Time Estimate**: 20-30 minutes (includes registration)

### 8. Correlates of War (Optional)
- **Status**: 🔶 **OPTIONAL**
- **Target**: `data/sources/external/raw/cow_*.csv`
- **Size**: ~1 MB total
- **Source**: Correlates of War Project
- **URL**: https://correlatesofwar.org/data-sets/

**Files**:
- Inter-State War Data v4.0
- Intra-State War Data v5.1

**Coverage**: 1816-2007
**Importance**: LOW - Supplementary conflict data, UCDP already downloaded
**Time Estimate**: 10-15 minutes

---

## Data Integration Readiness

### Current Capability
With the 3 downloaded datasets, we can:
- ✅ Validate K(t) against HDI (1990-2022)
- ✅ Validate K(t) against GDP per capita (1 CE - 2018)
- ✅ Validate K(t) against battle deaths (1989-2021)
- ✅ Demonstrate the validation pipeline works
- ✅ Generate partial validation report

### Missing Capability
Without Seshat and HYDE, we **cannot**:
- ❌ Compute K(t) for ancient period (3000 BCE - 500 CE)
- ❌ Compute K(t) for medieval period with real demographics
- ❌ Validate pre-modern K(t) trends
- ❌ Complete the full 5000-year analysis
- ❌ Submit for publication (real data required)

### Workaround: Synthetic Data Fallback
The `ancient_data.py` module gracefully falls back to synthetic data:
- ✅ Allows development to continue
- ✅ Demonstrates complete pipeline
- ✅ Tests all code paths
- ❌ NOT suitable for publication
- ❌ Synthetic patterns lack historical validation

---

## Priority Acquisition Plan

### Phase 1: Critical Downloads (Required for Publication)
**Time**: 2-4 hours
**Priority**: P0 - BLOCKING

1. **Seshat** (30-60 min)
   - Harvard Dataverse registration and download
   - OR email request to Seshat team
   - **Blocks**: Ancient period K(t), full time series

2. **HYDE 3.2** (1-2 hours)
   - DANS archive download (~2 GB)
   - Extraction and placement
   - **Blocks**: Demographic foundation, all periods

### Phase 2: Validation Enhancement (Improves Analysis)
**Time**: 30-60 minutes
**Priority**: P1 - IMPORTANT

3. **Polity V** (10-15 min)
   - Manual browser download
   - XLS to CSV conversion
   - **Improves**: Democracy validation coverage

4. **V-Dem** (20-30 min)
   - Registration and download
   - **Improves**: Democracy validation depth, longer time series

### Phase 3: Optional Supplements
**Time**: 10-15 minutes
**Priority**: P2 - NICE-TO-HAVE

5. **Correlates of War** (10-15 min)
   - Additional conflict data
   - **Improves**: Historical conflict validation

---

## Automated Processing After Manual Downloads

Once manual downloads complete, run:

```bash
# 1. Verify all data present
make data-fetch-all

# Expected output:
# ✓ Seshat: 4 files found
# ✓ HYDE: 100+ files found
# ✓ External: 5-7 files found

# 2. Process and integrate
make extended-compute
# → Computes K(t) with real Seshat + HYDE data
# → Output: logs/historical_k_extended/k_t_series_5000y.csv

# 3. Run external validation
make external-validate
# → Cross-validates K(t) against HDI, GDP, Polity, battle deaths
# → Output: logs/validation_external/validation_report.md

# 4. Test robustness
make robustness-test
# → 4 categories of sensitivity tests
# → Output: logs/robustness/robustness_report.md

# 5. Check publication readiness
make publication-ready
# → Comprehensive checklist verification
# → Identifies any remaining gaps
```

---

## Verification Commands

After each manual download:

### Verify Seshat
```bash
ls -lh data/sources/seshat/raw/
# Should show: polities.csv, social_complexity.csv, warfare.csv, religion.csv

poetry run python -c "from historical_k.seshat_integration import fetch_seshat_data; data = fetch_seshat_data(); print(f'Loaded {len(data)} records')"
# Expected: "Loaded 50-200 records"
```

### Verify HYDE
```bash
ls data/sources/hyde/raw/population/ | wc -l
# Should show: 100+ NetCDF files

ls data/sources/hyde/raw/cropland/ | wc -l
# Should show: 100+ NetCDF files

poetry run python -m historical_k.hyde_integration --check
# Expected: "✓ Found 100+ population files, 100+ cropland files"
```

### Verify External
```bash
ls -lh data/sources/external/raw/
# Should show: hdi.csv, maddison_gdp.xlsx, ucdp_battle_deaths.zip, polity5.csv, vdem.csv

poetry run python -m historical_k.external_validation --check
# Expected: "✓ 5 external datasets ready"
```

---

## Estimated Timeline

| Phase | Task | Time | Cumulative |
|-------|------|------|------------|
| ✅ Done | External auto-download | 5 min | 5 min |
| 🔶 P0 | Download Seshat | 30-60 min | 1.25 hours |
| 🔶 P0 | Download HYDE (~2 GB) | 1-2 hours | 3.25 hours |
| 🔶 P1 | Download Polity V | 10-15 min | 3.5 hours |
| 🔶 P1 | Download V-Dem | 20-30 min | 4 hours |
| ✅ Auto | Re-compute K(t) | 5 min | 4.1 hours |
| ✅ Auto | Run validation | 10 min | 4.25 hours |
| ✅ Auto | Run robustness | 15 min | 4.5 hours |

**Total Time to Publication-Ready Data**: ~4.5 hours (mostly waiting for HYDE download)

---

## Next Steps

### Immediate (Do Now)
1. **Download Seshat** from Harvard Dataverse
2. **Download HYDE 3.2** from DANS (~2 GB, start first)
3. While downloading: Continue manuscript drafting (Methods section)

### After Seshat + HYDE Complete
4. Run `make extended-compute` (real K(t) with ancient data)
5. Run `make external-validate` (cross-validation)
6. Run `make robustness-test` (methodological tests)

### After All Data Complete
7. Update Results section of manuscript
8. Generate publication figures
9. Run `make publication-ready` final check
10. Submit manuscript

---

## Support Resources

**For Download Issues**:
- Seshat: submissions@seshatdatabank.info
- HYDE: PBL Netherlands website contact form
- V-Dem: support@v-dem.net

**For Integration Issues**:
```bash
# Check what's blocking
make publication-ready

# Get detailed help
make help
```

---

## Summary

**What I Can Download**: ✅ External validation indices (HDI, GDP, battle deaths) - **DONE**

**What Requires Manual Action**:
- 🔶 Seshat (critical, 30-60 min)
- 🔶 HYDE 3.2 (critical, 1-2 hours, ~2 GB)
- 🔶 Polity V (important, 10-15 min)
- 🔶 V-Dem (important, 20-30 min)

**Recommended Approach**:
1. Start HYDE 3.2 download first (largest, ~2 GB)
2. While downloading: Get Seshat from Dataverse
3. While waiting: Continue manuscript drafting
4. After both critical datasets: Run automated validation pipeline

**Publication Blocker**: Seshat + HYDE are **required** for real 5000-year analysis. Current synthetic fallback is for development only.

---

**Status**: Ready to proceed with manual downloads. All automation infrastructure in place for processing once data acquired.
