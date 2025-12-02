"""
Unified Index Implementation for Paper 8
=========================================

Combines K-Index (magnitude coupling) with O/R Index (behavioral consistency)
into a unified coherence measure for consciousness-like behavior.

Usage:
    from unified_index_implementation import UnifiedIndex

    ui = UnifiedIndex()
    coherence, k, or_idx = ui.compute(obs_norms, act_norms, action_probs, observations)

Note: This is an implementation sketch. Copy to fre/metrics/ for production use.
"""

import numpy as np
from scipy.stats import pearsonr, spearmanr
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass


@dataclass
class UnifiedIndexResult:
    """Container for unified index computation results."""
    coherence: float          # Unified coherence score
    k_index: float            # K-Index component
    or_index: float           # O/R Index component
    k_ci: Tuple[float, float] # K-Index 95% CI
    or_ci: Tuple[float, float] # O/R Index 95% CI
    coherence_ci: Tuple[float, float]  # Coherence 95% CI


class UnifiedIndex:
    """
    Unified Index combining K-Index and O/R Index.

    K-Index: K = 2 × |ρ(||O||, ||A||)| ∈ [0, 2]
        - Measures magnitude coupling between observations and actions
        - High K = proportional responses to stimuli

    O/R Index: O/R = Var(P(a|o)) / Var(P(a)) - 1
        - Measures behavioral consistency
        - Low O/R = predictable action distributions

    Unified Coherence: C = K × (1 - tanh(O/R))
        - Combines both perspectives
        - High C = coherent and consistent behavior
    """

    def __init__(
        self,
        k_window: int = 50,
        action_bins: int = 10,
        observation_bins: int = 10,
        n_bootstrap: int = 1000,
    ):
        """
        Initialize unified index calculator.

        Args:
            k_window: Window size for K-Index computation
            action_bins: Number of bins for action discretization
            observation_bins: Number of bins for observation discretization
            n_bootstrap: Number of bootstrap samples for CI
        """
        self.k_window = k_window
        self.action_bins = action_bins
        self.observation_bins = observation_bins
        self.n_bootstrap = n_bootstrap

    def compute_k_index(
        self,
        obs_norms: np.ndarray,
        act_norms: np.ndarray,
    ) -> Tuple[float, float, float]:
        """
        Compute K-Index with confidence interval.

        Args:
            obs_norms: Observation norms [T]
            act_norms: Action norms [T]

        Returns:
            (k_estimate, k_lower, k_upper)
        """
        if len(obs_norms) < 2:
            return np.nan, np.nan, np.nan

        # Point estimate
        r, _ = pearsonr(obs_norms, act_norms)
        k = 2.0 * abs(r)

        # Bootstrap CI
        rng = np.random.default_rng(42)
        k_samples = []
        T = len(obs_norms)

        for _ in range(self.n_bootstrap):
            idx = rng.integers(0, T, size=T)
            obs_boot = obs_norms[idx]
            act_boot = act_norms[idx]
            r_boot, _ = pearsonr(obs_boot, act_boot)
            k_samples.append(2.0 * abs(r_boot))

        k_samples = np.array(k_samples)
        k_lower = np.percentile(k_samples, 2.5)
        k_upper = np.percentile(k_samples, 97.5)

        return k, k_lower, k_upper

    def compute_or_index(
        self,
        action_probs: np.ndarray,
        observations: np.ndarray,
    ) -> Tuple[float, float, float]:
        """
        Compute O/R Index with confidence interval.

        O/R = Var(P(a|o)) / Var(P(a)) - 1

        Args:
            action_probs: Action probability distributions [T, A]
            observations: Observation vectors [T, O]

        Returns:
            (or_estimate, or_lower, or_upper)
        """
        T, A = action_probs.shape

        if T < 2:
            return np.nan, np.nan, np.nan

        # Discretize observations into bins
        obs_flat = observations.mean(axis=1)  # Reduce to 1D
        obs_bins = np.digitize(
            obs_flat,
            np.linspace(obs_flat.min(), obs_flat.max(), self.observation_bins + 1)[1:-1]
        )

        # Compute conditional variances
        conditional_vars = []
        for b in range(self.observation_bins):
            mask = obs_bins == b
            if mask.sum() > 1:
                probs_in_bin = action_probs[mask]
                # Variance of action probs within this observation bin
                var_in_bin = probs_in_bin.var(axis=0).mean()
                conditional_vars.append(var_in_bin)

        if len(conditional_vars) == 0:
            return np.nan, np.nan, np.nan

        # Mean conditional variance
        var_conditional = np.mean(conditional_vars)

        # Marginal variance
        marginal_probs = action_probs.mean(axis=0)
        var_marginal = marginal_probs.var() + 1e-8  # Avoid division by zero

        # O/R Index
        or_index = var_conditional / var_marginal - 1

        # Bootstrap CI
        rng = np.random.default_rng(42)
        or_samples = []

        for _ in range(self.n_bootstrap):
            idx = rng.integers(0, T, size=T)
            action_probs_boot = action_probs[idx]
            observations_boot = observations[idx]

            obs_flat_boot = observations_boot.mean(axis=1)
            obs_bins_boot = np.digitize(
                obs_flat_boot,
                np.linspace(obs_flat_boot.min(), obs_flat_boot.max(), self.observation_bins + 1)[1:-1]
            )

            cond_vars_boot = []
            for b in range(self.observation_bins):
                mask = obs_bins_boot == b
                if mask.sum() > 1:
                    probs_in_bin = action_probs_boot[mask]
                    var_in_bin = probs_in_bin.var(axis=0).mean()
                    cond_vars_boot.append(var_in_bin)

            if len(cond_vars_boot) > 0:
                var_cond_boot = np.mean(cond_vars_boot)
                marg_probs_boot = action_probs_boot.mean(axis=0)
                var_marg_boot = marg_probs_boot.var() + 1e-8
                or_boot = var_cond_boot / var_marg_boot - 1
                or_samples.append(or_boot)

        if len(or_samples) == 0:
            return or_index, np.nan, np.nan

        or_samples = np.array(or_samples)
        or_lower = np.percentile(or_samples, 2.5)
        or_upper = np.percentile(or_samples, 97.5)

        return or_index, or_lower, or_upper

    def compute_unified_coherence(
        self,
        k: float,
        or_index: float,
    ) -> float:
        """
        Compute unified coherence score.

        Coherence = K × (1 - tanh(O/R))

        Properties:
        - Coherence → 0 when K → 0 or O/R → +∞
        - Coherence → 2K when O/R → -∞
        - Coherence ∈ [0, 4] theoretical, typically [0, 2]

        Args:
            k: K-Index value
            or_index: O/R Index value

        Returns:
            Unified coherence score
        """
        if np.isnan(k) or np.isnan(or_index):
            return np.nan

        return k * (1 - np.tanh(or_index))

    def compute(
        self,
        obs_norms: np.ndarray,
        act_norms: np.ndarray,
        action_probs: np.ndarray,
        observations: np.ndarray,
    ) -> UnifiedIndexResult:
        """
        Compute full unified index with all components and CIs.

        Args:
            obs_norms: Observation norms [T]
            act_norms: Action norms [T]
            action_probs: Action probability distributions [T, A]
            observations: Observation vectors [T, O]

        Returns:
            UnifiedIndexResult with all components
        """
        # K-Index
        k, k_lower, k_upper = self.compute_k_index(obs_norms, act_norms)

        # O/R Index
        or_idx, or_lower, or_upper = self.compute_or_index(action_probs, observations)

        # Unified Coherence
        coherence = self.compute_unified_coherence(k, or_idx)

        # Coherence CI (approximate via delta method)
        coherence_lower = self.compute_unified_coherence(k_lower, or_upper)
        coherence_upper = self.compute_unified_coherence(k_upper, or_lower)

        return UnifiedIndexResult(
            coherence=coherence,
            k_index=k,
            or_index=or_idx,
            k_ci=(k_lower, k_upper),
            or_ci=(or_lower, or_upper),
            coherence_ci=(coherence_lower, coherence_upper),
        )


class UnifiedIndexFitness:
    """
    Fitness function for CMA-ES optimization using unified index.

    Use this to optimize for coherent behavior (high K + low O/R)
    instead of just K-Index alone.
    """

    def __init__(
        self,
        env,
        n_episodes: int = 5,
        k_weight: float = 0.5,
        or_weight: float = 0.5,
    ):
        """
        Initialize fitness function.

        Args:
            env: Environment instance
            n_episodes: Episodes per fitness evaluation
            k_weight: Weight for K-Index component
            or_weight: Weight for O/R Index component
        """
        self.env = env
        self.n_episodes = n_episodes
        self.k_weight = k_weight
        self.or_weight = or_weight
        self.unified_index = UnifiedIndex()

    def __call__(self, agent) -> float:
        """
        Evaluate agent fitness based on unified coherence.

        Args:
            agent: Agent to evaluate

        Returns:
            Fitness score (higher = better)
        """
        coherences = []

        for _ in range(self.n_episodes):
            result = self._run_episode(agent)
            coherences.append(result.coherence)

        return np.mean(coherences)

    def _run_episode(self, agent) -> UnifiedIndexResult:
        """Run single episode and compute unified index."""
        obs_norms = []
        act_norms = []
        action_probs_list = []
        observations_list = []

        obs = self.env.reset()
        done = False

        while not done:
            # Get action probabilities from agent
            action_probs = agent.get_action_probs(obs)
            action = agent.sample_action(action_probs)

            # Record data
            obs_norms.append(np.linalg.norm(obs))
            act_norms.append(np.linalg.norm(action))
            action_probs_list.append(action_probs)
            observations_list.append(obs)

            # Step environment
            obs, reward, done, info = self.env.step(action)

        # Compute unified index
        return self.unified_index.compute(
            np.array(obs_norms),
            np.array(act_norms),
            np.array(action_probs_list),
            np.array(observations_list),
        )


# =============================================================================
# Alternative Unified Index Formulations
# =============================================================================

def additive_index(k: float, or_index: float) -> float:
    """
    Additive unified index: K - O/R

    Simple linear combination where high K and low O/R both contribute.
    """
    return k - or_index


def multiplicative_index(k: float, or_index: float) -> float:
    """
    Multiplicative unified index: K × (-O/R + 2)

    Shifts O/R to positive range, then multiplies.
    """
    return k * (-or_index + 2)


def vector_magnitude_index(k: float, or_index: float) -> float:
    """
    Vector magnitude index: sqrt(K² + O/R²)

    Treats (K, -O/R) as a 2D vector and returns magnitude.
    """
    return np.sqrt(k**2 + or_index**2)


def vector_direction_index(k: float, or_index: float) -> float:
    """
    Vector direction index: atan2(-O/R, K)

    Returns angle in radians. Near π/4 is balanced, 0 is K-dominant, π/2 is O/R-dominant.
    """
    return np.arctan2(-or_index, k)


# =============================================================================
# Statistical Tests
# =============================================================================

def test_k_or_correlation(
    k_values: np.ndarray,
    or_values: np.ndarray,
    method: str = "pearson",
) -> Dict[str, float]:
    """
    Test correlation between K-Index and O/R Index.

    Args:
        k_values: K-Index values [N]
        or_values: O/R Index values [N]
        method: "pearson", "spearman", or "kendall"

    Returns:
        Dictionary with correlation coefficient and p-value
    """
    from scipy.stats import pearsonr, spearmanr, kendalltau

    if method == "pearson":
        r, p = pearsonr(k_values, or_values)
    elif method == "spearman":
        r, p = spearmanr(k_values, or_values)
    elif method == "kendall":
        r, p = kendalltau(k_values, or_values)
    else:
        raise ValueError(f"Unknown method: {method}")

    return {"correlation": r, "p_value": p, "method": method}


def sobel_mediation_test(
    x: np.ndarray,  # Independent variable (e.g., K)
    m: np.ndarray,  # Mediator (e.g., O/R)
    y: np.ndarray,  # Dependent variable (e.g., performance)
) -> Dict[str, float]:
    """
    Sobel test for mediation: does M mediate the effect of X on Y?

    Tests the indirect effect a × b where:
    - a = effect of X on M
    - b = effect of M on Y controlling for X

    Args:
        x: Independent variable values [N]
        m: Mediator values [N]
        y: Dependent variable values [N]

    Returns:
        Dictionary with Sobel z-statistic, p-value, and effect sizes
    """
    from scipy import stats
    import statsmodels.api as sm

    # Path a: X → M
    X_with_const = sm.add_constant(x)
    model_a = sm.OLS(m, X_with_const).fit()
    a = model_a.params[1]
    se_a = model_a.bse[1]

    # Path b: M → Y (controlling for X)
    XM_with_const = sm.add_constant(np.column_stack([x, m]))
    model_b = sm.OLS(y, XM_with_const).fit()
    b = model_b.params[2]  # Coefficient for M
    se_b = model_b.bse[2]

    # Sobel test
    ab = a * b
    se_ab = np.sqrt(a**2 * se_b**2 + b**2 * se_a**2)
    z = ab / se_ab
    p = 2 * (1 - stats.norm.cdf(abs(z)))

    # Total effect (X → Y)
    model_total = sm.OLS(y, X_with_const).fit()
    c = model_total.params[1]

    # Direct effect (X → Y controlling for M)
    c_prime = model_b.params[1]  # Coefficient for X in full model

    # Proportion mediated
    proportion_mediated = ab / c if c != 0 else np.nan

    return {
        "sobel_z": z,
        "p_value": p,
        "indirect_effect": ab,
        "direct_effect": c_prime,
        "total_effect": c,
        "proportion_mediated": proportion_mediated,
        "path_a": a,
        "path_b": b,
    }


# =============================================================================
# Demo and Testing
# =============================================================================

if __name__ == "__main__":
    # Demo with synthetic data
    np.random.seed(42)
    T = 200
    O = 20
    A = 10

    # Generate synthetic episode data
    obs_norms = np.random.exponential(1.0, T)
    act_norms = obs_norms * 0.8 + np.random.normal(0, 0.2, T)  # Correlated with obs
    act_norms = np.abs(act_norms)

    # Action probabilities (softmax of random logits)
    logits = np.random.randn(T, A)
    action_probs = np.exp(logits) / np.exp(logits).sum(axis=1, keepdims=True)

    # Observations
    observations = np.random.randn(T, O)

    # Compute unified index
    ui = UnifiedIndex()
    result = ui.compute(obs_norms, act_norms, action_probs, observations)

    print("=== Unified Index Demo ===")
    print(f"K-Index:     {result.k_index:.4f} [{result.k_ci[0]:.4f}, {result.k_ci[1]:.4f}]")
    print(f"O/R Index:   {result.or_index:.4f} [{result.or_ci[0]:.4f}, {result.or_ci[1]:.4f}]")
    print(f"Coherence:   {result.coherence:.4f} [{result.coherence_ci[0]:.4f}, {result.coherence_ci[1]:.4f}]")

    # Alternative formulations
    print("\n=== Alternative Formulations ===")
    print(f"Additive:      {additive_index(result.k_index, result.or_index):.4f}")
    print(f"Multiplicative: {multiplicative_index(result.k_index, result.or_index):.4f}")
    print(f"Vector Mag:    {vector_magnitude_index(result.k_index, result.or_index):.4f}")
    print(f"Vector Dir:    {vector_direction_index(result.k_index, result.or_index):.4f} rad")
