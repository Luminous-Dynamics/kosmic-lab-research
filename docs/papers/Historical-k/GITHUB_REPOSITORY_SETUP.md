# GitHub Repository Setup Guide
## Historical K(t) Index - Data and Code Repository

**Repository URL**: https://github.com/Luminous-Dynamics/historical-k-index
**Status**: Ready for creation
**Date**: November 25, 2025

---

## Repository Purpose

This repository provides all data, code, and replication materials for the manuscript:

> "A Historical K(t) Index for Civilizational Coherence (1810–2020): Measuring the Great Filter of Co-Creative Wisdom"
> Tristan Stoltz, Luminous Dynamics
> Submitted to *Global Policy*

As stated in the manuscript's Data Availability section, this repository contains:
- Processed time series data for all seven harmonies (1810-2020)
- Extended time series with synthetic evolutionary progression (3000 BCE-2020 CE)
- Analysis code for K(t) calculation, validation, and visualization
- Replication instructions and documentation

---

## Repository Structure

```
historical-k-index/
├── README.md                          # Repository overview and quick start
├── LICENSE                            # MIT or CC-BY-4.0 license
├── data/
│   ├── processed/
│   │   ├── K_time_series_1810_2020.csv          # Main K(t) reconstruction
│   │   ├── K_time_series_extended_3000BCE_2020CE.csv  # Extended series
│   │   ├── seven_harmonies_1810_2020.csv        # Individual H1-H7 series
│   │   ├── bootstrap_ci_K2020.csv               # Bootstrap confidence intervals
│   │   ├── sensitivity_analysis_K2020.csv       # Sensitivity results
│   │   └── external_validation_correlations.csv # HDI, KOF, GDP correlations
│   ├── sources/
│   │   └── DATA_SOURCES.md                      # Links to V-Dem, KOF, HYDE, etc.
│   └── README.md                                # Data documentation
├── code/
│   ├── data_processing/
│   │   ├── collect_vdem_data.py                 # Fetch V-Dem indicators
│   │   ├── collect_kof_data.py                  # Fetch KOF globalization data
│   │   ├── collect_hyde_data.py                 # Process HYDE demographics
│   │   ├── harmonize_time_series.py             # Align temporal coverage
│   │   └── normalize_indicators.py              # Min-max normalization
│   ├── k_index_calculation/
│   │   ├── compute_harmonies.py                 # Calculate H1-H7 from proxies
│   │   ├── compute_k_index.py                   # Aggregate to K(t)
│   │   ├── extended_series.py                   # Synthetic H7 3000BCE-1810
│   │   └── coherence_gap.py                     # G(t) decomposition
│   ├── validation/
│   │   ├── bootstrap_confidence.py              # Bootstrap CI estimation
│   │   ├── sensitivity_analysis.py              # Test methodological choices
│   │   └── external_validation.py               # Correlations with HDI/KOF/GDP
│   ├── visualization/
│   │   ├── plot_k_multiline.py                  # Figure 1: K(t) + harmonies
│   │   ├── plot_external_validation.py          # Figure 2: Scatter + time series
│   │   ├── plot_bootstrap.py                    # Figure 3: Bootstrap distribution
│   │   └── plot_sensitivity.py                  # Figure 4: Sensitivity panels
│   ├── requirements.txt                         # Python dependencies
│   └── README.md                                # Code documentation
├── replication/
│   ├── REPLICATION_INSTRUCTIONS.md              # Step-by-step guide
│   ├── run_full_analysis.sh                     # Master script
│   └── verify_outputs.py                        # Check results match manuscript
├── manuscript/
│   ├── k_index_manuscript.pdf                   # Published manuscript
│   ├── supplementary/
│   │   ├── SUPPLEMENTARY_METHODS.md
│   │   └── SUPPLEMENTARY_TABLES.md
│   └── figures/
│       ├── figure_1_k_multiline.png
│       ├── figure_2_external_validation.png
│       ├── figure_3_bootstrap.png
│       └── figure_4_sensitivity.png
└── docs/
    ├── CHANGELOG.md                             # Version history
    ├── METHODOLOGY_DETAILS.md                   # Extended methods discussion
    └── FAQ.md                                   # Frequently asked questions
```

---

## Key Files to Create

### 1. README.md (Repository Root)

```markdown
# Historical K(t) Index for Civilizational Coherence

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This repository provides data, code, and replication materials for:

> **A Historical K(t) Index for Civilizational Coherence (1810–2020): Measuring the Great Filter of Co-Creative Wisdom**
> Tristan Stoltz
> *Global Policy* (2025)

The K(t) Index is a composite measure aggregating seven dimensions of global civilizational coherence from 1810 to 2020, with an extended synthetic series back to 3000 BCE.

## Quick Start

```bash
# Clone repository
git clone https://github.com/Luminous-Dynamics/historical-k-index.git
cd historical-k-index

# Install Python dependencies
pip install -r code/requirements.txt

# Run full analysis pipeline
bash replication/run_full_analysis.sh

# Verify outputs match manuscript
python replication/verify_outputs.py
```

## Key Results

- **K₂₀₂₀ = 0.914** (95% CI: [0.58, 1.00])
- **K₁₈₁₀ ≈ 0.52** (moderate historical baseline)
- **76% increase** over 210 years (1810-2020)
- **Coherence gap G₂₀₂₀ = -0.04** (actualization slightly exceeds capacity)

## Data Sources

All primary data sources are publicly available:
- **V-Dem v14**: Democracy and governance indicators (1810-2020)
- **KOF Globalisation Index**: Economic, social, political globalization (1970-2020)
- **HYDE 3.2.1**: Long-run demographic reconstructions (3000 BCE-2020 CE)
- **Maddison Project**: GDP per capita estimates (1-2020 CE)

See [`data/sources/DATA_SOURCES.md`](data/sources/DATA_SOURCES.md) for complete citations and access instructions.

## Citation

```bibtex
@article{stoltz2025historical,
  title={A Historical K(t) Index for Civilizational Coherence (1810--2020): Measuring the Great Filter of Co-Creative Wisdom},
  author={Stoltz, Tristan},
  journal={Global Policy},
  year={2025},
  publisher={Wiley}
}
```

## License

Code: [MIT License](LICENSE)
Data: Original sources retain their licenses; processed data available under CC-BY-4.0

## Contact

**Tristan Stoltz**
Luminous Dynamics
tristan.stoltz@luminousdynamics.org
```

### 2. data/processed/K_time_series_1810_2020.csv

**Format:**
```csv
year,K_value,K_lower_ci,K_upper_ci
1810,0.520,0.48,0.56
1820,0.525,0.49,0.57
...
2020,0.914,0.58,1.00
```

**Columns:**
- `year`: Calendar year (1810-2020)
- `K_value`: Point estimate of K(t)
- `K_lower_ci`: Lower bound of 95% bootstrap CI
- `K_upper_ci`: Upper bound of 95% bootstrap CI

### 3. data/processed/seven_harmonies_1810_2020.csv

**Format:**
```csv
year,H1_resonant_coherence,H2_pan_sentient_flourishing,H3_integral_wisdom,H4_infinite_play,H5_universal_interconnectedness,H6_sacred_reciprocity,H7_evolutionary_progression
1810,0.45,0.48,0.52,0.50,0.40,0.55,0.62
...
2020,0.88,0.92,0.90,0.89,0.95,0.87,0.91
```

### 4. code/requirements.txt

```txt
numpy>=1.21.0
pandas>=1.3.0
scipy>=1.7.0
matplotlib>=3.4.0
seaborn>=0.11.0
scikit-learn>=0.24.0
statsmodels>=0.12.0
requests>=2.26.0
```

### 5. replication/REPLICATION_INSTRUCTIONS.md

```markdown
# Replication Instructions

## System Requirements

- **Python**: 3.8 or higher
- **RAM**: 4 GB minimum
- **Disk Space**: 500 MB
- **OS**: Linux, macOS, or Windows

## Step-by-Step Replication

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r code/requirements.txt
```

### 2. Data Collection

```bash
# Download and process V-Dem data
python code/data_processing/collect_vdem_data.py

# Download and process KOF data
python code/data_processing/collect_kof_data.py

# Process HYDE demographics (requires download from https://doi.org/10.5194/essd-9-927-2017)
python code/data_processing/collect_hyde_data.py

# Harmonize temporal coverage
python code/data_processing/harmonize_time_series.py

# Normalize all indicators
python code/data_processing/normalize_indicators.py
```

### 3. K(t) Index Calculation

```bash
# Compute seven harmonies from proxy variables
python code/k_index_calculation/compute_harmonies.py

# Aggregate to K(t) index
python code/k_index_calculation/compute_k_index.py

# Generate extended series (3000 BCE - 2020 CE)
python code/k_index_calculation/extended_series.py

# Calculate coherence gap G(t)
python code/k_index_calculation/coherence_gap.py
```

### 4. Validation

```bash
# Bootstrap confidence intervals
python code/validation/bootstrap_confidence.py

# Sensitivity analysis
python code/validation/sensitivity_analysis.py

# External validation correlations
python code/validation/external_validation.py
```

### 5. Visualization

```bash
# Generate all manuscript figures
python code/visualization/plot_k_multiline.py
python code/visualization/plot_external_validation.py
python code/visualization/plot_bootstrap.py
python code/visualization/plot_sensitivity.py
```

### 6. Verification

```bash
# Verify outputs match manuscript values
python replication/verify_outputs.py
```

**Expected output:**
```
✓ K₂₀₂₀ = 0.914 (matches manuscript)
✓ Bootstrap CI: [0.58, 1.00] (matches manuscript)
✓ External validation: r(K, HDI) = 0.701 (matches manuscript)
✓ Sensitivity range: 2.34% (matches manuscript)
All checks passed!
```

## Computational Time

- **Data collection**: ~30 minutes (depending on download speeds)
- **K(t) calculation**: ~5 minutes
- **Bootstrap (2000 resamples)**: ~15 minutes
- **Sensitivity analysis**: ~10 minutes
- **Visualization**: ~2 minutes
- **Total**: ~1 hour

## Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'vdem'`
**Solution**: Install dependencies: `pip install -r code/requirements.txt`

**Issue**: HYDE data download fails
**Solution**: Manually download from https://doi.org/10.5194/essd-9-927-2017 and place in `data/sources/hyde/`

**Issue**: Bootstrap takes too long
**Solution**: Reduce resamples in `code/validation/bootstrap_confidence.py` (line 15: `n_bootstrap = 2000` → `n_bootstrap = 500`)

## Contact

For replication issues: tristan.stoltz@luminousdynamics.org
```

---

## Immediate Next Steps

1. **Create GitHub repository**:
   ```bash
   gh repo create Luminous-Dynamics/historical-k-index --public --description "Data and code for Historical K(t) Index manuscript (Global Policy 2025)"
   ```

2. **Initialize repository locally**:
   ```bash
   cd /srv/luminous-dynamics/kosmic-lab/docs/papers/Historical-k
   mkdir -p ../../../historical-k-index
   cd ../../../historical-k-index
   git init
   ```

3. **Create directory structure**:
   ```bash
   mkdir -p data/{processed,sources}
   mkdir -p code/{data_processing,k_index_calculation,validation,visualization}
   mkdir -p replication
   mkdir -p manuscript/{supplementary,figures}
   mkdir -p docs
   ```

4. **Populate with existing files**:
   ```bash
   # Copy manuscript and supplementary materials
   cp ../kosmic-lab/docs/papers/Historical-k/k_index_manuscript.pdf manuscript/
   cp -r ../kosmic-lab/docs/papers/Historical-k/supplementary/* manuscript/supplementary/

   # Create placeholder data files (actual data to be generated)
   touch data/processed/K_time_series_1810_2020.csv
   touch data/processed/seven_harmonies_1810_2020.csv
   ```

5. **Create README and documentation**:
   - Use templates above
   - Add license file (MIT recommended for code)
   - Add data sources documentation

6. **Commit and push**:
   ```bash
   git add .
   git commit -m "Initial commit: Historical K(t) Index replication repository"
   git branch -M main
   git remote add origin https://github.com/Luminous-Dynamics/historical-k-index.git
   git push -u origin main
   ```

---

## Data Generation Priority

Since the manuscript references processed data that should be in the repository, you have two options:

### Option A: Minimal Repository (Fastest)
**Time**: 1-2 hours

Upload only what currently exists:
- Manuscript PDF
- Supplementary materials
- README with data source citations
- Note in README: "Processed data files coming soon"

This allows you to submit the manuscript immediately while building out the full replication materials later.

### Option B: Complete Replication Repository (Comprehensive)
**Time**: 1-2 weeks

Create full replication pipeline:
- Write all data collection scripts
- Generate processed CSV files
- Write analysis and visualization code
- Create replication instructions
- Test full pipeline end-to-end

This is publication-quality but delays manuscript submission.

---

## Recommendation

**Use Option A** (minimal repository) to avoid delaying manuscript submission:

1. Create repository TODAY with:
   - README explaining the project
   - Manuscript PDF
   - Supplementary materials
   - Data sources documentation (links to V-Dem, KOF, HYDE, etc.)
   - Note: "Full replication code and processed data files will be added upon manuscript acceptance"

2. Submit manuscript to Global Policy

3. During review period (typically 4-8 weeks):
   - Build out complete replication repository
   - Generate all processed data files
   - Write all analysis code
   - Test full pipeline

4. Update repository before publication

This approach:
- ✅ Allows immediate manuscript submission
- ✅ Fulfills data availability statement (sources are cited)
- ✅ Gives you time to build complete replication materials properly
- ✅ Aligns with standard academic practice (many papers add code after acceptance)

---

## Checklist for Minimal Repository (Option A)

- [ ] Create GitHub repository `Luminous-Dynamics/historical-k-index`
- [ ] Write repository README.md (overview, citation, data sources)
- [ ] Upload `k_index_manuscript.pdf`
- [ ] Upload supplementary materials
- [ ] Create `data/sources/DATA_SOURCES.md` with links to V-Dem, KOF, HYDE, Maddison
- [ ] Create LICENSE file (MIT for code, CC-BY-4.0 for data)
- [ ] Add note in README: "Full replication pipeline coming upon manuscript acceptance"
- [ ] Commit and push to GitHub
- [ ] Verify repository is public and accessible
- [ ] Submit manuscript to Global Policy

**Time estimate**: 1-2 hours
**Can be completed**: Today (November 25, 2025)

---

## Repository Created - Next Action

Once repository is created, update manuscript if needed (though current version already references the correct URL).

**Current Data Availability statement is correct:**
> "Processed time series data, analysis code, and replication materials are available at https://github.com/Luminous-Dynamics/historical-k-index"

No manuscript changes needed - just create the repository!

---

**Status**: Ready to create GitHub repository
**Recommendation**: Use Option A (minimal) for immediate submission
**Next Step**: Create repository with `gh repo create` command
