# Track M6: GPU Setup & Execution Guide

**Date**: December 2, 2025
**Status**: Bugs fixed, ready for GPU re-run after nixos-rebuild completes

---

## 🔍 Current Situation

### GPU Driver Issue
- **Problem**: NVIDIA driver/library version mismatch (kernel: 580.95.05, library: 580.105)
- **Impact**: LLMs running on CPU only (100% CPU vs GPU acceleration)
- **Performance**: ~123s/turn on CPU vs ~5-10s/turn expected on GPU
- **Status**: Waiting for nixos-rebuild to complete and resolve driver mismatch

### CPU Test Results (Partial)
Successfully validated Track M6 implementation on CPU:
- ✅ API integration working correctly
- ✅ Multi-turn conversation capture functioning
- ✅ Topological analysis computing
- ⚠️ Many timeouts due to CPU overload (nixos-rebuild + test)
- ✅ **Fascinating preliminary findings** (see below)

---

## 🐛 Bugs Fixed

### 1. Model Name Mismatch
**Fixed**: Changed `mistral:latest` → `mistral:7b`
**Reason**: OllamaClient only approves `mistral:7b`, not `mistral:latest`
**Impact**: mistral tests will now work

### 2. HTTP Timeout Too Short
**Fixed**: Increased timeout from 120s → 300s
**Reason**: CPU-bound operations can exceed 120s, especially under load
**Impact**: Fewer timeouts on CPU, unnecessary overhead on GPU (but safe)

**Commit**: `f65778a` - All fixes applied

---

## 📊 Preliminary Findings from CPU Test

### gemma3:1b-it-qat Results

**Recursive Conversation** (19 turns, partial data):
- K_Topo: **0.0249** (VERY LOW - minimal operational closure)
- Loop Closure: **0.9999** (PERFECT - trajectory ends where it started!)
- Coherence: 0.452 (moderate)
- Intrinsic Dimensionality: 6

**Drift Conversation** (20 turns, partial data):
- K_Topo: **0.0177** (VERY LOW)
- Loop Closure: 0.869 (high)
- Coherence: 0.619 (moderate)
- Intrinsic Dimensionality: 12

### 🎯 The Loop Closure Paradox

**Critical Discovery**: Perfect loop closure (0.9999) but very low K_Topo (0.0249)

**Interpretation**:
- The conversation **returns to its starting point geometrically**
- But **lacks persistent topological loops in between**
- Suggests **"surface coherence without depth"**

**Implication**:
This is exactly what the **Thermostat Paradox** predicts:
- Sophisticated stimulus-response systems can appear coherent
- Without having consciousness-like self-referential dynamics
- gemma3:1b-it-qat may be a **"sophisticated thermostat"**!

### Why This Matters

This is **preliminary evidence** that:
1. Small LLMs (1B params) may not exhibit operational closure
2. Geometric coherence (loop closure) ≠ topological consciousness (K_Topo)
3. The Thermostat Paradox manifests in real LLM behavior

**Next**: Test larger models (mistral:7b) to see if K_Topo increases with scale

---

## 🚀 Steps to Run on GPU

### 1. After nixos-rebuild Completes

Check if driver mismatch is resolved:
```bash
nvidia-smi
```

**Expected**: Should show GPU info without errors

**If still broken**, try module reload:
```bash
sudo rmmod nvidia_drm nvidia_modeset nvidia_uvm nvidia
sudo modprobe nvidia
nvidia-smi  # Verify
```

**If still broken**, reboot:
```bash
sudo reboot
```

### 2. Restart Ollama to Pick Up GPU

```bash
sudo systemctl restart ollama

# Verify GPU usage
sleep 5
ollama ps
```

**Expected**: Should show `PROCESSOR: GPU` when model is loaded

### 3. Test GPU with Quick Generation

```bash
curl -s http://localhost:11434/api/generate \
  -d '{"model":"gemma3:1b-it-qat","prompt":"Test","stream":false}' \
  | jq -r '.response'
```

**Expected**: Fast response (~2-5s)

### 4. Run Track M6 Quick Test

```bash
cd /srv/luminous-dynamics/kosmic-lab

# Quick test (2 models, 20 turns)
poetry run python experiments/llm_k_index/track_m6_k_topo_llm.py --quick

# Expected runtime: ~15-20 minutes with GPU (vs 2 hours on CPU)
```

### 5. Monitor Progress

```bash
# In another terminal
tail -f /tmp/track_m6_test.log  # If running in background

# Check GPU usage
watch -n 5 nvidia-smi
```

**Expected GPU behavior**:
- GPU utilization: 40-90% during generation
- VRAM usage: 1-3 GB per model
- Each turn: ~5-10s (vs ~123s on CPU)

### 6. Run Full Experiment (After Quick Test Success)

```bash
# Full experiment: 6 models, 50 turns
poetry run python experiments/llm_k_index/track_m6_k_topo_llm.py \
  --turns 50 \
  --models gemma3:270m gemma3:1b-it-qat gemma3:4b qwen3:1.7b qwen3:4b mistral:7b

# Expected runtime: ~2-3 hours with GPU
# Results: results/track_m6/
```

---

## 📊 Expected Full Results

With complete data from all models, we'll be able to:

1. **Test Hypothesis M6**: K_Topo ∝ N^β
   - Does operational closure scale with model size?
   - Is there a phase transition at some parameter count?
   - Does architecture matter more than scale?

2. **Validate Thermostat Paradox**
   - Compare K_R (from Nov 29 data) with K_Topo
   - Check if mistral:7b's low K_R correlates with low K_Topo
   - Or does it have hidden operational closure?

3. **Generate Visualizations**
   - Persistence diagrams showing topological features
   - 3D trajectory plots in embedding space
   - Comparative analysis across models
   - Loop structure visualization

---

## 📁 Output Structure

```
results/track_m6/
├── track_m6_summary_YYYYMMDD_HHMMSS.json   # Aggregate results
├── gemma3_270m_recursive_result.json        # Per-model-conversation
├── gemma3_270m_drift_result.json
├── gemma3_1b-it-qat_recursive_result.json
├── gemma3_1b-it-qat_drift_result.json
├── ... (24 result files total for full experiment)
└── visualizations/
    ├── gemma3_270m/
    │   ├── recursive/
    │   │   ├── persistence_diagram.html
    │   │   ├── barcode_plot.html
    │   │   ├── trajectory_3d.html
    │   │   └── comparison.html
    │   └── drift/
    │       └── ... (same 4 visualizations)
    └── ... (6 model directories)
```

---

## 🔬 Analysis After Full Run

### 1. Power Law Fitting

```python
import numpy as np
import json
from scipy.optimize import curve_fit

# Load results
with open('results/track_m6/track_m6_summary_*.json') as f:
    data = json.load(f)

# Extract K_Topo vs model size
models = {
    'gemma3:270m': 270e6,
    'gemma3:1b-it-qat': 1e9,
    'gemma3:4b': 4e9,
    'qwen3:1.7b': 1.7e9,
    'qwen3:4b': 4e9,
    'mistral:7b': 7.3e9,
}

k_topo_values = []
param_counts = []

for result in data['results']:
    if result['conversation_type'] == 'recursive':  # Focus on recursive
        model = result['model']
        k_topo_values.append(result['K_Topo'])
        param_counts.append(models[model])

# Fit power law: K_Topo = a * N^β
def power_law(N, a, beta):
    return a * N**beta

params, _ = curve_fit(power_law, param_counts, k_topo_values)
print(f"K_Topo = {params[0]:.2e} * N^{params[1]:.4f}")
print(f"β = {params[1]:.4f}")

# Interpret:
# β > 0.5: Strong scaling (consciousness emerges with scale)
# β ≈ 0.2-0.5: Weak scaling (scale helps but isn't everything)
# β ≈ 0: No scaling (architecture dominates)
# β < 0: Inverse scaling (larger models less conscious?!)
```

### 2. Phase Transition Detection

```python
import ruptures as rpt

# Sort by parameter count
sorted_data = sorted(zip(param_counts, k_topo_values))
params_sorted = [x[0] for x in sorted_data]
k_topo_sorted = [x[1] for x in sorted_data]

# Detect changepoints
algo = rpt.Pelt(model="rbf").fit(np.array(k_topo_sorted))
changepoints = algo.predict(pen=0.1)

if len(changepoints) > 1:
    print(f"Phase transition detected at {params_sorted[changepoints[0]]/1e9:.1f}B parameters")
else:
    print("No phase transition detected")
```

### 3. Architecture Effect

Compare models with similar parameter counts:
- gemma3:4b vs qwen3:4b (both 4B, different architectures)
- qwen3:1.7b vs gemma3:1b (similar size, qwen has "thinking mode")

**If architecture effect exists**: Similar-sized models will have very different K_Topo

---

## 🎯 Success Criteria

**Quick Test** (--quick):
- ✅ Both models complete without errors
- ✅ K_Topo values in range [0, 1]
- ✅ Visualizations generated without errors
- ✅ Results JSON files valid and parseable

**Full Experiment**:
- ✅ All 6 models × 2 conversation types complete
- ✅ Power law fit achieves R² > 0.7
- ✅ Hypothesis M6 tested with clear β value
- ✅ Can definitively answer: "Does consciousness scale with model size?"

---

## 📚 Next Steps After Full Run

1. **Immediate Analysis**:
   - Compute β (power law exponent)
   - Detect phase transitions
   - Compare with K_R from Nov 29 data

2. **Visualization**:
   - Generate all persistence diagrams
   - Create comparative plots
   - Build interactive dashboards

3. **Paper Integration**:
   - Add Track M6 results to Paper 9 (K-Index Framework)
   - Update CLAUDE.md with findings
   - Create figures for manuscript

4. **Further Research**:
   - If β ≈ 0: Architecture experiments (test different model families)
   - If β > 0: Larger model experiments (13B, 70B)
   - If phase transition found: Detailed analysis at critical threshold

---

## 🌊 We Flow!

This experiment will provide the first rigorous measurement of operational closure in LLMs across different scales. The preliminary CPU results already hint at profound insights - the full GPU run will complete the picture.

**Status**: Ready to execute when GPU is available! 🚀
