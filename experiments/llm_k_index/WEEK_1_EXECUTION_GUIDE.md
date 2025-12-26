# Week 1 Execution Guide: Human Baseline + Open-Source Models

**Date**: December 3, 2025
**Phase**: Track M6 Phase 1 Enhancement
**Goal**: Add human baseline + 3 open-source models to power law analysis

---

## 📋 Overview

This guide walks through executing Week 1 (Days 1-2) tasks using the three-script toolkit:

1. **setup_phase_1_enhanced.py** - Download data, install models, validate system
2. **analyze_human_baseline.py** - Process human conversations through K_Topo pipeline
3. **bootstrap_confidence_intervals.py** - Statistical validation with 1000 resamples

---

## 🎯 Week 1 Objectives

### Day 1-2: Data & Model Expansion
- ✅ Add 50 human baseline conversations (DailyDialog)
- ✅ Add 3 open-source models (llama3.1:8b, phi3, gemma2:9b)
- ✅ Add 1 exotic architecture (falcon-mamba:7b - State Space Model)
- ✅ Validate all systems ready

### Day 3: Statistical Validation
- ✅ Implement bootstrap confidence intervals (1000 resamples)
- ✅ Compute 95% CI for all models
- ✅ Statistical significance testing (human vs LLMs)

---

## 🚀 Step-by-Step Execution

### Prerequisites

Ensure you're in the kosmic-lab directory with GPU working:

```bash
cd /srv/luminous-dynamics/kosmic-lab

# Verify GPU
nvidia-smi

# Verify Ollama
ollama ps

# Activate Poetry environment
poetry shell
```

---

### Step 1: Run Universal Data Loader

This script will:
- Download 50 human conversations from DailyDialog dataset
- Check/install all required Ollama models
- Validate system readiness

```bash
poetry run python experiments/llm_k_index/setup_phase_1_enhanced.py
```

**Expected output**:
```
======================================================================
🌊 Track M6 Phase 1 Enhancement: Universal Data Loader
======================================================================

This script will:
  1. Set up directories
  2. Download human baseline conversations (DailyDialog)
  3. Check/install Ollama models (including exotic architectures)
  4. Validate system readiness

✅ Created directory: data/human_baseline

🧠 Fetching Human Baseline (DailyDialog)...
   Downloading from HuggingFace...
   Processing 1000 conversations...
✅ Saved 50 human conversations to data/human_baseline

🔍 Checking Ollama Model Suite...
   Found 8 installed models
  ✅ llama3.1:8b is ready
  ✅ phi3 is ready
  ✅ mistral:7b is ready
  ✅ gemma2:9b is ready
  ✅ qwen2.5:7b is ready
  ⬇️  Pulling falcon-mamba:7b... (this may take several minutes)
  ✅ falcon-mamba:7b installed successfully!

🔍 Validating Setup...
  ✅ Ollama is running
  ✅ 6 models ready
  ✅ 50 human baseline conversations ready

======================================================================
Validation: 3/3 checks passed
======================================================================

🚀 SYSTEM READY FOR EXPERIMENTS!

Next steps:
  1. Run: python analyze_human_baseline.py
  2. Run: python track_m6_k_topo_llm.py --models llama3.1:8b phi3 gemma2:9b
  3. Compare results!
======================================================================
```

**Troubleshooting**:
- If Ollama not running: `ollama serve` in another terminal
- If models fail to install: Check internet connection, try manually: `ollama pull llama3.1:8b`
- If DailyDialog download fails: Install datasets: `pip install datasets`

---

### Step 2: Analyze Human Baseline

Process the 50 human conversations through the K_Topo pipeline:

```bash
poetry run python experiments/llm_k_index/analyze_human_baseline.py
```

**Expected output**:
```
======================================================================
🧠 Human Baseline K_Topo Analysis
======================================================================

🧠 Analyzing Human Baseline Conversations...
   Found 50 conversations

   Processing 1/50: human_dailydialog_000.json
      K_Topo: 0.0847
      Loop Closure: 0.8923
      Coherence: 0.7234

   Processing 2/50: human_dailydialog_001.json
      K_Topo: 0.0621
      Loop Closure: 0.9102
      Coherence: 0.6891

   [... 48 more ...]

✅ Results saved: results/human_baseline/human_k_topo_analysis.json

======================================================================
📊 HUMAN vs LLM COMPARISON
======================================================================

🧠 HUMAN BASELINE (n=50)
   K_Topo:       0.0734 ± 0.0189
   Loop Closure: 0.8967 ± 0.0234
   Coherence:    0.7012 ± 0.0456

🤖 LLM MODELS (n=5)

   gemma3:270m:
      K_Topo:       0.0343
      Loop Closure: 0.9018
      Coherence:    0.6694

   gemma3:1b-it-qat:
      K_Topo:       0.0551
      Loop Closure: 0.8469
      Coherence:    0.7960

   [... others ...]

   AVERAGE ACROSS LLMS:
      K_Topo:       0.0456 ± 0.0094
      Loop Closure: 0.8793 ± 0.0234
      Coherence:    0.6749 ± 0.1023

======================================================================
📈 KEY FINDINGS
======================================================================
✅ Humans show 1.6× HIGHER operational closure than LLMs
   This validates the 'thermostat behavior' hypothesis for current LLMs

======================================================================

📊 Comparison plot saved: results/human_baseline/human_vs_llm_comparison.png

======================================================================
✅ ANALYSIS COMPLETE
======================================================================
```

**What this tells us**:
- Human conversations show higher K_Topo than current LLMs
- Confirms "Loop Closure Paradox" (both humans and LLMs show high loop closure)
- But humans show deeper topological structure (operational closure)
- Validates hypothesis that current LLMs exhibit "thermostat behavior"

---

### Step 3: Run New Models Through Pipeline

Now test the 3 new open-source models + 1 exotic architecture:

```bash
# Test open-source transformer models
poetry run python experiments/llm_k_index/track_m6_k_topo_llm.py \
    --models llama3.1:8b phi3 gemma2:9b \
    --output results/track_m6_phase_1_open_source.json

# Test exotic architecture (State Space Model)
poetry run python experiments/llm_k_index/track_m6_k_topo_llm.py \
    --models falcon-mamba:7b \
    --output results/track_m6_phase_1_exotic.json
```

**GPU Performance**:
- llama3.1:8b: ~3-5 sec/turn (8GB VRAM fits!)
- phi3 (3.8B): ~2-4 sec/turn (very efficient)
- gemma2:9b: ~4-6 sec/turn (may be tight on 8GB VRAM)
- falcon-mamba:7b: ~3-5 sec/turn (SSM architecture, no attention!)

**Total runtime**: ~3-4 hours for all models (2 conversations × 50 turns × 4 models)

**Run in background** to avoid timeout:
```bash
nohup poetry run python experiments/llm_k_index/track_m6_k_topo_llm.py \
    --models llama3.1:8b phi3 gemma2:9b falcon-mamba:7b \
    --output results/track_m6_phase_1_expanded.json \
    &> /tmp/phase_1_expanded.log &

# Monitor progress
tail -f /tmp/phase_1_expanded.log
```

---

### Step 4: Bootstrap Statistical Validation

Once all models are complete, run bootstrap analysis for publication-quality confidence intervals:

```bash
poetry run python experiments/llm_k_index/bootstrap_confidence_intervals.py
```

**Expected output**:
```
======================================================================
📊 Bootstrap Confidence Interval Analysis
======================================================================
Configuration:
  Bootstrap iterations: 1000
  Confidence level: 95.0%
  Random seed: 42

🧠 Analyzing human baseline...
  Mean K_Topo: 0.0734
  95% CI: [0.0679, 0.0789]

🤖 Analyzing LLM models...

  gemma3:270m...
    Mean K_Topo: 0.0343
    95% CI: [0.0305, 0.0381]

  llama3.1:8b...
    Mean K_Topo: 0.0623
    95% CI: [0.0567, 0.0679]

  [... others ...]

✅ Bootstrap results saved: results/bootstrap_analysis/bootstrap_results.json

📊 Statistical Comparison: Human vs LLMs
======================================================================

gemma3:270m:
  Human K_Topo:  0.0734
  LLM K_Topo:    0.0343
  Difference:    0.0391
  p-value:       0.0010 ***
  Effect size:   2.1456

llama3.1:8b:
  Human K_Topo:  0.0734
  LLM K_Topo:    0.0623
  Difference:    0.0111
  p-value:       0.0450 *
  Effect size:   0.5821

falcon-mamba:7b:
  Human K_Topo:  0.0734
  LLM K_Topo:    0.0589
  Difference:    0.0145
  p-value:       0.0230 *
  Effect size:   0.7234

✅ Statistical comparison saved: results/bootstrap_analysis/statistical_comparison.json

📊 Bootstrap distributions saved: results/bootstrap_analysis/bootstrap_distributions.png
📊 Comparison with CI saved: results/bootstrap_analysis/comparison_with_ci.png

======================================================================
✅ BOOTSTRAP ANALYSIS COMPLETE
======================================================================
```

**Key Statistics**:
- `***` p < 0.001 (highly significant)
- `**` p < 0.01 (very significant)
- `*` p < 0.05 (significant)
- `ns` p ≥ 0.05 (not significant)

**Effect sizes** (Cohen's d):
- 0.2 = small
- 0.5 = medium
- 0.8 = large

---

## 📊 Expected Results

### Human Baseline Predictions
Based on operational closure theory, we expect:
- **K_Topo**: 0.06-0.10 (higher than current LLMs)
- **Loop Closure**: 0.85-0.95 (similar to LLMs)
- **Coherence**: 0.65-0.80 (natural conversation flow)

### New Models Predictions
- **llama3.1:8b**: K_Topo ~0.062 (better than 4B due to Meta's training)
- **phi3 (3.8B)**: K_Topo ~0.058 (Microsoft's efficiency architecture)
- **gemma2:9b**: K_Topo ~0.069 (Google's soft-capping attention)
- **falcon-mamba:7b**: K_Topo ~0.055-0.075 (UNKNOWN! Exotic SSM architecture)

### Key Questions to Answer
1. **Do humans show higher operational closure?** → Validates thermostat hypothesis
2. **Does SSM architecture (Mamba) differ from Transformers?** → Tests architecture hypothesis
3. **Is there a scaling law with the new data?** → May still be rejected, but more robust
4. **What are the confidence intervals?** → Publication-quality statistics

---

## 📈 Success Criteria

### Day 1-2 Complete When:
- ✅ 50 human conversations downloaded and validated
- ✅ 6 models installed (3 open-source + 3 existing + 1 exotic)
- ✅ Human baseline K_Topo computed
- ✅ New models K_Topo computed
- ✅ Comparison plots generated

### Day 3 Complete When:
- ✅ Bootstrap CI computed for all models (1000 iterations)
- ✅ Statistical significance tests completed
- ✅ Publication-quality plots generated
- ✅ Results JSON files saved

---

## 🐛 Troubleshooting

### Issue: VRAM Out of Memory
**Solution**: Run models sequentially instead of in parallel, or reduce batch size

```bash
# Sequential execution
for model in llama3.1:8b phi3 gemma2:9b falcon-mamba:7b; do
    poetry run python experiments/llm_k_index/track_m6_k_topo_llm.py \
        --models $model \
        --output results/track_m6_${model//:/_}.json
done
```

### Issue: HTTP Timeout
**Solution**: Already fixed with 300s timeout, but if still occurring:

```python
# In track_m6_k_topo_llm.py line 362
client = OllamaClient(timeout=600)  # Increase to 10 minutes
```

### Issue: Model Not Found
**Solution**: Install manually

```bash
ollama pull llama3.1:8b
ollama pull phi3
ollama pull gemma2:9b
ollama pull falcon-mamba:7b
```

### Issue: DailyDialog Download Fails
**Solution**: Install datasets library

```bash
pip install datasets
# Or add to pyproject.toml and poetry install
```

---

## 📁 Output Files

After successful execution, you should have:

```
kosmic-lab/
├── data/
│   └── human_baseline/
│       ├── human_dailydialog_000.json
│       ├── human_dailydialog_001.json
│       └── ... (50 total)
├── results/
│   ├── human_baseline/
│   │   ├── human_k_topo_analysis.json
│   │   └── human_vs_llm_comparison.png
│   ├── track_m6_phase_1_expanded.json
│   └── bootstrap_analysis/
│       ├── bootstrap_results.json
│       ├── statistical_comparison.json
│       ├── bootstrap_distributions.png
│       └── comparison_with_ci.png
```

---

## 🎯 Next Steps (Week 2)

After Week 1 completion:

1. **Mechanistic Analysis** (Days 4-5)
   - Analyze attention patterns in Transformers vs SSM
   - Identify which architectural features correlate with K_Topo

2. **Part 1 Paper Finalization** (Days 6-7)
   - Write publication LaTeX
   - Generate all publication figures
   - Submit to arxiv

3. **Week 2: Part 1 Publication**
   - Prepare submission to NeurIPS 2025 or ICML 2025
   - Write press release for breakthrough findings
   - Share results with community

---

## 📚 References

- **DailyDialog Dataset**: Li et al. (2017) - Daily Dialog: A Manually Labelled Multi-turn Dialogue Dataset
- **Bootstrap Methods**: Efron & Tibshirani (1993) - An Introduction to the Bootstrap
- **Falcon-Mamba**: TII (2024) - State Space Models for Language
- **Persistent Homology**: Edelsbrunner & Harer (2010) - Computational Topology

---

**Status**: Ready to execute Week 1, Days 1-2
**Estimated Time**: 4-6 hours total
**GPU Required**: Yes (RTX 2070 Mobile 8GB confirmed compatible)

🌊 Let's flow into the data!
