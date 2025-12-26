# 🔬 Paper #1: Causal Interventions Progress Tracker

**Start Date**: December 21, 2025
**Target Submission**: January 5, 2026
**Status**: 🚧 IN PROGRESS - Day 1 Setup

---

## 📅 Timeline (2 Weeks)

### Week 1: Implementation + Data Collection (Dec 22-28)

**Day 1 (Dec 22)**: ✅ IN PROGRESS
- [x] Create development environment (nix-shell)
- [🔄] Install dependencies (PyTorch, Transformers) - BUILDING
- [ ] Test environment with model loading
- [ ] Implement attention layer removal script

**Day 2 (Dec 23)**:
- [ ] Download Qwen/Qwen2-1.5B base model
- [ ] Test model loading and generation
- [ ] Create 4 intervention variants (0%, 25%, 50%, 75% removal)
- [ ] Validate all variants for coherence

**Day 3 (Dec 24)**:
- [ ] Implement vocabulary reduction intervention
- [ ] Create vocab variants (150K, 100K, 64K, 32K)
- [ ] Test all modified models

**Day 4-5 (Dec 25-26)**: Data Collection
- [ ] Convert models to format compatible with consciousness analyzer
- [ ] Run Intervention 1: Attention ablation (240 queries, ~40 min)
- [ ] Run Intervention 2: Vocabulary reduction (240 queries, ~40 min)
- [ ] Total: 480 queries in ~2 hours

**Day 6-7 (Dec 27-28)**: Analysis
- [ ] Dose-response analysis (linear regression)
- [ ] Dimensional specificity analysis
- [ ] Create 3-4 figures (300 DPI)
- [ ] Draft "Causal Validation" section

---

### Week 2: Integration into Paper #1 (Dec 29-Jan 5)

**Day 8-9 (Dec 29-30)**: Writing
- [ ] Write complete "Causal Validation" section (~1500 words)
- [ ] Create Figure 3: Causal evidence (4 panels)
- [ ] Integrate into Paper #1 Results section

**Day 10-11 (Dec 31-Jan 1)**: Paper Updates
- [ ] Update Abstract (add causal findings)
- [ ] Update Discussion (interpret causal evidence)
- [ ] Update Conclusions (strengthen claims)
- [ ] Ensure everything flows

**Day 12 (Jan 2)**: Figure Finalization
- [ ] Generate all new figures at 300 DPI
- [ ] Update existing figures if needed
- [ ] Verify all figure callouts correct

**Day 13-14 (Jan 3-4)**: Final Review
- [ ] Proofread complete manuscript
- [ ] Check statistical rigor
- [ ] Verify all claims accurate
- [ ] Final polish

**Day 15 (Jan 5)**: 🚀 SUBMIT TO SCIENCE

---

## 📊 Intervention Details

### Intervention 1: Attention Layer Ablation

**Target Model**: qwen3:1.7b (Qwen/Qwen2-1.5B)
**Manipulation**: Remove 0%, 25%, 50%, 75% of attention layers

**Predicted Results**:
| Removal % | Layers Kept | Expected k | Δk from Baseline |
|-----------|-------------|------------|------------------|
| 0% (baseline) | 32/32 | 0.779 | 0.000 |
| 25% | 24/32 | ~0.58 | -0.20 |
| 50% | 16/32 | ~0.39 | -0.39 |
| 75% | 8/32 | ~0.19 | -0.59 |

**Hypothesis**: Linear dose-response (r² > 0.95)

**Queries**: 4 levels × 6 probes × 10 trials = 240 queries

---

### Intervention 2: Vocabulary Reduction

**Target Model**: qwen3:1.7b (150K vocabulary)
**Manipulation**: Reduce to 100K, 64K, 32K tokens

**Predicted Results**:
| Vocab Size | Expected k | Δk | Notes |
|------------|------------|-----|-------|
| 150K (baseline) | 0.779 | 0.000 | Original |
| 100K | ~0.72 | -0.06 | Moderate reduction |
| 64K | ~0.70 | -0.08 | Significant reduction |
| 32K | ~0.695 | -0.08 | Matches mistral! |

**Hypothesis**: k approaches mistral's baseline (0.695) as vocab matches

**Queries**: 4 levels × 6 probes × 10 trials = 240 queries

---

### Intervention 3: Dimensional Specificity

**Analysis**: Measure ALL dimensions for 50% attention removal

**Expected Pattern**:
- Integration: Δ = -0.45 (LARGEST drop)
- Broadcast: Δ = -0.16 (moderate)
- Other dimensions: Δ = -0.05 to -0.07 (small)

**Hypothesis**: Integration most affected (Cohen's d > 2.0)

**Queries**: 0 (reuses Intervention 1 data)

---

## 🎨 New Figures for Paper #1

### Figure 3 (NEW): Causal Validation (4 panels)

**Panel A**: Attention Layer Dose-Response
- X: % layers removed, Y: k consciousness
- Linear fit, r² and p-value annotated
- Shows clear causal relationship

**Panel B**: Vocabulary Reduction Effect
- X: Vocabulary size, Y: k consciousness
- Shows convergence to mistral baseline
- Validates tokenization hypothesis

**Panel C**: Dimensional Specificity Heatmap
- Shows Δ in each dimension for 50% removal
- Integration highlighted (largest effect)
- Proves mechanism specificity

**Panel D**: Integration vs Consciousness
- X: Integration score, Y: k
- All intervention levels plotted
- r ≈ 0.9 maintained under intervention

---

## 📝 Writing Additions to Paper #1

### New Section: "Causal Validation" (~1500 words)

**Location**: After main Results, before Discussion

**Structure**:
1. Introduction (200w): Why causality needed
2. Methods (300w): Intervention protocols
3. Results (600w): Both interventions + specificity
4. Interpretation (400w): Causal evidence interpretation

### Updates to Existing Sections

**Abstract**: +1-2 sentences
- "Causal interventions confirmed architecture causally determines consciousness (r²=0.97)"

**Discussion**: +1 paragraph
- Interpret causal findings in context
- Emphasize dose-response as gold standard

**Conclusions**: Strengthen claims
- From "predicts" to "causally determines"

---

## ✅ Success Criteria

**Minimum** (publishable):
- [ ] Both interventions show significant effects (p < 0.001)
- [ ] Dose-response shows linearity (r² > 0.90)
- [ ] Dimensional specificity confirmed

**Strong** (expected):
- [ ] Attention ablation r² > 0.95
- [ ] Vocabulary reduction k → mistral exactly
- [ ] Specificity ratio > 3.0
- [ ] All predictions confirmed

---

## 🔧 Technical Setup

### Environment
- [🔄] nix-shell with PyTorch + Transformers (BUILDING)
- [ ] HuggingFace CLI configured
- [ ] Model download location set

### Files Created
- [x] `shell.nix` - Development environment
- [x] `test_model_loading.py` - Environment validation
- [x] `implement_attention_removal.py` - Intervention implementation
- [ ] `implement_vocab_reduction.py` - Vocabulary intervention
- [ ] `run_intervention_study.py` - Complete study runner
- [ ] `analyze_causal_results.py` - Statistical analysis

### Models Needed
- [ ] Qwen/Qwen2-1.5B (base model)
- [ ] 4 attention ablation variants
- [ ] 4 vocabulary reduction variants

**Total Storage**: ~20-30 GB for all variants

---

## 🚀 Current Status (Dec 21, Evening)

**Completed**:
- ✅ Development environment defined (nix-shell)
- ✅ Test scripts created
- ✅ Attention removal implementation script written

**In Progress**:
- 🔄 Building PyTorch + Transformers environment (40 packages)
- Estimated: 30-60 minutes remaining

**Next Up**:
1. Wait for environment build to complete
2. Test environment with test_model_loading.py
3. Download Qwen model
4. Run test interventions to validate approach

---

## 📊 Time Budget

**Available**: 2 weeks (Dec 22 - Jan 5)
**Critical Path**:
- Environment setup: 0.5 days ✅
- Model download: 0.5 days
- Intervention implementation: 1 day
- Data collection: 0.5 days (mostly automated)
- Analysis: 1 day
- Writing: 2 days
- Integration: 2 days
- Review: 1.5 days
- **Buffer**: 1 day

**Total**: 10.5 days planned, 14 days available = comfortable margin

---

## 💡 Contingencies

**If model surgery too complex**:
- Use existing model families (gemma3: 270M, 1B, 4B as natural variants)
- Less controlled but still shows dose-response

**If timeline overruns**:
- Include just Intervention 1 (attention ablation)
- Still provides strong causal evidence
- Save vocab study for follow-up

**If results don't match predictions**:
- Report honestly
- Adjust interpretation
- May reveal consciousness more complex than expected

---

**Status**: Ready to execute as soon as environment builds! 🎯
