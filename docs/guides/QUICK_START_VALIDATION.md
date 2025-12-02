# Quick Start: Validation Pipeline ⚡

**For when HYDE processing completes**

---

## Step 1: Verify HYDE Output ✅

```bash
# Check if processing completed successfully
ls -lh data/sources/hyde/processed/

# You should see:
# hyde_aggregated_-3000_2020.csv (size varies)
```

---

## Step 2: Run Complete Validation Pipeline 🚀

**Option A: Run all at once (90 minutes)**
```bash
make extended-compute && \
make extended-validate && \
make extended-plot && \
make external-validate && \
make robustness-test
```

**Option B: Run step-by-step (recommended for first time)**
```bash
# Stage 1: Compute 5000-year K(t) (~15-30 min)
make extended-compute

# Stage 2: Validate events (~10-15 min)
make extended-validate

# Stage 3: Generate plots (~5 min)
make extended-plot

# Stage 4: Cross-validate with HDI, GDP, etc. (~10-15 min)
make external-validate

# Stage 5: Robustness tests (~15-20 min)
make robustness-test
```

---

## Step 3: Verify All Outputs 📊

```bash
# Quick verification script
echo "Checking outputs..."
test -f logs/historical_k_extended/k_t_series_5000y.csv && echo "✓ K(t) series" || echo "✗ Missing K(t)"
test -f logs/historical_k_extended/detailed_results.csv && echo "✓ Detailed results" || echo "✗ Missing detailed"
test -d logs/historical_k_extended/plots && echo "✓ Plots generated" || echo "✗ Missing plots"
test -f logs/validation_external/validation_report.md && echo "✓ External validation" || echo "✗ Missing validation"
test -f logs/robustness/robustness_report.md && echo "✓ Robustness tests" || echo "✗ Missing robustness"
```

---

## Step 4: View Results 📈

**K(t) Time Series**:
```bash
head -20 logs/historical_k_extended/k_t_series_5000y.csv
```

**Validation Summary**:
```bash
cat logs/historical_k_extended/validation_report.md
```

**Plots** (Open in browser):
```bash
ls -1 logs/historical_k_extended/plots/*.png
# Copy to your local machine or view via file manager
```

---

## If Something Goes Wrong 🔧

### Error: "No HYDE data found"
```bash
# Re-check HYDE processing
ls -lh data/sources/hyde/processed/
cat /tmp/hyde_process.log

# If empty, HYDE is still processing - wait longer
ps aux | grep hyde_integration
```

### Error: "Missing dependencies"
```bash
# Reinstall with Poetry
poetry install --sync
```

### Error: "Config file errors"
```bash
# Verify config paths
cat historical_k/k_config_extended.yaml | grep path:
```

---

## After Validation Completes ✨

**Next Steps**:
1. Review all validation reports
2. Generate manuscript figures from plots
3. Write Results section with validation findings
4. Run publication readiness check:
   ```bash
   make publication-ready
   ```
5. Prepare submission to Nature Human Behaviour

---

## Current Status

**Data**: ✅ All 32 datasets + HYDE + Seshat ready
**Scripts**: ✅ Integration and computation scripts ready
**HYDE**: ⏳ Processing (6:32 elapsed, ~20-30 min total)
**Validation**: 📋 Ready to execute

**Estimated time to Results section**: ~2 hours after HYDE completes

---

*Quick reference created: 2025-11-21*
