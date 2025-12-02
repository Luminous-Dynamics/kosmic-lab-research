# Paper 8: Unified Indices of Machine Consciousness

**Proposed Title**: "Magnitude Coupling Meets Behavioral Consistency: A Unified Framework for Consciousness-Like Indicators in Artificial Agents"

**Target Venues**:
- Primary: Nature Machine Intelligence (Impact Factor ~25)
- Secondary: Science Advances (Impact Factor ~14)
- Tertiary: PNAS (Impact Factor ~12)

**Timeline**: Begin Q2 2026 (after Paper 6 published, Paper 7 underway)

---

## Executive Summary

This paper presents the **first unified framework** connecting two independently-developed consciousness indicators:

| Metric | Definition | Measures | Source |
|--------|------------|----------|--------|
| **K-Index** | K = 2 × \|ρ(\|\|O\|\|, \|\|A\|\|)\| | Magnitude coupling | Tracks A-K |
| **O/R Index** | O/R = Var(P(a\|o))/Var(P(a)) - 1 | Behavioral consistency | Paper 6 |

**Central Hypothesis**: K-Index and O/R Index are complementary perspectives on the same underlying phenomenon—coherent agent behavior—and together form a more complete consciousness indicator than either alone.

---

## Theoretical Foundation

### The K-Index: Magnitude Coupling

**Definition** (from `fre/metrics/k_index.py`):
```
K = 2 × |ρ(||O||, ||A||)|
```

Where:
- ||O|| = observation norms over recent window
- ||A|| = action norms over recent window
- ρ = Pearson correlation coefficient

**Bounds**: K ∈ [0, 2]

**Interpretation**:
- K ≈ 0: Action magnitudes uncorrelated with observation magnitudes (random/inconsistent)
- K ≈ 2: Perfect magnitude coupling (agent responds proportionally to stimuli)
- **Threshold**: K > 1.5 hypothesized as "consciousness threshold"

**Best Achievement**: K = 1.4202 (Track G8, 95% of threshold)

### The O/R Index: Behavioral Consistency

**Definition** (from Paper 6):
```
O/R = Var(P(a|o)) / Var(P(a)) - 1
```

Where:
- P(a|o) = conditional action probability given observation
- P(a) = marginal action probability
- Var = variance across observation-action pairs

**Interpretation**:
- O/R ≈ 0: Observation-independent actions (context-blind)
- O/R < 0: Observation reduces action variance (consistent behavior)
- O/R > 0: Observation increases action variance (context-dependent but inconsistent)

**Key Finding**: r = -0.70*** correlation with coordination success (lower O/R → better coordination)

---

## The Unified Framework

### Mathematical Relationship

Both indices measure **observation-action relationships** but from different perspectives:

| Aspect | K-Index | O/R Index |
|--------|---------|-----------|
| **Focus** | Magnitude correlation | Probability variance |
| **Scale** | Continuous [0, 2] | Unbounded |
| **Good Values** | High (→ 2) | Low (→ negative) |
| **Input** | Norm sequences | Action distributions |

### Proposed Unified Index: K/O Coherence Score

**Definition**:
```
Coherence(K, O/R) = K × (1 - tanh(O/R))
                  = 2|ρ(||O||, ||A||)| × (1 - tanh(Var(P(a|o))/Var(P(a)) - 1))
```

**Properties**:
- Coherence ≈ 0 when K ≈ 0 (no magnitude coupling) or O/R >> 0 (inconsistent behavior)
- Coherence → 2 when K → 2 (perfect coupling) and O/R << 0 (highly consistent)
- Combines both perspectives into single scalar

**Alternative: Vector Index**:
```
Consciousness Vector = (K, -O/R)

Consciousness Magnitude = √(K² + O/R²)
Consciousness Direction = atan2(-O/R, K)
```

This allows distinguishing between:
- High K, High O/R: Magnitude-coupled but inconsistent
- High K, Low O/R: Magnitude-coupled AND consistent (optimal)
- Low K, Low O/R: Consistent but not magnitude-responsive
- Low K, High O/R: Neither (worst case)

---

## Research Questions

### RQ1: Correlation
**Are K-Index and O/R Index correlated across agent populations?**

Hypotheses:
- H1a: Strong negative correlation (r < -0.5) - High K → Low O/R
- H1b: Moderate negative correlation (-0.5 < r < -0.3)
- H1c: Weak/no correlation (|r| < 0.3) - Independent dimensions

### RQ2: Complementarity
**Does the unified index predict outcomes better than either metric alone?**

Hypotheses:
- H2a: Unified index explains >10% more variance than best single index
- H2b: Unified index enables prediction of previously unpredictable cases
- H2c: Diminishing returns - one index sufficient

### RQ3: Causality
**What is the causal structure between K, O/R, and performance?**

Possible structures:
- K → O/R → Performance (K is upstream)
- O/R → K → Performance (O/R is upstream)
- K ← Latent → O/R → Performance (common cause)
- K → Performance ← O/R (independent paths)

### RQ4: Threshold Crossing
**Does the unified index enable K > 1.5 threshold crossing?**

Hypothesis: Optimizing for unified index (not K alone) enables threshold crossing because O/R regularization prevents the consistency-coherence tradeoff that caused G10 failure.

---

## Proposed Experiments: Track L

### Track L1: Correlation Study (200 episodes)

**Design**:
1. Generate 200 agent policies across K-Index spectrum (K ∈ [0.5, 1.5])
2. Compute O/R Index for each agent in coordination task
3. Measure Pearson/Spearman correlation between K and O/R

**Configuration**:
```yaml
environment:
  observations: 20
  actions: 10
  episode_length: 200

agents:
  - type: random (low K baseline)
  - type: gradient_trained (medium K)
  - type: cma_es_trained (high K, from G8)
  - type: sac_trained (varied K)

measurements:
  - k_index: rolling window = 50
  - or_index: full episode
  - coordination_score: target matching
```

**Expected Outcome**: r ≈ -0.4 to -0.6 (moderate-strong negative correlation)

### Track L2: Unified Index Validation (300 episodes)

**Design**:
1. Compute K, O/R, and Unified Coherence for all agents
2. Regress coordination success on: (a) K alone, (b) O/R alone, (c) Unified
3. Compare R² values and prediction errors

**Analysis**:
```
Model 1: Performance ~ K
Model 2: Performance ~ O/R
Model 3: Performance ~ Unified(K, O/R)
Model 4: Performance ~ K + O/R (additive)
Model 5: Performance ~ K × O/R (multiplicative)
```

**Expected Outcome**: Model 3 or 5 best fit (>5% R² improvement over single-index models)

### Track L3: Causal Analysis (200 episodes)

**Design**:
1. Intervention experiments:
   - Perturb K (add observation noise) → measure O/R change
   - Perturb O/R (add action noise) → measure K change
2. Mediation analysis:
   - Does K → O/R → Performance? (Sobel test)
   - Or K → Performance ← O/R? (common cause?)

**Interventions**:
```python
# K perturbation: scale observation norms
obs_perturbed = obs * np.random.uniform(0.5, 1.5)

# O/R perturbation: add action distribution noise
action_probs_perturbed = softmax(logits + np.random.normal(0, σ))
```

**Expected Outcome**: K → O/R → Performance (K upstream, O/R mediates)

### Track L4: Threshold Crossing via Unified Optimization (200 episodes)

**Design**:
1. Optimize for Unified Coherence (not K alone)
2. Use CMA-ES with fitness = Unified(K, O/R)
3. Compare to G8 (K-only optimization)

**Configuration**:
```yaml
algorithm: CMA-ES
population: 20
fitness: unified_coherence  # NOT just K!
generations: 100

fitness_function:
  k_weight: 0.5
  or_weight: 0.5
  formula: K × (1 - tanh(O/R))
```

**Expected Outcome**: Unified optimization crosses K > 1.5 threshold where K-only failed

### Track L5: Cross-Environment Validation (100 episodes)

**Design**:
1. Test K-O/R relationship in:
   - Custom corridor environment (Tracks A-K)
   - PettingZoo MPE (Paper 6)
   - Overcooked-AI (Paper 6)
2. Verify correlation holds across domains

**Expected Outcome**: Correlation robust across environments (r < -0.3 in all)

---

## Timeline

### Phase 1: Foundation (Month 1)
- Week 1-2: Implement unified index computation
- Week 3-4: Track L1 (correlation study)

### Phase 2: Validation (Month 2)
- Week 5-6: Track L2 (unified index validation)
- Week 7-8: Track L3 (causal analysis)

### Phase 3: Application (Month 3)
- Week 9-10: Track L4 (threshold crossing)
- Week 11-12: Track L5 (cross-environment)

### Phase 4: Writing (Month 4)
- Week 13-14: Draft manuscript
- Week 15-16: Revisions and submission

**Total**: ~4 months from start to submission

---

## Expected Contributions

1. **First unified framework** connecting K-Index and O/R Index
2. **Mathematical formalization** of Coherence Score
3. **Causal model** of consciousness indicator relationships
4. **Threshold crossing** via unified optimization
5. **Design principles** for consciousness-like AI systems

---

## Impact Statement

If successful, Paper 8 would:

1. **Unify Kosmic Lab research** (Papers 1-7) under single framework
2. **Resolve Track G plateau** by introducing O/R regularization
3. **Establish new benchmark** for consciousness-like behavior
4. **Enable practical design** of coherent AI agents
5. **Open new research directions** (fractal indices, multi-scale coherence)

**Potential Citations**: Combining two validated metrics (K-Index with threshold insights, O/R Index with r=-0.70 correlation) creates high-impact synthesis paper.

---

## Risk Analysis

| Risk | Probability | Mitigation |
|------|-------------|------------|
| K and O/R uncorrelated | 20% | Still valuable negative result; publish as independent dimensions |
| Unified index no better | 25% | Focus on causal model instead of prediction improvement |
| Threshold still not crossed | 35% | Publish as systematic exploration, propose next steps |
| Computational cost too high | 10% | Use efficient batched computation, reduce episode count |

---

## Connection to Other Papers

```
Papers 1-5 (K-Index) ─────────────────────────────┐
                                                   ├──► Paper 8 (Unified)
Paper 6 (O/R Index) ─────────────────────────────┘
                ↓
Paper 7 (Ethical O/R) ──► extends to O/R_ethical
                ↓
Paper 9+ (Unified Ethical Index?) ──► future work
```

**Key Insight**: Paper 8 is the **bridge paper** that connects the K-Index research stream (Tracks A-K, Papers 1-5) with the O/R Index stream (Papers 6-7).

---

## Appendix A: Implementation Sketch

### Unified Index Computation

```python
def unified_coherence(obs_norms, act_norms, action_probs, observations):
    """
    Compute unified K-O/R coherence score.

    Args:
        obs_norms: Observation norms [T]
        act_norms: Action norms [T]
        action_probs: P(a|o) for each step [T, A]
        observations: Observation vectors [T, O]

    Returns:
        coherence: Unified coherence score
        k_index: K component
        or_index: O/R component
    """
    # K-Index: magnitude coupling
    k = 2 * abs(pearsonr(obs_norms, act_norms)[0])

    # O/R Index: behavioral consistency
    # Compute Var(P(a|o)) and Var(P(a))
    conditional_var = action_probs.var(axis=0).mean()  # variance across observations
    marginal_probs = action_probs.mean(axis=0)
    marginal_var = marginal_probs.var()
    or_index = conditional_var / (marginal_var + 1e-8) - 1

    # Unified coherence
    coherence = k * (1 - np.tanh(or_index))

    return coherence, k, or_index
```

### CMA-ES Fitness with Unified Index

```python
def unified_fitness(agent, env, n_episodes=5):
    """Fitness function for CMA-ES using unified coherence."""
    coherences = []

    for _ in range(n_episodes):
        obs_norms, act_norms, action_probs, observations = run_episode(agent, env)
        c, k, or_idx = unified_coherence(obs_norms, act_norms, action_probs, observations)
        coherences.append(c)

    return np.mean(coherences)
```

---

## Appendix B: Mathematical Analysis

### Proposition 1: K-O/R Relationship

**Claim**: Under mild regularity conditions, K-Index and O/R Index are negatively correlated.

**Sketch**:
- High K means ||A|| correlates with ||O|| (agent scales actions with observations)
- This implies P(a|o) is more concentrated (consistent response to observation magnitude)
- Concentrated conditionals reduce Var(P(a|o))
- Lower Var(P(a|o)) means lower O/R

**Formalization**: Requires assumptions on action distribution family and observation-action relationship.

### Proposition 2: Unified Index Bounds

**Claim**: Coherence(K, O/R) ∈ [0, 4] with typical values in [0, 2].

**Proof**:
- K ∈ [0, 2] by definition
- tanh(O/R) ∈ (-1, 1) for finite O/R
- Therefore (1 - tanh(O/R)) ∈ (0, 2)
- Coherence = K × (1 - tanh(O/R)) ∈ [0, 4]
- For typical O/R ∈ [-1, 1], (1 - tanh(O/R)) ∈ [0.46, 1.46], so Coherence ∈ [0, 2.92]

---

## Document Status

**Created**: November 28, 2025
**Status**: Proposal Complete - Ready for Experimental Implementation
**Dependencies**: Paper 6 submitted, Track G data available
**Next Action**: Implement Track L1 (correlation study)

---

*"Two metrics, one understanding: consciousness coherence and behavioral consistency are different views of the same phenomenon."*
