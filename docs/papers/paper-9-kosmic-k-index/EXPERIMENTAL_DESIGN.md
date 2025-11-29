# Kosmic K-Index: Experimental Design

## Validating the 7D Framework Through Controlled Experiments

**Date**: November 29, 2025
**Status**: Design Phase

---

## Overview

This document outlines the experimental strategy for validating the 7D Kosmic K-Vector framework. The approach is phased to build confidence incrementally.

---

## Phase 1: The Cognitive Tetrad (K_R, K_A, K_I, K_P)

### 1.1 Environment: Track L / Overcooked

Use existing coordination environments where:
- Observations are rich (multi-dimensional)
- Actions affect environment state
- Reward requires coordination

### 1.2 Agent Types

| Agent Type | Expected Profile |
|------------|------------------|
| Random | Low K_R, Low K_A, Low K_P |
| Linear (reactive) | High K_R, Low K_A, Low K_P |
| CMA-ES trained | High K_R, Medium K_A, Medium K_P |
| PPO trained | High K_R, High K_A, High K_P |

### 1.3 Hypotheses

**H1**: K_R alone is necessary but insufficient
- Test: High K_R agents with low reward exist
- Measure: Correlation(K_R, Reward) < Correlation(K_vector, Reward)

**H2**: K_A adds predictive power
- Test: Controlling for K_R, K_A correlates with reward
- Analysis: Partial correlation or regression

**H3**: K_P distinguishes good from great agents
- Test: Among high-K_R agents, K_P differentiates performance
- Analysis: Stratified comparison

### 1.4 Metrics to Log

For each episode:
```python
{
    "episode_id": int,
    "agent_type": str,
    "reward": float,
    "K_R": float,
    "K_A": float,
    "K_I": float,
    "K_P": float,
    "observations": np.ndarray,  # For post-hoc analysis
    "actions": np.ndarray,
}
```

### 1.5 Analysis Plan

1. Compute K-vector for all agents
2. Correlation matrix: K components vs reward
3. Regression: Reward ~ K_R + K_A + K_I + K_P
4. Visualize: 2D projections (K_R vs K_A, K_R vs K_P, etc.)

---

## Phase 2: The Temporal Dimension (K_M)

### 2.1 Environment: Delayed-Reward Tasks

Design environments where:
- Reward is delayed by T steps
- Current optimal action depends on history
- Pure reflex fails

**Example: Delayed Foraging**
- Agent sees food locations at t=0
- Food becomes collectible at t=T
- Agent must remember locations

### 2.2 Agent Types

| Agent Type | Architecture | Expected K_M |
|------------|--------------|--------------|
| Feedforward | MLP only | ~0 |
| Recurrent | LSTM/GRU | High |
| Transformer | Attention | High |

### 2.3 Hypotheses

**H4**: K_M predicts success in delayed tasks
- Test: Correlation(K_M, Reward) in delayed environments
- Control: K_R, K_A, K_P similar across architectures

**H5**: Feedforward agents have K_M ≈ 0
- Test: Even with high K_R, feedforward K_M → 0
- Validates that K_M measures something distinct

### 2.4 Experimental Protocol

1. Train identical reward functions with different architectures
2. Evaluate on varying delay lengths (T = 1, 5, 10, 20)
3. Compute full K-vector at each delay
4. Plot K_M vs delay and K_M vs reward

---

## Phase 3: The Social Dimension (K_S)

### 3.1 Environment: Multi-Agent Overcooked

Standard Overcooked with:
- 2 agents sharing kitchen
- Coordination required for efficiency
- Individual vs team reward options

### 3.2 Training Conditions

| Condition | Training | Expected K_S |
|-----------|----------|--------------|
| A: Independent | Self-play, individual reward | Low |
| B: Cooperative | Self-play, shared reward | Medium |
| C: Centralized | CTDE, shared reward | High |
| D: With Communication | Message channel | Highest |

### 3.3 Hypotheses

**H6**: K_S increases with coordination training
- Test: K_S(A) < K_S(B) < K_S(C) < K_S(D)

**H7**: K_S predicts team reward beyond individual K
- Test: Team_Reward ~ K_R_avg + K_S
- K_S has significant positive coefficient

**H8**: Low K_S leads to interference
- Test: In A condition, agents block each other more
- Metric: Count of collision/blocking events

### 3.4 Measurement

For each team:
```python
{
    "team_id": int,
    "condition": str,
    "team_reward": float,
    "K_S": float,  # Action correlation between agents
    "K_R_A": float,  # Agent A's reactivity
    "K_R_B": float,  # Agent B's reactivity
    "collisions": int,
    "successful_handoffs": int,
}
```

---

## Phase 4: The Harmonic Dimension (K_H)

### 4.1 Environment: "The Commons"

A resource management gridworld:

**Features**:
- Renewable resources (spawn slowly)
- Depletable resources (finite)
- Sustainability threshold (over-harvest → collapse)
- Multiple agents competing/cooperating

**Dynamics**:
- Resource R regenerates: dR/dt = r(1 - R/K) - harvest
- If R < threshold: collapse (R → 0)
- Agents choose harvest rate

### 4.2 Agent Types

| Type | Strategy | Expected K_H |
|------|----------|--------------|
| Greedy | Maximize immediate harvest | Low |
| Myopic | Short-term optimization | Low-Medium |
| Sustainable | Respect regeneration limits | High |
| Optimal | Long-term value maximization | High |

### 4.3 Hypotheses

**H9**: K_H predicts long-term survival
- Test: High-reward/low-K_H agents eventually collapse
- Metric: Time-to-collapse vs K_H

**H10**: K_H requires forward modeling
- Test: High K_H correlates with high K_P
- Sustainability requires prediction

**H11**: Tragedy of the commons with low collective K_H
- Test: Multi-agent with individually low K_H → system collapse
- Even if individual reward is temporarily high

### 4.4 Normative Reference

Define K_H relative to sustainable harvest rate:
```python
sustainable_rate = resource_regeneration_rate

def compute_k_harmonic_commons(harvest_rate):
    deviation = abs(harvest_rate - sustainable_rate)
    return np.exp(-deviation / sustainable_rate)
```

### 4.5 Long-Run Protocol

1. Run simulations for T=1000 timesteps
2. Track resource level over time
3. Identify collapse events (R < 0.1)
4. Compute K_H in early phase (t < 100)
5. Correlate early K_H with eventual collapse

---

## Phase 5: Integration and the Full 7D Space

### 5.1 The "Kosmic Quadrant" Hypothesis

**Hypothesis**: Successful agents occupy a specific region of K-space where all dimensions are moderately high.

**Test**:
1. Train many agents across environments
2. Compute full K-vector for each
3. Cluster in 7D space
4. Characterize clusters by performance

**Expected Clusters**:
- Thermostats: High K_R, low everything else
- Zombies: High K_R, K_A, low K_P, K_M
- Greedy: High K_R, K_A, K_P, low K_H
- **Kosmic**: Balanced high across all dimensions

### 5.2 Threshold Surfaces

Instead of single threshold (K > 1.5), define region:
```
K_R > τ_R AND K_A > τ_A AND K_I > τ_I AND ...
```

**Analysis**:
1. Fit logistic regression: Success ~ K_vector
2. Learn weights for each dimension
3. Derive effective thresholds from decision boundary

### 5.3 Dimensionality Analysis

**Question**: Are 7 dimensions necessary or redundant?

**Analysis**:
1. PCA on K-vectors across many agents
2. How many components explain 95% variance?
3. If < 7, identify which dimensions are redundant

---

## Summary: Experimental Roadmap

| Phase | Focus | Environment | Key Metric | Timeline |
|-------|-------|-------------|------------|----------|
| 1 | Tetrad | Track L | K_R, K_A, K_I, K_P | Week 1-2 |
| 2 | Temporal | Delayed tasks | K_M | Week 3-4 |
| 3 | Social | Multi-agent | K_S | Week 5-6 |
| 4 | Harmonic | Commons | K_H | Week 7-8 |
| 5 | Integration | All | Full vector | Week 9-10 |

---

## Appendix: Environment Specifications

### A.1 Track L (Existing)

- Observation: 8D continuous
- Action: 2D continuous
- Reward: Task completion + efficiency
- Episode length: 100 steps

### A.2 Delayed Foraging (New)

- Grid: 10x10
- Observation: Agent position + food locations (visible at t=0)
- Action: 4 discrete (NSEW)
- Delay: T ∈ {1, 5, 10, 20}
- Reward: +1 per food collected after delay

### A.3 Multi-Agent Overcooked (Existing)

- Standard Overcooked layouts
- 2 agents
- Observation: Local view + partner position
- Action: 6 discrete
- Reward: Dishes delivered

### A.4 The Commons (New)

- Grid: 20x20
- Resources: R ∈ [0, 100]
- Regeneration: r = 0.1
- Harvest: Agent chooses h ∈ [0, 1]
- Observation: Local resources + global R
- Reward: Harvest amount
- Collapse: R < 10 → episode ends

---

*Experimental Design v1.0*
*November 29, 2025*
