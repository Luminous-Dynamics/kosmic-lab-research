# WVS Time Series Variable Mapping for A₁ (Governance Quality)

**Dataset**: WVS_Time_Series_1981-2022_csv_v5_0.csv
**Size**: 1.4 GB
**Observations**: 443,489 individual responses
**Coverage**: 1981-2022 (7 waves)
**Delimiter**: Comma (not semicolon as initially expected)

---

## Variable Naming Structure

The WVS Time Series dataset uses **alphabetic codes** (A, D, E, F, G, etc.) instead of the V-codes used in individual wave datasets.

### Key Variable Prefixes

- **S variables**: Survey identifiers (country, year, wave)
- **A variables**: Social values and norms (148 total)
- **D variables**: Confidence in institutions (81 total)
- **E variables**: Social capital and trust (221 total)
- **F variables**: Economic values (125 total)
- **G variables**: Political values (114 total)

---

## Identified Variables for A₁ Trust Component

### Identifier Variables
- **S003**: Country code (column 4)
- **S020**: Year of survey (column 23)
- **S002**: Wave number 1-7 (relates to S002VS in header)
- **COUNTRY_ALPHA**: 3-letter country code (column 5)

### Trust Variables (E series)
| Variable | Column | Description (inferred) |
|----------|--------|------------------------|
| **E018** | 391 | Trust in people you know personally |
| **E023** | 395 | Generalized trust ("Most people can be trusted") |
| **E025** | 396 | Trust in people you meet for the first time |

### Institutional Confidence Variables (D series)
| Variable | Column | Description |
|----------|--------|-------------|
| **D069** | 363 | Confidence in: Parliament |
| **D071** | 365 | Confidence in: Political parties |
| **D072** | 366 | Confidence in: Government |
| **D075** | 369 | Confidence in: The courts |

**Additional D variables** (D001-D081): Confidence in other institutions (churches, armed forces, press, police, etc.) - 81 total confidence variables available.

---

## Data Processing Requirements

### Challenge: Individual → Country-Year Aggregation
WVS data is at the **individual respondent level** (443,489 rows), but we need **country-year averages** to merge with:
- V-Dem data (country-year level)
- K(t) harmonies (global-year level)

### Processing Steps Required
1. Filter to relevant variables (S003, S020, E023, D069, D071, D072, D075)
2. Handle missing data codes (-4 = "Not asked", -2 = "No answer", etc.)
3. Recode variables to [0-1] scale if needed
4. Group by (S003, S020) = (country, year)
5. Compute country-year means for each trust variable
6. Merge with V-Dem A₁ preliminary data (matching on country-year)

### Expected Output
- **trust_wvs_1981_2022.csv** with columns:
  - country_code
  - year
  - generalized_trust (E023 mean)
  - confidence_parliament (D069 mean)
  - confidence_parties (D071 mean)
  - confidence_government (D072 mean)
  - confidence_courts (D075 mean)
  - institutional_trust (composite of D069, D071, D072, D075)
  - n_respondents (sample size for validation)

---

## Integration with A₁ Preliminary

### Current A₁ Formula (V-Dem only)
```
A₁_preliminary = 0.5 × democratic_quality + 0.5 × policy_effectiveness
```

### Planned A₁ Final Formula (V-Dem + WVS)
```
A₁_final = 0.3 × democratic_quality + 0.3 × policy_effectiveness + 0.4 × trust
```

Where:
- **democratic_quality** = 0.4×v2x_libdem + 0.3×v2x_delibdem + 0.3×v2x_egaldem (from V-Dem)
- **policy_effectiveness** = 0.6×(1-v2x_execorr) + 0.4×v2xlg_legcon (from V-Dem)
- **trust** = 0.5×generalized_trust (E023) + 0.5×institutional_trust (D069-D075 mean) (from WVS)

### Coverage Limitations
- **V-Dem**: 1789-2024 (236 years, 27,913 country-year observations)
- **WVS**: 1981-2022 (41 years, sparse country coverage per wave)

**Implication**: Final A₁ can only be computed for **1981-2022** where WVS data exists. For 1789-1980, use A₁_preliminary as proxy.

---

## Alternative: Use A₁ Preliminary for Full Analysis

### Current A₁ Preliminary Performance (2020)
- **K₁ (Capacity)**: 0.825
- **A₁ (Quality)**: 0.471
- **Gap₁**: 0.354 (35.4% capacity unutilized) ✅ **Within expected range 0.20-0.40**
- **Coverage**: 1789-2024 (full historical period!)

### Advantages of A₁ Preliminary
1. ✅ **Full historical coverage**: 1789-2024 (not just 1981-2022)
2. ✅ **Already validated**: Gap₁ within expected range
3. ✅ **High-quality data**: V-Dem is gold standard for governance metrics
4. ✅ **Ready for use**: Can proceed to A₂-A₇ immediately
5. ✅ **Comparable**: Top/bottom countries make intuitive sense (Nordics vs conflict zones)

### Disadvantages of Skipping WVS
1. ❌ **Missing trust dimension**: No direct measure of societal trust
2. ❌ **Incomplete A₁**: Only 2 of 3 planned components
3. ❌ **Validation gap**: Can't confirm governance quality perception matches institutional reality

---

## Recommended Next Steps

### Option A: Process WVS Now (2-3 days additional work)
**Pros**: Complete A₁ with full trust component, more robust for 1981-2022 period
**Cons**: Complex processing, sparse coverage, delays A₂-A₇ implementation

### Option B: Proceed with A₁ Preliminary (recommended for now)
**Pros**: Full historical coverage, already validated, faster progress to complete A(t)
**Cons**: Missing direct trust measure (though V-Dem includes some trust proxies in democracy indices)

### Option C: Hybrid Approach
1. Use A₁ preliminary for full 1789-2024 analysis
2. Compute A₁ final (with WVS) for 1981-2022 as sensitivity check
3. Include both in Supplementary Materials
4. Show that results are robust regardless of trust component

---

## Technical Notes

### Missing Data Codes in WVS
- `-1`: Don't know
- `-2`: No answer
- `-3`: Not applicable
- `-4`: Not asked in this wave
- `-5`: Other missing

**Handling**: Exclude all negative values when computing means.

### Scale Harmonization
- **E023 (Trust)**: Typically binary (1 = Most people can be trusted, 2 = Need to be very careful)
  - Recode: 1 → 1.0, 2 → 0.0
- **D069-D075 (Confidence)**: Typically 4-point scale (1 = A great deal, 2 = Quite a lot, 3 = Not very much, 4 = None at all)
  - Recode: 1 → 1.0, 2 → 0.67, 3 → 0.33, 4 → 0.0

---

**Date**: 2025-11-27
**Status**: Variable mapping complete, ready for processing decision
**Next**: Decide Option A vs B vs C for A₁ completion
