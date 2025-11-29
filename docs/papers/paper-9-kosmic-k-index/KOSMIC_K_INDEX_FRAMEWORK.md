# The Kosmic K-Index Framework

## A 7-Dimensional Measure of Consciousness Potentiality

**Version**: 1.0
**Date**: November 29, 2025
**Status**: Theoretical Framework - Ready for Implementation

---

## Executive Summary

This document presents the **Kosmic K-Index Framework**, an evolution from the simple magnitude-coupling metric (K = 2|ρ(||O||, ||A||)|) to a comprehensive 7-dimensional vector that captures the multi-faceted nature of consciousness as articulated in the "Kosmic Theory of Conscious Potentiality."

The framework addresses a fundamental gap: the original K measures only **reactivity** (Spinozist parallelism), but consciousness—as defined by IIT, FEP, and autopoiesis theory—requires **integration**, **prediction**, **operational closure**, **temporal depth**, **social coherence**, and **normative alignment**.

---

## Part I: The Gap Between Current K and Kosmic Theory

### 1.1 Current K Definition

```
K = 2 × |ρ(||O||, ||A||)|
```

Where:
- ρ = Pearson correlation coefficient
- ||O|| = magnitude (norm) of observations
- ||A|| = magnitude (norm) of actions

**What it captures**: Stimulus-response magnitude coupling ("parallelism")

**What it misses**:

| Theoretical Pillar | Key Concept | Current K Captures? |
|-------------------|-------------|---------------------|
| IIT (Tononi) | Integration (Φ) | ❌ No |
| FEP (Friston) | Active Inference / Prediction | ❌ No |
| Autopoiesis | Operational Closure | ❌ No |
| Whitehead | Prehension / Process | 🟡 Partial |
| Thermodynamics | Dissipation / Efficiency | ❌ No |
| Symbiogenesis | Collective Intelligence | ❌ No |
| Scaling Laws | Harmonic Alignment | ❌ No |

### 1.2 The "Thermostat Problem"

A system with high current K could be a simple "zombie thermostat"—perfectly reactive but with:
- No internal model
- No prediction capability
- No operational closure
- No temporal memory
- No social coherence
- No normative alignment

This is insufficient for measuring "consciousness potentiality" as defined in the Kosmic Theory.

---

## Part II: The 7-Dimensional Kosmic K-Vector

We define the **Kosmic K-Vector**:

```
K = (K_R, K_A, K_I, K_P, K_M, K_S, K_H)
```

Each dimension corresponds to a pillar of the Kosmic Theory:

| Dimension | Name | Theoretical Source | Range |
|-----------|------|-------------------|-------|
| K_R | Reactivity / Coupling | Spinoza (Parallelism) | [0, 2] |
| K_A | Agency / Causal Closure | Autopoiesis (Maturana/Varela) | [0, 1] |
| K_I | Integrative Complexity | IIT (Tononi) / Ashby | [0, 1] |
| K_P | Predictive Alignment | FEP (Friston) | [0, 1] |
| K_M | Meta / Temporal Depth | Whitehead (Process) | [0, 1] |
| K_S | Social Coherence | Symbiogenesis (Margulis) | [0, 1] |
| K_H | Harmonic / Normative | Scaling Laws (West) | [0, 1] |

---

## Part III: Mathematical Definitions

### 3.1 K_R: Reactivity / Coupling (The Original K)

**Source**: Spinozist parallelism—Thought and Extension move together.

**Definition**:
```
K_R = 2 × |ρ(||O||, ||A||)|
```

**Implementation**:
```python
def compute_k_reactivity(observations: np.ndarray, actions: np.ndarray) -> float:
    obs_norms = np.linalg.norm(observations, axis=1)
    act_norms = np.linalg.norm(actions, axis=1)

    if np.std(obs_norms) < 1e-10 or np.std(act_norms) < 1e-10:
        return 0.0

    correlation = np.corrcoef(obs_norms, act_norms)[0, 1]
    return 2.0 * abs(correlation)
```

**Interpretation**:
- K_R = 0: No coupling (random/constant actions)
- K_R ≈ 1: Moderate reactivity
- K_R = 2: Perfect magnitude coupling

---

### 3.2 K_A: Agency / Causal Closure

**Source**: Autopoiesis (Maturana/Varela), Levin's morphogenesis—the agent "writes" reality, not just "reads" it.

**Definition**:
```
K_A = |ρ(||A_t||, Δ||O_{t+1}||)|
```

Where Δ||O_{t+1}|| = ||O_{t+1}|| - ||O_t|| (change in observation magnitude)

**Implementation**:
```python
def compute_k_agency(observations: np.ndarray, actions: np.ndarray) -> float:
    obs_norms = np.linalg.norm(observations, axis=1)
    act_norms = np.linalg.norm(actions, axis=1)

    if len(obs_norms) < 2:
        return 0.0

    delta_obs = np.abs(np.diff(obs_norms))  # Change in reality
    act_aligned = act_norms[:-1]             # Actions that caused it

    if np.std(delta_obs) < 1e-10 or np.std(act_aligned) < 1e-10:
        return 0.0

    return abs(np.corrcoef(act_aligned, delta_obs)[0, 1])
```

**Interpretation**:
- K_A ≈ 0: Actions don't reliably affect future observations
- K_A ≈ 1: Actions systematically sculpt the sensory field

---

### 3.3 K_I: Integrative Complexity

**Source**: IIT (Tononi), Ashby's Law of Requisite Variety—agent complexity matches environmental complexity.

**Definition**:
```
K_I = 2 × min(H_O, H_A) / (H_O + H_A + ε)
```

Where H_O and H_A are Shannon entropies of observation and action norms.

**Implementation**:
```python
def compute_k_integration(observations: np.ndarray, actions: np.ndarray) -> float:
    def shannon_entropy(data: np.ndarray, bins: int = 32) -> float:
        hist, _ = np.histogram(data, bins=bins, density=True)
        p = hist / (np.sum(hist) + 1e-12)
        p = p[p > 0]
        return -np.sum(p * np.log(p))

    obs_norms = np.linalg.norm(observations, axis=1)
    act_norms = np.linalg.norm(actions, axis=1)

    h_obs = shannon_entropy(obs_norms)
    h_act = shannon_entropy(act_norms)

    denom = h_obs + h_act + 1e-12
    return 2.0 * min(h_obs, h_act) / denom
```

**Interpretation**:
- K_I ≈ 0: Massive mismatch between observation and action complexity
- K_I ≈ 1: Action repertoire matches environmental richness

---

### 3.4 K_P: Predictive Alignment (FEP Proxy)

**Source**: Free Energy Principle (Friston)—agents minimize prediction error.

**Definition**:
```
K_P = 1 - NPE
```

Where NPE = Normalized Prediction Error:
```
NPE = E[||O_{t+1} - Ô_{t+1}||²] / E[||O_{t+1} - Ō||²]
```

And Ô_{t+1} = f(O_t, A_t) is a learned world model prediction.

**Implementation**:
```python
def compute_k_predictive(observations: np.ndarray, actions: np.ndarray) -> float:
    """
    Fit a simple world model and measure prediction accuracy.
    """
    from sklearn.linear_model import Ridge
    from sklearn.model_selection import train_test_split

    if len(observations) < 10:
        return 0.0

    # Prepare data: (O_t, A_t) -> O_{t+1}
    X = np.hstack([observations[:-1], actions[:-1]])
    y = observations[1:]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

    # Fit simple model
    model = Ridge(alpha=1.0)
    model.fit(X_train, y_train)

    # Predictions
    y_pred = model.predict(X_test)

    # Baseline: predict mean
    y_mean = np.mean(y_train, axis=0)

    # Compute errors
    pred_error = np.mean((y_test - y_pred) ** 2)
    baseline_error = np.mean((y_test - y_mean) ** 2)

    if baseline_error < 1e-10:
        return 1.0  # Perfect prediction (constant environment)

    npe = pred_error / baseline_error
    return max(0.0, 1.0 - npe)
```

**Interpretation**:
- K_P ≈ 0: No better than predicting the mean
- K_P ≈ 1: Near-perfect world model

---

### 3.5 K_M: Meta / Temporal Depth

**Source**: Whitehead (process philosophy), recursive self-use—agent uses its own history.

**Definition**:
```
K_M = clip((L_0 - L_H) / (L_0 + ε), 0, 1)
```

Where:
- L_0 = loss of Markov model (predict action from current observation only)
- L_H = loss of history-aware model (predict action from observation window)

**Implementation**:
```python
def compute_k_meta(observations: np.ndarray, actions: np.ndarray,
                   history_len: int = 5) -> float:
    """
    Measure how much history improves action prediction.
    """
    from sklearn.linear_model import Ridge
    from sklearn.model_selection import train_test_split

    if len(observations) < history_len + 10:
        return 0.0

    obs_norms = np.linalg.norm(observations, axis=1)
    act_norms = np.linalg.norm(actions, axis=1)

    # Markov model: O_t -> A_t
    X_markov = obs_norms[history_len:].reshape(-1, 1)
    y = act_norms[history_len:]

    # History model: O_{t-k:t} -> A_t
    X_history = np.array([
        obs_norms[i:i+history_len] for i in range(len(obs_norms) - history_len)
    ])

    X_m_train, X_m_test, y_train, y_test = train_test_split(
        X_markov, y, test_size=0.3, random_state=42
    )
    X_h_train, X_h_test, _, _ = train_test_split(
        X_history, y, test_size=0.3, random_state=42
    )

    # Fit models
    model_markov = Ridge(alpha=1.0)
    model_history = Ridge(alpha=1.0)

    model_markov.fit(X_m_train, y_train)
    model_history.fit(X_h_train, y_train)

    # Compute losses
    l_0 = np.mean((y_test - model_markov.predict(X_m_test)) ** 2)
    l_h = np.mean((y_test - model_history.predict(X_h_test)) ** 2)

    if l_0 < 1e-10:
        return 0.0

    return max(0.0, min(1.0, (l_0 - l_h) / (l_0 + 1e-10)))
```

**Interpretation**:
- K_M ≈ 0: History doesn't help (pure reflex / thermostat)
- K_M ≈ 1: Behaviour strongly depends on temporal context

---

### 3.6 K_S: Social / Intersubjective Coherence

**Source**: Symbiogenesis (Margulis), collective intelligence (Levin)—coherence with other agents.

**Definition** (for multi-agent systems):
```
K_S = |ρ(||A^A_t||, ||A^B_t||)|
```

Or via cross-prediction improvement:
```
K_S = (L_base - L_cross) / (L_base + ε)
```

**Implementation**:
```python
def compute_k_social(actions_A: np.ndarray, actions_B: np.ndarray) -> float:
    """
    Measure coordination between two agents.
    """
    act_norms_A = np.linalg.norm(actions_A, axis=1)
    act_norms_B = np.linalg.norm(actions_B, axis=1)

    if np.std(act_norms_A) < 1e-10 or np.std(act_norms_B) < 1e-10:
        return 0.0

    return abs(np.corrcoef(act_norms_A, act_norms_B)[0, 1])
```

**Interpretation**:
- K_S ≈ 0: Agents act independently
- K_S ≈ 1: Highly coordinated / coherent behaviour

---

### 3.7 K_H: Harmonic / Normative Coherence

**Source**: Scaling Laws (West), "sacred reciprocity"—alignment with higher-level constraints.

**Definition**:
```
K_H = exp(-α × D(p_agent || p_norm))
```

Where D is KL divergence between agent's state-action distribution and a normative reference.

**Implementation**:
```python
def compute_k_harmonic(observations: np.ndarray, actions: np.ndarray,
                       normative_dist: callable = None) -> float:
    """
    Measure alignment with normative constraints.

    If no normative_dist provided, uses efficiency proxy:
    reward achieved per unit action magnitude.
    """
    if normative_dist is None:
        # Default: efficiency proxy
        act_norms = np.linalg.norm(actions, axis=1)
        mean_action = np.mean(act_norms)

        # Assume lower action magnitude = more efficient
        # Normalize to [0, 1]
        efficiency = 1.0 / (1.0 + mean_action)
        return efficiency

    # With explicit normative distribution
    from scipy.stats import entropy
    from scipy.special import kl_div

    # Compute agent's empirical distribution
    obs_act = np.hstack([observations, actions])
    # ... (histogram-based KL computation)

    return np.exp(-alpha * kl_divergence)
```

**Interpretation**:
- K_H ≈ 0: Behaviour far from normative ideal
- K_H ≈ 1: Behaviour closely matches harmonic constraints

---

## Part IV: Composite Scores

### 4.1 Scalar Composite: K_Σ

For cases where a single number is needed:

```
K_Σ = K_R × K_A × K_I × K_P × K_M × K_S × K_H
```

Or geometric mean (less harsh):
```
K_geo = (K_R × K_A × K_I × K_P × K_M × K_S × K_H)^(1/7)
```

### 4.2 The K-Vector as Primary

**Recommendation**: Always preserve the 7D vector for analysis. The composite is secondary.

```python
def compute_kosmic_index(observations: np.ndarray, actions: np.ndarray,
                         observations_B: np.ndarray = None,
                         actions_B: np.ndarray = None) -> dict:
    """
    Compute the full 7D Kosmic K-Vector.
    """
    k_r = compute_k_reactivity(observations, actions)
    k_a = compute_k_agency(observations, actions)
    k_i = compute_k_integration(observations, actions)
    k_p = compute_k_predictive(observations, actions)
    k_m = compute_k_meta(observations, actions)

    # Social requires second agent
    if observations_B is not None and actions_B is not None:
        k_s = compute_k_social(actions, actions_B)
    else:
        k_s = None

    k_h = compute_k_harmonic(observations, actions)

    # Composite (excluding None values)
    components = [k_r, k_a, k_i, k_p, k_m, k_h]
    if k_s is not None:
        components.append(k_s)

    k_sigma = np.prod(components)
    k_geo = np.power(np.prod(components), 1.0 / len(components))

    return {
        "K_vector": {
            "K_R": k_r,
            "K_A": k_a,
            "K_I": k_i,
            "K_P": k_p,
            "K_M": k_m,
            "K_S": k_s,
            "K_H": k_h,
        },
        "K_sigma": k_sigma,
        "K_geo": k_geo,
    }
```

---

## Part V: Theoretical Grounding

### 5.1 Mapping to Kosmic Theory Pillars

| K Dimension | Kosmic Theory Section | Key Concept |
|-------------|----------------------|-------------|
| K_R | Part I (Spinoza) | Attribute parallelism |
| K_A | Part II (Autopoiesis) | Operational closure |
| K_I | Part III (IIT) | Integrated information |
| K_P | Part III (FEP) | Free energy minimization |
| K_M | Part I (Whitehead) | Process / temporal depth |
| K_S | Part II (Symbiogenesis) | Collective intelligence |
| K_H | Part IV (Scaling Laws) | Normative alignment |

### 5.2 The Recursive Meta-Intelligence Loop

The 7D K-vector captures the four-stage recursive loop from Part IV:

1. **Bottom-Up Emergence** (K_R): Coupling to environment
2. **Scaling and Collectivization** (K_S): Coordination with others
3. **Top-Down Constraint** (K_H): Normative alignment
4. **Modeling and Modification** (K_P, K_M): Predictive self-use

---

## Part VI: Experimental Design

### 6.1 Phase 1: Validate the Cognitive Tetrad (K_R, K_A, K_I, K_P)

**Environment**: Current Track L / Overcooked
**Goal**: Show that K_R alone is insufficient; K_A and K_P add predictive power for performance.

**Hypotheses**:
- H1: High K_R is necessary but not sufficient for high reward
- H2: K_A (agency) correlates with reward independently of K_R
- H3: K_P (prediction) correlates with reward independently of K_R

### 6.2 Phase 2: Validate Temporal Depth (K_M)

**Environment**: Delayed-reward tasks, POMDPs
**Goal**: Show that K_M distinguishes memory-using agents from reflexive agents.

**Experimental Conditions**:
- Condition A: Feedforward policy (no memory)
- Condition B: Recurrent policy (LSTM/GRU)

**Hypotheses**:
- H4: In POMDPs, high K_M correlates with success
- H5: Feedforward agents have K_M ≈ 0 even with high K_R

### 6.3 Phase 3: Validate Social Coherence (K_S)

**Environment**: Multi-agent Overcooked
**Goal**: Show that K_S predicts team performance beyond individual metrics.

**Experimental Conditions**:
- Condition A: Selfish agents (individual reward)
- Condition B: Cooperative agents (shared reward)
- Condition C: Explicitly coordinated agents

**Hypotheses**:
- H6: K_S increases from A → B → C
- H7: K_S predicts team reward better than individual K values

### 6.4 Phase 4: Validate Harmonic Alignment (K_H)

**Environment**: "The Commons" (resource management with sustainability constraints)
**Goal**: Show that K_H predicts long-term survival vs tragedy-of-the-commons.

**Experimental Conditions**:
- Condition A: Greedy agents (maximize immediate reward)
- Condition B: Sustainable agents (respect resource limits)

**Hypotheses**:
- H8: High-reward/low-K_H agents eventually collapse
- H9: Moderate-reward/high-K_H agents survive long-term

---

## Part VII: Future Horizons

### 7.1 From Vectors to Geometry

The 7D K-vector is a "reductionist scaffold" that compresses rich dynamics into scalars. The Kosmic Theory posits reality as **geometric and processual**. Future work will move from vectors to manifolds.

### 7.2 Topological K (K_Topo)

Using **Topological Data Analysis (TDA)** and **Persistent Homology**:

- Analyze agent trajectories in (O, A)-space as point clouds
- Compute Betti numbers:
  - β₀: Integration (connected components)
  - β₁: Operational closure (loops)
  - β₂: Higher-dimensional structure

**Definition**:
```
K_Topo = Maximum persistence of 1D features (loops)
```

**Interpretation**: Autopoiesis is a loop. High K_Topo indicates stable operational closure.

### 7.3 Spectral K (K_Spectral)

Using **Spectral Graph Theory**:

- Model multi-agent system as interaction graph
- Compute Laplacian matrix L
- Use spectral gap λ₂ (Fiedler value) as coherence measure

**Definition**:
```
K_Spectral = λ₂(L_interaction)
```

**Interpretation**: λ₂ > 0 indicates connected, synchronized collective. λ₂ ≈ 0 indicates fragmentation.

### 7.4 The Kosmic Tensor (Ω)

Treat the 7D K-dynamics as a flow on a "Kosmic manifold":

- Define phase-space density ρ(K_R, ..., K_H)
- Volume Ω = ∫ det(J) dt where J is Jacobian of flows

**Interpretation**: Total "causal power" or "expressed potentiality" of an agent.

This represents the transition from "Newtonian" (vectors) to "Relativistic" (manifolds) physics of consciousness.

---

## Part VIII: Implementation Roadmap

### Phase 1 (Current Paper): Cognitive Tetrad
- Implement: K_R, K_A, K_I, K_P
- Validate in Track L experiments
- Timeline: Immediate

### Phase 2 (Next Paper): Temporal + Social
- Implement: K_M, K_S
- Design POMDP and multi-agent experiments
- Timeline: 2-3 months

### Phase 3 (Theory Paper): Full 7D + Geometry
- Implement: K_H
- Sketch: K_Topo, K_Spectral
- Present unified framework
- Timeline: 6 months

---

## Appendix A: Complete Implementation

```python
"""
kosmic_k_index.py

Complete implementation of the 7D Kosmic K-Index Framework.
"""

import numpy as np
from typing import Dict, Optional, Tuple
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split


def _shannon_entropy(data: np.ndarray, bins: int = 32) -> float:
    """Compute Shannon entropy of data using histogram estimation."""
    hist, _ = np.histogram(data, bins=bins, density=True)
    p = hist / (np.sum(hist) + 1e-12)
    p = p[p > 0]
    return -np.sum(p * np.log(p)) if len(p) > 0 else 0.0


def compute_k_reactivity(observations: np.ndarray, actions: np.ndarray) -> float:
    """K_R: Reactivity / Coupling (Spinozist parallelism)."""
    obs_norms = np.linalg.norm(observations, axis=1)
    act_norms = np.linalg.norm(actions, axis=1)

    if np.std(obs_norms) < 1e-10 or np.std(act_norms) < 1e-10:
        return 0.0

    correlation = np.corrcoef(obs_norms, act_norms)[0, 1]
    if np.isnan(correlation):
        return 0.0
    return 2.0 * abs(correlation)


def compute_k_agency(observations: np.ndarray, actions: np.ndarray) -> float:
    """K_A: Agency / Causal Closure (Autopoiesis)."""
    obs_norms = np.linalg.norm(observations, axis=1)
    act_norms = np.linalg.norm(actions, axis=1)

    if len(obs_norms) < 2:
        return 0.0

    delta_obs = np.abs(np.diff(obs_norms))
    act_aligned = act_norms[:-1]

    if np.std(delta_obs) < 1e-10 or np.std(act_aligned) < 1e-10:
        return 0.0

    correlation = np.corrcoef(act_aligned, delta_obs)[0, 1]
    if np.isnan(correlation):
        return 0.0
    return abs(correlation)


def compute_k_integration(observations: np.ndarray, actions: np.ndarray) -> float:
    """K_I: Integrative Complexity (IIT / Ashby)."""
    obs_norms = np.linalg.norm(observations, axis=1)
    act_norms = np.linalg.norm(actions, axis=1)

    h_obs = _shannon_entropy(obs_norms)
    h_act = _shannon_entropy(act_norms)

    denom = h_obs + h_act + 1e-12
    return 2.0 * min(h_obs, h_act) / denom


def compute_k_predictive(observations: np.ndarray, actions: np.ndarray) -> float:
    """K_P: Predictive Alignment (FEP proxy)."""
    if len(observations) < 20:
        return 0.0

    try:
        X = np.hstack([observations[:-1], actions[:-1]])
        y = observations[1:]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )

        model = Ridge(alpha=1.0)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_mean = np.mean(y_train, axis=0)

        pred_error = np.mean((y_test - y_pred) ** 2)
        baseline_error = np.mean((y_test - y_mean) ** 2)

        if baseline_error < 1e-10:
            return 1.0

        npe = pred_error / baseline_error
        return max(0.0, 1.0 - npe)
    except Exception:
        return 0.0


def compute_k_meta(observations: np.ndarray, actions: np.ndarray,
                   history_len: int = 5) -> float:
    """K_M: Meta / Temporal Depth (Whitehead process)."""
    if len(observations) < history_len + 20:
        return 0.0

    try:
        obs_norms = np.linalg.norm(observations, axis=1)
        act_norms = np.linalg.norm(actions, axis=1)

        X_markov = obs_norms[history_len:].reshape(-1, 1)
        X_history = np.array([
            obs_norms[i:i+history_len]
            for i in range(len(obs_norms) - history_len)
        ])
        y = act_norms[history_len:]

        X_m_train, X_m_test, y_train, y_test = train_test_split(
            X_markov, y, test_size=0.3, random_state=42
        )
        X_h_train, X_h_test, _, _ = train_test_split(
            X_history, y, test_size=0.3, random_state=42
        )

        model_markov = Ridge(alpha=1.0)
        model_history = Ridge(alpha=1.0)

        model_markov.fit(X_m_train, y_train)
        model_history.fit(X_h_train, y_train)

        l_0 = np.mean((y_test - model_markov.predict(X_m_test)) ** 2)
        l_h = np.mean((y_test - model_history.predict(X_h_test)) ** 2)

        if l_0 < 1e-10:
            return 0.0

        return max(0.0, min(1.0, (l_0 - l_h) / (l_0 + 1e-10)))
    except Exception:
        return 0.0


def compute_k_social(actions_A: np.ndarray, actions_B: np.ndarray) -> float:
    """K_S: Social / Intersubjective Coherence (Symbiogenesis)."""
    act_norms_A = np.linalg.norm(actions_A, axis=1)
    act_norms_B = np.linalg.norm(actions_B, axis=1)

    min_len = min(len(act_norms_A), len(act_norms_B))
    act_norms_A = act_norms_A[:min_len]
    act_norms_B = act_norms_B[:min_len]

    if np.std(act_norms_A) < 1e-10 or np.std(act_norms_B) < 1e-10:
        return 0.0

    correlation = np.corrcoef(act_norms_A, act_norms_B)[0, 1]
    if np.isnan(correlation):
        return 0.0
    return abs(correlation)


def compute_k_harmonic(observations: np.ndarray, actions: np.ndarray) -> float:
    """K_H: Harmonic / Normative Coherence (Scaling Laws)."""
    act_norms = np.linalg.norm(actions, axis=1)
    mean_action = np.mean(act_norms)

    # Default: efficiency proxy (lower action = more efficient)
    efficiency = 1.0 / (1.0 + mean_action)
    return efficiency


def compute_kosmic_index(
    observations: np.ndarray,
    actions: np.ndarray,
    actions_B: Optional[np.ndarray] = None,
) -> Dict:
    """
    Compute the complete 7D Kosmic K-Index.

    Args:
        observations: Agent observations [T, obs_dim]
        actions: Agent actions [T, act_dim]
        actions_B: Optional second agent actions for K_S

    Returns:
        Dictionary with K-vector, composite scores, and metadata
    """
    k_r = compute_k_reactivity(observations, actions)
    k_a = compute_k_agency(observations, actions)
    k_i = compute_k_integration(observations, actions)
    k_p = compute_k_predictive(observations, actions)
    k_m = compute_k_meta(observations, actions)
    k_h = compute_k_harmonic(observations, actions)

    k_s = None
    if actions_B is not None:
        k_s = compute_k_social(actions, actions_B)

    # Composite scores
    components = [k_r, k_a, k_i, k_p, k_m, k_h]
    if k_s is not None:
        components.append(k_s)

    k_sigma = float(np.prod(components))
    k_geo = float(np.power(np.prod(components), 1.0 / len(components)))

    return {
        "K_vector": {
            "K_R (Reactivity)": k_r,
            "K_A (Agency)": k_a,
            "K_I (Integration)": k_i,
            "K_P (Prediction)": k_p,
            "K_M (Meta)": k_m,
            "K_S (Social)": k_s,
            "K_H (Harmonic)": k_h,
        },
        "K_sigma": k_sigma,
        "K_geo": k_geo,
        "n_samples": len(observations),
    }


# Alias for backwards compatibility
def compute_k_index(observations: np.ndarray, actions: np.ndarray) -> float:
    """Original K-Index (now K_R)."""
    return compute_k_reactivity(observations, actions)
```

---

## Appendix B: References

### Primary Sources (from Kosmic Theory)

1. **Spinoza, B.** - *Ethics* (Substance Monism, Parallelism)
2. **Whitehead, A.N.** - *Process and Reality* (Actual Entities, Prehensions)
3. **Tegmark, M.** - Mathematical Universe Hypothesis
4. **Tononi, G.** - Integrated Information Theory (IIT)
5. **Friston, K.** - Free Energy Principle (FEP)
6. **Maturana & Varela** - Autopoiesis
7. **Margulis, L.** - Symbiogenesis
8. **Levin, M.** - Bioelectric Morphogenesis
9. **West, G.** - Scaling Laws

### Implementation References

10. **Edelsbrunner & Harer** - *Computational Topology* (for TDA)
11. **Chung, F.** - *Spectral Graph Theory* (for Spectral K)

---

*Document Version: 1.0*
*Last Updated: November 29, 2025*
*Status: Framework Complete - Ready for Phase 1 Implementation*
