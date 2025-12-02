# A(t) Processing Scripts

**Purpose**: Build the A(t) (Actualization/Quality) Index to complement K(t) (Capacity) Index

**Status**: Ready to run `process_vdem.py` for A₁ (Governance) prototype

---

## Quick Start

```bash
cd /srv/luminous-dynamics/kosmic-lab/docs/papers/Historical-k/processing_scripts

# Step 1: Process V-Dem for A₁ preliminary
python3 process_vdem.py

# Expected output:
# - governance_quality_vdem_1789_2024.csv in ../data_sources/processed/
# - A₁ preliminary values for 27,914 country-year observations
# - 2020 validation: Gap₁ should be 0.27-0.33 (within expected range)
```

---

## Available Scripts

### ✅ `process_vdem.py` (Ready to Run)
**Purpose**: Extract governance quality indicators from V-Dem v15  
**Input**: `../data_sources/external/vdem/V-Dem-CY-Core-v15.csv` (204 MB)  
**Output**: `../data_sources/processed/governance_quality_vdem_1789_2024.csv`  
**Coverage**: 1789-2024 (236 years!)  

**Components Computed**:
- `democratic_quality`: 40% liberal democracy + 30% deliberative + 30% egalitarian
- `policy_effectiveness`: 60% anti-corruption + 40% legislative constraints
- `a1_preliminary`: 50% democratic + 50% effectiveness (before WVS trust merge)

**Validation**: Compares A₁₂₀₂₀ to K₁₂₀₂₀ = 0.825, expects Gap₁ ≈ 0.27-0.33

### 🚧 `process_wvs.py` (Planned)
**Purpose**: Extract trust and cooperation data from World Values Survey  
**Input**: `../data_sources/external/wvs/WVS_Time_Series_1981-2022_csv_v5_0.csv` (1.4 GB)  
**Output**: `../data_sources/processed/trust_wvs_1981_2022.csv`  
**Coverage**: 1981-2022 (7 waves)

**Variables to Extract**:
- V24: Generalized trust ("Most people can be trusted")
- V108-V123: Confidence in institutions (government, parliament, civil service)

**Next Step**: Merge with A₁ preliminary (40% weight for trust component)

### 🚧 `compute_a1_governance.py` (Planned)
**Purpose**: Merge V-Dem + WVS for final A₁ (Governance Quality)  
**Formula**: A₁ = 0.3×Democratic_Quality + 0.3×Effectiveness + 0.4×Trust  
**Output**: `../data_sources/processed/a1_governance_final_1810_2022.csv`

---

## Expected Results

### A₁ (Governance Quality) for 2020

**Hypothesis**: K₁₂₀₂₀ = 0.825 (high capacity) but A₁₂₀₂₀ ≈ 0.50 (moderate quality)

**Expected Gap₁₂₀₂₀**:
```
Gap₁ = K₁ - A₁ = 0.825 - 0.50 = 0.325 (33% capacity unutilized)
```

**Interpretation**:
- High governance *capacity*: Institutions, legal frameworks, democratic structures exist
- Moderate governance *quality*: Corruption, trust erosion, policy effectiveness gaps
- This gap explains why "democracy feels broken" despite high formal capacity

### Historical Evolution (1810 vs 2020)

**1810**: Expect small gap (limited capacity = limited quality expectations)
- K₁₁₈₁₀ ≈ 0.022 (very low capacity)
- A₁₁₈₁₀ ≈ 0.015-0.020 (very low quality)
- Gap₁₁₈₁₀ ≈ 0.002-0.007 (capacity mostly utilized, just low overall)

**2020**: Expect large gap (high capacity not fully actualized)
- K₁₂₀₂₀ = 0.825 (high capacity)
- A₁₂₀₂₀ ≈ 0.50 (moderate quality)
- Gap₁₂₀₂₀ ≈ 0.325 (33% capacity gap - major finding!)

**Key Insight**: Gap grew over time as capacity increased faster than quality

---

## Data Status

### ✅ Extracted and Ready
- V-Dem v15: 27,914 observations, 1789-2024
- WVS: 443,489 observations, 1981-2022
- Pew: 2024 governance trust survey
- Gini: 271 observations, 1960-2023

### ⏳ Still Needed (Priority 2)
- World Bank Governance Indicators (WGI)
- World Happiness Report (WHR)
- Transparency International CPI

---

## Next Steps

### Immediate (1-2 hours):
1. ✅ Run `process_vdem.py`
2. Inspect output in `../data_sources/processed/`
3. Verify 2020 Gap₁ is within expected range

### This Week (3-5 days):
1. Build `process_wvs.py` to extract trust data
2. Merge V-Dem + WVS for final A₁
3. Compute provisional A(t) = geometric_mean(A₁...A₇)
4. Calculate Gap(t) and Ratio(t) time series

### Manuscript Integration (Week 2):
1. Add A(t) methodology to Methods section
2. Present Gap(t) results (major finding!)
3. Discuss capacity-quality distinction in Discussion
4. Update Conclusion with landmark contribution

---

## Validation Criteria

### Mathematical Properties
- ✅ 0 ≤ A₁ ≤ 1 for all observations
- ✅ A₁ ≤ K₁ (quality cannot exceed capacity)
- ✅ Gap₁ = K₁ - A₁ ≥ 0 (always non-negative)

### Expected Ranges (2020)
- Gap₁: 0.20-0.40 (20-40% capacity unutilized)
- Ratio₁: 0.60-0.80 (60-80% capacity actualized)
- A₁ mean: 0.45-0.55 globally

### Red Flags
- ⚠️ If A₁ > K₁ for any observation (impossible!)
- ⚠️ If Gap₁ < 0.10 or > 0.50 for 2020 (outside plausible range)
- ⚠️ If historical Gap₁₁₈₁₀ > Gap₁₂₀₂₀ (contradicts hypothesis)

---

**Created**: 2025-11-27  
**Author**: Tristan Stoltz & Claude Code  
**Project**: Historical K(t) Index - Phase 2 A(t) Implementation
