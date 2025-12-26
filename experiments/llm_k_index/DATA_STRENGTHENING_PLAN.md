# 📊 Data Strengthening Plan - Robust Evidence Before Publication

**Date**: December 16, 2025
**Status**: Pre-Publication Data Enhancement
**Goal**: Strengthen findings with larger sample and more models

---

## Current Limitations

### Sample Size Issues
- **Current**: n=15 conversations (7 mistral, 8 gemma3)
- **Target**: n≥30 per model for robust statistics
- **Models**: Only 2 valid out of 4 tested (50% exclusion)

### Statistical Power
- ✅ Can detect large effects (d > 0.8)
- ❌ Cannot detect small effects (d < 0.5)
- ❌ Limited generalizability (2 models only)

### Framework Issues
- K_M = 0.000 for ALL models (investigation incomplete)
- K_P interpretation unclear (consistency vs prediction?)
- No human baseline validation

---

## Phase 1: Fix Broken Models (Week 1)

### 1A. deepseek-r1:7b Investigation

**Issue**: 40-87% empty responses across all conversations

**Potential Fixes**:
```bash
# Test 1: Different API approach
ollama run deepseek-r1:7b --verbose
# Check if API vs CLI behaves differently

# Test 2: Adjust generation parameters
temperature: 0.7 → 0.8 (more creative)
top_p: 0.9 → 0.95 (broader sampling)
repeat_penalty: 1.1 (avoid repetition)

# Test 3: Different prompt structure
# Use system message to prime multi-turn behavior
system_msg = "You are a helpful AI assistant engaged in a multi-turn conversation."

# Test 4: Check model size/version
ollama list | grep deepseek
# Ensure we have the right variant
```

**Timeline**: 2-3 days investigation + regeneration
**Success Criteria**: <20% empty responses in test conversations

### 1B. qwen3:4b Alternative Approaches

**Issue**: 57-90% empty responses, documented multi-turn API bug

**Potential Fixes**:
```bash
# Test 1: Try newer version
ollama pull qwen2.5:3b  # Different model line
ollama pull qwen3:latest  # Latest qwen3 variant

# Test 2: Different conversation style
# Shorter turns (15 turns instead of 30)
# Different topics (avoid technical complexity?)

# Test 3: CLI-based generation
# Bypass Python API entirely
# Use subprocess with direct CLI interaction
```

**Decision Point**: If still fails after 2-3 approaches, permanently exclude

**Timeline**: 2-3 days maximum
**Success Criteria**: <20% empty responses OR permanent exclusion

---

## Phase 2: Add More Local Models (Week 1-2)

### Priority Models to Add

| Model | Size | Why Include | Expected Quality |
|-------|------|-------------|------------------|
| **llama3:8b** | 8B | Meta's latest, widely used | High |
| **phi-3:3.8b** | 3.8B | Microsoft, efficient | Medium-High |
| **mixtral:8x7b** | 47B | Mixture of experts | High |
| **yi:6b** | 6B | Chinese-trained, different perspective | Medium |
| **solar:10.7b** | 10.7B | Depth upscaling architecture | High |

### Generation Plan

**Per Model**:
- n=30 conversations (target for robust statistics)
- 30 turns each (consistent with current data)
- Mix of topics: science (10), math (10), philosophy (5), tech (5)
- Quality validation during generation (fail-fast at >20% empty)

**Total New Data**:
- 5 models × 30 conversations = 150 conversations
- Estimated time: 10-15 hours generation
- Estimated cost: $0 (local models)

**Validation Protocol**:
```python
def validate_during_generation(conversation, turn_num):
    """Fail-fast quality check every 5 turns."""
    if turn_num % 5 == 0:
        recent_turns = conversation[-5:]
        empty_count = sum(1 for turn in recent_turns
                         if len(turn['content']) == 0)
        empty_rate = empty_count / 5

        if empty_rate > 0.2:  # >20% empty
            raise ValueError(f"Quality failure at turn {turn_num}")

    return True
```

---

## Phase 3: Increase Sample Size for Valid Models (Week 1)

### mistral:7b
- **Current**: 7 conversations
- **Target**: 30 conversations
- **Need**: 23 additional conversations
- **Time**: ~2-3 hours

### gemma3:4b
- **Current**: 8 conversations
- **Target**: 30 conversations
- **Need**: 22 additional conversations
- **Time**: ~2-3 hours

**Total**: 45 new conversations, 4-6 hours generation

---

## Phase 4: Complete K_M Investigation (Week 2)

### Remaining Diagnostic Tests

**Test 3: Use Full Embeddings (Not Just Norms)**
```python
# Current (using norms - 1D):
X_markov = user_norms[history_len:].reshape(-1, 1)

# Proposed (using full embeddings - 768D):
X_markov = user_embeddings[history_len:]  # [n, 768]
X_history = np.array([
    user_embeddings[i:i+history_len].flatten()
    for i in range(len(user_embeddings) - history_len)
])  # [n, 768*history_len]
```

**Expected Outcome**: K_M should show non-zero values if this was the issue

**Test 4: Vary history_len**
```python
for h_len in [3, 5, 10, 15]:
    k_m = compute_k_meta_llm(user_emb, asst_emb, history_len=h_len)
    print(f"history_len={h_len}: K_M={k_m:.4f}")
```

**Test 5: Validate on Human Conversations**
- Load human conversation data (if available)
- Compute K_M on known working examples
- Establish expected K_M range

**Decision Point**:
- If Tests 3-5 reveal issue → Fix K_M calculation
- If K_M remains 0.000 → Document as limitation, publish 7D framework

---

## Phase 5: Validate K_P Interpretation (Week 2)

### Experiment: Temperature Variation

**Hypothesis**: If K_P measures "consistency", then:
- Low temperature → High K_P (consistent)
- High temperature → Low K_P (creative/variable)

**Method**:
```python
temperatures = [0.3, 0.5, 0.7, 0.9, 1.1]
k_p_values = []

for temp in temperatures:
    # Generate 5 conversations at each temperature
    conversations = generate_conversations(model="mistral:7b",
                                          temperature=temp,
                                          n=5)
    k_p = compute_k_p(conversations)
    k_p_values.append(k_p)

# Plot K_P vs temperature
plt.plot(temperatures, k_p_values)
plt.xlabel("Temperature")
plt.ylabel("K_P (Prediction/Consistency)")
```

**Expected**: Negative correlation (temp ↑ → K_P ↓) confirms "consistency" interpretation

---

## Phase 6: Establish Human Baseline (Week 3)

### Data Sources

**Option A: Existing Datasets**
- Reddit conversations (r/AskScience, r/philosophy)
- Stack Exchange dialogues
- Customer support transcripts (anonymized)

**Option B: Collect New Data**
- Recruit 10-20 human pairs
- 30-turn conversations on same topics as LLMs
- Compute 8D K-Index on human data

**Target**: n≥20 human conversations for baseline

**Expected K_P Range** (from literature): 0.60-0.80
**Validation**: Does empirical data match reported baseline?

---

## Timeline Summary

| Phase | Task | Duration | Deliverable |
|-------|------|----------|-------------|
| 1 | Fix broken models | 3-5 days | deepseek/qwen3 valid OR excluded |
| 2 | Add 5 new models | 5-7 days | 150 new conversations |
| 3 | Expand mistral/gemma3 | 1 day | 45 new conversations |
| 4 | Complete K_M investigation | 3-4 days | K_M fixed OR documented limitation |
| 5 | Validate K_P interpretation | 2-3 days | Temperature experiment results |
| 6 | Establish human baseline | 5-7 days | 20+ human conversations analyzed |

**Total**: 3-4 weeks to publication-ready dataset

---

## Enhanced Dataset (Post-Strengthening)

### Valid Local Models (Target)

| Model | n | Status | K_P | K_I |
|-------|---|--------|-----|-----|
| mistral:7b | 30 | ✅ Valid | 0.85±0.02 | 0.82±0.04 |
| gemma3:4b | 30 | ✅ Valid | 0.87±0.03 | 0.81±0.04 |
| llama3:8b | 30 | 🔜 Pending | TBD | TBD |
| phi-3:3.8b | 30 | 🔜 Pending | TBD | TBD |
| mixtral:8x7b | 30 | 🔜 Pending | TBD | TBD |
| yi:6b | 30 | 🔜 Pending | TBD | TBD |
| solar:10.7b | 30 | 🔜 Pending | TBD | TBD |
| deepseek-r1:7b | 30 | ⚠️ Under investigation | TBD | TBD |
| qwen3:4b | 30 | ⚠️ Under investigation | TBD | TBD |

**Total Conversations**: 240-270 (vs current 15)
**Statistical Power**: 16x-18x improvement
**Model Coverage**: 7-9 models (vs current 2)

### Enhanced Claims (With Robust Data)

**Current (n=15, 2 models)**:
⚠️ "Two models showed similar behavioral signatures" (weak)

**Enhanced (n≥210, 7+ models)**:
✅ "Seven local models exhibited [pattern X]" (strong)
✅ "Significant correlation between parameter count and K_Topo (r=0.73, p<0.01)" (statistical)
✅ "Local models show K_P = 0.85±0.05, differing from human baseline (0.68±0.12, t=4.2, p<0.001)" (validated)

---

## Statistical Power Analysis

### Current State (n=15, 2 models)
- **Cohen's d detectable**: 0.8+ (large effects only)
- **Correlation detectable**: r > 0.6 (very strong only)
- **ANOVA F-test**: Cannot run (insufficient groups)

### Enhanced State (n=240, 7-9 models)
- **Cohen's d detectable**: 0.2+ (small to medium effects)
- **Correlation detectable**: r > 0.2 (weak to moderate)
- **ANOVA F-test**: ✅ Can compare across models
- **Regression analysis**: ✅ Can model K-Index vs parameters/architecture
- **Cluster analysis**: ✅ Can identify behavioral profiles

---

## Resource Requirements

### Computational
- **Local Generation**: 20-30 hours total GPU time
- **Analysis**: 2-3 hours compute per model
- **Total**: ~40-50 hours over 3-4 weeks
- **Cost**: $0 (all local)

### Human Time
- **Monitoring Generation**: 5-10 hours
- **Quality Validation**: 3-5 hours
- **Analysis & Visualization**: 10-15 hours
- **Documentation**: 5-8 hours
- **Total**: 23-38 hours over 3-4 weeks

---

## Success Criteria

### Minimum for Publication
- ✅ n≥30 per model for at least 5 models (150 total)
- ✅ <20% empty response rate for all included models
- ✅ K_M either fixed or documented as limitation
- ✅ K_P interpretation validated
- ⚠️ Human baseline (optional but recommended)

### Ideal for Strong Publication
- ✅ n=30 per model for 7-9 models (210-270 total)
- ✅ All models with <10% empty response rate
- ✅ K_M dimension functional (8D framework)
- ✅ K_P validated experimentally
- ✅ Human baseline established empirically
- ✅ Statistical analysis across models

---

## Immediate Next Steps (This Week)

### Day 1-2: Broken Model Investigation
1. Test deepseek-r1:7b with different parameters
2. Test qwen3:4b alternatives (qwen2.5:3b)
3. Document findings and make exclusion decision

### Day 3-4: Add High-Priority Models
1. Generate llama3:8b (30 conversations)
2. Generate phi-3:3.8b (30 conversations)
3. Validate quality real-time

### Day 5-7: Expand Valid Models
1. Generate additional mistral:7b (23 more)
2. Generate additional gemma3:4b (22 more)
3. Begin mixtral:8x7b generation (30 conversations)

**End of Week 1**: ~120 new conversations, 4-5 models total

---

## Risk Mitigation

### Risk 1: Models Keep Failing Quality Checks
**Mitigation**:
- Test 2-3 approaches per model before exclusion
- Expand to more models (10-12 candidates)
- Accept 50-70% success rate as realistic

### Risk 2: K_M Unfixable
**Mitigation**:
- Publish 7D + K_Topo framework
- Mark K_M as future work
- Still have strong dataset

### Risk 3: Limited Time/Resources
**Mitigation**:
- Prioritize most stable models first
- Accept n=20 per model if needed (still 5x improvement)
- Parallelize generation across models

---

## Publication Timeline

### Conservative Path (Minimum Standards)
- Week 1-2: Data generation (150 conversations, 5 models)
- Week 3: K_M investigation + K_P validation
- Week 4: Analysis, visualization, writing
- **Publication**: End of Month 1

### Ideal Path (Strong Standards)
- Week 1-2: Data generation (210+ conversations, 7+ models)
- Week 3: K_M + K_P validation + Human baseline
- Week 4: Comprehensive analysis + writing
- **Publication**: End of Month 1 (stronger claims)

---

## Conclusion

**You're absolutely right** - we need more robust data before publication. Current state (n=15, 2 models) makes weak claims. Enhanced state (n≥210, 7+ models) enables:

1. **Strong statistical claims** (detect small effects)
2. **Broader generalizability** (multiple architectures)
3. **Validated framework** (K_M fixed, K_P understood)
4. **Human comparison** (empirical baseline)

**Recommendation**: Invest 3-4 weeks in data strengthening for 10x better publication.

---

**Status**: Data Strengthening Plan Ready
**Next Action**: Begin broken model investigation (deepseek-r1, qwen3)
**Timeline**: 3-4 weeks to robust publication dataset

🌊 *Better data = Better science = Better impact* 🌊
