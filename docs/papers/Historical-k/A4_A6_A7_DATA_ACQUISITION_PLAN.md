# A₄, A₆, A₇ Data Acquisition Plan

**Date**: 2025-11-27
**Session**: Session 3 Continuation (Part 3)
**Status**: Data sources identified, acquisition steps documented

---

## Executive Summary

After successfully generating A₂ (Interconnection), A₃ (Reciprocity), and A₅ (Knowledge) using V-Dem data, we now have **4/7 harmonies complete** (including A₁ Governance from Session 2). This document provides a structured plan for acquiring data and creating the remaining three quality indices: A₄ (Complexity/Diversity), A₆ (Wellbeing), and A₇ (Technology).

**Current Status**:
- ✅ **A₁, A₂, A₃, A₅**: Complete with 1789-2024 coverage
- 📥 **A₄, A₆**: Require external dataset downloads
- 🔧 **A₇**: Partially available data, needs confirmation/acquisition

---

## A₄ (Complexity/Diversity Quality) - Data Acquisition

### Formula (from CREATIVE_A_INDEX_PROXIES.md)
```
A₄ = 0.30×innovation_impact + 0.25×(1-gini) + 0.25×education_diversity + 0.20×economic_resilience
```

### Required Datasets

#### 1. Economic Complexity Index (ECI)
**Source**: Harvard Atlas of Economic Complexity
**URL**: https://atlas.cid.harvard.edu/
**Coverage**: 1963-2020
**Format**: Country-year panel data
**Variables Needed**:
- Economic Complexity Index (ECI)
- Product Complexity Index (PCI)
- Export diversity metrics

**Download Instructions**:
1. Visit https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/T4CHWJ
2. Download "country_partner_sitcproduct4digit_year.tab" (export data)
3. Download ECI rankings CSV
4. Expected size: ~500MB (export data), ~2MB (ECI rankings)

**Processing**:
- Extract country-level ECI scores by year
- Use as proxy for innovation_impact component (0.30 weight)

#### 2. Patent Data
**Source**: WIPO IP Statistics Data Center
**URL**: https://www.wipo.int/ipstats/en/
**Coverage**: 1883-2023 (country-level from ~1980+)
**Format**: Country-year applications and grants

**Download Instructions**:
1. Visit https://www.wipo.int/ipstats/en/statistics/country_profile/
2. Download "Patent applications by origin" dataset
3. Download "Patents in force" dataset
4. Expected size: ~10-20MB per file

**Processing**:
- Patents per capita as innovation output
- Combine with ECI for innovation_impact
- Focus on 1980+ for quality country coverage

#### 3. Gini Coefficient (Already Have!)
**Source**: World Bank / UNU-WIDER
**Current File**: `API_SI.POV.GINI_DS2_en_csv_v2_252305.zip` (19KB)
**Coverage**: 1960-2023
**Status**: ✅ **Already downloaded**

**Processing**:
- Extract and process ZIP file
- Create country-year panel
- Use (1-gini) for economic equality component (0.25 weight)

#### 4. Education Diversity/Quality
**Source**: UNESCO Institute for Statistics (UIS)
**URL**: http://data.uis.unesco.org/
**Coverage**: 1970-2024
**Variables Needed**:
- Tertiary education enrollment by field
- STEM graduation rates
- Education quality indices

**Download Instructions**:
1. Visit http://data.uis.unesco.org/
2. Navigate to "Education" → "Completion and graduation"
3. Download bulk data for tertiary education by field
4. Expected size: ~5-10MB

**Processing**:
- Calculate diversity index across educational fields
- STEM % of graduates as quality proxy
- Use for education_diversity component (0.25 weight)

#### 5. Economic Resilience
**Source**: World Bank / IMF Financial Soundness Indicators
**Current File**: `imf_fsi_raw.csv` (89MB) - May already have relevant data!
**Coverage**: 1990-2023
**Status**: 🔧 **Need to examine existing file**

**Download Instructions** (if needed):
1. World Bank economic volatility data: https://data.worldbank.org/
2. Download GDP growth volatility, trade openness, reserve adequacy
3. Expected size: ~5-10MB

**Processing**:
- Economic volatility (inverse of GDP growth std dev)
- Trade diversification
- Financial system stability
- Use for economic_resilience component (0.20 weight)

### A₄ Implementation Priority
**Estimated Coverage**: 1980-2020 (limited by patent data country coverage)
**Time to Complete**: 1-2 weeks (including downloads, processing, validation)
**Dependencies**: None - can proceed immediately

---

## A₆ (Wellbeing Quality) - Data Acquisition

### Formula (from CREATIVE_A_INDEX_PROXIES.md)
```
A₆ = 0.30×healthy_years_ratio + 0.25×life_satisfaction + 0.20×mental_health +
     0.15×(1-poverty) + 0.10×mortality_improvement
```

### Required Datasets

#### 1. WHO HALE (Healthy Life Expectancy)
**Source**: WHO Global Health Observatory
**URL**: https://www.who.int/data/gho
**Coverage**: 1990-2023
**Format**: Country-year HALE and life expectancy

**Download Instructions**:
1. Visit https://www.who.int/data/gho/data/indicators/indicator-details/GHO/gho-ghe-hale-healthy-life-expectancy-at-birth
2. Download full dataset (Excel or CSV)
3. Expected size: ~2-5MB

**Processing**:
- HALE / Life Expectancy ratio
- Use for healthy_years_ratio component (0.30 weight)

#### 2. World Happiness Report
**Source**: World Happiness Report
**URL**: https://worldhappiness.report/data/
**Coverage**: 2005-2024
**Format**: Country-year life satisfaction scores

**Download Instructions**:
1. Visit https://worldhappiness.report/data/
2. Download "DataForTable2.1.xls" (latest report)
3. Expected size: ~1-2MB

**Processing**:
- Life satisfaction / Cantril Ladder scores
- Normalize to 0-1 scale
- Use for life_satisfaction component (0.25 weight)

#### 3. Mental Health Data
**Source**: Our World in Data (IHME Global Burden of Disease)
**URL**: https://ourworldindata.org/mental-health
**Coverage**: 1990-2019
**Format**: Country-year prevalence rates

**Download Instructions**:
1. Visit https://ourworldindata.org/mental-health#mental-health-use-substance-use-and-suicide
2. Download "Share of population with mental health disorder" dataset
3. Expected size: ~5-10MB

**Processing**:
- (1 - mental_disorder_prevalence) as mental health quality
- Use for mental_health component (0.20 weight)

#### 4. Poverty Data
**Source**: World Bank / UN SDG Database
**URL**: https://data.worldbank.org/
**Coverage**: 1990-2023
**Format**: Country-year poverty headcount ratios

**Download Instructions**:
1. Visit https://data.worldbank.org/indicator/SI.POV.DDAY
2. Download "$2.15 per day poverty rate" dataset
3. Expected size: ~2-5MB

**Processing**:
- (1 - poverty_rate) as wellbeing quality
- Use for poverty component (0.15 weight)

#### 5. Mortality Improvement
**Source**: World Bank / WHO
**URL**: https://data.worldbank.org/indicator/SP.DYN.IMRT.IN
**Coverage**: 1960-2023
**Format**: Country-year infant mortality rates

**Download Instructions**:
1. Visit World Bank data portal
2. Download infant mortality and under-5 mortality datasets
3. Expected size: ~2-5MB

**Processing**:
- Year-over-year improvement rate
- Normalize to 0-1 scale
- Use for mortality_improvement component (0.10 weight)

### A₆ Implementation Priority
**Estimated Coverage**: 1990-2023 (limited by HALE and mental health data)
**Time to Complete**: 1-2 weeks
**Dependencies**: None - can proceed immediately

---

## A₇ (Technology Quality) - Data Assessment

### Formula (from CREATIVE_A_INDEX_PROXIES.md)
```
A₇ = 0.30×tech_access_equality + 0.30×beneficial_tech_share +
     0.20×sustainability + 0.20×efficiency_gains
```

### Current Data Status

#### 1. ITU ICT Indicators - ⚠️ NEEDS VERIFICATION
**Current File**: `ITU_regional_global_Key_ICT_indicator_aggregates_Nov_2025.xlsx` (110KB)
**Issue**: File name suggests "regional_global" aggregates, not country-level
**Need**: Country-level ICT access and usage data

**Action Required**:
1. Examine existing file to confirm data structure
2. If regional aggregates only, download country-level data:
   - Visit https://www.itu.int/en/ITU-D/Statistics/Pages/stat/default.aspx
   - Download "Individuals using the Internet" by country
   - Download "Mobile cellular subscriptions" by country
   - Expected size: ~5-10MB per indicator

**Processing** (if country-level):
- Internet access equality (Gini-style coefficient)
- Mobile penetration equality
- Use for tech_access_equality component (0.30 weight)

#### 2. Renewable Energy Data - 🔧 NEEDS CONFIRMATION
**Possible Source**: OWID Energy Data or IEA
**Coverage Needed**: 1990-2023 country-level
**Variables**: Renewable energy % of total, clean energy access

**Download Instructions**:
1. Our World in Data: https://github.com/owid/energy-data
2. Download "owid-energy-data.csv"
3. Expected size: ~10-20MB

**OR**

1. IEA World Energy Statistics: https://www.iea.org/data-and-statistics
2. Download renewable energy dataset
3. Expected size: ~20-50MB

**Processing**:
- Renewable % of total energy production
- Year-over-year growth in renewables
- Use for beneficial_tech_share component (0.30 weight)

#### 3. Environmental Sustainability - 📥 NEED TO DOWNLOAD
**Source**: UNEP Environmental Performance Index (EPI)
**URL**: https://epi.yale.edu/
**Coverage**: 2006-2024 (biennial)
**Format**: Country-year EPI scores

**Download Instructions**:
1. Visit https://epi.yale.edu/downloads
2. Download "EPI 2024 Results" Excel file
3. Download historical data (2006-2022)
4. Expected size: ~5-10MB total

**Processing**:
- Climate change performance scores
- Air quality metrics
- Use for sustainability component (0.20 weight)

#### 4. Energy Efficiency - 🔧 PARTIALLY AVAILABLE
**Source**: World Bank / IEA Energy Efficiency Indicators
**Coverage Needed**: 1990-2023
**Variables**: Energy intensity (GDP per unit energy), efficiency improvements

**Download Instructions**:
1. World Bank: https://data.worldbank.org/indicator/EG.EGY.PRIM.PP.KD
2. Download "Energy intensity level of primary energy"
3. Expected size: ~2-5MB

**OR**

1. IEA Efficiency database: https://www.iea.org/data-and-statistics/data-tools/energy-efficiency-indicators
2. Requires registration (free)
3. Expected size: ~10-20MB

**Processing**:
- Inverse of energy intensity as efficiency
- Year-over-year improvement rate
- Use for efficiency_gains component (0.20 weight)

### A₇ Implementation Priority
**Estimated Coverage**: 2000-2023 (limited by EPI data starting 2006, but can use OWID CO₂ data for earlier years)
**Time to Complete**: 3-5 days (if ITU country-level data confirmed available)
**Dependencies**: Need to verify ITU file structure first

---

## Implementation Roadmap

### Phase 1: Data Verification (1 day)
1. **Examine existing files**:
   - Unzip and process `API_SI.POV.GINI_DS2_en_csv_v2_252305.zip` (Gini for A₄)
   - Examine `imf_fsi_raw.csv` (89MB - may contain A₄ resilience data)
   - Check `ITU_regional_global_Key_ICT_indicator_aggregates_Nov_2025.xlsx` structure

2. **Update this document** with findings

### Phase 2: A₇ First (3-5 days) - IF Data Available
**Rationale**: Potentially quickest path to 5/7 harmonies

1. **IF** ITU file contains country-level data:
   - Create `process_technology_quality.py`
   - Download OWID energy data
   - Download EPI data (or use OWID CO₂ as proxy for early years)
   - Download World Bank energy intensity
   - Process and validate A₇

2. **Result**: 5/7 harmonies complete (A₁, A₂, A₃, A₅, A₇)

### Phase 3: A₄ Implementation (1-2 weeks)
**Priority**: Second priority (economic complexity is important)

1. Download Harvard Atlas ECI data
2. Download WIPO patent data
3. Process existing Gini data
4. Download UNESCO education data
5. Process IMF FSI data for resilience OR download World Bank alternatives
6. Create `process_complexity_quality.py`
7. Validate against expected quality gaps

### Phase 4: A₆ Implementation (1-2 weeks)
**Priority**: Third priority (wellbeing data most recent, shortest historical coverage)

1. Download WHO HALE data
2. Download World Happiness Report data
3. Download OWID mental health data
4. Download World Bank poverty data
5. Download mortality improvement data
6. Create `process_wellbeing_quality.py`
7. Validate against expected quality gaps

### Phase 5: Integration (3-5 days)
1. Compute provisional A(t) with available harmonies
2. Compute full A(t) = geometric_mean(A₁, A₂, A₃, A₄, A₅, A₆, A₇)
3. Calculate Gap(t) = K(t) - A(t) time series
4. Generate validation plots
5. Update manuscript with empirical results

---

## Expected Coverage Summary

| Harmony | Data Sources | Expected Coverage | Priority |
|---------|--------------|-------------------|----------|
| **A₁ Governance** | V-Dem | 1789-2024 | ✅ Complete |
| **A₂ Interconnection** | V-Dem | 1789-2024 | ✅ Complete |
| **A₃ Reciprocity** | V-Dem, Gini | 1789-2024 | ✅ Complete |
| **A₄ Complexity** | Harvard, WIPO, UNESCO, Gini | 1980-2020 | 2nd |
| **A₅ Knowledge** | V-Dem | 1789-2024 | ✅ Complete |
| **A₆ Wellbeing** | WHO, World Happiness, OWID | 1990-2023 | 3rd |
| **A₇ Technology** | ITU, OWID, EPI, World Bank | 2000-2023 | 1st |

**Full 7-harmony coverage**: Expected 2000-2020 (intersection of all datasets)
**Partial coverage (4-6 harmonies)**: Possible extension to 1789-2024 depending on final formulas

---

## Data Download Size Estimates

| Dataset | Size | Download Time (10 Mbps) |
|---------|------|-------------------------|
| Harvard Atlas ECI | ~500 MB | ~7 minutes |
| WIPO Patents | ~20 MB | ~20 seconds |
| UNESCO Education | ~10 MB | ~10 seconds |
| WHO HALE | ~5 MB | ~5 seconds |
| World Happiness | ~2 MB | ~2 seconds |
| OWID Mental Health | ~10 MB | ~10 seconds |
| OWID Energy | ~20 MB | ~20 seconds |
| EPI Data | ~10 MB | ~10 seconds |
| World Bank (various) | ~20 MB | ~20 seconds |
| **Total** | **~600 MB** | **~10 minutes** |

---

## Quality Gap Validation Targets

Based on A₁, A₂, A₃, A₅ results, we expect:

| Harmony | Expected Gap | Current Result | Status |
|---------|--------------|----------------|--------|
| H1 Governance | 30-45% | 35.4% | ✅ Within range |
| H2 Interconnection | 30-45% | 28.6% | ⚠️ Slightly low but reasonable |
| H3 Reciprocity | 35-50% | 27.0% | ⚠️ Below range but consistent |
| H4 Complexity | 25-40% | TBD | 🔮 To validate |
| H5 Knowledge | 25-40% | 30.7% | ✅ Within range |
| H6 Wellbeing | 30-50% | TBD | 🔮 To validate |
| H7 Technology | 35-50% | TBD | 🔮 To validate |

**Hypothesis**: Quality gaps should cluster around **25-45%** across all harmonies, reflecting modern civilization's pattern of high coordination capacity but moderate quality utilization.

---

## Next Immediate Actions

1. **Verify existing data files** (1 hour):
   ```bash
   # Process Gini data
   cd /srv/luminous-dynamics/kosmic-lab/historical_k/data_sources/external
   unzip API_SI.POV.GINI_DS2_en_csv_v2_252305.zip

   # Examine IMF FSI data structure
   head -100 imf_fsi_raw.csv

   # Check ITU file (requires openpyxl/pandas)
   python3 -c "import pandas as pd; df = pd.read_excel('ITU_regional_global_Key_ICT_indicator_aggregates_Nov_2025.xlsx'); print(df.head())"
   ```

2. **Download OWID Energy Data** (5 minutes):
   ```bash
   wget https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv
   ```

3. **Start with provisional A(t)** using A₁, A₂, A₃, A₅ (2 hours):
   ```python
   # Create provisional A(t) = geometric_mean(A₁, A₂, A₃, A₅)
   # This gives us 4/7 harmonies coverage for 1789-2024!
   ```

4. **User Decision Point**:
   - **Option A**: Start downloads for A₄, A₆, A₇ (parallel, ~1 hour total)
   - **Option B**: Focus on provisional A(t) analysis first, downloads later
   - **Option C**: Prioritize specific harmony based on manuscript narrative needs

---

## References

- **Harvard Atlas**: https://atlas.cid.harvard.edu/
- **WIPO**: https://www.wipo.int/ipstats/en/
- **UNESCO**: http://data.uis.unesco.org/
- **WHO GHO**: https://www.who.int/data/gho
- **World Happiness**: https://worldhappiness.report/data/
- **Our World in Data**: https://ourworldindata.org/
- **World Bank**: https://data.worldbank.org/
- **Yale EPI**: https://epi.yale.edu/
- **IEA**: https://www.iea.org/data-and-statistics

---

*"If human minds can sense quality differences, empirical traces must exist in measurable data." - This plan operationalizes that philosophy for the remaining three harmonies.*
