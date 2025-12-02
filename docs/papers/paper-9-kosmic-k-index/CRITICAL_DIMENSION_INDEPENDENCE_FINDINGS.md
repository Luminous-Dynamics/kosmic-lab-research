# Critical Dimension Independence Findings

**Date**: November 29, 2025
**Status**: REQUIRES PAPER REVISION

---

## Executive Summary

Analysis of **1,450 real agent trajectories** from Track L experiments reveals that the paper's claim of dimension independence (mean |r| = 0.109) is **NOT supported** by the data.

**Actual finding**: mean |r| = **0.455** (4.2× higher than claimed)

---

## Key Findings

### 1. Overall Correlation Structure (n=1,450)

| Pair | Correlation | Status |
|------|-------------|--------|
| K_I-K_P | 0.782 | ❌ High |
| K_R-K_H | 0.779 | ❌ High |
| K_R-K_A | 0.771 | ❌ High |
| K_I-K_H | 0.704 | ❌ High |
| K_R-K_I | 0.657 | ❌ High |
| K_A-K_H | 0.614 | ❌ High |
| K_A-K_I | 0.544 | ❌ Moderate |
| K_P-K_H | 0.519 | ❌ Moderate |
| K_R-K_P | 0.492 | ❌ Moderate |
| K_A-K_P | 0.399 | ❌ Moderate |
| K_I-K_M | 0.186 | ✅ Independent |
| K_A-K_M | 0.135 | ✅ Independent |
| K_P-K_M | 0.100 | ✅ Independent |
| K_M-K_H | 0.099 | ✅ Independent |
| K_R-K_M | -0.043 | ✅ Independent |

**Independent pairs**: 5/15 (33%)
**Correlated pairs**: 10/15 (67%)

### 2. The Only Truly Independent Dimension: K_M

K_M (Meta/Memory) is the **only dimension** that shows independence from all others:
- K_R-K_M: r = -0.043
- K_A-K_M: r = 0.135
- K_I-K_M: r = 0.186
- K_P-K_M: r = 0.100
- K_H-K_M: r = 0.099

This validates K_M as measuring something genuinely different (temporal memory depth).

### 3. Correlated Clusters Identified

**Cluster 1: "Reactive-Behavioral" (K_R, K_A, K_H)**
- All highly correlated (r > 0.6)
- May represent a single underlying "behavioral intensity" factor

**Cluster 2: "Model Quality" (K_I, K_P)**
- r = 0.782
- Entropy matching and prediction accuracy are related

### 4. Environment Dependence

| Environment | Mean |r| | Status |
|-------------|---------|--------|
| Commons | 0.252 | ✅ Good |
| Delayed | 0.251 | ✅ Good |
| Simple | 0.401 | ⚠️ Moderate |
| Unknown | 0.533 | ❌ High |

Independence is **better in specific environments** (Commons, Delayed).

### 5. Agent Type Dependence

| Agent Type | Mean |r| | Status |
|------------|---------|--------|
| linear_untrained | 0.189 | ✅ Best |
| recurrent | 0.335 | ⚠️ Moderate |
| linear_trained | 0.450 | ❌ High |
| random | 0.493 | ❌ High |
| cmaes | 0.553 | ❌ High |

Independence is **best in untrained agents** before learning induces correlations.

---

## Root Cause Analysis

### Why are dimensions correlated?

1. **Behavioral Coupling**: Agents that respond strongly (high K_R) tend to have high agency (K_A) and match norms (K_H) - this is expected for well-behaved agents.

2. **Model Coupling**: Integration (K_I) and Prediction (K_P) both reflect internal model quality - correlation is expected.

3. **Training Effect**: Trained agents develop coordinated behaviors that correlate multiple dimensions.

### Why is K_M independent?

K_M measures **temporal depth** (history utilization), which is:
- Architecturally determined (recurrent vs feedforward)
- Independent of behavioral style
- Not optimized during typical training

---

## Recommendations for Paper Revision

### Option A: Revise the Claim (Recommended)

**Old text**: "Mean |r| = 0.109, supporting dimensional orthogonality"

**New text**:
> "While K_M shows consistent independence from other dimensions (all |r| < 0.2), the remaining dimensions form two correlated clusters: a 'behavioral' cluster (K_R, K_A, K_H; mean r ≈ 0.7) and a 'model quality' cluster (K_I, K_P; r = 0.78). The overall mean |r| = 0.45 reflects that dimensions capture related but distinct aspects of agent behavior. The 7D framework remains valuable: correlated dimensions are not redundant when they measure conceptually distinct properties, and K_M provides unique discriminative power for memory-dependent tasks."

### Option B: Refocus on K_M

Emphasize that **K_M is the novel contribution** - it's truly independent and captures something no other dimension does.

### Option C: Reduce to 4D

Consider reducing to: K_R, K_I, K_M, K_S (one per cluster + independent ones).
But this loses interpretability.

---

## Action Items

1. [ ] **Update paper Section 4.5**: Replace 0.109 with 0.455 and add nuanced discussion
2. [ ] **Add correlation matrix**: Include full 7×7 correlation matrix in supplementary
3. [ ] **Emphasize K_M uniqueness**: Highlight K_M as the novel independent dimension
4. [ ] **Acknowledge limitations**: Dimensions correlate in practice, which is expected
5. [ ] **Add environment analysis**: Note that independence varies by environment

---

## Conclusion

This is not a fatal flaw but requires honest acknowledgment. The K-Vector framework remains valuable because:

1. **K_M is genuinely novel** - no existing metric captures memory depth
2. **Correlation ≠ Redundancy** - correlated dimensions can measure distinct properties
3. **Environment matters** - in specific environments, independence improves
4. **Interpretability preserved** - 7D is more interpretable than 3D PCA

The key revision is moving from "orthogonal dimensions" to "partially correlated dimensions capturing distinct behavioral aspects."

---

*Analysis performed on 1,450 real agent trajectories from Track L experiments*
*Date: November 29, 2025*
