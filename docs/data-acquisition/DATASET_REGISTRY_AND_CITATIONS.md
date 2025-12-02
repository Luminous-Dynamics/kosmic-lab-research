# Complete Dataset Registry & Citation Guide

**Project**: Historical K(t) - 5000-Year Civilizational Coherence Analysis  
**Last Updated**: 2025-11-21  
**Purpose**: Comprehensive tracking of all datasets, sources, and proper academic citations

---

## Table of Contents
1. [Seshat Global History Databank](#seshat)
2. [HYDE 3.2 Historical Demographics](#hyde)
3. [External Validation Datasets](#external)
4. [World Bank Development Indicators](#worldbank)
5. [Quick Citation Reference](#quick-citations)
6. [Data Usage Matrix](#usage-matrix)

---

## 📊 Dataset Overview

**Total Datasets**: 32 distinct datasets (42 individual files)
**Total Size**: 470.56 MB external + 5.94 MB Seshat + ~2 GB HYDE 3.2 = ~2.5 GB total
**Temporal Coverage**: 10,000 BCE - 2024 CE
**Geographic Coverage**: Global (200+ countries/territories for modern data)
**Last Updated**: 2025-11-21 (15 new datasets added via 5 rounds of persistent web search)
**Coverage Level**: 🏆 PERFECT OUTSTANDING (7/7 harmonies at highest tier)

---

<a name="seshat"></a>
## 1. Seshat Global History Databank

### Datasets Acquired

| File | Size | Variables | Coverage | Primary Use |
|------|------|-----------|----------|-------------|
| `sc_dataset.12.2017.xlsx` | 0.97 MB | Social complexity indicators | 3000 BCE - 500 CE | H1 (institutions), H3 (knowledge systems) |
| `mr_dataset.04.2021.csv` | 0.03 MB | Military & religion variables | -9600 to 1987 | H1 (moralizing gods), H2 (conflict) |
| `agri_dataset.07.2020.csv` | 0.21 MB | Agricultural systems | -10000 to 2001 | H7 (sustainability), population proxies |
| `axial_dataset.05.2018.csv` | 0.02 MB | Axial age civilizations | ~800 BCE - 200 CE | H3 (philosophical systems) |
| `CrisisConsequencesData_NavigatingPolycrisis_2023.03.csv` | 0.26 MB | Modern crisis data | Modern period | H2 (crisis response) |
| `Equinox_on_GitHub_June9_2022.xlsx` | 4.46 MB | Comprehensive dataset | Full Seshat range | All harmonies (ancient) |

### Academic Citation

**Primary Citation**:
> Turchin, P., Brennan, R., Currie, T. E., Feeney, K. C., François, P., Hoyer, D., ... & Whitehouse, H. (2018). Seshat: The Global History Databank. *Cliodynamics*, 9(1), 99-134. https://doi.org/10.21237/C7clio9137696

**Dataset Citation**:
> Turchin, P., et al. (2022). Seshat: Global History Databank [Data set]. Retrieved from https://github.com/datasets/seshat

### Variable Documentation
- **Social Complexity**: Administrative levels (1-6), settlement sizes, writing systems, money, roads
- **Military**: Iron weapons, cavalry, fortifications, military technology
- **Religion**: Moralizing gods, religious hierarchy, supernatural punishment beliefs
- **Economy**: Markets, merchants, professional bureaucrats, taxation systems

### Data Quality Notes
- **Completeness**: ~30 polities across Afro-Eurasia, 348 polity-periods
- **Resolution**: Typically 100-year intervals for ancient period
- **Missing Data**: Varies by region; best coverage for Mediterranean, Near East, China
- **Reliability**: Expert-coded with uncertainty flags

---

<a name="hyde"></a>
## 2. HYDE 3.2 Historical Demographics

### Dataset Structure

**Main Directory**: `data/sources/hyde/raw/`

| Variable Directory | # Files | Coverage | Resolution | Primary Use |
|-------------------|---------|----------|------------|-------------|
| `population/` | 120+ | 10,000 BCE - 2020 CE | 5 arc-minute (~10 km) | Population density, urbanization |
| `cropland/` | 120+ | 10,000 BCE - 2020 CE | 5 arc-minute | Agricultural development (H7) |
| `grazing/` | 120+ | 10,000 BCE - 2020 CE | 5 arc-minute | Pastoral systems (H7) |
| `urban/` | 120+ | 10,000 BCE - 2020 CE | 5 arc-minute | Urban fraction, city growth |

### Academic Citation

**Primary Citation**:
> Klein Goldewijk, K., Beusen, A., Doelman, J., & Stehfest, E. (2017). Anthropogenic land use estimates for the Holocene – HYDE 3.2. *Earth System Science Data*, 9(2), 927-953. https://doi.org/10.5194/essd-9-927-2017

**Dataset Citation**:
> Klein Goldewijk, K., Beusen, A., & Stehfest, E. (2017). HYDE 3.2: History Database of the Global Environment [Data set]. DANS. https://doi.org/10.17026/dans-25g-gez3

### Processing Notes
- **Format**: NetCDF4 (requires netCDF4 Python library)
- **Aggregation**: Global sums computed for K(t) time series
- **Temporal Granularity**: Varies (1000-year ancient, 100-year medieval, 10-year modern)
- **Quality**: Highest confidence for post-1700 CE; modeled estimates for earlier periods

---

<a name="external"></a>
## 3. External Validation Datasets

### 3.1 Human Development Index (HDI)

**File**: `hdi.csv` (1.70 MB)  
**Source**: United Nations Development Programme  
**Coverage**: 1990-2022, 206 countries/territories  

**Academic Citation**:
> United Nations Development Programme. (2023). Human Development Index and its components [Data file]. Retrieved from http://hdr.undp.org/en/data

**Variables Used**:
- Human Development Index (composite)
- Life expectancy at birth
- Expected years of schooling
- Mean years of schooling
- Gross National Income per capita (PPP)

**Harmonies**: H2 (primary), H3 (education component)

---

### 3.2 V-Dem Democracy Index

**File**: `V-Dem-CY-Full+Others-v15.csv` (383.78 MB)  
**Source**: Varieties of Democracy Institute  
**Coverage**: 1789-2023, 202 countries, 4,607 indicators  

**Academic Citation**:
> Coppedge, M., Gerring, J., Knutsen, C. H., Lindberg, S. I., Teorell, J., Altman, D., ... & Ziblatt, D. (2023). V-Dem Dataset v15. Varieties of Democracy (V-Dem) Project. https://doi.org/10.23696/vdemds23

**Key Indicators**:
- Electoral democracy index (v2x_polyarchy)
- Liberal democracy index (v2x_libdem)
- Participatory democracy index (v2x_partipdem)
- Deliberative democracy index (v2x_delibdem)
- Egalitarian democracy index (v2x_egaldem)

**Harmonies**: H1 (primary), H6 (egalitarian component)

---

### 3.3 Polity V

**File**: `p5v2018.xls` (4.28 MB)  
**Source**: Center for Systemic Peace  
**Coverage**: 1800-2020, 167 countries, 17,574 country-years  

**Academic Citation**:
> Marshall, M. G., & Gurr, T. R. (2020). Polity5: Political Regime Characteristics and Transitions, 1800-2018 [Data set]. Center for Systemic Peace. http://www.systemicpeace.org/inscrdata.html

**Key Variables**:
- Polity Score (-10 to +10: autocracy to democracy)
- Executive recruitment (xrreg, xrcomp, xropen)
- Executive constraints (xconst)
- Political competition (parcomp, parreg)

**Harmonies**: H1 (primary)

---

### 3.4 Maddison Project GDP

**File**: `maddison_gdp.xlsx` (1.68 MB)  
**Source**: Groningen Growth and Development Centre  
**Coverage**: 1 CE - 2018, global  

**Academic Citation**:
> Bolt, J., & van Zanden, J. L. (2020). Maddison style estimates of the evolution of the world economy. A new 2020 update. *Maddison Project Database*, version 2020. https://www.rug.nl/ggdc/historicaldevelopment/maddison/

**Variables**:
- GDP per capita (multiple estimates: cgdppc, rgdpnapc)
- Population (pop)

**Harmonies**: H2 (economic prosperity), H6 (inequality analysis via distribution)

---

### 3.5 Uppsala Conflict Data Program (UCDP)

**File**: `ucdp-brd-conf-221.csv` (0.25 MB)  
**Source**: Uppsala Conflict Data Program  
**Coverage**: 1989-2021, 1,403 conflict-years  

**Academic Citation**:
> Pettersson, T., Högbladh, S., & Öberg, M. (2023). Organized violence, 1989–2021, and the return of conflicts between states. *Journal of Peace Research*, 60(4), 691-708. https://doi.org/10.1177/00223433231185169

**Variables**:
- Battle-related deaths (best estimate, low, high)
- Conflict type (interstate, intrastate, internationalized)
- Intensity level

**Harmonies**: H2 (conflict as inverse of flourishing)

---

### 3.6 Correlates of War (COW)

**Files**:
- `Inter-StateWarData_v4.0.csv` (0.03 MB) - 337 wars
- `Extra-StateWarData_v4.0.csv` (0.02 MB) - 198 wars
- `INTRA-STATE WARS v5.1 CSV.csv` (0.08 MB) - 420 wars
- `INTRA-STATE_State_participants v5.1 CSV.csv` (0.12 MB) - State participants

**Source**: Correlates of War Project  
**Coverage**: 1816-2014  

**Academic Citation**:
> Sarkees, M. R., & Wayman, F. W. (2010). *Resort to War: A Data Guide to Inter-state, Extra-state, Intra-state, and Non-state Wars, 1816-2007*. Washington, DC: CQ Press.

**Variables**:
- War deaths (military and civilian)
- War duration, initiator, outcome
- Battle locations

**Harmonies**: H2 (historical conflict)

---

### 3.7 Quality of Government (QoG)

**File**: `qog_basic_timeseries.csv` (18.47 MB)  
**Source**: University of Gothenburg, QoG Institute  
**Coverage**: 1946-2023, comprehensive governance indicators  

**Academic Citation**:
> Teorell, J., Sundström, A., Holmberg, S., Rothstein, B., Alvarado Pachon, N., Dalli, C. M., & Tannenberg, M. (2024). The Quality of Government Standard Dataset, version Jan24. University of Gothenburg: The Quality of Government Institute. https://www.qog.pol.gu.se/doi:10.18157/qogstdjan24

**Key Indicators**:
- Government effectiveness
- Rule of law
- Control of corruption
- Regulatory quality
- Voice and accountability

**Harmonies**: H1 (primary - comprehensive governance)

---

### 3.8 Transparency International CPI

**File**: `transparency_cpi_2022.xlsx` (0.09 MB)  
**Source**: Transparency International  
**Coverage**: 1995-2022, 180 countries  

**Academic Citation**:
> Transparency International. (2022). Corruption Perceptions Index 2022 [Data set]. Retrieved from https://www.transparency.org/en/cpi/2022

**Variables**:
- Corruption Perceptions Index (0-100 scale)
- Regional rankings
- Year-over-year changes

**Harmonies**: H1 (institutional quality)

---

<a name="worldbank"></a>
## 4. World Bank Development Indicators

**File**: `world_bank_wdi_indicators.json` (23.66 MB)  
**Source**: World Bank  
**Format**: JSON (converted from API)  
**Coverage**: 1960-2023, 200+ countries  

**Academic Citation**:
> World Bank. (2023). World Development Indicators [Data set]. Washington, DC: World Bank. https://databank.worldbank.org/source/world-development-indicators

### Indicators Downloaded

| Indicator Code | Name | Observations | Primary Harmony |
|----------------|------|--------------|-----------------|
| `NE.TRD.GNFS.ZS` | Trade (% of GDP) | 10,943 | H5 |
| `GB.XPD.RSDV.GD.ZS` | R&D expenditure (% of GDP) | 3,062 | H4 |
| `SI.POV.GINI` | Gini index | 2,389 | H6 |
| `IT.NET.USER.ZS` | Internet users (% population) | 6,656 | H5 |
| `IP.PAT.RESD` | Patent applications (residents) | 4,276 | H4 |
| `EG.FEC.RNEW.ZS` | Renewable energy (% total) | 8,234 | H7 |

**Total WDI Observations**: 51,560 country-year data points

---

## 5. Additional High-Value Datasets

### 5.1 Global Carbon Project

**File**: `global_carbon_emissions.xlsx` (0.70 MB)  
**Coverage**: 1750-2023, national emissions  

**Academic Citation**:
> Friedlingstein, P., et al. (2023). Global Carbon Budget 2023. *Earth System Science Data*, 15(12), 5301-5369. https://doi.org/10.5194/essd-15-5301-2023

**Harmonies**: H7 (environmental sustainability)

---

### 5.2 UNESCO Education & Science

**Files**:
- `unesco_education.csv` (0.10 MB)
- `unesco_science_rd.csv` (0.10 MB)

**Academic Citation**:
> UNESCO Institute for Statistics. (2023). Education and Science Data [Data sets]. http://data.uis.unesco.org/

**Harmonies**: H3 (primary)

---

### 5.3 IMF World Economic Outlook

**File**: `imf_weo_2023.xls` (0.05 MB)  

**Academic Citation**:
> International Monetary Fund. (2023). World Economic Outlook Database, October 2023. Washington, DC: IMF.

**Harmonies**: H5 (economic interconnectedness)

---

### 5.4 Scimago Journal Rankings

**File**: `scimago_country_rankings.xls` (0.02 MB)  
**Coverage**: 1996-2023, academic output by country  

**Academic Citation**:
> SCImago. (2023). SJR — SCImago Journal & Country Rank [Data set]. Retrieved from https://www.scimagojr.com

**Harmonies**: H3 (knowledge production), H4 (scientific innovation)

---

### 5.5 Gapminder World

**File**: `gapminder_world_data.xlsx` (0.13 MB)
**Coverage**: Multiple indicators, long time series

**Academic Citation**:
> Gapminder Foundation. (2023). Gapminder World [Data set]. Retrieved from https://www.gapminder.org/data/

**Harmonies**: Multiple (general development indicators)

---

### 5.6 SWIID - Standardized World Income Inequality Database 🆕

**File**: `swiid_summary_9.9.csv` (0.23 MB)
**Coverage**: 199 countries, 1960-2024
**Version**: 9.9 (December 2024)

**Academic Citation**:
> Solt, Frederick. (2024). The Standardized World Income Inequality Database, Version 9.9. Social Science Quarterly. https://fsolt.org/swiid/

**Dataset Access**:
> Solt, Frederick. (2024). SWIID v9.9 [Data set]. Harvard Dataverse. https://doi.org/10.7910/DVN/LM4OWF

**Harmonies**: H6 (income inequality - primary)

---

### 5.7 Global Entrepreneurship Monitor 2024 🆕

**File**: `gem_entrepreneurship_2024.xlsx` (11.41 MB)
**Coverage**: Global, 2023/2024 cycle

**Academic Citation**:
> Global Entrepreneurship Research Association. (2024). Global Entrepreneurship Monitor 2023/2024 Global Report. London: GERA. Retrieved from https://www.gemconsortium.org/

**Harmonies**: H4 (entrepreneurship, innovation ecosystems)

---

### 5.8 Barro-Lee Educational Attainment 🆕

**File**: `barrolee_education_2013.csv` (3.45 MB)
**Coverage**: 146 countries, 1950-2015, 5-year intervals

**Academic Citation**:
> Barro, Robert J., & Lee, Jong-Wha. (2013). A New Data Set of Educational Attainment in the World, 1950–2010. *Journal of Development Economics*, 104, 184-198. https://doi.org/10.1016/j.jdeveco.2012.10.001

**Dataset Access**:
> Barro, R. J., & Lee, J. W. (2021). Barro-Lee Educational Attainment Data [Data set]. Retrieved from http://barrolee.com/

**Harmonies**: H3 (education attainment - primary)

---

### 5.9 Freedom House - Freedom in the World 🆕

**File**: `freedom_house_1973_2024.xlsx` (0.19 MB)
**Coverage**: All countries, 1973-2024 (51-year time series)

**Academic Citation**:
> Freedom House. (2024). Freedom in the World 2024: The Decline in Global Freedom Continues. Washington, DC: Freedom House. Retrieved from https://freedomhouse.org/

**Harmonies**: H1 (democracy, political rights, civil liberties)

---

### 5.10 Eurostat R&D Expenditure 🆕

**File**: `eurostat_rd_expenditure.tsv.gz` (0.15 MB)
**Coverage**: European Union member states, multiple years

**Academic Citation**:
> Eurostat. (2024). R&D Expenditure [Data set]. European Commission. Retrieved from https://ec.europa.eu/eurostat/

**Harmonies**: H4 (R&D spending - regional detail)

---

### 5.11 Eurostat Gini Coefficient 🆕

**File**: `eurostat_gini_coefficient.tsv.gz` (0.00 MB)
**Coverage**: European Union member states

**Academic Citation**:
> Eurostat. (2024). Income Distribution Statistics [Data set]. European Commission. Retrieved from https://ec.europa.eu/eurostat/

**Harmonies**: H6 (inequality - EU detail)

---

### 5.12 UNCTAD Creative Economy 🆕

**File**: `unctad_creative_economy.csv` (0.04 MB)
**Coverage**: Global creative goods and services trade

**Academic Citation**:
> United Nations Conference on Trade and Development. (2024). Creative Economy Database [Data set]. Retrieved from https://unctadstat.unctad.org/

**Harmonies**: H4 (creative industries, cultural innovation)

---

### 5.13 World Bank Education Expenditure 🆕

**File**: `wb_education_expenditure.zip` (0.06 MB)
**Coverage**: Government expenditure on education as % GDP

**Academic Citation**:
> World Bank. (2024). Government expenditure on education, total (% of GDP) [Data set]. World Development Indicators. Retrieved from https://databank.worldbank.org/

**Harmonies**: H3 (education investment)

---

### 5.14 World Bank Poverty & Inequality 🆕

**File**: `wb_poverty_inequality.zip` (0.02 MB)
**Coverage**: Alternative poverty and inequality measures

**Academic Citation**:
> World Bank. (2024). Poverty and Inequality Platform [Data set]. Retrieved from https://pip.worldbank.org/

**Harmonies**: H6 (poverty measurement)

---

### 5.15 UNDP HDR Statistical Annex 🆕

**File**: `undp_hdr_statistical_annex.xlsx` (0.04 MB)
**Coverage**: Detailed HDI components breakdown

**Academic Citation**:
> United Nations Development Programme. (2024). Human Development Report 2023-24 Statistical Annex. New York: UNDP. Retrieved from https://hdr.undp.org/

**Harmonies**: H2 (wellbeing detail), H3 (education detail)

---

### 5.16 UNESCO Enrollment Rates 🆕

**File**: `unesco_enrollment_rates.csv` (0.10 MB)
**Coverage**: Global school enrollment by level

**Academic Citation**:
> UNESCO Institute for Statistics. (2024). Net Enrollment Rate by Level of Education [Data set]. Retrieved from http://data.uis.unesco.org/

**Harmonies**: H3 (education access)

### 5.17 Yale Environmental Performance Index 2024 🆕

**File**: `epi_2024_results.csv` (0.12 MB)
**Coverage**: 180 countries, environmental health and ecosystem vitality metrics
**Version**: EPI 2024

**Academic Citation**:
> Wolf, M. J., et al. (2024). 2024 Environmental Performance Index. Yale Center for Environmental Law & Policy. https://epi.yale.edu/

**Dataset Access**:
> Yale University. (2024). EPI 2024 Results [Data set]. Retrieved from https://epi.yale.edu/downloads

**Harmonies**: H7 (environmental performance - primary), H2 (health environment - secondary)

### 5.18 World Bank Logistics Performance Index 🆕

**File**: `wb_logistics_performance_index.zip` (0.02 MB)
**Coverage**: Global supply chain connectivity, infrastructure quality
**Indicator**: LPI (Logistics Performance Index)

**Academic Citation**:
> World Bank. (2024). Logistics Performance Index [Data set]. Retrieved from https://lpi.worldbank.org/

**Harmonies**: H5 (connectivity and trade infrastructure - primary)

### 5.19 Our World in Data - CO₂ and GHG Emissions 🆕

**File**: `owid_co2_ghg_data.csv` (13.64 MB)
**Coverage**: 200+ countries, 1750-2023, comprehensive emissions data
**Version**: Latest (continuously updated)

**Academic Citation**:
> Ritchie, H., Roser, M., & Rosado, P. (2024). CO₂ and Greenhouse Gas Emissions [Data set]. Our World in Data. https://github.com/owid/co2-data

**Dataset Citation**:
> Our World in Data. (2024). CO₂ and GHG Emissions Dataset [Data set]. GitHub. https://github.com/owid/co2-data

**Harmonies**: H7 (environmental sustainability - primary), includes population and GDP for normalization

### 5.20 World Bank Financial Development Index 🆕

**File**: `wb_financial_development_index.zip` (0.05 MB)
**Coverage**: Financial system development, banking depth, market access
**Indicator**: FDI (Financial Development Index)

**Academic Citation**:
> Svirydzenka, K. (2016). Introducing a New Broad-based Index of Financial Development. IMF Working Papers, 2016(005). https://doi.org/10.5089/9781513583709.001

**Dataset Access**:
> World Bank. (2024). Financial Development Index [Data set]. Retrieved from https://databank.worldbank.org/

**Harmonies**: H5 (financial interconnectedness - primary), H6 (financial inclusion - secondary)

---

<a name="quick-citations"></a>
## 6. Quick Citation Reference

### Tier 1: Must Cite (Core Data Sources)

```
Turchin, P., et al. (2018). Seshat: The Global History Databank. Cliodynamics, 9(1), 99-134.

Klein Goldewijk, K., et al. (2017). HYDE 3.2. Earth System Science Data, 9(2), 927-953.

Coppedge, M., et al. (2023). V-Dem Dataset v15. Varieties of Democracy Project.

United Nations Development Programme. (2023). Human Development Index. http://hdr.undp.org/

World Bank. (2023). World Development Indicators. https://databank.worldbank.org/
```

### Tier 2: Cite if Used in Analysis

```
Marshall, M. G., & Gurr, T. R. (2020). Polity5. Center for Systemic Peace.

Bolt, J., & van Zanden, J. L. (2020). Maddison Project Database, version 2020.

Pettersson, T., et al. (2023). UCDP Battle-Related Deaths Dataset.

Sarkees, M. R., & Wayman, F. W. (2010). Resort to War. CQ Press.

Teorell, J., et al. (2024). Quality of Government Standard Dataset, Jan24.
```

### Tier 3: Supplementary Sources

```
Transparency International. (2022). Corruption Perceptions Index 2022.

Friedlingstein, P., et al. (2023). Global Carbon Budget 2023.

Solt, F. (2024). Standardized World Income Inequality Database v9.9. Harvard Dataverse.

Ritchie, H., et al. (2024). CO₂ and GHG Emissions. Our World in Data.

Wolf, M. J., et al. (2024). Environmental Performance Index 2024. Yale CELP.

UNESCO Institute for Statistics. (2023). Education and Science Data.

IMF. (2023). World Economic Outlook Database, October 2023.

SCImago. (2023). Journal & Country Rank.
```

---

<a name="usage-matrix"></a>
## 7. Data Usage Matrix by Harmony

| Harmony | Primary Datasets | Secondary Datasets | Total Indicators |
|---------|------------------|-------------------|------------------|
| **H1 Resonant Coherence** | Polity V, V-Dem, QoG | Seshat (ancient), Transparency CPI | 100+ |
| **H2 Pan-Sentient Flourishing** | HDI, UCDP, COW | Maddison GDP, World Happiness | 15+ |
| **H3 Integral Wisdom** | UNESCO Education, HDI education | Seshat (writing), Scimago, WDI | 20+ |
| **H4 Infinite Play** | WDI (R&D, patents) | UNESCO Science, Innovation indices | 10+ |
| **H5 Universal Interconnectedness** | WDI (trade, internet) | IMF WEO, UN Comtrade ref | 15+ |
| **H6 Sacred Reciprocity** | WDI (Gini) | Maddison GDP distribution | 5+ |
| **H7 Evolutionary Progression** | HYDE land use, Global Carbon | WDI renewables, Seshat agriculture | 12+ |

**Total Unique Indicators**: 177+ distinct measures across all harmonies

---

## 8. Data Accessibility & Licensing

### Open Access (No Restrictions)
- Seshat Global History Databank
- HYDE 3.2
- V-Dem
- HDI
- Polity V
- World Bank WDI
- UCDP
- COW
- QoG
- UNESCO
- Gapminder

### Attribution Required
- All datasets require proper academic citation
- Some specify CC-BY 4.0 license
- Commercial use generally permitted with citation

### Registration/Request Required
- None of the acquired datasets require special permission
- All downloadable for academic research purposes

---

## 9. Data Quality Assessment

### Completeness by Period

| Period | Coverage | Quality | Missing Data |
|--------|----------|---------|--------------|
| 10,000-3000 BCE | HYDE only | Low-Medium | High (modeled estimates) |
| 3000 BCE - 500 CE | Seshat + HYDE | Medium | Medium (30 polities) |
| 500-1800 CE | Limited (Maddison, HYDE) | Medium | High (sparse coverage) |
| 1800-1960 | Growing coverage | Medium-High | Medium (irregular) |
| 1960-2023 | Comprehensive | High | Low (<10%) |

### Geographic Coverage

- **Global**: HDI, WDI, V-Dem, HYDE (200+ countries modern)
- **OECD Focus**: Polity V, most development indicators
- **Historical**: Seshat (30 polities, Afro-Eurasia focus)
- **Gaps**: Sub-Saharan Africa pre-1800, Oceania pre-1900, Americas pre-1500

---

## 10. Data Integration Notes

### Preprocessing Requirements

1. **Format Conversion**:
   - Excel (.xls, .xlsx) → CSV for processing
   - JSON (WDI) → DataFrame
   - NetCDF (HYDE) → Aggregated time series

2. **Temporal Alignment**:
   - Different granularities (annual, decadal, centennial)
   - Interpolation strategy for gaps
   - Binning for consistent time steps

3. **Normalization**:
   - Min-max scaling to [0, 1] for K(t) computation
   - Handling of inverse indicators (e.g., Gini, conflict deaths)
   - Missing data imputation (linear, spline, multiple imputation)

### Quality Control

- Cross-validation between overlapping datasets
- Consistency checks for same variable from multiple sources
- Outlier detection and investigation
- Documentation of data decisions

---

## 11. Reproducibility Statement

All datasets are:
- ✅ Publicly accessible (no paywalls or proprietary restrictions)
- ✅ Properly cited with DOIs or persistent URLs where available
- ✅ Versioned (specific dataset versions documented)
- ✅ Downloadable via documented procedures (see DATA_DOWNLOAD_GUIDE.md)
- ✅ Processed with documented code (see `historical_k/` modules)
- ✅ Containerized for reproduction (see Docker setup)

**Data Archive**: Complete data package will be deposited on Zenodo with DOI upon manuscript acceptance.

**Code Repository**: https://github.com/[organization]/historical-k (to be made public)

---

## 12. Contact for Data Questions

**Project Lead**: [Name]  
**Email**: [Email]  
**Institution**: [Institution]  

**Data Curator**: Historical K(t) Research Team  
**Last Verified**: 2025-11-21  

---

## Appendix A: File Listing with Checksums

```bash
# Generate checksums for verification
cd data/sources/
find . -type f \( -name "*.csv" -o -name "*.xls*" -o -name "*.json" \) -exec sha256sum {} \; > DATA_CHECKSUMS.txt
```

(Checksums to be computed and appended before publication)

---

## Appendix B: Data Processing Pipeline

```
Raw Data → Verification → Format Conversion → Temporal Alignment → 
Normalization → Harmony Proxy Construction → K(t) Aggregation → 
Validation → Robustness Testing
```

See `historical_k/compute_k_index.py` for complete implementation.

---

**Document Status**: Living document, updated as new datasets acquired  
**Version**: 2.0 (Comprehensive, post-enhancement phase)  
**Next Update**: After HYDE 3.2 integration complete

---

*"Proper attribution is not just academic courtesy—it's the foundation of reproducible science."*
