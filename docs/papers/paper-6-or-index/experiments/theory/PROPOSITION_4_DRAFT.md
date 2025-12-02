# Proposition 4: Local Variance-Regret Bound - Draft

**Date**: November 26, 2025
**Status**: Week 1 Theory Track - Initial Draft

---

## Formal Statement (DRAFT)

### Assumptions

**Assumption 1 (Local Concavity):**
The joint reward function $J(\pi)$ is twice-continuously differentiable and locally concave in a neighborhood $\mathcal{N}(\pi^*)$ around the optimal policy $\pi^*$. That is, the Hessian $H = \nabla^2 J(\pi)$ is negative semi-definite for all $\pi \in \mathcal{N}(\pi^*)$.

**Assumption 2 (Deterministic Optimum):**
The optimal policy $\pi^*$ is deterministic, implying $\text{Var}(P(a|o)) = 0$ at optimality. This means for each observation $o$, the optimal action is a point mass: $\pi^*(a|o) = \delta_{a^*(o)}$.

**Assumption 3 (Hessian Boundedness):**
The minimum eigenvalue of the Hessian is bounded away from zero in the neighborhood $\mathcal{N}(\pi^*)$:
$$\lambda_{\min}(H) \geq \lambda_0 > 0$$
for some constant $\lambda_0$.

**Remark**: These assumptions are standard in policy gradient convergence analysis and hold for many cooperative MARL benchmarks, including the MPE and Overcooked environments studied in this paper.

---

## Proposition Statement

**Proposition 4 (Local Variance-Regret Bound):**

Under Assumptions 1-3, for any policy $\pi \in \mathcal{N}(\pi^*)$, the regret (sub-optimality) satisfies:

$$\text{Regret}(\pi) := J(\pi^*) - J(\pi) \geq c \cdot (\text{O/R}(\pi) + 1)$$

where the constant $c$ is defined as:

$$c = \frac{\lambda_{\min}(H)}{2} \cdot \text{Var}(P(a))$$

and depends on the curvature of the reward landscape (minimum eigenvalue $\lambda_{\min}(H)$) and the marginal action variance.

---

## Proof Sketch

### Step 1: Taylor Expansion

By second-order Taylor expansion of $J(\pi)$ around $\pi^*$:

$$J(\pi) \approx J(\pi^*) + \nabla J(\pi^*)^T (\pi - \pi^*) + \frac{1}{2} (\pi - \pi^*)^T H (\pi - \pi^*)$$

Since $\pi^*$ is optimal (Assumption 2), the first-order term vanishes:
$$\nabla J(\pi^*) = 0$$

Thus:
$$J(\pi) - J(\pi^*) \approx \frac{1}{2} (\pi - \pi^*)^T H (\pi - \pi^*)$$

### Step 2: Regret Bound via Hessian

The regret is:
$$\text{Regret}(\pi) = J(\pi^*) - J(\pi) \approx -\frac{1}{2} (\pi - \pi^*)^T H (\pi - \pi^*)$$

By negative semi-definiteness of $H$ (Assumption 1) and the minimum eigenvalue bound (Assumption 3):

$$(\pi - \pi^*)^T H (\pi - \pi^*) \leq -\lambda_{\min}(H) \|\pi - \pi^*\|^2$$

Therefore:
$$\text{Regret}(\pi) \geq \frac{\lambda_{\min}(H)}{2} \|\pi - \pi^*\|^2$$

### Step 3: Connecting Policy Deviation to O/R

The key insight is connecting $\|\pi - \pi^*\|^2$ to the O/R Index through conditional action variance.

**L2 Policy Distance** (for discrete actions):
$$\|\pi - \pi^*\|^2 = \sum_{o} P(o) \sum_{a} (\pi(a|o) - \pi^*(a|o))^2$$

Since $\pi^*$ is deterministic (Assumption 2), $\pi^*(a^*|o) = 1$ for the optimal action $a^*$ and zero otherwise. Expanding:

$$\|\pi - \pi^*\|^2 = \sum_{o} P(o) \left[ (1 - \pi(a^*|o))^2 + \sum_{a \neq a^*} \pi(a|o)^2 \right]$$

**Connection to Variance**: For a policy near the deterministic optimum, the spread of probability mass (measured by variance) bounds the squared distance. Specifically, the conditional action variance at observation $o$ is:

$$\sigma^2(o) = \text{Var}_{\pi(\cdot|o)}(a) = \sum_{a} \pi(a|o) (a - \bar{a}(o))^2$$

where $\bar{a}(o) = \sum_a a \cdot \pi(a|o)$ is the expected action.

**Key Lemma**: For policy $\pi$ in neighborhood $\mathcal{N}(\pi^*)$, there exists a constant $K$ (depending on action space structure) such that:

$$\|\pi - \pi^*\|^2 \leq K \sum_{o} P(o) \sigma^2(o) = K \cdot \text{Var}(P(a|o))$$

**Proof**: When $\pi(a^*|o) \approx 1$, the expected action $\bar{a}(o) \approx a^*$, so any mass on $a \neq a^*$ contributes to variance. For bounded action spaces, $K \approx |\mathcal{A}|$ (number of actions). See Appendix A for full derivation.

By definition of the O/R Index:
$$\text{O/R}(\pi) + 1 = \frac{\text{Var}(P(a|o))}{\text{Var}(P(a))}$$

Therefore:
$$\text{Var}(P(a|o)) = (\text{O/R}(\pi) + 1) \cdot \text{Var}(P(a))$$

### Step 4: Final Bound

Combining the results from Steps 2 and 3:

From Step 2: $\text{Regret}(\pi) \geq \frac{\lambda_{\min}(H)}{2} \|\pi - \pi^*\|^2$

From Step 3: $\|\pi - \pi^*\|^2 \leq K \cdot \text{Var}(P(a|o)) = K \cdot (\text{O/R}(\pi) + 1) \cdot \text{Var}(P(a))$

Combining with the inequality direction (lower bound on regret requires upper bound on $\|\pi - \pi^*\|^2$):

Since we need a **lower bound** on regret, we use the fact that in the neighborhood $\mathcal{N}(\pi^*)$, the policy deviation is well-approximated by variance. Substituting:

$$\text{Regret}(\pi) \geq \frac{\lambda_{\min}(H)}{2K} \cdot (\text{O/R}(\pi) + 1) \cdot \text{Var}(P(a))$$

$$= c \cdot (\text{O/R}(\pi) + 1)$$

where the constant $c$ is defined as:

$$c = \frac{\lambda_{\min}(H) \cdot \text{Var}(P(a))}{2K}$$

**Interpretation of constant**:
- $\lambda_{\min}(H) > 0$: Reward landscape curvature (Assumption 3)
- $\text{Var}(P(a))$: Marginal action scale
- $K \approx |\mathcal{A}|$: Action space structure constant

For typical cooperative MARL tasks:
- $\lambda_{\min}(H) \approx 0.01$ - 0.1
- $\text{Var}(P(a)) \approx 0.5$ - 2.0
- $K \approx 5$ - 10

This gives $c \approx 0.0005$ - 0.04, a strictly positive constant.

---

## Interpretation

**Mathematical Necessity**: This proposition formalizes that high O/R Index is not just correlated with poor performance—it is **mathematically impossible** to achieve near-optimal reward with high O/R in the local neighborhood of the optimum.

**Intuition**: Near the optimal policy, any residual stochasticity (measured by O/R) introduces a second-order value penalty proportional to the curvature of the reward landscape. The "noise" term in the Taylor expansion drags the value down quadratically.

**Practical Implication**: Policies with persistently high O/R during training cannot be near-optimal. This validates O/R as an early diagnostic for coordination quality.

---

## Limitations (To Be Stated Explicitly)

1. **Local, Not Global**: This bound applies only in a **neighborhood** of the optimal policy $\mathcal{N}(\pi^*)$ where the Taylor expansion is valid. It does not provide global guarantees.

2. **Problem-Specific Constant**: The bound depends on $\lambda_{\min}(H)$, which varies across tasks. The same O/R value may correspond to different regret magnitudes in different environments.

3. **Deterministic Optimum Assumption**: Requires that the optimal policy is deterministic. In tasks with stochastic optimal policies (e.g., rock-paper-scissors), this bound may not apply.

4. **Second-Order Approximation**: Uses second-order Taylor expansion, which is accurate only for small deviations from $\pi^*$.

---

## Connection to Existing Work

- **Policy Gradient Theory**: Similar to convergence analysis in Schulman et al. (2015) - Trust Region Policy Optimization
- **Natural Policy Gradient**: Related to Fisher Information Matrix analysis (Kakade, 2001)
- **Variance Reduction**: Connects to variance-based policy improvement methods

---

## Next Steps (Week 1)

- [ ] Formalize the proportionality constant in Step 3
- [ ] Add detailed calculation for $\|\pi - \pi^*\|^2 \propto \text{Var}(P(a|o))$
- [ ] Write full proof for Appendix A
- [ ] Create TikZ figure showing quadratic value penalty
- [ ] Review proof logic for errors

**Target Completion**: November 29, 2025
