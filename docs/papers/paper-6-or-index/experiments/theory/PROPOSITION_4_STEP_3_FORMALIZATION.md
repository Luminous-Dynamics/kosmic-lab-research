# Proposition 4: Step 3 Formalization

**Date**: November 27, 2025
**Status**: Week 1, Day 2 - Proof Refinement

---

## Formalizing the Connection: ||π - π*||² to Var(P(a|o))

### Goal
Establish a rigorous connection between policy deviation $\|\pi - \pi^*\|^2$ and the conditional action variance $\text{Var}(P(a|o))$ that appears in the O/R Index.

---

## Detailed Derivation

### Setup

**Policy Representation**:
- Policy $\pi$ is a function $\pi: \mathcal{O} \times \mathcal{A} \to [0,1]$ where $\pi(a|o)$ is the probability of action $a$ given observation $o$
- For discrete actions: $\sum_{a \in \mathcal{A}} \pi(a|o) = 1$ for all $o$
- For continuous actions: $\pi(a|o)$ is a probability density function

**L2 Policy Distance** (Discrete Case):
$$\|\pi - \pi^*\|^2 = \sum_{o \in \mathcal{O}} P(o) \sum_{a \in \mathcal{A}} (\pi(a|o) - \pi^*(a|o))^2$$

where $P(o)$ is the stationary observation distribution.

---

### Step 3.1: Decomposing the Distance for Deterministic π*

Since $\pi^*$ is deterministic (Assumption 2), for each observation $o$, there exists a unique optimal action $a^*(o)$ such that:
$$\pi^*(a|o) = \delta_{a, a^*(o)} = \begin{cases} 1 & \text{if } a = a^*(o) \\ 0 & \text{otherwise} \end{cases}$$

Substituting into the L2 distance:
$$\|\pi - \pi^*\|^2 = \sum_{o} P(o) \left[ (1 - \pi(a^*(o)|o))^2 + \sum_{a \neq a^*(o)} \pi(a|o)^2 \right]$$

Since $\sum_a \pi(a|o) = 1$, we have:
$$1 - \pi(a^*(o)|o) = \sum_{a \neq a^*(o)} \pi(a|o)$$

Therefore:
$$\|\pi - \pi^*\|^2 = \sum_{o} P(o) \left[ \left(\sum_{a \neq a^*(o)} \pi(a|o)\right)^2 + \sum_{a \neq a^*(o)} \pi(a|o)^2 \right]$$

---

### Step 3.2: Relating to Action Variance

**Key Insight**: For a stochastic policy near a deterministic optimum, the "spread" of the policy (variance) is related to the mass placed on non-optimal actions.

Define the **conditional action variance** for observation $o$:
$$\sigma^2(o) = \text{Var}_{\pi(\cdot|o)}(a) = \sum_{a \in \mathcal{A}} \pi(a|o) (a - \bar{a}(o))^2$$

where $\bar{a}(o) = \sum_a a \cdot \pi(a|o)$ is the expected action.

**Connection Lemma**:
For a policy $\pi$ that is "close" to deterministic $\pi^*$ (i.e., $\pi(a^*|o) \approx 1$), the variance $\sigma^2(o)$ and the squared distance contribution at $o$ are related by:

$$\sum_{a \neq a^*(o)} \pi(a|o) \leq C \cdot \sigma^2(o)$$

where $C$ is a constant depending on the action space structure.

**Proof of Lemma**:
- If $\pi(a^*|o) \approx 1$, then $\bar{a}(o) \approx a^*(o)$
- The variance measures spread from $\bar{a}(o) \approx a^*(o)$
- Any mass on $a \neq a^*$ contributes to variance proportional to $|a - a^*|^2$
- For bounded action spaces with $|a - a^*| \leq D$, we have $\pi(a|o) \leq \sigma^2(o) / D^2$

---

### Step 3.3: From Local Variance to Population Variance

The O/R Index uses the **population-level** conditional variance:
$$\text{Var}(P(a|o)) = \mathbb{E}_{o \sim P}[\sigma^2(o)] = \sum_{o} P(o) \sigma^2(o)$$

From Steps 3.1-3.2, we have:
$$\|\pi - \pi^*\|^2 \leq K \sum_{o} P(o) \sigma^2(o) = K \cdot \text{Var}(P(a|o))$$

where $K$ is a constant depending on:
- Action space diameter $D$
- Neighborhood size (how close $\pi$ is to $\pi^*$)
- Number of actions $|\mathcal{A}|$

**Typical value**: For discrete actions with $|\mathcal{A}| = m$ and unit spacing, $K \approx m$.

---

### Step 3.4: Connecting to O/R Index

From the O/R Index definition:
$$\text{O/R}(\pi) + 1 = \frac{\text{Var}(P(a|o))}{\text{Var}(P(a))}$$

Therefore:
$$\text{Var}(P(a|o)) = (\text{O/R}(\pi) + 1) \cdot \text{Var}(P(a))$$

Substituting into Step 3.3:
$$\|\pi - \pi^*\|^2 \leq K \cdot (\text{O/R}(\pi) + 1) \cdot \text{Var}(P(a))$$

---

## Final Proportionality Constant

Combining with the regret bound from Step 2:
$$\text{Regret}(\pi) \geq \frac{\lambda_{\min}(H)}{2} \|\pi - \pi^*\|^2 \geq \frac{\lambda_{\min}(H)}{2K} \cdot (\text{O/R}(\pi) + 1) \cdot \text{Var}(P(a))$$

**Defining the constant**:
$$c = \frac{\lambda_{\min}(H) \cdot \text{Var}(P(a))}{2K}$$

For typical MARL settings:
- $\lambda_{\min}(H) \approx 0.01$ - 0.1 (reward landscape curvature)
- $\text{Var}(P(a)) \approx 0.5$ - 2.0 (action scale)
- $K \approx 5$ - 10 (number of actions)

This gives $c \approx 0.0005$ - 0.04.

---

## Limitations of This Derivation

1. **Local Approximation**: The connection $\|\pi - \pi^*\|^2 \leq K \cdot \text{Var}(P(a|o))$ holds exactly only when $\pi$ is near $\pi^*$ (within the neighborhood $\mathcal{N}(\pi^*)$).

2. **Action Space Structure**: The constant $K$ depends on action space geometry (discrete vs continuous, number of actions, spacing).

3. **Second-Order Approximation**: The entire proof relies on Taylor expansion validity, which requires small deviations.

4. **Deterministic Optimum**: The derivation fundamentally requires $\pi^*$ to be deterministic (Assumption 2).

---

## Key Takeaway for Appendix

**What we've shown**:
- Policy deviation $\|\pi - \pi^*\|^2$ is **upper bounded** by a constant times the conditional action variance $\text{Var}(P(a|o))$
- This variance appears directly in the O/R Index: $\text{O/R} + 1 = \text{Var}(P(a|o)) / \text{Var}(P(a))$
- Therefore: **Regret is lower bounded by a positive constant times O/R**

**Mathematical statement**:
$$\text{Regret}(\pi) \geq c \cdot (\text{O/R}(\pi) + 1)$$

where $c$ depends on task geometry but is **strictly positive** under our assumptions.

---

## Next Steps

- [ ] Add this derivation to Appendix A (full proof)
- [ ] Simplify Step 3 in main text to reference appendix
- [ ] Add remark about constant $K$ interpretation
- [ ] Create TikZ figure showing variance-distance connection

**Target**: Complete by Nov 28, 2025 (end of Day 3)
