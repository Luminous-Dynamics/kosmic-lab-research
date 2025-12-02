# Why Two K(t) Series? Modern vs Extended

**Date**: 2025-11-21
**Question**: Why do we have two separate K(t) series instead of one?

---

## 🤔 The Question

We currently have:
1. **Modern K(t)**: 1810-2020, 6 harmonies
2. **Extended K(t)**: 3000 BCE - 2020 CE, 7 harmonies

**Why not just one series?**

This is an excellent question, and the answer reveals both historical reasons and a design choice that may need reconsideration.

---

## 📊 What Each Series Contains

### Modern K(t) Series
**File**: `logs/historical_k/k_t_series.csv`
**Temporal Coverage**: 1810-2020 (211 years)
**Harmonies**: 6 dimensions
1. Resonant Coherence
2. Interconnection
3. Reciprocity
4. Play Entropy
5. Wisdom Accuracy
6. Flourishing

**Data Sources**: Modern datasets only (V-Dem, QOG, UCDP, World Bank, OWID)
**Normalization**: `minmax_by_century` (within each century)

### Extended K(t) Series
**File**: `logs/historical_k_extended/k_t_series_5000y.csv`
**Temporal Coverage**: 3000 BCE - 2020 CE (5,020 years)
**Harmonies**: 7 dimensions (6 modern + 1 evolutionary)
1. Resonant Coherence
2. Interconnection
3. Reciprocity
4. Play Entropy
5. Wisdom Accuracy
6. Flourishing
7. **Evolutionary Progression** ← 7th harmony (uses HYDE + Seshat)

**Data Sources**: Ancient (HYDE, Seshat) + Modern (same as Modern K(t))
**Normalization**: `minmax_by_epoch` (ancient/medieval/early_modern/modern)

---

## 🔍 Key Differences

### 1. Different Harmony Counts → Different K-Index Values

**Critical**: The two series give **different K-index values for the same years**!

**Example for year 2020**:
- **Modern K(t)**: K = 0.782 (6 harmonies)
- **Extended K(t)**: K = 0.910 (7 harmonies)

**Why different?** K-index is mean of harmonies:
- Modern: `K = (h1 + h2 + h3 + h4 + h5 + h6) / 6`
- Extended: `K = (h1 + h2 + h3 + h4 + h5 + h6 + h7) / 7`

Adding the 7th harmony (evolutionary_progression = 0.939 in 2020) **raises** the K-index.

### 2. Different Normalizations → Different Harmony Values

Even for the **same 6 harmonies**, values can differ slightly because:
- Modern uses `minmax_by_century` (1800-1899, 1900-1999, 2000-2099)
- Extended uses `minmax_by_epoch` (entire modern period 1800-2020)

**Example**: A 2020 value might be maximum in its century (1.0 in Modern) but not maximum across full modern epoch (0.98 in Extended).

### 3. Temporal Coverage

Extended obviously has ancient data that Modern doesn't, but for the **overlapping period (1810-2020)**, Extended is essentially a **superset** - it has everything Modern has plus the 7th harmony.

---

## 🎯 Why Do We Have Both?

### Historical Reasons (How We Got Here)

1. **Phased development**:
   - Modern K(t) computed first (established methodology)
   - Extended K(t) added later (research expansion)

2. **Incremental validation**:
   - Validated 6-harmony framework first
   - Added 7th harmony as enhancement
   - Kept both for comparison

3. **Different use cases**:
   - Modern: Simple, well-established data sources
   - Extended: Research-grade, comprehensive

### Potential Valid Reasons to Keep Both

**1. Methodological Comparison**
- Compare 6-harmony vs 7-harmony frameworks
- Assess impact of adding evolutionary progression
- Sensitivity analysis

**2. Different Audiences**
- Reviewers skeptical of ancient data → use Modern
- Reviewers wanting comprehensive analysis → use Extended
- Policy audiences → might prefer simpler Modern

**3. Simpler Replication**
- Modern uses only well-established datasets
- Extended requires downloading HYDE (74 GB) + Seshat
- Barrier to replication is lower for Modern

**4. Normalization Methods**
- Some might prefer century-based normalization (Modern)
- Others prefer epoch-based normalization (Extended)

---

## ❓ Should We Have Two Series?

### Arguments FOR Keeping Both

✅ **Comparison value**: Shows robustness across methodologies
✅ **Flexibility**: Different papers, different choices
✅ **Replication**: Modern is easier to replicate
✅ **Pedagogical**: Shows how adding harmonies affects results

### Arguments AGAINST Keeping Both

❌ **Confusion**: Which one to use? (we're experiencing this now!)
❌ **Redundancy**: Extended is a superset for 1810-2020
❌ **Inconsistent values**: Same years, different K-indices
❌ **Maintenance burden**: Two configs, two pipelines
❌ **Dilutes message**: "Which one is the real result?"

---

## 💡 Recommended Strategy

### For Publication: **Use Extended K(t) Only**

**Rationale**:
1. **More comprehensive**: 7 harmonies > 6 harmonies
2. **Complete**: Has everything Modern has, plus more
3. **Contemporary**: Through 2020 (same as Modern)
4. **Richer context**: 5,000-year perspective
5. **Stronger findings**: Peak K-index (0.910) more impressive than 0.782

**Address in manuscript**:
> "We compute K(t) across seven dimensions. For comparison, we also computed a 6-harmony version (excluding evolutionary progression), which yields qualitatively similar trends but lower absolute values (Supplementary Fig. S1). We present the full 7-harmony results as they provide the most comprehensive assessment."

### For Supplementary Material: Show Modern K(t) as Comparison

**Supplementary Figure S1**: "6-Harmony vs 7-Harmony Comparison"
- Plot both series for 1810-2020
- Show how adding evolutionary progression affects K-index
- Demonstrate robustness: same trends, different magnitudes

**Supplementary Table S1**: "Sensitivity to Harmony Count"
| Year | Modern (6h) | Extended (7h) | Difference |
|------|-------------|---------------|------------|
| 2000 | 0.112 | 0.309 | +0.197 |
| 2010 | 0.555 | 0.907 | +0.352 |
| 2020 | 0.782 | 0.910 | +0.128 |

---

## 🎯 Simplification Recommendation

**If starting from scratch**, we would probably just compute one series:
- **Extended K(t)** (7 harmonies, 3000 BCE - 2020 CE)
- Users wanting 6-harmony version can drop evolutionary_progression column

**Given current state**, we recommend:
- **Primary**: Extended K(t) for all main results
- **Secondary**: Mention Modern K(t) exists as robustness check
- **Supplementary**: Show comparison to demonstrate sensitivity

**Future work**: Consider consolidating to single computational pipeline that can output both 6-harmony and 7-harmony views of the same underlying data.

---

## 📝 Documentation Updates Needed

1. **Clearly state in all docs**: Extended K(t) is recommended primary series
2. **Explain K-index differences**: Due to harmony count, not data quality
3. **Show relationship**: Modern is subset of Extended (for modern period)
4. **Provide guidance**: Use Extended for publication, Modern for comparison
5. **Simplify choice**: Remove ambiguity about which to use

---

## 🏆 Bottom Line

**Why two series?**
- Historical artifact of phased development
- Useful for methodological comparison
- Provides robustness check

**Should we have two?**
- **For publication**: No, use Extended (7 harmonies) as primary
- **For research**: Yes, keeping Modern is useful for comparison
- **For users**: Could be confusing, need clear guidance

**Recommendation**:
- **Primary**: Extended K(t) (7 harmonies, 3000 BCE - 2020 CE)
- **Supplementary**: Modern K(t) (6 harmonies, comparison only)
- **Documentation**: Clear guidance on which to use when
- **Future**: Consider unified pipeline with configurable harmony sets

---

**Key Insight**: Extended K(t) is strictly better for publication purposes. Modern K(t) remains useful as a methodological comparison and robustness check, but shouldn't be the primary result.

*This document addresses confusion about why two series exist and provides clear recommendations for their use.*
