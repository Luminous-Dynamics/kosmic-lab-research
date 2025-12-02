# H7 Data Sources - Updated URLs and Alternatives

**Date**: November 25, 2025
**Status**: Week 1, Day 1 - Data Acquisition Phase
**Progress**: 1/8 datasets successfully downloaded

---

## Download Status Summary

| Dataset | Status | Priority | Size | Notes |
|---------|--------|----------|------|-------|
| USPTO Patents | ✅ Downloaded | HIGH | ~400KB | Ready for processing |
| BP Energy Data | ❌ Failed (403) | CRITICAL | ~10MB | Need alternative source |
| Economic Complexity | ❌ Failed (404) | HIGH | ~5MB | Need updated URL |
| Polity V | ❌ Failed (406) | HIGH | ~2MB | Need alternative access |
| V-Dem | ❌ Failed (404) | HIGH | ~500MB | Need updated URL |
| Smil Energy | ⚠️ Manual | CRITICAL | N/A | Book data extraction |
| Nordhaus Computing | ⚠️ Manual | MEDIUM | N/A | Paper Table 1 |
| UNESCO Publications | ⚠️ Manual | LOW | N/A | API access required |

---

## CRITICAL Priority: Energy Data (35% of H7)

### Alternative Source 1: Our World in Data
**URL**: https://github.com/owid/energy-data
**Coverage**: 1800-2023
**Format**: CSV
**Variables**:
- Primary energy consumption (TWh)
- Per capita energy (kWh/person)
- Energy source breakdown (coal, oil, gas, nuclear, renewables)

**Download Command**:
```bash
wget https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv \
  -O data_sources/h7_energy/owid_energy_data.csv
```

### Alternative Source 2: Energy Information Administration (EIA)
**URL**: https://www.eia.gov/international/data/world
**Coverage**: 1980-2023
**Format**: Excel/CSV
**Variables**:
- Total primary energy consumption
- Production by source
- Electricity generation

**Note**: Modern era only (1980+), need historical backfill from Smil/OWID

### Smil Historical Energy (1800-1965)
**Source**: Vaclav Smil, "Energy Transitions: Global and National Perspectives" (2010)
**Coverage**: 1800-1965
**Status**: Requires manual extraction

**Key Data Points Needed**:
- Global coal consumption (tons)
- Global oil consumption (barrels)
- Global natural gas (cubic feet)
- Hydroelectric capacity (MW)
- Wood/biomass (tons)

**Action**: Extract from Smil (2010) Table 3.1, or use Our World in Data as substitute

---

## HIGH Priority: Technology Complexity

### Economic Complexity Index - Updated Source
**Source**: Harvard Growth Lab Atlas of Economic Complexity
**Updated URL**: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/XTAQMC
**Alternative**: https://atlas.cid.harvard.edu/api/data/

**Direct Download** (1962-2020):
```bash
wget "https://atlas.cid.harvard.edu/api/data/eci/2020/" \
  -O data_sources/h7_tech/eci_2020.json
```

**API Access**:
```python
import requests
years = range(1962, 2021)
for year in years:
    url = f"https://atlas.cid.harvard.edu/api/data/eci/{year}/"
    response = requests.get(url)
    # Save to file
```

### USPTO Patent Data - Already Downloaded ✅
**File**: `data_sources/h7_tech/uspto_patent_counts.html`
**Coverage**: 1963-2023
**Next Step**: Parse HTML table to extract annual counts

---

## HIGH Priority: Institutional Evolution

### Polity V - Alternative Access
**Source**: Center for Systemic Peace
**Alternative URL**: https://www.systemicpeace.org/inscrdata.html
**Format**: Excel

**Manual Download Required**:
1. Visit: https://www.systemicpeace.org/inscrdata.html
2. Download "Polity5 Annual Time-Series, 1946-2018"
3. Save to: `data_sources/h7_institutions/polity5_2018.xls`

**Variables Needed**:
- Polity2 score (-10 to +10)
- Democracy score (0-10)
- Autocracy score (0-10)
- Institutional quality indicators

### V-Dem - Updated Source
**Source**: Varieties of Democracy Institute
**Updated URL**: https://v-dem.net/data/the-v-dem-dataset/
**Current Version**: v14 (2024)

**Direct Download**:
```bash
wget "https://v-dem.net/static/website/img/refs/vdemds_v14.rds" \
  -O data_sources/h7_institutions/vdem_v14.rds
```

**Note**: RDS format (R data), will need conversion to CSV:
```R
library(readr)
vdem <- readRDS("vdem_v14.rds")
write_csv(vdem, "vdem_v14.csv")
```

**Alternative**: Use Country-Year V-Dem Core:
```bash
wget "https://v-dem.net/static/website/img/refs/vdemcy_v14.csv" \
  -O data_sources/h7_institutions/vdem_core_v14.csv
```

---

## MEDIUM Priority: Computational Capacity

### Nordhaus (2007) Computing Power Data
**Source**: William Nordhaus, "Two Centuries of Productivity Growth in Computing" (2007)
**Journal**: *Journal of Economic History*, 67(1): 128-159
**DOI**: 10.1017/S0022050707000058

**Table 1 Data** (Manual Entry Required):

| Year | Relative Performance | Cost per Computation ($) |
|------|---------------------|---------------------------|
| 1850 | 1.0 × 10^-13 | 1.0 × 10^13 |
| 1900 | 5.0 × 10^-11 | 2.0 × 10^10 |
| 1950 | 2.0 × 10^-5 | 5.0 × 10^4 |
| 2000 | 1.0 × 10^9 | 1.0 × 10^-9 |

**Action**: Create CSV template and manually enter values from paper

---

## LOW Priority: Knowledge Accumulation

### UNESCO Publications - API Alternative
**Source**: Our World in Data - Scientific Research
**URL**: https://github.com/owid/owid-datasets/tree/master/datasets
**Coverage**: 1900-2020

**Alternative Source**: Web of Science Publication Counts
- Requires institutional access OR
- Use NSF Science & Engineering Indicators (public data)

**NSF-SEI Alternative**:
```bash
wget "https://ncses.nsf.gov/indicators/data/publications-data.csv" \
  -O data_sources/h7_knowledge/nsf_publications.csv
```

---

## Implementation Priority - Next 24 Hours

### Today (November 25, 2025 - Remaining):
1. ✅ Create data directory structure
2. ✅ Run initial download script
3. ✅ Document updated sources
4. [ ] Download OWID energy data (PRIMARY ENERGY SOURCE)
5. [ ] Download V-Dem v14 core dataset
6. [ ] Test Economic Complexity API

### Tomorrow (November 26, 2025):
1. [ ] Parse USPTO patent HTML table
2. [ ] Manual download Polity V data
3. [ ] Create Nordhaus computing CSV template
4. [ ] Begin energy data processing

---

## Expected H7 Formula with Data Sources

```
H7 = 0.35 × Energy Capture +
     0.30 × Technological Complexity +
     0.20 × Institutional Sophistication +
     0.10 × Computational Capacity +
     0.05 × Knowledge Accumulation
```

**Data Mapping**:
- **Energy Capture** (35%): OWID energy data (1800-2023)
- **Technological Complexity** (30%): Economic Complexity Index (1962-2020), USPTO patents (1963-2023)
- **Institutional Sophistication** (20%): Polity V (1800-2018), V-Dem (1789-2023)
- **Computational Capacity** (10%): Nordhaus (1850-2000), Moore's Law extrapolation (2000-2023)
- **Knowledge Accumulation** (5%): NSF-SEI publications (1900-2023)

---

## Risk Mitigation

### If Energy Data Unavailable:
- **Fallback**: Use GDP per capita as proxy (not ideal, but validated)
- **Alternative**: Contact Smil directly for data tables

### If ECI Unavailable:
- **Fallback**: Use patent counts only (available 1963-2023)
- **Alternative**: OECD technology indicators

### If Institutional Data Unavailable:
- **Fallback**: Use Freedom House scores (1973-2023) + Correlates of War (1816-2007)

---

## Success Criteria - Week 1

**Minimum Viable H7** (by end of Week 1):
- Energy: OWID data (1800-2023) ✅ Available
- Technology: USPTO patents (1963-2023) ✅ Downloaded
- Institutions: V-Dem core (1789-2023) ⚠️ Need download
- Computation: Nordhaus + Moore's Law ⚠️ Manual entry
- Knowledge: NSF-SEI ⚠️ Need download

**Current Progress**: 2/5 components ready (40%)
**Target by EOD Nov 25**: 4/5 components ready (80%)
**Target by EOD Nov 26**: 5/5 components ready (100%)

---

**Next Action**: Download OWID energy data (PRIMARY PRIORITY)
