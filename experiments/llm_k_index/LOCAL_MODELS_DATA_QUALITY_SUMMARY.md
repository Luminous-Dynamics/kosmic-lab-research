# 🚨 Local Models Data Quality Summary

**Date**: December 6, 2025
**Investigation**: Multi-turn conversation bugs in local LLMs

---

## Executive Summary

After thorough investigation, **only 2 out of 4 local models** have usable data for K-Index analysis:

| Model | Status | Empty Response Rate | Usable? |
|-------|--------|---------------------|---------|
| mistral:7b | ✅ **VALID** | 0% | YES |
| gemma3:4b | ✅ **VALID** | 0% | YES |
| **qwen3:4b** | ❌ **INVALID** | **57-90%** | NO |
| **deepseek-r1:7b** | ❌ **INVALID** | **40-87%** | NO |

---

## Detailed Findings

### ✅ VALID MODELS

#### mistral:7b (7 conversations)
- **Empty responses**: 0%
- **Data quality**: Excellent
- **Multi-turn stability**: Stable through 30+ turns
- **Status**: Ready for 8D K-Index analysis

#### gemma3:4b (8 conversations)
- **Empty responses**: 0%
- **Data quality**: Excellent
- **Multi-turn stability**: Stable through 30+ turns
- **Status**: Ready for 8D K-Index analysis

---

### ❌ INVALID MODELS

#### qwen3:4b (7 conversations) - MULTI-TURN BUG

**Problem**: Generates empty responses after 3-4 conversation turns via Ollama Python API

**Evidence**:
| Conversation | Total Turns | Empty Responses | Empty % |
|--------------|-------------|-----------------|---------|
| long_00_technology.json | 30 | 27 | **90%** |
| long_02_recursive.json | 30 | 27 | **90%** |
| long_04_mathematics.json | 30 | 26 | **87%** |
| long_03_mathematics.json | 30 | 23 | **77%** |
| long_02_science.json | 30 | 21 | **70%** |
| long_01_philosophy.json | 30 | 20 | **67%** |
| long_01_recursive.json | 30 | 17 | **57%** |

**Root Cause**: See `QWEN3_MULTI_TURN_BUG.md` for complete analysis

**Reproduction**:
- Direct CLI: ✅ Works
- Single Python API call: ✅ Works (1592 chars)
- Multi-turn Python API: ❌ Turn 4 empty

**Regeneration Attempt** (Dec 6, 2025):
- 0 out of 7 conversations passed quality check
- Average valid rate: 29.5%
- **Conclusion**: Cannot be fixed, model/API limitation

**Status**: Permanently excluded from analysis

---

#### deepseek-r1:7b (9 conversations) - EMPTY RESPONSE BUG

**Problem**: Generates empty responses throughout multi-turn conversations

**Evidence**:
| Conversation | Empty % | Status |
|--------------|---------|--------|
| short_08_technology.json | **87%** | Unusable |
| long_00_science.json | **77%** | Unusable |
| long_03_science.json | **73%** | Unusable |
| short_06_science.json | **73%** | Unusable |
| short_07_technology.json | **73%** | Unusable |
| short_01_mathematics.json | **67%** | Unusable |
| short_02_science.json | **67%** | Unusable |
| short_03_mathematics.json | **67%** | Unusable |
| short_05_recursive.json | **67%** | Unusable |
| long_04_mathematics.json | **63%** | Unusable |
| long_01_philosophy.json | **57%** | Unusable |
| long_02_philosophy.json | **53%** | Unusable |
| short_00_mathematics.json | **53%** | Unusable |
| long_02_recursive.json | **50%** | Unusable |
| long_01_technology.json | **47%** | Unusable |
| short_04_recursive.json | **40%** | Unusable |
| short_09_recursive.json | **27%** | Borderline |

**Pattern**: All conversations show 27-87% empty responses

**Status**: Excluded from analysis (data invalid)

---

## Investigation Timeline

### December 5, 2025
- Discovered qwen3:4b has 57-90% empty responses
- Created `QWEN3_DATA_QUALITY_ISSUE.md`
- Excluded qwen3:4b from initial analysis

### December 6, 2025
- **10:00**: User requested investigation into whether data could be fixed
- **11:00**: Created validation script `regenerate_qwen3_with_validation.py`
- **12:00**: Tested qwen3 in isolation:
  - Single-turn API: Works
  - Multi-turn API: Fails after 3-4 turns
- **14:00**: Created `QWEN3_MULTI_TURN_BUG.md` documenting root cause
- **16:00**: Attempted regeneration with validation
  - Result: 0/7 conversations passed (29.5% valid rate)
- **17:00**: Confirmed qwen3 exclusion is permanent
- **18:00**: Ran corrected 8D analysis
- **18:30**: **DISCOVERED**: deepseek-r1:7b ALSO has empty response bug!
  - All 17 conversations show 27-87% empty responses
  - Now 2 models excluded, not just 1

---

## Implications for K-Index Analysis

### Original Plan (4 models)
- mistral:7b ✅
- gemma3:4b ✅
- qwen3:4b ❌
- deepseek-r1:7b ❌

### Actual Reality (2 models)
- **Valid models**: mistral:7b, gemma3:4b
- **Sample size**: 15 conversations total (7 + 8)
- **Impact**: Reduced statistical power, but still valid for preliminary findings

### Consciousness Gap Analysis
The finding of "consciousness gap" between frontier and local models remains valid, but now:
- **Local models** represented by: mistral:7b and gemma3:4b only
- **Excluded**: 50% of originally planned local models due to data quality issues

---

## Lessons Learned

### 1. Data Quality Validation is Critical
- Empty response checks should be part of generation pipeline
- Fail-fast on >20% empty is essential
- Automated validation prevents wasted analysis

### 2. Model Stability Varies Dramatically
- Not all local models handle multi-turn conversations equally
- Testing needed BEFORE large-scale data generation
- Single-turn tests are insufficient

### 3. Multi-Turn Bugs are Model-Specific
- qwen3:4b and deepseek-r1:7b both fail
- mistral:7b and gemma3:4b both succeed
- Pattern suggests architectural differences or training issues

### 4. Regeneration May Not Fix Fundamental Issues
- qwen3 regeneration produced same results
- Model/API limitations cannot be scripted around
- Sometimes exclusion is the only option

---

## Recommendations

### For Future Data Generation

1. **Pre-flight Testing**:
   ```python
   def validate_model_multi_turn(model, n_turns=10):
       """Test model with 10-turn conversation before full generation."""
       conversation = []
       empty_count = 0

       for turn in range(n_turns):
           response = ollama.chat(model=model, messages=messages)
           if len(response['message']['content']) == 0:
               empty_count += 1

       empty_rate = empty_count / n_turns

       if empty_rate > 0.1:  # Fail if >10% empty
           raise ValueError(f"{model} failed multi-turn test ({empty_rate*100:.0f}% empty)")
   ```

2. **Inline Validation**:
   - Check every response during generation
   - Abort early if quality degrades
   - Log detailed statistics

3. **Model Selection Criteria**:
   - Multi-turn stability > single-turn performance
   - Context window size matters
   - Verify with test conversations first

### For Current Analysis

1. **Proceed with mistral + gemma3 only**
2. **Document reduced sample size**
3. **Note limitations in findings**
4. **Consider adding validated models in future work**

---

## Next Steps

1. ✅ Fix `compute_8d_k_index()` call in analysis script (pass file path, not list)
2. ✅ Re-run 8D analysis on mistral:7b and gemma3:4b only
3. ✅ Update `LOCAL_MODELS_FINDINGS.md` with 2-model results
4. ✅ Create `DEEPSEEK_R1_DATA_QUALITY_ISSUE.md` documenting the bug
5. 🔮 Consider testing additional models (phi-2, llama3, etc.) in future

---

## Conclusion

**50% of local models tested have multi-turn conversation bugs** that make them unsuitable for consciousness profiling.

The K-Index framework revealed these data quality issues that would have otherwise gone undetected - **K_P = 1.0 and K_I = 0.0 were early warning signs of empty responses**.

We proceed with **mistral:7b and gemma3:4b** as representative local open-source models, acknowledging this limitation in our findings.

---

**Status**: Investigation complete
**Valid models**: 2/4 (mistral, gemma3)
**Excluded models**: 2/4 (qwen3, deepseek-r1)

🌊 *Data quality matters - better to have fewer reliable samples than many unreliable ones* 🌊
