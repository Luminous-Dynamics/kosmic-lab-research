# Phase 1: Fix 2001-2020 Coverage - Action Plan

**Date**: 2025-11-21
**Status**: 🔄 **READY TO EXECUTE**
**Priority**: **HIGH** - Blocks extension to 2025

---

## ✅ Completed Steps

### 1. Root Cause Identified
- Modern K(t) file (`logs/historical_k/k_t_series.csv`) only has data through 2010
- Extended computation loads this file and merges with ancient data
- Result: Years 2011-2020 only have HYDE data (evolutionary_progression), missing other 6 harmonies

### 2. Data Coverage Assessed
**Confirmed available datasets with 2011-2020 data**:
- ✅ V-Dem: 1789-2024 (EXCELLENT!)
- ✅ QOG: 1946-2023 (EXCELLENT!)
- 🟡 UCDP: 1989-2021 (GOOD)

**Missing/problematic**:
- 🔴 Inter-State Wars: 1823-2003 (needs update)
- ❌ Most Excel files: Format/parsing issues
- ⚠️ UNESCO, HDI: Year column issues

### 3. Configuration Updated
- ✅ `historical_k/k_config.yaml` now explicitly specifies:
  ```yaml
  temporal_coverage:
    start_year: 1810
    end_year: 2020
    granularity: 10
  ```
- ✅ Backup created: `k_config.yaml.backup-2025-11-21`

---

## 🎯 Remaining Actions

### Option A: Quick Fix - Recompute with Existing Data (RECOMMENDED)

**Approach**: Recompute standard K(t) through 2020 using V-Dem + QOG + UCDP
**Feasibility**: ⭐⭐⭐⭐⭐ (5/5) - High confidence
**Timeline**: 30-60 minutes

**Steps**:

1. **Verify ETL will load data through 2020** (5 min)
   ```bash
   # Check if compute_k.py respects temporal_coverage config
   # May need to inspect historical_k/etl.py
   ```

2. **Run standard K(t) computation** (15-30 min)
   ```bash
   poetry run python historical_k/compute_k.py \
       --config historical_k/k_config.yaml \
       2>&1 | tee logs/recompute_k_2020.log
   ```

3. **Validate output** (5 min)
   ```bash
   # Check that k_t_series.csv now has rows through 2020
   tail -n 5 logs/historical_k/k_t_series.csv

   # Count total rows (should be 22: 1810-2020 in decades + header)
   wc -l logs/historical_k/k_t_series.csv
   ```

4. **Rerun extended computation** (10 min)
   ```bash
   poetry run python historical_k/compute_k_extended.py \
       --config historical_k/k_config_extended.yaml
   ```

5. **Verify complete K-index 1850-2020** (5 min)
   ```bash
   # Check for complete harmonies in 2010, 2020
   grep "^2010\|^2020" logs/historical_k_extended/k_t_series_5000y.csv
   ```

**Expected Outcome**:
- ✅ Modern K(t) complete through 2020
- ✅ Extended K(t) has all 7 harmonies for years 1850-2020
- ✅ Ready to extend to 2023-2025

**Risk**: LOW - V-Dem + QOG should provide sufficient proxy coverage

---

### Option B: Complete Fix - Update All Datasets First

**Approach**: Fix all dataset issues before recomputing
**Feasibility**: ⭐⭐⭐☆☆ (3/5) - More complex
**Timeline**: 2-4 hours

**Additional Steps**:

1. **Fix Excel file parsing** (1-2 hours)
   - Investigate format of each Excel file
   - Add manual parsing logic if needed
   - Test coverage assessment on fixed files

2. **Fix CSV encoding issues** (30 min)
   - Re-download INTRA-STATE datasets with correct encoding
   - Or convert existing files: `iconv -f latin1 -t utf-8`

3. **Investigate UNESCO/HDI formats** (30 min)
   - Manual inspection to find year columns
   - Update ETL to handle non-standard formats

4. **Update Inter-State Wars** (15 min)
   - Download Correlates of War v6.0
   - Replace outdated 2003 version

5. **Then proceed with Option A steps**

**Expected Outcome**:
- ✅ All datasets functional
- ✅ Complete proxy coverage
- ✅ Foundation for easy future updates

**Risk**: MEDIUM - May discover additional format issues

---

## 💡 Recommendation: Start with Option A

**Rationale**:
1. V-Dem + QOG + UCDP provide excellent 2011-2020 coverage
2. Low risk, high reward
3. Can still do Option B improvements later
4. Gets us to publication faster

**If Option A succeeds**:
- ✅ Problem solved!
- Can proceed directly to Phase 2 (extension to 2023)

**If Option A encounters issues**:
- Switch to Option B
- Fix datasets systematically
- Retry computation

---

## 🚀 Next Immediate Actions

**ACTION 1**: Verify ETL respects `temporal_coverage` config
```bash
# Check if compute_k.py loads data based on config end_year
grep -n "temporal_coverage\|end_year" historical_k/compute_k.py historical_k/etl.py
```

**ACTION 2**: Run test computation (quick validation)
```bash
# Run with verbose logging to see what years are processed
poetry run python historical_k/compute_k.py --config historical_k/k_config.yaml --verbose
```

**ACTION 3**: If successful, rerun extended computation
```bash
poetry run python historical_k/compute_k_extended.py --config historical_k/k_config_extended.yaml
```

---

## 📊 Success Criteria

### Must Have ✅
- [ ] Modern K(t) file has rows through 2020
- [ ] Year 2010 row has all 6 harmony values (not zero/empty)
- [ ] Year 2020 row has all 6 harmony values (not zero/empty)
- [ ] Extended K(t) shows K-index for years 2010 and 2020

### Should Have 🎯
- [ ] All harmonies have non-zero values for 2001-2020
- [ ] K-index shows realistic progression from 2000 to 2020
- [ ] No sudden jumps or unrealistic values

### Nice to Have 💎
- [ ] All external datasets working (Excel files parsed correctly)
- [ ] Complete temporal coverage documentation
- [ ] Automated data availability checks in pipeline

---

## 🔄 Rollback Plan

If recomputation causes issues:

1. **Restore original config**
   ```bash
   sudo cp historical_k/k_config.yaml.backup-2025-11-21 historical_k/k_config.yaml
   ```

2. **Keep original K(t) series**
   - Already exists at `logs/historical_k/k_t_series.csv`
   - Unchanged unless recomputation succeeds

3. **Re-evaluate approach**
   - May need to debug ETL data loading
   - May need to fix specific dataset issues first

---

## ⏱️ Time Estimates

| Task | Optimistic | Realistic | Pessimistic |
|------|------------|-----------|-------------|
| **Option A** | 30 min | 45 min | 1 hour |
| Verify ETL | 5 min | 10 min | 15 min |
| Recompute K(t) | 15 min | 20 min | 30 min |
| Rerun extended | 5 min | 10 min | 15 min |
| Validation | 5 min | 5 min | 10 min |

| **Option B** | 2 hours | 3 hours | 4 hours |
| Fix Excel files | 1 hour | 1.5 hours | 2 hours |
| Fix encodings | 20 min | 30 min | 45 min |
| Update datasets | 10 min | 15 min | 20 min |
| Option A steps | 30 min | 45 min | 1 hour |

---

## 📝 Decision Point

**Do we proceed with Option A (quick fix) or Option B (complete fix)?**

**My recommendation**: **Option A**

Reasoning:
- Gets us to results faster
- Lower risk
- V-Dem + QOG are high-quality, well-maintained datasets
- Can always improve datasets later if needed
- Publication timeline benefits from speed

**If you agree**, I'll proceed with:
1. Verify ETL configuration handling
2. Recompute modern K(t) through 2020
3. Rerun extended computation
4. Validate complete 1850-2020 series

**If you prefer Option B**, I'll:
1. Systematically fix all dataset issues
2. Document each fix
3. Run comprehensive coverage assessment
4. Then recompute with full dataset confidence

---

*Plan created: 2025-11-21*
*Status: AWAITING EXECUTION DECISION*
