# Paper 1: Historical K(t) Index - 5000 Years of Global Civilizational Coherence

**Status**: Manuscript compiled, ready for final revisions
**Last Updated**: November 22, 2025
**Target Journals**: Nature, Science, PNAS

---

## ⚠️ IMPORTANT: K-Index Disambiguation

**There are TWO different K-indices in Kosmic Lab research:**

1. **This Paper (Historical K(t))**: Civilizational coherence across 5000 years
2. **Other Papers (Bioelectric K)**: Morphological coherence in developmental biology

**See [`K_INDEX_DISAMBIGUATION.md`](../../K_INDEX_DISAMBIGUATION.md) for complete explanation.**

**TLDR**: Same philosophical framework (Seven Harmonies), different operational definitions:
- **Civilizational K(t)**: HDI, GDP, V-Dem, trade data
- **Bioelectric K**: Φ, Transfer Entropy, IoU, behavioral coherence

---

## Files in This Directory

### Core Manuscript Files
- **`k_index_manuscript.tex`** - Main LaTeX manuscript
- **`k_index_manuscript.pdf`** - Compiled PDF (12 pages)
- **`k_index_references.bib`** - Complete bibliography

### Formalism & Methods
- **`K_INDEX_CIVILIZATIONAL_FORMALISM.md`** - Complete mathematical specification (70KB)
  - Use this as source for Methods section
  - Publication-ready formalism
  - All 32+ data sources documented
  - Complete statistical framework

### Compilation & Guidance
- **`K_INDEX_COMPILATION_GUIDE.md`** - How to compile the LaTeX manuscript
- **`REVIEWER_FEEDBACK_RESPONSE.md`** - Action plan for completing manuscript

### Build Artifacts
- `k_index_manuscript.aux`, `.log`, `.out` - LaTeX build files

---

## Quick Start

### Compile the Manuscript
```bash
cd /srv/luminous-dynamics/kosmic-lab/docs/papers/Historical-k

# Using project flake (LaTeX already configured)
nix develop -c bash -c "
  pdflatex k_index_manuscript.tex && \
  bibtex k_index_manuscript && \
  pdflatex k_index_manuscript.tex && \
  pdflatex k_index_manuscript.tex
"

# Output: k_index_manuscript.pdf
```

### Read the Formalism
```bash
# Complete mathematical specification
less K_INDEX_CIVILIZATIONAL_FORMALISM.md

# Or view in browser/editor
code K_INDEX_CIVILIZATIONAL_FORMALISM.md
```

---

## Manuscript Structure

### ✅ Complete Sections
- **Abstract** - K₂₀₂₀ estimates (0.782 and 0.914), validation summary, Great Filter framing
- **Introduction** - Great Filter paragraph, civilizational risk context
- **Results Section 3.4** - Complete Track C validation (external, bootstrap, sensitivity)
- **Discussion Sections 4.4-4.6** - Civilizational risk, economic design, ethics
- **References** - Complete bibliography

### 🔧 Sections Needing Completion
- **Section 2 (Methods)** - [TO BE ADDED] from formalism doc
- **Section 3.1 (Historical Reconstruction)** - [TO BE ADDED] describe K(t) curve
- **Section 4.5 (Limitations)** - [TO BE ADDED] comprehensive limitations
- **All (??) citations** - Need replacement with real references

**See `REVIEWER_FEEDBACK_RESPONSE.md` for complete task list and priorities.**

---

## Key Statistics (Canonical)

### Two K₂₀₂₀ Estimates

**Six-Harmony (Conservative, Primary)**:
```
K₂₀₂₀ = 0.782
95% CI: [0.58, 0.91]
Basis: Six validated harmonies, real data only
```

**Seven-Harmony (Extended, Exploratory)**:
```
K₂₀₂₀ = 0.914
95% CI: [0.58, 1.00]
Basis: Six validated + one synthetic (HYDE demographic proxies)
```

**Critical Finding**: Both versions identify **year 2020 as peak coherence**.

### External Validation (Under-Powered)
- **HDI** (Human Development Index): r = 0.701, p = 0.299, n = 4
- **KOF** (Globalization Index): r = 0.701, p = 0.121, n = 6
- **GDP** (Maddison): r = 0.431, p = 0.058, n = 20

**Language**: "Directionally consistent but under-powered" (NOT "validated" or "significant")

### Bootstrap Confidence Intervals
- **95% CI**: [0.584, 0.998]
- **Relative width**: 45.3% (wide, reflects measurement uncertainty)

### Sensitivity Analysis
- **Weight sensitivity**: 2.14%
- **Normalization sensitivity**: 0.63%
- **Combined**: 2.34% (highly robust to methodological choices)

---

## Seven Harmonies (Civilizational K(t))

| Harmony | Conceptual Meaning | Key Proxies |
|---------|-------------------|-------------|
| **H₁: Resonant Coherence** | Governance + communication | V-Dem democracy, ICRG governance, telecom density |
| **H₂: Interconnection** | Trade + migration | Trade openness, bilateral trade, migration stocks |
| **H₃: Sacred Reciprocity** | Bilateral balance | Trade symmetry, alliances, aid reciprocity |
| **H₄: Infinite Play** | Innovation diversity | Occupational entropy, patent diversity, cultural diversity |
| **H₅: Integral Wisdom** | Research + forecasting | R&D expenditure, researchers per capita, forecast accuracy |
| **H₆: Pan-Sentient Flourishing** | Wellbeing + environment | Life expectancy, education, GDP per capita, EPI |
| **H₇: Evolutionary Progression** | **⚠️ Synthetic** | HYDE population proxies (planned: WIPO patents, Barro-Lee education) |

**See `K_INDEX_CIVILIZATIONAL_FORMALISM.md` for complete operational definitions.**

---

## Data Sources (32+ Datasets)

### Primary Modern Data
- **V-Dem v14**: Liberal democracy index (1789-2023)
- **World Bank WDI**: Trade, R&D, life expectancy, GDP (1960-2020)
- **UN Comtrade**: Bilateral trade flows (1962-2020)
- **Quality of Government**: ICRG governance indicators
- **Barro-Lee**: Educational attainment (1950-2015)
- **Maddison Project**: Historical GDP (1-2020 CE)

### Historical Reconstructions
- **Seshat Global History Databank**: Ancient civilizations (3000 BCE-500 CE)
- **HYDE 3.2**: Demographic data (10000 BCE-2020 CE)
- **Fouquin & Hugot**: Historical trade (1810-1960)

**All sources publicly accessible. See formalism doc for complete list.**

---

## Related Documentation

### In This Directory
- `K_INDEX_CIVILIZATIONAL_FORMALISM.md` - Mathematical specification
- `K_INDEX_COMPILATION_GUIDE.md` - Compilation instructions
- `REVIEWER_FEEDBACK_RESPONSE.md` - Current status and action plan

### In Parent Directories
- `../../K_INDEX_DISAMBIGUATION.md` - **Master reference** explaining two K-indices
- `../../K_INDEX_BIOELECTRIC_FORMALISM.md` - Bioelectric K formalism (NOT this paper)
- `../../historical-k/COMPLETION_REPORT_HONEST.md` - Canonical statistics source
- `../../historical-k/FINAL_DELIVERABLES_SUMMARY.md` - All Track C deliverables

### Figures & Data
- `../../../logs/visualizations/k_harmonies_multiline.png` - Main K(t) plot
- `../../../logs/validation_external/` - External validation plots (HDI, GDP, KOF)
- `../../../logs/bootstrap_ci/` - Bootstrap distribution
- `../../../logs/sensitivity_c3/` - Sensitivity analysis plots

---

## Compilation Troubleshooting

### Missing LaTeX Packages
LaTeX is pre-configured in the project flake (`texlive.combined.scheme-medium`).

If compilation fails:
```bash
# Check flake has LaTeX
grep texlive /srv/luminous-dynamics/kosmic-lab/flake.nix

# Should show: pkgs.texlive.combined.scheme-medium
```

### Missing Figures
If figures are missing:
```bash
# Check if figures exist
ls -lh ../../../logs/visualizations/k_harmonies_multiline.png
ls -lh ../../../logs/validation_external/
ls -lh ../../../logs/bootstrap_ci/
ls -lh ../../../logs/sensitivity_c3/

# If missing, regenerate (see Track C scripts)
cd ../../../historical_k
poetry run python visualize_harmonies.py
poetry run python external_validation.py
poetry run python bootstrap_ci_c2.py
poetry run python sensitivity_analysis_c3.py
```

---

## Submission Checklist

Before submitting to journal:

### Content Completeness
- [ ] Both K₂₀₂₀ estimates presented with clear disclosure
- [ ] External validation with appropriate statistical humility
- [ ] Bootstrap CI wide interval acknowledged
- [ ] Sensitivity emphasizes stability, not validation
- [ ] Great Filter framing flagged as exploratory
- [ ] Economic implications frame K as compass, not target
- [ ] Ethics section raises Goodhart's Law and dual-use concerns
- [ ] All placeholders filled (Methods, 3.1, 4.5, citations)

### Formatting
- [ ] All figure numbers updated to match manuscript
- [ ] All table numbers updated to match manuscript
- [ ] All section numbers consistent
- [ ] Citations formatted to match journal style
- [ ] Word count within journal limits

### Quality Checks
- [ ] All numbers consistent across document (K₂₀₂₀, correlations, CIs, sensitivity)
- [ ] No (??) citation placeholders remain
- [ ] All figures referenced correctly
- [ ] Manuscript compiles without errors
- [ ] PDF renders correctly

---

## Contact & Collaboration

**Primary Author**: Tristan Stoltz (tristan.stoltz@evolvingresonantcocreationism.com)
**Organization**: Kosmic Lab, Luminous Dynamics
**GitHub**: Luminous-Dynamics/kosmic-lab

---

## License

**Manuscript**: Copyright © 2025 Kosmic Lab Research Team. All rights reserved until publication.

**Code & Data**: MIT License (code) + CC-BY 4.0 (data processing scripts)

**Upon Publication**: Manuscript text will be CC-BY 4.0, all code and data fully open.

---

**README Status**: ✅ Complete guide for Paper 1 (Historical K(t))
**Last Updated**: November 22, 2025
**Next Update**: After Methods section drafted

---

*This is Paper 1 of the Kosmic Lab research program. For other papers (bioelectric K), see parent `papers/` directory.*
