# K-Index Manuscript Compilation Guide

**Date**: November 21, 2025
**Manuscript**: `k_index_manuscript.tex`
**Status**: Ready for compilation and submission

---

## Quick Start

### Compile on NixOS (Using Project Flake)
```bash
cd /srv/luminous-dynamics/kosmic-lab/manuscript

# LaTeX is already in the flake (texlive.combined.scheme-medium)
# Just enter the dev shell and compile:

nix develop -c bash -c "
  pdflatex k_index_manuscript.tex && \
  bibtex k_index_manuscript && \
  pdflatex k_index_manuscript.tex && \
  pdflatex k_index_manuscript.tex
"

# Output: k_index_manuscript.pdf
```

### Compile on Other Linux/Mac
```bash
# Install texlive-full if not already installed
# Ubuntu/Debian: sudo apt-get install texlive-full
# Mac: brew install --cask mactex

pdflatex k_index_manuscript.tex
bibtex k_index_manuscript
pdflatex k_index_manuscript.tex
pdflatex k_index_manuscript.tex
```

---

## Files Included

### Main Manuscript
- **`k_index_manuscript.tex`** - Complete LaTeX source (ready to compile)
- **`k_index_references.bib`** - Bibliography in BibTeX format

### Required Figures
All figures referenced in the manuscript are located in `../logs/`:

#### Main K(t) Visualization
- `../logs/visualizations/k_harmonies_multiline.png` - Main figure with all harmonies

#### Track C Validation Figures
- `../logs/validation_external/validation_hdi.png` - HDI correlation plot
- `../logs/validation_external/validation_gdp.png` - GDP correlation plot
- `../logs/validation_external/validation_kof.png` - KOF correlation plot
- `../logs/bootstrap_ci/bootstrap_distribution.png` - Bootstrap confidence interval
- `../logs/sensitivity_c3/weight_sensitivity.png` - Weight scheme sensitivity
- `../logs/sensitivity_c3/normalization_sensitivity.png` - Normalization sensitivity

**Note**: Before compiling, verify all figure files exist. If missing, regenerate using scripts in `../historical_k/`.

---

## Manuscript Structure

### Complete Sections:
✅ **Title, Authors, Abstract** - Institutional details need filling
✅ **Introduction** - Includes Great Filter framing paragraph
✅ **Results Section 3.4** - Complete Track C validation:
   - Two K₂₀₂₀ estimates (0.782 and 0.914)
   - External validation (HDI, GDP, KOF)
   - Bootstrap confidence intervals
   - Sensitivity analysis
✅ **Discussion Sections 4.4-4.6**:
   - Implications for Civilizational Risk (Adolescent God)
   - Implications for Economic Design (K as compass, Goodhart's Law)
   - Ethical Considerations (dual-use concerns)
✅ **References** - Complete BibTeX bibliography

### Placeholders to Complete:
- [ ] **Authors**: Fill in co-author names and institutions
- [ ] **Acknowledgments**: Add funding sources and acknowledgments
- [ ] **Methods** section (marked [TO BE ADDED])
- [ ] **Main Results** section before 3.4 (marked [TO BE ADDED])
- [ ] **Limitations** subsection in Discussion (marked [TO BE ADDED])
- [ ] **Figure numbering**: Update to match your manuscript (currently 5, 6, 7)
- [ ] **Table numbering**: Update to match your manuscript (currently 4)
- [ ] **Section numbering**: Update if needed (currently 3.4, 4.4, 4.5, 4.6)

---

## Statistics and Key Findings

### K₂₀₂₀ Estimates (Present Both):
- **Conservative (6-harmony)**: 0.782 [95% CI: 0.58, 0.91]
- **Extended (7-harmony)**: 0.914 [95% CI: 0.58, 1.00]
- Trade-off: Temporal depth (5000 years) vs synthetic component (HYDE proxy)

### External Validation (Directionally Consistent, Under-Powered):
- **HDI** (Human Development Index): r = 0.701, p = 0.299, n = 4
- **KOF** (Globalization Index): r = 0.701, p = 0.121, n = 6
- **GDP** (Maddison): r = 0.431, p = 0.058, n = 20

### Bootstrap Confidence Intervals:
- **95% CI**: [0.584, 0.998]
- **Relative width**: 45.3% (wide, reflects measurement uncertainty)

### Sensitivity Analysis:
- **Weight sensitivity**: 2.14%
- **Normalization sensitivity**: 0.63%
- **Combined**: 2.34% (highly robust)

---

## Language Guidelines (Statistically Honest)

### ✅ DO Say:
- "Directionally consistent but under-powered evidence"
- "Provisional, exploratory index"
- "Convergent evidence supports"
- "Future work needed to establish validity"
- "Methodologically stable/robust"
- "K as monitoring tool/compass, not optimization target"
- "Subject to Goodhart's Law if used prescriptively"

### ❌ DON'T Say:
- "Validated" (for external validation with n=4, n=6)
- "Statistically significant" (p>0.05 for HDI, KOF)
- "Proves" or "demonstrates conclusively"
- "K should be maximized"
- "Definitive metric"

---

## Troubleshooting

### Missing Packages
If you get "File X.sty not found" errors:
- NixOS: Use `scheme-full` as shown above
- Ubuntu/Debian: `sudo apt-get install texlive-full`
- Mac: Use MacTeX (includes all packages)

### Figure Not Found
If you get "File X.png not found":
```bash
# Check if figures exist
ls -lh ../logs/visualizations/k_harmonies_multiline.png
ls -lh ../logs/validation_external/
ls -lh ../logs/bootstrap_ci/
ls -lh ../logs/sensitivity_c3/

# If missing, regenerate
cd ../historical_k
poetry run python visualize_harmonies.py
poetry run python external_validation.py
poetry run python bootstrap_ci_c2.py
poetry run python sensitivity_analysis_c3.py
```

### Bibtex Errors
If you get citation errors:
1. Check `k_index_references.bib` for syntax errors
2. Ensure all cited keys exist in .bib file
3. Run the full compilation sequence (pdflatex → bibtex → pdflatex → pdflatex)

---

## Journal Submission Checklist

Before submitting, verify:

### Content Completeness:
- [ ] Both K₂₀₂₀ estimates presented with clear disclosure
- [ ] External validation with appropriate statistical humility
- [ ] Bootstrap CI wide interval acknowledged
- [ ] Sensitivity emphasizes stability, not validation
- [ ] Great Filter framing flagged as exploratory
- [ ] Economic implications frame K as compass, not target
- [ ] Ethics section raises Goodhart's Law and dual-use concerns
- [ ] All placeholders filled (authors, institutions, methods)

### Formatting:
- [ ] All figure numbers updated to match manuscript
- [ ] All table numbers updated to match manuscript
- [ ] All section numbers updated if needed
- [ ] Citations formatted to match journal style
- [ ] Word count within journal limits

### Figures:
- [ ] All 7-8 figures generated and correctly referenced
- [ ] Figure captions complete and accurate
- [ ] Figure quality suitable for publication (300 DPI)

### References:
- [ ] All 15+ new references added to bibliography
- [ ] All citations in text match bibliography
- [ ] Reference format matches journal requirements

---

## Word Count

**Added by Track C integration**: ~2900 words

### Core sections (~2400 words - cannot cut):
- Results Section 3.4: ~1200 words
- Introduction addition: ~200 words
- Discussion Section 4.4 (Civilizational Risk): ~600 words
- Discussion Section 4.6 (Ethics): ~400 words

### Optional section (~500 words - can cut if needed):
- Discussion Section 4.5 (Economic Design): ~500 words
  - Can be cut entirely or trimmed to 1 paragraph (~250 words)

---

## Next Steps

1. **Fill placeholders** (authors, institutions, methods section)
2. **Verify figures** exist and compile correctly
3. **Compile manuscript** following instructions above
4. **Review PDF** for formatting and completeness
5. **Submit** to journal or send to co-authors

---

## Related Documents

- **`../docs/historical-k/FINAL_DELIVERABLES_SUMMARY.md`** - Complete Track C summary
- **`../docs/historical-k/COMPLETION_REPORT_HONEST.md`** - Canonical statistics source
- **`../docs/historical-k/MANUSCRIPT_SECTIONS_READY_TO_PASTE.md`** - Alternative text
- **`../docs/historical-k/GREAT_FILTER_INTEGRATION_GUIDE.md`** - Integration principles

---

**Status**: ✅ **READY FOR COMPILATION**

*K-Index manuscript compilation guide created: 2025-11-21*
