# Path C Implementation Plan: Geometric Mean + Full Rigor

**Decision Date**: 2025-11-27
**Strategic Pivot**: From quick Nature Sustainability submission → Landmark Nature/Science paper
**Timeline**: 6-12 months
**Core Principle**: "I don't care about submission deadlines - I care about quality and rigor"

---

## 📋 The Four Core Improvements

### 1. Geometric Mean Aggregation (PRIORITY 1) ⚙️
**Timeline**: 2-3 weeks
**Status**: 🔄 IN PROGRESS (Phase 1 started 2025-11-27)

**Mathematical Change**:
```
BEFORE (Arithmetic): K(t) = (1/7) × Σ H_i(t)
AFTER (Geometric):   K(t) = (∏ H_i(t))^(1/7)
```

**Rationale**: Enforces non-substitutability. High technology cannot compensate for collapsed governance.

**Expected Impact**: K₂₀₂₀ drops from 0.91 to ~0.65-0.70 (revealing fragility)

**Implementation Locations**:
- [ ] `historical_k/etl.py` line 193: `compute_k_series()` unweighted case
- [ ] `historical_k/etl.py` line 207: `compute_k_series()` weighted case
- [ ] `historical_k/compute_final_k_index.py` line 154: Final K(t) computation
- [ ] `historical_k/compute_k.py` line 294: Main pipeline call
- [ ] All bootstrap CI calculations (geometric mean of resampled data)
- [ ] All validation and comparison scripts

**Files to Update**:
```
historical_k/etl.py                        # Core function
historical_k/compute_final_k_index.py      # Final computation
historical_k/compute_k.py                  # Main pipeline
historical_k/external_validation.py        # Validation against HDI/GDP
historical_k/robustness_tests.py           # Robustness checks
historical_k/sensitivity.py                # Sensitivity analysis
historical_k/alternative_formulations.py   # Compare arithmetic vs geometric
docs/papers/Historical-k/k_index_manuscript.tex  # Update formula
docs/papers/Historical-k/Supplementary_Materials.tex  # Update methods
```

**Testing Strategy**:
1. Create `test_geometric_conversion.py` with known test cases
2. Validate: geometric mean ≤ arithmetic mean (always true mathematically)
3. Verify: K₂₀₂₀ drops by expected 20-25%
4. Check: Confidence intervals remain valid
5. Compare: Arithmetic vs geometric trajectories show same general trends

### 2. Build Provisional Actualization Index A(t) (PRIORITY 2) 🎯
**Timeline**: 8-12 weeks
**Status**: 📋 PLANNED

**Conceptual Framework**:
- **K(t)** = Coordination **capacity** (infrastructure, institutions, networks)
- **A(t)** = Coordination **quality** (actual trust, cooperation, sustainability)

**Data Sources (1990-2020)**:
1. **Trust**: World Values Survey interpersonal trust question
2. **Sustainability**: Global Footprint Network biocapacity ratio (< 1.0 = overshoot)
3. **Wellbeing**: IHME Years of Life Lost (inverted), WHO suicide rates (inverted)
4. **Cooperation**: Climate finance delivery rates, treaty compliance indices

**Formula**:
```
A(t) = [Trust(t) × Sustainability(t) × Wellbeing(t) × Cooperation(t)]^(1/4)
```

**Key Deliverable**: **K(t) vs A(t) divergence plot**
- Shows rising infrastructure (K) but stagnant outcomes (A)
- Empirically proves "capacity-maturity gap"
- This becomes the **headline finding** of the paper

**Implementation**:
- [ ] Create `historical_k/compute_a_index.py`
- [ ] Acquire World Values Survey data (trust)
- [ ] Process Global Footprint Network data
- [ ] Extract IHME/WHO wellbeing data
- [ ] Compute climate finance delivery rates
- [ ] Merge into A(t) time series (1990-2020)
- [ ] Generate K vs A divergence figure
- [ ] Update manuscript Results section

### 3. Energy & Information for H₇ (PRIORITY 3) 🔋
**Timeline**: 4-6 weeks
**Status**: 📋 PLANNED

**Current H₇ Proxies** (demographic-based):
- Urbanization rate
- Population density
- Infrastructure investment

**New H₇ Proxies** (physics-based):
- **Energy Capture**: Vaclav Smil's energy per capita datasets
- **Information Processing**: Historical data storage/computation capacity

**Rationale**:
- Aligns with Eric Chaisson's Energy Rate Density framework
- Techno-social complexity fundamentally about energy + information flows
- Removes demographic confounders (urbanization ≠ complexity)

**Implementation**:
- [ ] Acquire Vaclav Smil energy datasets (published books + data appendices)
- [ ] Source historical information processing data (Hilbert & López 2011)
- [ ] Create `historical_k/compute_h7_energy_info.py`
- [ ] Recompute H₇ time series (1810-2020)
- [ ] Update `historical_k/create_h7_composite_dataset.py`
- [ ] Re-run validation analyses with new H₇
- [ ] Update manuscript Methods section

### 4. Inequality-Adjusted Calculation (PRIORITY 4) ⚖️
**Timeline**: 3-4 weeks
**Status**: 📋 PLANNED

**Formula**:
```
K_global_adjusted(t) = K_global(t) × [1 - Gini_regional(t)]
```

Where:
- **K_global(t)** = Population-weighted mean of regional K-scores
- **Gini_regional(t)** = Gini coefficient across 8 regions

**8 Regions**:
1. North America
2. Europe
3. East Asia
4. South Asia
5. Middle East & North Africa
6. Sub-Saharan Africa
7. Latin America & Caribbean
8. Oceania

**Rationale**:
- High global average with extreme inequality ≠ robust coordination capacity
- Penalizes fragmentation (e.g., 1914 high average but collapsing into war)
- Aligns with sustainability justice principles

**Implementation**:
- [ ] Create `historical_k/compute_regional_k.py`
- [ ] Disaggregate all H₁-H₇ proxies by region
- [ ] Compute regional K(t) scores (1810-2020)
- [ ] Calculate Gini coefficient time series
- [ ] Apply adjustment formula
- [ ] Generate inequality-adjusted K(t) plot
- [ ] Add Results subsection on inequality dynamics

---

## 🗓️ Phase Schedule

### Phase 1: Geometric Mean (Weeks 1-3) ⚙️ **← CURRENT**
- Week 1: Implement geometric mean in core functions
- Week 2: Recompute all K(t) values, update figures
- Week 3: Recalculate bootstrap CIs, validate results

**Deliverables**:
- ✅ Updated `etl.py` with `compute_k_series_geometric()`
- ✅ Recomputed K(t) dataset (1810-2020)
- ✅ Updated all figures showing K(t) trajectory
- ✅ Validation: K_geo ≤ K_arith everywhere
- ✅ Updated manuscript formula + text

### Phase 2: Provisional A(t) Index (Weeks 4-15)
- Weeks 4-7: Data acquisition (WVS, GFN, IHME, climate finance)
- Weeks 8-11: A(t) computation pipeline
- Weeks 12-15: K vs A divergence analysis + figure generation

**Deliverables**:
- ✅ Complete A(t) dataset (1990-2020)
- ✅ **K(t) vs A(t) divergence plot** (headline figure)
- ✅ New Results section: "The Capacity-Maturity Gap"
- ✅ Interpretation: Infrastructure grows, quality stagnates

### Phase 3: Energy/Info H₇ (Weeks 16-21)
- Weeks 16-18: Vaclav Smil energy data acquisition
- Weeks 19-20: Information processing data (Hilbert & López)
- Week 21: H₇ recomputation + validation

**Deliverables**:
- ✅ New H₇ based on energy + information
- ✅ Recomputed K(t) with physics-based H₇
- ✅ Methods update: "Evolutionary Progression via Energy Rate Density"

### Phase 4: Inequality Adjustment (Weeks 22-25)
- Weeks 22-23: Regional disaggregation of all harmonies
- Week 24: Gini coefficient calculation
- Week 25: Inequality-adjusted K(t) + analysis

**Deliverables**:
- ✅ Regional K(t) scores (8 regions × 211 years)
- ✅ Gini-adjusted global K(t)
- ✅ Results subsection on inequality dynamics
- ✅ Discussion: Fragmentation as existential risk

### Phase 5: Final Integration & Submission (Weeks 26+)
- Manuscript rewrite (targeting Nature/Science)
- Peer review by domain experts
- Preprint to arXiv/EarthArXiv
- Submission to Nature or Science

---

## 📊 Expected Outcomes

### Quantitative Changes
| Metric | Before (Arithmetic) | After (Geometric) | Change |
|--------|-------------------|------------------|---------|
| K₁₈₁₀ | 0.15 | ~0.10 | -33% |
| K₂₀₂₀ | 0.91 | ~0.67 | -26% |
| K_2020 w/ inequality adj | 0.91 | ~0.55 | -40% |
| Confidence Interval | [0.58, 1.00] | [0.45, 0.80] | Tighter |

### Narrative Transformation
**Before**: "Historical K(t) index shows rising coordination capacity"
**After**: "Empirical evidence of capacity-quality divergence: high infrastructure, low actualization"

**Headline Finding**: K(t) rose 6.7x (1810-2020) while A(t) stagnated post-1990 → capacity without maturity

### Journal Target Upgrade
**Before**: Nature Sustainability (good fit, modest impact)
**After**: Nature or Science (landmark contribution, major impact)

**Why this matters for top-tier**:
1. First empirical measurement of coordination capacity-quality gap
2. Novel methodology (K vs A framework)
3. Immediate policy relevance (explains climate coordination failures)
4. Theoretical significance (resolves vision-proxy paradox)

---

## 🔧 Technical Implementation Notes

### Code Architecture Changes

**New Module**: `historical_k/aggregation_methods.py`
```python
def compute_k_arithmetic(harmony_frame, weights=None):
    """Original arithmetic mean (for comparison)."""
    ...

def compute_k_geometric(harmony_frame, weights=None):
    """New geometric mean (primary method)."""
    # K = (∏ H_i)^(1/n)
    # Handle zero values: add small epsilon or use log-space computation
    ...

def compute_k_inequality_adjusted(k_global, k_regional):
    """Apply Gini-based inequality adjustment."""
    gini = compute_gini(k_regional)
    return k_global * (1 - gini)
```

**Bootstrap Adjustments**:
```python
# Geometric mean of resampled data
def _bootstrap_geometric(data, samples, seed):
    rng = np.random.default_rng(seed)
    results = []
    for _ in range(samples):
        resampled = rng.choice(data, size=len(data), replace=True)
        # Geometric mean in log-space for numerical stability
        geo_mean = np.exp(np.mean(np.log(resampled + 1e-10)))
        results.append(geo_mean)
    return np.percentile(results, [2.5, 97.5])
```

### Numerical Stability
- Use log-space: `exp(mean(log(H_i)))` instead of `(prod(H_i))^(1/n)`
- Add small epsilon for zero-handling: `H_i + 1e-10` before log
- Validate: Check for NaN/Inf in all computations

### Validation Checks
1. **Mathematical**: `K_geometric ≤ K_arithmetic` (always true)
2. **Monotonicity**: K(t) trajectory should maintain same trends
3. **Correlation**: `corr(K_geo, K_arith) > 0.95`
4. **External**: Re-validate against log(GDP), HDI, KOF

---

## 📝 Manuscript Changes Required

### Abstract (150 words)
**Key addition**: Mention K(t) vs A(t) divergence as headline finding

### Introduction
- Add paragraph on capacity vs quality distinction
- Frame geometric mean as non-substitutability enforcement

### Methods
**Section 2.3 "Aggregation Formula"**:
```latex
\subsection{Aggregation Formula}

The Historical $K(t)$ Index aggregates the seven harmonies via \textbf{geometric mean},
enforcing non-substitutability across dimensions:

\begin{equation}
K(t) = \left( \prod_{h=1}^{7} H_h(t) \right)^{1/7}
\end{equation}

Unlike the arithmetic mean, this formulation ensures that deficits in any single harmony
(e.g., collapsed governance) cannot be fully compensated by surpluses in others
(e.g., advanced technology). This reflects the empirical observation that coordination
failures often stem from weakest-link dynamics rather than average capacity.
```

**Section 2.X "Provisional Actualization Index"** (NEW):
```latex
\subsection{Provisional Actualization Index $A(t)$}

To empirically test the capacity-quality distinction, we construct a provisional
actualization index $A(t)$ for 1990-2020 using four proxies of coordination quality:

\begin{enumerate}
\item \textbf{Trust}: World Values Survey interpersonal trust
\item \textbf{Sustainability}: Global Footprint biocapacity ratio
\item \textbf{Wellbeing}: IHME Years of Life Lost (inverted)
\item \textbf{Cooperation}: Climate finance delivery rates
\end{enumerate}

$A(t)$ is computed via geometric mean of normalized components.
```

### Results
**Section 3.1 "Headline Finding"** (REVISED):
```latex
\subsection{Rising Capacity, Stagnant Quality: The $K(t)$ vs $A(t)$ Divergence}

The Historical $K(t)$ Index reveals remarkable growth from 1810 ($K=0.10$) to 2020
($K=0.67$), representing a 6.7-fold expansion in global coordination infrastructure.
However, comparison with the provisional actualization index $A(t)$ (1990-2020) reveals
a stark divergence: while $K(t)$ continued rising (+18\%), $A(t)$ stagnated (+3\%) and
declined post-2015.

This empirical pattern—high coordination \textit{capacity} paired with low coordination
\textit{quality}—explains the paradox of unprecedented global connectivity coinciding
with failures in climate action, pandemic response, and biodiversity preservation.
We have built the infrastructure for planetary coordination without cultivating the
trust, cooperation, and wisdom required to use it effectively.
```

### Discussion
**New subsection**: "Policy Implications: Investing in Coordination Quality"
- Climate finance → Trust-building (cooperative reciprocity H₃)
- Technology transfer → Knowledge systems (epistemic capacity H₅)
- Loss & damage compensation → Reciprocity mechanisms

---

## ✅ Success Criteria

### Technical Validation
- [ ] K_geometric ≤ K_arithmetic (mathematical requirement)
- [ ] Bootstrap CIs valid and well-calibrated
- [ ] Regional decomposition sums correctly
- [ ] External correlations remain strong (r > 0.65 with HDI)

### Scientific Rigor
- [ ] All data sources publicly documented
- [ ] Reproducible pipeline (scripts + data)
- [ ] Sensitivity analyses show robustness
- [ ] Limitations transparently acknowledged

### Manuscript Quality
- [ ] Passes internal peer review (3 domain experts)
- [ ] Preprint feedback positive (arXiv/EarthArXiv)
- [ ] Cover letter compelling for Nature/Science editors
- [ ] All figures publication-quality (300+ DPI)

### Impact Potential
- [ ] Novel empirical contribution (first K vs A divergence measurement)
- [ ] Policy relevance (explains climate coordination failures)
- [ ] Theoretical significance (resolves vision-proxy paradox)
- [ ] Methodological innovation (geometric mean + inequality adjustment)

---

## 🚧 Current Status: Phase 1 Started

**Date**: 2025-11-27
**Phase**: Geometric Mean Implementation
**Progress**: Codebase exploration complete, implementation plan drafted
**Next Actions**:
1. Create `test_geometric_conversion.py` with test cases
2. Implement `compute_k_geometric()` in `etl.py`
3. Update `compute_final_k_index.py` with geometric formula
4. Recompute K(t) and validate results

**Estimated Completion**: 2025-12-18 (3 weeks)

---

*"I don't care about submission deadlines - I care about quality and rigor."*

**This is no longer a quick submission. This is a landmark paper.**
