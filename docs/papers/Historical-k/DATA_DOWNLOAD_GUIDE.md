# Phase 2 Data Download Guide

**Purpose**: Data sources for provisional A(t) actualization index
**Your Task**: Download these datasets while I update the manuscript

---

## Priority 1: Trust & Quality Indicators

### 1. World Values Survey (WVS)
**URL**: https://www.worldvaluessurvey.org/WVSDocumentationWVL.jsp
**Download**: Longitudinal data file (1981-2022)
**Variables needed**:
- Generalized trust (V24): "Most people can be trusted"
- Confidence in institutions: V108-V123 (government, parliament, courts)
- Save to: `historical_k/data_sources/external/wvs_longitudinal.csv`

### 2. World Happiness Report (WHR)
**URL**: https://worldhappiness.report/data/
**Download**: Complete dataset (2005-2023)
**Variables needed**:
- Life satisfaction (Cantril Ladder)
- Log GDP per capita
- Social support
- Healthy life expectancy
- Freedom to make life choices
- Generosity
- Perceptions of corruption
- Save to: `historical_k/data_sources/external/whr_complete.csv`

### 3. Transparency International - Corruption Perceptions Index (CPI)
**URL**: https://www.transparency.org/en/cpi/2023
**Download**: Time series data (1995-2023)
**Note**: Download historical data page
**Save to**: `historical_k/data_sources/external/cpi_timeseries.csv`

### 4. Pew Global Attitudes
**URL**: https://www.pewresearch.org/global/datasets/
**Download**: Trust in government datasets
**Years**: 2002-2023 (various surveys)
**Save to**: `historical_k/data_sources/external/pew_trust/`

---

## Priority 2: Performance & Effectiveness

### 5. World Bank Governance Indicators
**URL**: https://info.worldbank.org/governance/wgi/
**Download**: All 6 indicators (1996-2022)
**Indicators**:
- Voice and Accountability
- Political Stability
- Government Effectiveness ← KEY
- Regulatory Quality
- Rule of Law
- Control of Corruption
**Save to**: `historical_k/data_sources/external/wgi_timeseries.csv`

### 6. V-Dem Democracy Indices (CRITICAL - Best historical depth)
**URL**: https://www.v-dem.net/data/the-v-dem-dataset/
**Download**: V-Dem Dataset v13 (1789-2022)
**Variables needed**:
- Liberal democracy index (v2x_libdem)
- Electoral democracy index (v2x_polyarchy)
- Participatory democracy index (v2x_partipdem)
- Deliberative democracy index (v2x_delibdem)
- Egalitarian democracy index (v2x_egaldem)
**Format**: Country-year panel
**Save to**: `historical_k/data_sources/external/vdem_v13.csv`
**Note**: This is the BEST source for H1 (Governance) back to 1810!

### 7. OECD Better Life Index
**URL**: https://www.oecdbetterlifeindex.org/data/
**Download**: All indicators (2011-2023)
**Save to**: `historical_k/data_sources/external/oecd_bli.csv`

### 8. WHO Mental Health Atlas
**URL**: https://www.who.int/teams/mental-health-and-substance-use/data-research
**Download**: Mental health indicators (2005-2020)
**Save to**: `historical_k/data_sources/external/who_mental_health.csv`

---

## Priority 3: Information & Knowledge Quality

### 9. PISA Scores (OECD)
**URL**: https://www.oecd.org/pisa/data/
**Download**: PISA datasets (2000-2022)
**Variables needed**:
- Problem-solving scores
- Science literacy scores
- Reading scores
- Mathematics scores
**Save to**: `historical_k/data_sources/external/pisa_scores.csv`

### 10. ITU Digital Divide Metrics
**URL**: https://www.itu.int/en/ITU-D/Statistics/Pages/stat/default.aspx
**Download**: ICT indicators (2000-2023)
**Variables**:
- Internet access
- Mobile subscriptions
- Digital skills
**Save to**: `historical_k/data_sources/external/itu_digital_divide.csv`

---

## Priority 4: Economic Quality

### 11. World Bank - Gini Coefficients
**URL**: https://data.worldbank.org/indicator/SI.POV.GINI
**Download**: Gini index time series (1960-2023)
**Save to**: `historical_k/data_sources/external/gini_coefficients.csv`

### 12. World Bank - Shared Prosperity
**URL**: https://www.worldbank.org/en/topic/poverty/brief/global-database-of-shared-prosperity
**Download**: Shared prosperity database
**Save to**: `historical_k/data_sources/external/shared_prosperity.csv`

### 13. IMF Financial Stability Index
**URL**: https://data.imf.org/?sk=388DFA60-1D26-4ADE-B505-A05A558D9A42
**Download**: Financial Soundness Indicators (1980-2023)
**Save to**: `historical_k/data_sources/external/imf_fsi.csv`

---

## Download Instructions

### Quick Start
```bash
# Create directory structure
mkdir -p historical_k/data_sources/external/{wvs,pew_trust}

# Start with easiest downloads (have direct CSV):
# 1. World Happiness Report (single CSV)
# 2. Transparency International CPI (Excel → convert to CSV)
# 3. World Bank indicators (bulk download)
# 4. V-Dem (CRITICAL - register for download)
```

### Critical First Steps

**1. V-Dem (MUST DO FIRST)**
- Register at https://www.v-dem.net/
- Download V-Dem Dataset v13
- This gives us H1 (Governance) back to 1810!
- File is large (~200MB) but essential

**2. World Values Survey**
- Download longitudinal aggregate file
- Focus on trust variables (V24, V108-V123)

**3. World Happiness Report**
- Single CSV download
- Easy to process
- Critical for wellbeing validation

### Processing Notes

**After downloading**:
- Save all files to `historical_k/data_sources/external/`
- Keep original files unchanged (for reproducibility)
- Create processing scripts in `historical_k/process_external_data.py`
- Document data cleaning decisions in `historical_k/data_sources/external/PROCESSING_LOG.md`

---

## Estimated Download Time

| Dataset | Size | Time | Priority |
|---------|------|------|----------|
| V-Dem | 200 MB | 10 min | **HIGH** |
| WVS | 50 MB | 5 min | **HIGH** |
| WHR | 2 MB | 1 min | **HIGH** |
| CPI | 1 MB | 1 min | **HIGH** |
| WGI | 5 MB | 2 min | Medium |
| PISA | 100 MB | 10 min | Medium |
| Others | 50 MB | 10 min | Low |
| **Total** | **~400 MB** | **~40 min** | - |

---

## Next Steps After Download

1. **Document what you downloaded**: Update `PROCESSING_LOG.md`
2. **Check data quality**: Run basic pandas checks (missing values, year range)
3. **Signal completion**: Let me know which datasets are ready
4. **I'll create processing scripts**: To compute A₁-A₇ from raw data

---

## Questions & Troubleshooting

**Q: Need to register for access?**
- V-Dem: Yes (free, instant)
- WVS: No registration needed for aggregate data
- WHR: No registration needed
- Others: Most are open access

**Q: Data format issues?**
- Excel files: Use pandas `read_excel()` then save as CSV
- SPSS files (.sav): Use pandas `read_spss()` then save as CSV
- Stata files (.dta): Use pandas `read_stata()` then save as CSV

**Q: Missing years for some countries?**
- Expected - we'll handle interpolation in processing
- Focus on getting major countries (US, China, EU, etc.)

---

**Your Mission**: Start with Priority 1 datasets (WVS, WHR, CPI, Pew). These are most critical for Phase 2.

**My Mission**: Update manuscript Methods/Results/Discussion for Phase 1 while you download.

**Parallel work maximizes progress!** ✅
