# 📄 Paper 8: Unified Indices - Claude Development Context

**Paper Title**: Unified Indices of Machine Consciousness: When Combining Metrics Fails and What We Learn From It
**Current Status**: Draft Requires Revision - O/R Bug Fixed
**Last Updated**: November 28, 2025

---

## 🚨 CRITICAL UPDATE: O/R Computation Bug Fixed

The original experiments used a **buggy O/R computation** that showed a positive K-O/R correlation (r = +0.61). After fixing to match Paper 6 methodology, we found:

- **Corrected K-O/R correlation**: r = -0.21 (p = 0.002) - **NEGATIVE, as expected**
- **Main finding unchanged**: K-only optimization still outperforms all unified indices

---

## 🔧 Quick Compilation

```bash
cd /srv/luminous-dynamics/kosmic-lab
nix develop

cd docs/papers/paper-8-unified-indices
pdflatex paper_8_unified_indices.tex
```

**Output**: 8 pages, ~443KB PDF

---

## 📊 Key Results Summary (CORRECTED)

### The Core Finding

**All approaches to combining K-Index and O/R Index perform worse than K-only optimization.**

| Approach | Best K | % of 1.5 | vs K-only |
|----------|--------|----------|-----------|
| **k_only (baseline)** | **1.3288** | **88.6%** | --- |
| log_scaled | 1.2583 | 83.9% | -5.3% |
| original | 1.1666 | 77.8% | -12.2% |
| multiplicative | 1.0105 | 67.4% | -24.0% |
| **or_only (control)** | **0.9740** | **64.9%** | **-26.7%** |
| additive | 0.6390 | 42.6% | -51.9% |

### Corrected Discovery

**K and O/R are WEAKLY NEGATIVELY correlated** (r = -0.21, p = 0.002)

- **Consistent with Paper 6**: well-trained agents have high K and moderate O/R
- Explains why unified indices fail: O/R introduces noise orthogonal to K signal
- K measures magnitude coupling; O/R measures behavioral variability

### O/R-Only Control (NEW)

Added per reviewer request: **O/R-only optimization achieves K = 0.9740** (26.7% worse than K-only).

This confirms O/R should NOT be used as an optimization target.

---

## 📁 Key Files

### Main Paper
- `paper_8_unified_indices.tex` - Complete paper (needs revision)
- `paper_8_unified_indices.pdf` - Compiled output

### Experimental Code
- `track_l_runner.py` - All Track L experiments (O/R FIXED)
- `unified_index_implementation.py` - Formula implementations
- `cmaes_stability_investigation.py` - CMA-ES stability diagnosis (NEW)

### Results
- `TRACK_L_INITIAL_RESULTS.md` - Complete analysis (UPDATED)
- `CMAES_STABILITY_FINDINGS.md` - Major discovery (NEW)
- `logs/track_l/` - Track L experiment data (JSON)
- `logs/stability/` - CMA-ES investigation data (JSON)

---

## 🎯 Paper Thesis (REVISED)

> "K-Index and O/R Index measure distinct aspects of agent behavior: K measures magnitude coupling while O/R measures behavioral variability. These metrics are **weakly negatively correlated** (r = -0.21), and combining them in optimization objectives is counterproductive. K-only optimization achieves the best results, while O/R is valuable as a **diagnostic metric** (O/R > 0 indicates learned structure) but not as an optimization target."

---

## 📈 Track L Experiments (CORRECTED)

### L1: Correlation Study (n=200, corrected O/R)
- K ↔ O/R correlation: **r = -0.21*** (negative, p = 0.002)
- CMA-ES agents: High K (1.5±0.2), Moderate O/R (1.2±1.0)
- Linear agents: Moderate K (0.8±0.5), High O/R (5.2±8.4)

### L4: Formula Comparison (100 generations, corrected O/R)
- Tested 6 formulas: k_only, or_only, original, multiplicative, additive, log_scaled
- K-only wins decisively (K = 1.3288)
- O/R-only control confirms O/R alone doesn't help K (K = 0.9740)

---

## ✅ Practical Recommendations

| Use Case | Recommended? | Rationale |
|----------|--------------|-----------|
| K as optimization target | ✅ Yes | Best results (K = 1.3288) |
| O/R as optimization target | ❌ No | K = 0.9740 (26.7% worse) |
| Unified (K + O/R) | ❌ No | All formulas underperform |
| **O/R as diagnostic** | ✅ Yes | O/R > 0 indicates structure |
| **O/R for coordination** | ✅ Yes | Paper 6's validated use case |

---

## 🔬 Future Work

1. **Multi-environment validation**: Test K-O/R relationship in diverse domains
2. **Alternative optimizers**: Genetic algorithms, gradient-based methods
3. **Theoretical analysis**: Why does K-only optimization work best?
4. ~~**Threshold investigation**: Why is 1.5 so hard to cross?~~ **ANSWERED** - See below

---

## 🚨 MAJOR DISCOVERY: CMA-ES Stability Investigation (Nov 28, 2025)

**The "early peak degradation" in Track L is NOT fundamental to K-Index!**

In a simplified environment, CMA-ES achieves:
- **Best K = 1.9147** (well above 1.5 threshold!)
- **Degradation = 1.8%** (vs 30-50% in Track L)
- **Best generation = 36** (vs early peak at gen 0-10 in Track L)
- **Early peak rate = 0/10** (none peaked before gen 10)

### Key Findings

| Environment | Best K | Degradation | Peak Gen |
|-------------|--------|-------------|----------|
| **Simplified** | **1.91** | **1.8%** | **36** |
| Track L | 1.33 | ~30% | 0-10 |

### Implications

1. **K-Index CAN exceed 1.5** - The "consciousness threshold" is achievable
2. **Track L environment is problematic** - Not K-Index itself
3. **CMA-ES works correctly** - Outperforms random search (1.91 vs 1.90)
4. **New research question**: "What properties of Track L cause K instability?"

### Files
- `cmaes_stability_investigation.py` - Investigation script
- `CMAES_STABILITY_FINDINGS.md` - Complete documentation
- `logs/stability/investigation_20251128_190541.json` - Raw data

---

## ⚠️ Required Paper Revisions

1. **Fix K-O/R correlation**: Change from +0.61 to -0.21
2. **Update interpretation**: Metrics are weakly negatively correlated, not positively
3. **Add O/R-only control**: Include new experiment (K = 0.9740)
4. **Acknowledge limitations**: Single environment, need multi-domain validation
5. **Update tables**: Use corrected Best K values

---

*Last updated: November 28, 2025*
*Status: O/R bug fixed, experiments re-run, paper needs revision*
