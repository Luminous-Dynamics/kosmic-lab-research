# Data Sources Documentation

**Last Updated**: November 25, 2025

This document provides complete citations, access instructions, and variable definitions for all primary data sources used in constructing the Historical K(t) Index.

---

## Primary Data Sources

### 1. Varieties of Democracy (V-Dem) v14

**Coverage**: 1810–2020 (202 countries)
**Access**: https://www.v-dem.net/
**License**: Free for academic use (registration required)
**File**: Country-Year: V-Dem Full+Others v14 (CSV)

**Citation**:
```bibtex
@techreport{vdem2024,
  title={V-Dem Dataset v14},
  author={Coppedge, Michael and Gerring, John and Knutsen, Carl Henrik and
          Lindberg, Staffan I. and Teorell, Jan and Altman, David and
          Angiolillo, Fabio and Bernhard, Michael and Cornell, Agnes and
          Fish, M. Steven and Gastaldi, Lisa and Gjerløw, Haakon and
          Glynn, Adam and Grahn, Sandra and Hicken, Allen and
          Kinzelbach, Katrin and Marquardt, Kyle L. and McMann, Kelly and
          Mechkova, Valeriya and Paxton, Pamela and Pemstein, Daniel and
          von Römer, Johannes and Seim, Brigitte and Sigman, Rachel and
          Skaaning, Svend-Erik and Staton, Jeffrey and Tzelgov, Eitan and
          Uberti, Luca and Wang, Yi-ting and Wig, Tore and Ziblatt, Daniel},
  institution={Varieties of Democracy (V-Dem) Project},
  year={2024},
  url={https://www.v-dem.net/}
}
```

**Variables Used**:

For **H₁ (Resonant Coherence)**:
- `v2x_polyarchy`: Electoral democracy index (0-1)
- `v2x_partipdem`: Participatory democracy index (0-1)
- `v2x_cspart`: Civil society participation index (0-1)
- `v2xcs_ccsi`: Core civil society index (0-1)

For **H₂ (Pan-Sentient Flourishing)** (supplemental to HDI):
- `v2pepwrgen`: Power distributed by gender (0-1)
- `v2clacjust`: Access to justice for men (0-1)
- `v2cltrnslw`: Transparent laws with predictable enforcement (0-1)

For **H₆ (Sacred Reciprocity)**:
- `v2exrescon`: Executive respects constitution (0-1)
- `v2cltort`: Freedom from torture (0-1)
- `v2clslavem`: Freedom from slavery (0-1)

**Processing**:
1. Downloaded country-year CSV from V-Dem website
2. Filtered to years 1810-2020
3. Aggregated country values to global means (weighted by population)
4. Normalized to [0,1] scale using min-max normalization anchored to historical range

---

### 2. KOF Globalisation Index

**Coverage**: 1970–2020 (203 countries)
**Access**: https://kof.ethz.ch/en/forecasts-and-indicators/indicators/kof-globalisation-index.html
**License**: Free for academic use
**File**: KOF Globalisation Index - Data (XLSX)

**Citation**:
```bibtex
@article{gygli2019,
  title={The KOF Globalisation Index -- Revisited},
  author={Gygli, Savina and Haelg, Florian and Potrafke, Niklas and Sturm, Jan-Egbert},
  journal={Review of International Organizations},
  volume={14},
  number={3},
  pages={543--574},
  year={2019},
  doi={10.1007/s11558-019-09344-2}
}
```

**Variables Used**:

For **H₅ (Universal Interconnectedness)**:
- `KOFGI`: Overall globalisation index (0-100)
- `KOFEcGI`: Economic globalisation (0-100)
- `KOFSoGI`: Social globalisation (0-100)
- `KOFPoGI`: Political globalisation (0-100)

Sub-indices:
- `KOFTrGI`: Trade globalisation
- `KOFIpGI`: Interpersonal globalisation
- `KOFCuGI`: Cultural globalisation

**Processing**:
1. Downloaded XLSX data file
2. Extracted overall and sub-index values for 1970-2020
3. Aggregated to global means (population-weighted)
4. Re-scaled from [0,100] to [0,1]
5. For years 1810-1969: Linear interpolation from baseline (0.10 in 1810) to first observed value (1970)

---

### 3. HYDE 3.2.1 (History Database of the Global Environment)

**Coverage**: 10000 BCE–2020 CE (global gridded data)
**Access**: https://doi.org/10.5194/essd-9-927-2017
**License**: CC-BY-4.0
**File**: HYDE 3.2.1 baseline population density grids (NetCDF)

**Citation**:
```bibtex
@article{kleingoldewijk2017,
  title={Anthropogenic land use estimates for the Holocene -- HYDE 3.2},
  author={Klein Goldewijk, Kees and Beusen, Arthur and Doelman, Jonathan and Stehfest, Elke},
  journal={Earth System Science Data},
  volume={9},
  number={2},
  pages={927--953},
  year={2017},
  doi={10.5194/essd-9-927-2017}
}
```

**Variables Used**:

For **H₇ (Evolutionary Progression)**:
- `pop`: Total population (persons)
- `popc`: Urban population (persons)
- `cropland`: Cropland area (km²)
- `grazing`: Grazing land area (km²)

**Processing**:
1. Downloaded baseline population grids from DANS repository
2. Summed global population from gridded data for all time steps
3. Computed log-normalized population: H₇(t) = log₁₀(pop(t)) / log₁₀(pop_max)
4. Anchored to modern maximum (pop₂₀₂₀ ≈ 7.8 billion)
5. For K(t) reconstruction: Used H₇ only for pre-1810 extended series
6. For 1810-2020: Used six-harmony formulation (H₁-H₆) as primary

**Note**: H₇ is synthetic/reconstructed for the extended time series (3000 BCE - 2020 CE). For the core analysis (1810-2020), H₇ is available but not strictly necessary; the six-harmony formulation provides a conservative estimate using only direct observational data.

---

### 4. Maddison Project Database 2020

**Coverage**: 1–2020 CE (GDP per capita estimates)
**Access**: https://www.rug.nl/ggdc/historicaldevelopment/maddison/
**License**: Free for academic use
**File**: Maddison Project Database 2020 (XLSX)

**Citation**:
```bibtex
@misc{boltetal2020,
  title={Maddison style estimates of the evolution of the world economy. A new 2020 update},
  author={Bolt, Jutta and van Zanden, Jan Luiten},
  year={2020},
  publisher={Maddison Project Database},
  url={https://www.rug.nl/ggdc/historicaldevelopment/maddison/}
}
```

**Variables Used**:

For **H₂ (Pan-Sentient Flourishing)** and **H₄ (Infinite Play)**:
- `gdppc`: GDP per capita in 2011 US dollars (PPP)

**Processing**:
1. Downloaded country-year GDP per capita estimates
2. Computed global average GDP per capita (population-weighted)
3. Log-normalized: GDP_norm = log₁₀(gdppc) / log₁₀(gdppc_max)
4. Used as component of H₂ (along with HDI) and H₄ (adaptive capacity correlate)

---

### 5. United Nations Human Development Index (HDI)

**Coverage**: 1990–2020 (189 countries)
**Access**: https://hdr.undp.org/
**License**: Free for academic use
**File**: Human Development Report 2023-24 Data (CSV)

**Citation**:
```bibtex
@techreport{undp2023,
  title={Human Development Report 2023-24: Breaking the Gridlock},
  author={{United Nations Development Programme}},
  institution={United Nations Development Programme},
  address={New York, NY},
  year={2023},
  url={https://hdr.undp.org/}
}
```

**Variables Used**:

For **H₂ (Pan-Sentient Flourishing)**:
- `hdi`: Human Development Index (0-1)
- `le`: Life expectancy at birth (years)
- `mys`: Mean years of schooling
- `eys`: Expected years of schooling
- `gni_pc`: Gross national income per capita (PPP $)

**Processing**:
1. Downloaded HDI data and component indicators
2. Computed global HDI (population-weighted average)
3. For pre-1990: Backwards extrapolation using Maddison GDP per capita, life expectancy estimates from historical demography, and literacy proxies
4. Normalized to [0,1] using historical range 1810-2020

---

## Supplementary Sources

### Proxy Variables for Harmonies Without Direct Data

**H₃ (Integral Wisdom)**:
- Education data from V-Dem (`v2peedueq`: Educational equality)
- Historical literacy rates from UNESCO and national archives
- Patent grants per capita (proxy for innovation)
- Scientific publications (post-1945, from Web of Science)

**H₄ (Infinite Play)**:
- Cultural diversity index (constructed from linguistic fractionalization data)
- Adaptive governance metrics (V-Dem flexibility indicators)
- Economic diversification (Herfindahl index from trade data)

**H₆ (Sacred Reciprocity)**:
- Cooperative norms from V-Dem civil society indicators
- Trust metrics from World Values Survey (1981-2020) and historical proxies
- Mutual aid indicators (NGO density, volunteer rates)

---

## Data Harmonization Procedures

### Temporal Alignment

Different sources have different temporal coverage. Harmonization steps:

1. **Core Period (1810-2020)**:
   - V-Dem: Native coverage
   - KOF: Interpolate backwards from 1970 using GDP and trade proxies
   - HDI: Extrapolate backwards from 1990 using component indicators
   - Maddison: Native coverage
   - HYDE: Native coverage

2. **Extended Period (3000 BCE - 1810)**:
   - Only H₇ (HYDE population) has direct data
   - H₁-H₆: Not estimated (insufficient data)
   - Extended K(t) uses only H₇ for this period

### Spatial Aggregation

All country-level data aggregated to global values using population weights:

```
Global_Indicator(t) = Σᵢ [Indicator_i(t) × Population_i(t)] / Σᵢ Population_i(t)
```

Where i indexes countries with available data in year t.

### Missing Data

- **Within-series gaps**: Linear interpolation if gap < 5 years; otherwise excluded
- **Country coverage**: Only countries with >50% temporal coverage included
- **Global aggregates**: Require >80% of global population represented

---

## Normalization Methods

All indicators normalized to [0,1] scale using historical min-max:

```
Normalized(t) = [Raw(t) - Min(1810-2020)] / [Max(1810-2020) - Min(1810-2020)]
```

**Exceptions**:
- Life expectancy: Anchored to biological plausible range [20, 90 years]
- GDP per capita: Log-transformed before normalization
- Population (H₇): Log-transformed and anchored to modern maximum

---

## Data Quality and Limitations

### Coverage Issues

1. **Pre-1900 Data Sparsity**:
   - V-Dem democracy data sparse before 1900 (few independent states)
   - GDP estimates uncertain before 1820
   - Health/education proxies highly uncertain before 1900

2. **Country Representation**:
   - Early period (1810-1850): ~30 countries
   - Mid-period (1900-1950): ~60 countries
   - Modern period (1990-2020): ~180 countries
   - Population coverage generally >90% throughout

### Proxy Variable Limitations

- **H₃ (Integral Wisdom)**: Innovation difficult to measure pre-1900; relies heavily on education proxies
- **H₄ (Infinite Play)**: Cultural diversity and adaptiveness lack standardized historical measures
- **H₆ (Sacred Reciprocity)**: Trust and cooperation norms measurable only post-1980; historical values inferred from institutional proxies

### Interpolation Uncertainty

- KOF (1810-1969): Linear interpolation introduces smoothing bias
- HDI (1810-1989): Backwards extrapolation assumes component relationships stable over time
- All uncertainty quantified via bootstrap confidence intervals

---

## Download Instructions

### Automated Download (Future Release)

Full replication package will include automated download scripts:

```bash
# Download all source data
python code/data_processing/download_vdem.py
python code/data_processing/download_kof.py
python code/data_processing/download_hyde.py
python code/data_processing/download_maddison.py
python code/data_processing/download_hdi.py
```

### Manual Download (Current)

1. **V-Dem**: Register at v-dem.net, download "Country-Year: V-Dem Full+Others v14 (CSV)"
2. **KOF**: Visit kof.ethz.ch, download "KOF Globalisation Index - Data (XLSX)"
3. **HYDE**: Access https://doi.org/10.5194/essd-9-927-2017, download baseline population NetCDF files
4. **Maddison**: Download from rug.nl/ggdc/historicaldevelopment/maddison/
5. **HDI**: Download from hdr.undp.org

Place all files in `data/sources/raw/` directory.

---

## Processed Data Files (Coming Upon Manuscript Acceptance)

The repository will include fully processed time series ready for immediate use:

- `data/processed/K_time_series_1810_2020.csv`: Core K(t) reconstruction
- `data/processed/K_time_series_extended_3000BCE_2020CE.csv`: Extended series
- `data/processed/seven_harmonies_1810_2020.csv`: Individual H₁-H₇ values
- `data/processed/bootstrap_ci_K2020.csv`: Bootstrap confidence interval distribution
- `data/processed/sensitivity_analysis_K2020.csv`: Sensitivity to methodological choices
- `data/processed/external_validation_correlations.csv`: Correlations with HDI, KOF, GDP

All files include:
- Clear column headers
- Data documentation in README
- Units and scale information
- Missing data coding (-999)
- Processing metadata (date created, script version)

---

**Last Updated**: November 25, 2025
**Contact**: tristan.stoltz@luminousdynamics.org
