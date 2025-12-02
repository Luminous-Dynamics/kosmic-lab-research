# Track L: Results Analysis

**Date**: November 28, 2025
**Status**: Complete - O/R Bug Fixed, All Experiments Re-Run ✅

---

## 🚨 CRITICAL UPDATE: O/R Computation Bug Fixed

### The Bug
Original Track L experiments used a **buggy O/R computation** that:
- Used continuous action probability values instead of discrete histograms
- Computed variance of probability values instead of variance of action distributions
- Resulted in O/R values inconsistent with Paper 6 methodology

### The Fix
Corrected `compute_or_index` to match Paper 6:
- Discretize actions by NORM into 5 bins (matching Paper 6's 5 discrete actions)
- Use FIXED bins (linspace), not quantile bins
- Compute variance of action histograms per observation bin

### Impact on Results

| Metric | Before Fix (WRONG) | After Fix (CORRECT) |
|--------|-------------------|---------------------|
| K ↔ O/R correlation | **+0.61*** | **-0.21*** |
| CMA-ES O/R | 5.61 | 0.5-2.0 |
| Linear O/R | 1.42 | 1.0-25.0 |
| Interpretation | K and O/R are complementary | K and O/R are inversely related |

**The negative correlation is now CONSISTENT with Paper 6!**

---

## Updated Formula Comparison (100 generations, corrected O/R)

| Formula | Best K | Coherence | K Rank | Notes |
|---------|--------|-----------|--------|-------|
| **k_only** | **1.3288** | 1.3288 | **1st** | Pure K optimization wins! |
| log_scaled | 1.2583 | 2.6816 | 2nd | Dampened O/R contribution |
| original | 1.1666 | 0.3278 | 3rd | Penalizes high O/R |
| multiplicative | 1.0105 | 11.71 | 4th | O/R contribution too strong |
| **or_only** | **0.9740** | 9.5133 | **5th** | 🆕 Control: O/R-only fails! |
| additive | 0.6390 | 6.4086 | 6th | O/R dominates objective |

### Key Finding: K-only STILL Best (Even After Bug Fix!)

Despite fixing the O/R computation (which now shows the expected negative correlation), **K-only optimization still outperforms all unified index formulas**.

### O/R-Only Control Experiment 🆕

Added per reviewer request. Result: **O/R-only achieves K = 0.9740** (worse than K-only's 1.3288).

This confirms:
- Optimizing O/R alone does NOT improve K-Index
- O/R and K measure related but distinct aspects
- Direct K optimization remains optimal

---

## Updated Correlation Study (Track L1, n=200, corrected O/R)

### Agent Type Breakdown

| Agent Type | n | K-Index (mean±std) | O/R Index (mean±std) |
|------------|---|-------------------|---------------------|
| Random | 50 | 0.09 ± 0.07 | 0.6 ± 0.3 |
| Linear | 50 | 0.83 ± 0.48 | 5.2 ± 8.4 |
| CMA-ES | 50 | 1.55 ± 0.21 | 1.2 ± 1.0 |
| Pretrained | 50 | 0.62 ± 0.40 | 0.8 ± 0.5 |

### Correlation Matrix (CORRECTED)

```
              K-Index    O/R Index    Performance
K-Index        1.00      -0.21***      0.02
O/R Index     -0.21***    1.00        -0.15
Performance    0.02      -0.15         1.00
```

**Spearman's rho (K ↔ O/R)**: ρ = -0.21, p = 0.002

### Critical Observation

**CMA-ES agents have HIGH K but MODERATE O/R**:
- K-Index: 1.55 ± 0.21 (highest)
- O/R Index: 1.2 ± 1.0 (moderate, not extreme)

**Linear agents have MODERATE K but HIGH O/R**:
- K-Index: 0.83 ± 0.48 (moderate)
- O/R Index: 5.2 ± 8.4 (highest variance)

This is **consistent with Paper 6**: well-trained agents develop behavioral consistency (lower O/R variance) while achieving high K.

---

## Revised Thesis for Paper 8

### Original Thesis (REJECTED)
> "Unified indices combining K and O/R will outperform single metrics"

### Revised Thesis (SUPPORTED)
> "K-Index and O/R Index measure distinct aspects of agent behavior. K measures magnitude coupling (how observation intensity drives action intensity), while O/R measures behavioral variability (how context-dependent actions are). These metrics are **weakly negatively correlated** (r = -0.21), and combining them in optimization objectives is counterproductive because:
> 1. K-only optimization achieves the highest K values
> 2. O/R-only optimization fails to improve K
> 3. All unified indices dilute the K signal with O/R noise"

### Practical Recommendations

| Use Case | Recommended? | Rationale |
|----------|--------------|-----------|
| K as optimization target | ✅ Yes | Best K results achieved |
| O/R as optimization target | ❌ No | K = 0.9740 (worse than K-only) |
| Unified (K + O/R) | ❌ No | All formulas underperform K-only |
| **O/R as diagnostic** | ✅ Yes | O/R > 0 indicates learned structure |
| **O/R for coordination** | ✅ Yes | Paper 6's validated use case |

---

## Summary Statistics (All Results with Corrected O/R)

### Formula Comparison

| Formula | Best K | % of 1.5 | vs K-only |
|---------|--------|----------|-----------|
| **k_only** | **1.3288** | **88.6%** | --- |
| log_scaled | 1.2583 | 83.9% | -5.3% |
| original | 1.1666 | 77.8% | -12.2% |
| multiplicative | 1.0105 | 67.4% | -24.0% |
| or_only | 0.9740 | 64.9% | -26.7% |
| additive | 0.6390 | 42.6% | -51.9% |

### Key Numbers

- **Best K achieved**: 1.3288 (K-only formula)
- **K-O/R correlation**: r = -0.21 (p = 0.002)
- **1.5 threshold crossed**: ❌ No (best is 88.6%)
- **O/R-only control**: K = 0.9740 (confirms O/R alone doesn't help)

---

## Raw Data Files

### Track L1 (Corrected O/R)
- `logs/track_l/track_l_l1_20251128_151652.json` - n=200 correlation study

### Track L4 (Formula Comparison, Corrected O/R)
- `logs/track_l/track_l_l4_20251128_152034.json` - k_only (K=1.3288)
- `logs/track_l/track_l_l4_20251128_152208.json` - original (K=1.1666)
- `logs/track_l/track_l_l4_20251128_152340.json` - multiplicative (K=1.0105)
- `logs/track_l/track_l_l4_20251128_152508.json` - additive (K=0.6390)
- `logs/track_l/track_l_l4_20251128_152650.json` - log_scaled (K=1.2583)
- `logs/track_l/track_l_l4_20251128_152934.json` - or_only (K=0.9740) 🆕

---

## Limitations & Future Work

### Acknowledged Limitations

1. **Single environment**: All experiments run in one coordination environment
2. **Sample size**: n=200 for correlation, 100 generations for optimization
3. **CMA-ES only**: Did not test other optimization algorithms
4. **Continuous → Discrete**: O/R discretization introduces binning artifacts

### Future Work

1. **Multi-environment validation**: Test K-O/R relationship across diverse domains
2. **Alternative optimizers**: Genetic algorithms, gradient-based methods
3. **Theoretical analysis**: Why does K-only optimization work best?
4. ~~**Threshold investigation**: Why is 1.5 so hard to cross?~~ **ANSWERED** - See below

---

## 🚨 MAJOR DISCOVERY: CMA-ES Stability (Nov 28, 2025)

**See `CMAES_STABILITY_FINDINGS.md` for complete details.**

A follow-up investigation revealed that the "early peak degradation" in Track L is **environment-specific, NOT fundamental to K-Index**:

| Environment | Best K | Degradation | Peak Gen |
|-------------|--------|-------------|----------|
| **Simplified** | **1.91** | **1.8%** | **36** |
| Track L | 1.33 | ~30% | 0-10 |

**Key Implications**:
- K-Index CAN exceed 1.5 with proper environment
- Track L environment causes instability, not K-Index itself
- CMA-ES works correctly (outperforms random search)
- New question: "What properties of Track L cause K instability?"

---

## Conclusion

The **corrected O/R computation** reveals that K and O/R are **weakly negatively correlated** (r = -0.21), consistent with Paper 6's interpretation. However, this does NOT change our main finding:

**K-only optimization outperforms all unified indices.**

Adding O/R to the optimization objective—whether as a target, regularizer, or adaptive control—degrades K-Index performance. O/R is valuable as a **diagnostic metric** (indicating learned structure) but not as an optimization target.

The CMA-ES stability investigation further shows that the difficulty reaching K > 1.5 is specific to Track L's environment, not a fundamental property of K-Index optimization.

---

*Last updated: November 28, 2025*
*Status: Corrected results documented, CMA-ES stability investigated*
