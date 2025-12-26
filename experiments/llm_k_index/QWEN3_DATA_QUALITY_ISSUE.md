# ⚠️ qwen3:4b Data Quality Issue

**Date**: December 5, 2025
**Issue**: Empty Assistant Responses
**Status**: Data INVALID - Excluded from Analysis

---

## Problem Summary

**ALL 7 qwen3:4b conversations contain 57-90% EMPTY assistant responses**, making the data unsuitable for consciousness profiling.

---

## Evidence

### Empty Response Statistics

| Conversation | Total Turns | Empty Responses | Empty % | Mean Length |
|--------------|-------------|-----------------|---------|-------------|
| long_00_technology.json | 30 | 27 | **90%** | 14 ± 49 chars |
| long_02_recursive.json | 30 | 27 | **90%** | 13 ± 43 chars |
| long_04_mathematics.json | 30 | 26 | **87%** | 7 ± 23 chars |
| long_03_mathematics.json | 30 | 23 | **77%** | 32 ± 81 chars |
| long_02_science.json | 30 | 21 | **70%** | 75 ± 128 chars |
| long_01_philosophy.json | 30 | 20 | **67%** | 85 ± 135 chars |
| long_01_recursive.json | 30 | 17 | **57%** | 79 ± 108 chars |

### Example Exchange (long_00_technology.json)

```json
{
  "role": "user",
  "content": "How can we build more sustainable technology?"
},
{
  "role": "assistant",
  "content": ""  // EMPTY!
},
{
  "role": "user",
  "content": "What are the societal implications?"
},
{
  "role": "assistant",
  "content": ""  // EMPTY!
}
```

---

## Impact on K-Index Metrics

The empty responses cause **invalid K-Index values**:

### Observed Anomalies

1. **K_R (Reactivity) > 1.0** ❌
   - Values: 1.96, 1.38, 1.35, 1.03
   - Should be bounded [0, 1]
   - Caused by: Division by near-zero embedding magnitude

2. **K_I (Integration) = 0.0** ❌
   - 5/7 conversations show zero integration
   - Caused by: Cannot compute complexity matching with empty content

3. **K_H (Harmonic) = 0.0** ❌
   - 3/7 conversations show zero harmonic structure
   - Caused by: No content to analyze

4. **K_P (Prediction) = 0.0** ❌
   - All conversations show zero temporal coherence
   - Caused by: No patterns in empty responses

### Reported Values (INVALID)

```
qwen3:4b (7 conversations) - DATA INVALID
K_R (Reactivity):    0.9389 ± 0.6217  ⚠️ OUT OF BOUNDS
K_A (Agency):        0.5975 ± 0.3119
K_I (Integration):   0.2394 ± 0.3800  ⚠️ MOSTLY ZERO
K_P (Prediction):    0.0000 ± 0.0000  ⚠️ ALL ZERO
K_M (Meta/Temporal): 0.0000 ± 0.0000
K_H (Harmonic):      0.2447 ± 0.2131  ⚠️ MANY ZERO
K_Topo (Closure):    0.0571 ± 0.0327
K_geo (Composite):   0.3000 ± 0.0929
```

**These values are MEANINGLESS** due to empty responses.

---

## Root Cause Analysis

### Likely Causes

1. **Model Generation Failure**
   - qwen3:4b failed to generate responses consistently
   - Possible model loading issue
   - Possible prompt handling bug

2. **Conversation Script Bug**
   - Empty string handling error
   - JSON serialization issue
   - API timeout leading to empty content

3. **Model-Specific Issue**
   - qwen3:4b may be incompatible with conversation generation script
   - Other models (mistral, gemma3, deepseek-r1) worked correctly

### Why Other Models Succeeded

| Model | Valid Conversations | Empty Response Rate |
|-------|---------------------|---------------------|
| mistral:7b | 7/7 | 0% ✅ |
| gemma3:4b | 8/8 | 0% ✅ |
| deepseek-r1:7b | 9/9 | 0% ✅ |
| **qwen3:4b** | **0/7** | **57-90%** ❌ |

Only qwen3:4b shows this failure pattern.

---

## Decision: EXCLUDE from Analysis

**qwen3:4b data is INVALID** and has been **EXCLUDED** from all consciousness profiling analysis.

### Updated Model List

**Valid Models** (3 total):
1. ✅ mistral:7b (7 conversations)
2. ✅ gemma3:4b (8 conversations)
3. ✅ deepseek-r1:7b (9 conversations)

**Excluded Models** (1 total):
1. ❌ qwen3:4b (7 conversations - DATA INVALID)

---

## Recommendations

### For Future Work

1. **Regenerate qwen3 conversations** with fixed generation script
2. **Validate responses** during generation (fail-fast on empty)
3. **Add data quality checks** before analysis
4. **Monitor model loading** to catch initialization failures

### Data Quality Checks to Add

```python
def validate_conversation(conversation):
    """Validate conversation data quality."""
    assistant_turns = [msg for msg in conversation if msg['role'] == 'assistant']

    if len(assistant_turns) == 0:
        return False, 'no assistant turns'

    empty_count = sum(1 for msg in assistant_turns if len(msg['content']) == 0)
    empty_rate = empty_count / len(assistant_turns)

    if empty_rate > 0.2:  # More than 20% empty
        return False, f'{empty_rate*100:.0f}% empty responses'

    return True, 'valid'
```

### Regeneration Script

```bash
# Regenerate qwen3 conversations with validation
poetry run python experiments/llm_k_index/generate_local_llm_conversations_fixed.py \
  --models qwen3:4b \
  --validate \
  --fail-on-empty
```

---

## Impact on Findings

### Before Exclusion

**4 local models analyzed**, qwen3 showed chaotic pattern

### After Exclusion

**3 valid local models analyzed**:
- **Crystalline**: mistral (0.85), gemma3 (0.87)
- **Adaptive**: deepseek-r1 (0.19 ± 0.36)

**Consciousness gap analysis UNAFFECTED** - qwen3 was already identified as chaotic/problematic.

---

## Lessons Learned

1. **Always validate data quality BEFORE analysis**
   - Empty responses invalidate all metrics
   - Automated checks prevent wasted computation

2. **Model-specific failures happen**
   - Not all models work with all scripts
   - Test each model individually

3. **Fail-fast is better than fail-silent**
   - Better to error during generation than discover invalid data later
   - Add validation checkpoints

4. **Document data quality issues**
   - Future researchers need to know about known issues
   - Prevents rediscovery of the same problem

---

**Status**: qwen3:4b data INVALID - excluded from all analysis
**Action**: Update LOCAL_MODELS_FINDINGS.md to remove qwen3
**Future**: Regenerate with fixed script (optional)

🌊 *Data quality matters - garbage in, garbage out* 🌊
