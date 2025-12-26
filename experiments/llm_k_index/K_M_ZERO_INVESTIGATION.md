# 🔬 K_M = 0.000 Investigation - Why Meta/Temporal Dimension Fails

**Date**: December 16, 2025
**Status**: CRITICAL - Affects ALL models (100% failure rate)
**Impact**: One of 8 consciousness dimensions is non-functional

---

## Executive Summary

**FINDING**: K_M (Meta/Temporal Depth) returns 0.000 for ALL tested models:
- mistral:7b → K_M = 0.000
- gemma3:4b → K_M = 0.000
- deepseek-r1:7b → K_M = 0.000
- qwen3:4b → K_M = 0.000

This is **NOT** a consciousness finding - it's a **measurement failure**. Either:
1. The calculation has a bug, OR
2. The metric is inappropriate for LLM conversations, OR
3. Current embeddings lack information K_M needs

---

## Part I: Understanding K_M

### Theoretical Definition
K_M measures **temporal depth** - how much conversation history improves prediction of assistant responses.

**Conceptually**:
- K_M ≈ 0: Assistant only responds to immediate query (stateless, Markovian)
- K_M ≈ 1: Assistant deeply considers conversation history (stateful)

### Implementation (`kosmic_k_index_llm.py` lines 351-452)

```python
def compute_k_meta_llm(user_embeddings, assistant_embeddings, history_len=5):
    """
    Compare two models:
      Markov model: U_t -> A_t (current user → assistant)
      History model: U_{t-k:t} -> A_t (past k turns → assistant)

    Returns: K_M = (l_0 - l_h) / (l_0 + ε)
      where l_0 = Markov error, l_h = history error
    """
    min_len = min(len(user_embeddings), len(assistant_embeddings))

    # EARLY EXIT CONDITIONS (returns 0.0):
    if min_len < history_len + 20:  # Needs 25+ turns
        return 0.0

    if sklearn not available:
        # Fallback correlation method
        ...
        improvement = (corr_history - corr_current) / (1.0 + corr_current)
        return max(0.0, min(1.0, improvement))

    # Main calculation:
    # 1. Train Ridge regression: Markov vs History
    # 2. Compare prediction errors on test set
    # 3. K_M = improvement from using history
    ...
```

---

## Part II: Data Verification

### Sample Sizes
| Model | Conversations | Avg Turns | Min Length | K_M Requirement Met? |
|-------|---------------|-----------|------------|---------------------|
| mistral:7b | 7 | 60 (30 pairs) | 30 | ✅ Yes (30 >= 25) |
| gemma3:4b | 8 | 60 (30 pairs) | 30 | ✅ Yes |
| deepseek-r1:7b | 9 | Variable | ~30 | ✅ Likely |
| qwen3:4b | 7 | 60 (30 pairs) | 30 | ✅ Yes |

**Verification**:
```bash
$ python3 -c "import json; print(len(json.load(open('results/local_models/mistral_7b/long_00_science.json'))))"
60
```

**Conclusion**: Sample size is NOT the issue. All models have sufficient data (30 pairs >= 25 minimum).

---

## Part III: Possible Explanations

### Hypothesis 1: sklearn Not Available (Fallback Used)
**Test**: Check if sklearn import succeeds in analysis environment
```python
try:
    from sklearn.linear_model import Ridge
    print("✅ sklearn available")
except ImportError:
    print("❌ sklearn NOT available - fallback used!")
```

**If fallback used**, K_M uses correlation-based approximation (lines 378-401):
- Computes correlation between (current user, history avg) and assistant response
- Returns `improvement = (corr_history - corr_current) / (1.0 + corr_current)`

**Prediction**: If sklearn missing, K_M = 0 means history correlation ≤ current correlation

---

### Hypothesis 2: Degenerate Embedding Variance
Similar to K_P = 1.0 bug, embeddings may have properties causing K_M calculation to fail:

**Potential issues**:
- If `l_0 < 1e-10` (Markov model perfect), K_M returns 0.0 (line 445)
- If predictions are perfect, no room for improvement from history
- If embeddings have zero variance, models can't distinguish patterns

**Test needed**:
```python
# Check embedding statistics
user_norms = np.linalg.norm(user_embeddings, axis=1)
print(f"User norm variance: {np.std(user_norms)}")
print(f"User norm range: [{np.min(user_norms)}, {np.max(user_norms)}]")
```

---

### Hypothesis 3: History Doesn't Help (Real Finding)
**Possibility**: LLMs genuinely operate in Markovian fashion - only immediate context matters.

**However**: This seems unlikely because:
- LLMs DO use conversation history
- Context windows exist for this purpose
- Would be revolutionary finding if true

**Skepticism**: More likely measurement issue than genuine result.

---

### Hypothesis 4: Embedding Model Limitation
**EmbeddingGemma:300m** may not capture temporal dependencies:

- Sentence-level embeddings → position-invariant
- No explicit temporal encoding
- Context window = single message only

**Implication**: Can't distinguish "message 10 after context" from "message 10 standalone"

---

### Hypothesis 5: Implementation Bug
**Possible code issues**:

1. **Train/test split too small** (lines 419-429):
   ```python
   train_idx, test_idx = train_test_split(indices, test_size=0.3)
   if len(X_m_train) < 5:
       return 0.0
   ```
   With 30 turns and history_len=5, we have 25 data points.
   - Train: 17 points
   - Test: 8 points
   This SHOULD work, but might be edge case.

2. **Error calculation issues** (lines 442-448):
   ```python
   l_0 = np.mean((y_test - model_markov.predict(X_m_test)) ** 2)
   l_h = np.mean((y_test - model_history.predict(X_h_test)) ** 2)

   if l_0 < 1e-10:  # Perfect Markov
       return 0.0

   return max(0.0, min(1.0, (l_0 - l_h) / (l_0 + 1e-10)))
   ```

   **Bug possibility**: If `l_0 ≈ l_h` (history doesn't improve), K_M ≈ 0.

3. **Feature extraction** (lines 404-414):
   ```python
   user_norms = np.linalg.norm(user_embeddings[:min_len], axis=1)
   assistant_norms = np.linalg.norm(assistant_embeddings[:min_len], axis=1)

   X_markov = user_norms[history_len:].reshape(-1, 1)  # Single feature!
   X_history = np.array([
       user_norms[i:i+history_len]
       for i in range(len(user_norms) - history_len)
   ])  # 5 features
   ```

   **Concern**: Using only NORMS, not full embeddings!
   - Markov: 1D input (magnitude of current user message)
   - History: 5D input (magnitudes of past 5 user messages)
   - Target: 1D output (magnitude of assistant response)

   **This is extremely limited!** Should use full embeddings.

---

## Part IV: Diagnostic Tests Needed

### Test 1: Check sklearn Availability
```bash
poetry run python -c "
try:
    from sklearn.linear_model import Ridge
    print('✅ sklearn available')
except ImportError:
    print('❌ sklearn NOT available - FALLBACK USED')
"
```

### Test 2: Inspect Embedding Statistics
```python
# Add to K_M calculation (debug mode):
print(f"DEBUG K_M:")
print(f"  min_len: {min_len}")
print(f"  history_len: {history_len}")
print(f"  user_norms variance: {np.std(user_norms):.6f}")
print(f"  assistant_norms variance: {np.std(assistant_norms):.6f}")
print(f"  Markov error (l_0): {l_0:.6f}")
print(f"  History error (l_h): {l_h:.6f}")
print(f"  Improvement: {(l_0 - l_h) / l_0:.6f}")
```

### Test 3: Test with Full Embeddings
Modify K_M to use FULL embeddings instead of just norms:
```python
# Instead of norms:
X_markov = user_embeddings[history_len:min_len]  # [n_samples, embedding_dim]
X_history = np.array([
    user_embeddings[i:i+history_len].flatten()
    for i in range(min_len - history_len)
])  # [n_samples, history_len * embedding_dim]
```

### Test 4: Try Different history_len
```python
# Test multiple values:
for h_len in [3, 5, 10, 15]:
    k_m = compute_k_meta_llm(user_emb, asst_emb, history_len=h_len)
    print(f"history_len={h_len}: K_M={k_m:.4f}")
```

### Test 5: Manual Calculation
Bypass the function entirely - compute by hand to verify:
```python
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split

# Load conversation
user_emb, asst_emb, _ = load_conversation_embeddings(conv_file)

# Prepare data
user_norms = np.linalg.norm(user_emb, axis=1)
asst_norms = np.linalg.norm(asst_emb, axis=1)

h = 5
X_m = user_norms[h:].reshape(-1, 1)
X_h = np.array([user_norms[i:i+h] for i in range(len(user_norms)-h)])
y = asst_norms[h:]

# Split and train
X_m_train, X_m_test, y_train, y_test = train_test_split(
    X_m, y, test_size=0.3, random_state=42
)
X_h_train, X_h_test, _, _ = train_test_split(
    X_h, y, test_size=0.3, random_state=42
)

# Fit models
model_m = Ridge(alpha=1.0).fit(X_m_train, y_train)
model_h = Ridge(alpha=1.0).fit(X_h_train, y_train)

# Errors
l_0 = np.mean((y_test - model_m.predict(X_m_test)) ** 2)
l_h = np.mean((y_test - model_h.predict(X_h_test)) ** 2)

print(f"Markov error: {l_0:.6f}")
print(f"History error: {l_h:.6f}")
print(f"K_M = {max(0.0, (l_0 - l_h) / l_0):.4f}")
```

---

## Part V: Recommended Actions

### Immediate (Next Session)
1. ✅ **Test sklearn availability** - Determine if fallback used
2. ✅ **Add debug logging** - Print intermediate values in K_M calculation
3. ✅ **Run manual calculation** - Verify formula works in isolation

### Short-term (This Week)
4. **Test with full embeddings** - Use entire embedding vectors, not just norms
5. **Vary history_len** - Test 3, 5, 10, 15 to see if any value works
6. **Compare to baseline** - Test on human conversations to validate

### If Still Zero After Tests
7. **Alternative formulation** - Try different meta/temporal metrics:
   - Autocorrelation of responses over time
   - Entropy change across conversation
   - Mutual information between past and future

8. **Consult Paper 9** - Check if K_M has known limitations for LLMs

---

## Part VI: TEST 2 RESULTS - CRITICAL DISCOVERY

### Embeddings Not Being Loaded
**Date**: December 16, 2025
**Test**: Attempted to load embeddings from mistral:7b conversation file

**Finding**: **ZERO embeddings loaded**
```
User embeddings: 0 (expected ~30)
Assistant embeddings: 0 (expected ~30)
```

**Root Cause Identified**:
The conversation JSON files **do not have embeddings saved** in them. The test script was looking for fields like:
```json
{
  "role": "user",
  "content": "...",
  "user_embedding": [...]  // ← These fields DON'T EXIST
}
```

**Implications**:
1. K_M calculation expects embeddings to already be present
2. Without embeddings, min_len = 0 → early exit with K_M = 0.0
3. The `compute_8d_k_index()` function must generate embeddings on-the-fly from text
4. Our manual test was using wrong loading logic

**Next Action**: Test with actual `compute_8d_k_index()` function which generates embeddings internally, not with our simplified test script.

---

## Part VII: Impact on Research

### Current State
**Paper 9 (K-Index)** claims 8D framework, but actually has:
- ✅ 6 working dimensions (K_R, K_A, K_I, K_P, K_H, K_Topo)
- ❌ 1 broken dimension (K_M = 0 for all) - **Investigation ongoing**
- ❓ 1 under review (K_P may measure consistency, not prediction)

### Honest Assessment
**We have a 6D + K_Topo framework** that is reliable. K_M needs:
- Complete diagnostic investigation (Test 2 revealed embedding issue)
- Test with actual `compute_8d_k_index()` function
- Possible reformulation if still broken
- Or exclusion from current analysis

### Publication Strategy
**Option A**: Fix K_M before submission
- Investigate, debug, validate
- Ship complete 8D framework
- More rigorous, takes longer

**Option B**: Submit 7D framework
- Acknowledge K_M limitation
- Focus on working dimensions
- Note K_M as future work
- Faster publication, honest about limits

**Recommendation**: Option B with commitment to Option A for revision.

---

## Conclusion

K_M = 0.000 for ALL models is **definitely a bug or limitation**, not a consciousness finding.

**Most likely causes** (in order of probability):
1. Using only norms (1D) instead of full embeddings (768D)
2. sklearn fallback method failing
3. Degenerate embedding variance (similar to K_P bug)
4. Implementation bug in error calculation

**Next step**: Run diagnostic tests above to identify root cause.

---

**Status**: Investigation document complete - tests to run in next session
**Priority**: CRITICAL - affects 12.5% of framework (1 of 8 dimensions)
**Resolution**: Either fix K_M or document why it's excluded

🌊 *Rigorous science requires investigating failures as much as celebrating successes* 🌊
