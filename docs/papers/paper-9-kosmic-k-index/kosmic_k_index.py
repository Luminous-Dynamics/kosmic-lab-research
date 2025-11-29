"""
kosmic_k_index.py

Complete implementation of the 7D Kosmic K-Index Framework.

Based on the Kosmic Theory of Conscious Potentiality, this module provides
metrics for measuring consciousness potentiality across seven dimensions:

    K_R: Reactivity / Coupling (Spinoza)
    K_A: Agency / Causal Closure (Autopoiesis)
    K_I: Integrative Complexity (IIT / Ashby)
    K_P: Predictive Alignment (FEP)
    K_M: Meta / Temporal Depth (Whitehead)
    K_S: Social Coherence (Symbiogenesis)
    K_H: Harmonic / Normative (Scaling Laws)

Usage:
    from kosmic_k_index import compute_kosmic_index

    result = compute_kosmic_index(observations, actions)
    print(result["K_vector"])

Author: Kosmic Lab
Date: November 29, 2025
Version: 1.0
"""

import numpy as np
from typing import Dict, Optional, Tuple, List
import warnings


def _safe_corrcoef(x: np.ndarray, y: np.ndarray) -> float:
    """Compute correlation coefficient with safety checks."""
    if len(x) < 2 or len(y) < 2:
        return 0.0
    if np.std(x) < 1e-10 or np.std(y) < 1e-10:
        return 0.0

    corr = np.corrcoef(x, y)[0, 1]
    if np.isnan(corr):
        return 0.0
    return corr


def _shannon_entropy(data: np.ndarray, bins: int = 32) -> float:
    """
    Compute Shannon entropy of data using histogram estimation.

    Args:
        data: 1D array of values
        bins: Number of histogram bins

    Returns:
        Shannon entropy in nats
    """
    if len(data) < 2:
        return 0.0

    # Handle constant data
    if np.std(data) < 1e-10:
        return 0.0

    hist, _ = np.histogram(data, bins=bins, density=True)
    # Normalize to get probabilities
    p = hist / (np.sum(hist) + 1e-12)
    p = p[p > 0]

    if len(p) == 0:
        return 0.0

    return -np.sum(p * np.log(p + 1e-12))


# =============================================================================
# Core K-Index Components
# =============================================================================

def compute_k_reactivity(observations: np.ndarray, actions: np.ndarray) -> float:
    """
    K_R: Reactivity / Coupling (Spinozist Parallelism)

    Measures how strongly observation magnitude correlates with action magnitude.
    This is the original K-Index definition.

    Formula: K_R = 2 × |ρ(||O||, ||A||)|

    Args:
        observations: Array of shape [T, obs_dim]
        actions: Array of shape [T, act_dim]

    Returns:
        K_R in range [0, 2]

    Interpretation:
        K_R = 0: No magnitude coupling
        K_R ≈ 1: Moderate reactivity
        K_R = 2: Perfect coupling
    """
    if len(observations) < 2:
        return 0.0

    obs_norms = np.linalg.norm(observations, axis=1)
    act_norms = np.linalg.norm(actions, axis=1)

    correlation = _safe_corrcoef(obs_norms, act_norms)
    return 2.0 * abs(correlation)


def compute_k_agency(observations: np.ndarray, actions: np.ndarray) -> float:
    """
    K_A: Agency / Causal Closure (Autopoiesis)

    Measures whether actions systematically affect future observations.
    Based on Maturana & Varela's operational closure concept.

    Formula: K_A = |ρ(||A_t||, Δ||O_{t+1}||)|

    Args:
        observations: Array of shape [T, obs_dim]
        actions: Array of shape [T, act_dim]

    Returns:
        K_A in range [0, 1]

    Interpretation:
        K_A ≈ 0: Actions don't reliably affect observations
        K_A ≈ 1: Actions systematically sculpt the sensory field
    """
    if len(observations) < 3:
        return 0.0

    obs_norms = np.linalg.norm(observations, axis=1)
    act_norms = np.linalg.norm(actions, axis=1)

    # Change in observation magnitude
    delta_obs = np.abs(np.diff(obs_norms))
    # Aligned actions (A_t affects O_{t+1})
    act_aligned = act_norms[:-1]

    correlation = _safe_corrcoef(act_aligned, delta_obs)
    return abs(correlation)


def compute_k_integration(observations: np.ndarray, actions: np.ndarray) -> float:
    """
    K_I: Integrative Complexity (IIT / Ashby's Law)

    Measures whether action complexity matches observation complexity.
    Based on Ashby's Law of Requisite Variety and IIT's integration concept.

    Formula: K_I = 2 × min(H_O, H_A) / (H_O + H_A + ε)

    Args:
        observations: Array of shape [T, obs_dim]
        actions: Array of shape [T, act_dim]

    Returns:
        K_I in range [0, 1]

    Interpretation:
        K_I ≈ 0: Large mismatch between O and A complexity
        K_I ≈ 1: Action repertoire matches environmental richness
    """
    if len(observations) < 10:
        return 0.0

    obs_norms = np.linalg.norm(observations, axis=1)
    act_norms = np.linalg.norm(actions, axis=1)

    h_obs = _shannon_entropy(obs_norms)
    h_act = _shannon_entropy(act_norms)

    denom = h_obs + h_act + 1e-12
    return 2.0 * min(h_obs, h_act) / denom


def compute_k_predictive(observations: np.ndarray, actions: np.ndarray,
                         test_size: float = 0.3) -> float:
    """
    K_P: Predictive Alignment (Free Energy Principle Proxy)

    Measures how well a simple world model can predict future observations.
    Based on Friston's Free Energy Principle.

    Formula: K_P = 1 - NPE (Normalized Prediction Error)

    Args:
        observations: Array of shape [T, obs_dim]
        actions: Array of shape [T, act_dim]
        test_size: Fraction of data for testing

    Returns:
        K_P in range [0, 1]

    Interpretation:
        K_P ≈ 0: No better than predicting the mean
        K_P ≈ 1: Near-perfect world model
    """
    if len(observations) < 20:
        return 0.0

    try:
        from sklearn.linear_model import Ridge
        from sklearn.model_selection import train_test_split
    except ImportError:
        warnings.warn("sklearn not available, using simplified K_P")
        return _compute_k_predictive_simple(observations, actions)

    try:
        # Prepare data: (O_t, A_t) -> O_{t+1}
        X = np.hstack([observations[:-1], actions[:-1]])
        y = observations[1:]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        if len(X_train) < 5 or len(X_test) < 5:
            return 0.0

        # Fit simple model
        model = Ridge(alpha=1.0)
        model.fit(X_train, y_train)

        # Predictions
        y_pred = model.predict(X_test)
        y_mean = np.mean(y_train, axis=0)

        # Compute errors
        pred_error = np.mean((y_test - y_pred) ** 2)
        baseline_error = np.mean((y_test - y_mean) ** 2)

        if baseline_error < 1e-10:
            return 1.0  # Perfect prediction (constant environment)

        npe = pred_error / baseline_error
        return max(0.0, min(1.0, 1.0 - npe))

    except Exception as e:
        warnings.warn(f"K_P computation failed: {e}")
        return 0.0


def _compute_k_predictive_simple(observations: np.ndarray,
                                  actions: np.ndarray) -> float:
    """Simplified K_P without sklearn."""
    # Use autocorrelation of observations as proxy
    obs_norms = np.linalg.norm(observations, axis=1)
    if len(obs_norms) < 3:
        return 0.0

    # Correlation between O_t and O_{t+1}
    autocorr = _safe_corrcoef(obs_norms[:-1], obs_norms[1:])
    return abs(autocorr)


def compute_k_meta(observations: np.ndarray, actions: np.ndarray,
                   history_len: int = 5) -> float:
    """
    K_M: Meta / Temporal Depth (Whitehead Process)

    Measures how much history improves action prediction.
    Based on Whitehead's process philosophy.

    Formula: K_M = (L_0 - L_H) / (L_0 + ε)

    Where:
        L_0 = Markov model loss (predict from O_t only)
        L_H = History model loss (predict from O_{t-k:t})

    Args:
        observations: Array of shape [T, obs_dim]
        actions: Array of shape [T, act_dim]
        history_len: Number of past steps to consider

    Returns:
        K_M in range [0, 1]

    Interpretation:
        K_M ≈ 0: History doesn't help (pure reflex)
        K_M ≈ 1: Behaviour strongly depends on temporal context
    """
    if len(observations) < history_len + 20:
        return 0.0

    try:
        from sklearn.linear_model import Ridge
        from sklearn.model_selection import train_test_split
    except ImportError:
        warnings.warn("sklearn not available, using simplified K_M")
        return _compute_k_meta_simple(observations, actions, history_len)

    try:
        obs_norms = np.linalg.norm(observations, axis=1)
        act_norms = np.linalg.norm(actions, axis=1)

        # Markov model: O_t -> A_t
        X_markov = obs_norms[history_len:].reshape(-1, 1)

        # History model: O_{t-k:t} -> A_t
        X_history = np.array([
            obs_norms[i:i+history_len]
            for i in range(len(obs_norms) - history_len)
        ])

        y = act_norms[history_len:]

        # Split data
        indices = np.arange(len(y))
        train_idx, test_idx = train_test_split(
            indices, test_size=0.3, random_state=42
        )

        X_m_train = X_markov[train_idx]
        X_m_test = X_markov[test_idx]
        X_h_train = X_history[train_idx]
        X_h_test = X_history[test_idx]
        y_train = y[train_idx]
        y_test = y[test_idx]

        if len(X_m_train) < 5:
            return 0.0

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

    except Exception as e:
        warnings.warn(f"K_M computation failed: {e}")
        return 0.0


def _compute_k_meta_simple(observations: np.ndarray, actions: np.ndarray,
                           history_len: int) -> float:
    """Simplified K_M without sklearn."""
    obs_norms = np.linalg.norm(observations, axis=1)
    act_norms = np.linalg.norm(actions, axis=1)

    if len(obs_norms) < history_len + 5:
        return 0.0

    # Compare correlation with current vs with history average
    current = obs_norms[history_len:]
    history_avg = np.array([
        np.mean(obs_norms[i:i+history_len])
        for i in range(len(obs_norms) - history_len)
    ])
    target = act_norms[history_len:]

    corr_current = abs(_safe_corrcoef(current, target))
    corr_history = abs(_safe_corrcoef(history_avg, target))

    if corr_current < 1e-10:
        return 0.0

    improvement = (corr_history - corr_current) / (1.0 + corr_current)
    return max(0.0, min(1.0, improvement))


def compute_k_social(actions_A: np.ndarray, actions_B: np.ndarray) -> float:
    """
    K_S: Social / Intersubjective Coherence (Symbiogenesis)

    Measures coordination between two agents' actions.
    Based on Margulis's symbiogenesis and collective intelligence.

    Formula: K_S = |ρ(||A^A_t||, ||A^B_t||)|

    Args:
        actions_A: First agent's actions [T, act_dim]
        actions_B: Second agent's actions [T, act_dim]

    Returns:
        K_S in range [0, 1]

    Interpretation:
        K_S ≈ 0: Agents act independently
        K_S ≈ 1: Highly coordinated behaviour
    """
    act_norms_A = np.linalg.norm(actions_A, axis=1)
    act_norms_B = np.linalg.norm(actions_B, axis=1)

    # Align lengths
    min_len = min(len(act_norms_A), len(act_norms_B))
    if min_len < 2:
        return 0.0

    act_norms_A = act_norms_A[:min_len]
    act_norms_B = act_norms_B[:min_len]

    correlation = _safe_corrcoef(act_norms_A, act_norms_B)
    return abs(correlation)


def compute_k_harmonic(observations: np.ndarray, actions: np.ndarray,
                       normative_reference: Optional[callable] = None) -> float:
    """
    K_H: Harmonic / Normative Coherence (Scaling Laws)

    Measures alignment with higher-level constraints or values.
    Based on West's scaling laws and normative alignment.

    Args:
        observations: Array of shape [T, obs_dim]
        actions: Array of shape [T, act_dim]
        normative_reference: Optional function that computes ideal action
                            given observation. If None, uses efficiency proxy.

    Returns:
        K_H in range [0, 1]

    Interpretation:
        K_H ≈ 0: Behaviour far from normative ideal
        K_H ≈ 1: Behaviour matches harmonic constraints
    """
    act_norms = np.linalg.norm(actions, axis=1)

    if normative_reference is None:
        # Default: efficiency proxy (lower action magnitude = more efficient)
        mean_action = np.mean(act_norms)
        efficiency = 1.0 / (1.0 + mean_action)
        return efficiency

    # With explicit normative reference
    try:
        ideal_actions = np.array([normative_reference(o) for o in observations])
        ideal_norms = np.linalg.norm(ideal_actions, axis=1)

        # Compute deviation
        deviation = np.mean(np.abs(act_norms - ideal_norms))
        mean_ideal = np.mean(ideal_norms) + 1e-10

        return np.exp(-deviation / mean_ideal)

    except Exception as e:
        warnings.warn(f"K_H with normative reference failed: {e}")
        # Fall back to efficiency proxy
        mean_action = np.mean(act_norms)
        return 1.0 / (1.0 + mean_action)


# =============================================================================
# Main Interface
# =============================================================================

def compute_kosmic_index(
    observations: np.ndarray,
    actions: np.ndarray,
    actions_B: Optional[np.ndarray] = None,
    normative_reference: Optional[callable] = None,
    history_len: int = 5,
) -> Dict:
    """
    Compute the complete 7D Kosmic K-Index.

    This is the main entry point for the Kosmic K-Index Framework.

    Args:
        observations: Agent observations [T, obs_dim]
        actions: Agent actions [T, act_dim]
        actions_B: Optional second agent actions for K_S
        normative_reference: Optional function for K_H
        history_len: History length for K_M

    Returns:
        Dictionary containing:
            - K_vector: Dict with all 7 components
            - K_sigma: Product composite score
            - K_geo: Geometric mean composite score
            - metadata: Additional information

    Example:
        >>> obs = np.random.randn(100, 8)
        >>> act = np.random.randn(100, 2)
        >>> result = compute_kosmic_index(obs, act)
        >>> print(result["K_vector"])
        {'K_R': 0.12, 'K_A': 0.08, 'K_I': 0.95, ...}
    """
    # Ensure arrays
    observations = np.atleast_2d(observations)
    actions = np.atleast_2d(actions)

    # Compute all components
    k_r = compute_k_reactivity(observations, actions)
    k_a = compute_k_agency(observations, actions)
    k_i = compute_k_integration(observations, actions)
    k_p = compute_k_predictive(observations, actions)
    k_m = compute_k_meta(observations, actions, history_len)
    k_h = compute_k_harmonic(observations, actions, normative_reference)

    # Social requires second agent
    k_s = None
    if actions_B is not None:
        actions_B = np.atleast_2d(actions_B)
        k_s = compute_k_social(actions, actions_B)

    # Build component list for composites
    components = [k_r, k_a, k_i, k_p, k_m, k_h]
    component_names = ["K_R", "K_A", "K_I", "K_P", "K_M", "K_H"]

    if k_s is not None:
        components.append(k_s)
        component_names.append("K_S")

    # Compute composites
    # Handle zeros gracefully
    nonzero_components = [c for c in components if c > 1e-10]

    if len(nonzero_components) == 0:
        k_sigma = 0.0
        k_geo = 0.0
    else:
        k_sigma = float(np.prod(components))
        k_geo = float(np.power(np.prod(nonzero_components),
                               1.0 / len(nonzero_components)))

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
        "metadata": {
            "n_samples": len(observations),
            "obs_dim": observations.shape[1] if observations.ndim > 1 else 1,
            "act_dim": actions.shape[1] if actions.ndim > 1 else 1,
            "has_social": k_s is not None,
            "history_len": history_len,
        }
    }


# =============================================================================
# Backwards Compatibility
# =============================================================================

def compute_k_index(observations: np.ndarray, actions: np.ndarray) -> float:
    """
    Original K-Index (now K_R).

    Provided for backwards compatibility with existing code.

    Args:
        observations: Array of shape [T, obs_dim]
        actions: Array of shape [T, act_dim]

    Returns:
        K value in range [0, 2]
    """
    return compute_k_reactivity(observations, actions)


# =============================================================================
# Utility Functions
# =============================================================================

def print_kosmic_report(result: Dict, name: str = "Agent") -> None:
    """Print a formatted report of Kosmic K-Index results."""
    print(f"\n{'='*60}")
    print(f"KOSMIC K-INDEX REPORT: {name}")
    print(f"{'='*60}")

    print("\n7D K-Vector:")
    for key, value in result["K_vector"].items():
        if value is not None:
            bar = "█" * int(value * 20) + "░" * (20 - int(value * 20))
            print(f"  {key:25s} {value:.4f} [{bar}]")
        else:
            print(f"  {key:25s} N/A (requires second agent)")

    print(f"\nComposite Scores:")
    print(f"  K_sigma (product):        {result['K_sigma']:.6f}")
    print(f"  K_geo (geometric mean):   {result['K_geo']:.4f}")

    print(f"\nMetadata:")
    for key, value in result["metadata"].items():
        print(f"  {key}: {value}")

    print(f"{'='*60}\n")


def compare_agents(results: List[Tuple[str, Dict]]) -> None:
    """Compare K-Index results across multiple agents."""
    print(f"\n{'='*80}")
    print("AGENT COMPARISON")
    print(f"{'='*80}")

    # Header
    names = [r[0] for r in results]
    print(f"{'Metric':25s}", end="")
    for name in names:
        print(f"{name:15s}", end="")
    print()
    print("-" * (25 + 15 * len(names)))

    # K components
    components = ["K_R (Reactivity)", "K_A (Agency)", "K_I (Integration)",
                  "K_P (Prediction)", "K_M (Meta)", "K_S (Social)",
                  "K_H (Harmonic)"]

    for comp in components:
        print(f"{comp:25s}", end="")
        for _, result in results:
            value = result["K_vector"].get(comp)
            if value is not None:
                print(f"{value:15.4f}", end="")
            else:
                print(f"{'N/A':15s}", end="")
        print()

    print("-" * (25 + 15 * len(names)))

    # Composites
    print(f"{'K_geo':25s}", end="")
    for _, result in results:
        print(f"{result['K_geo']:15.4f}", end="")
    print()

    print(f"{'='*80}\n")


# =============================================================================
# Self-Test
# =============================================================================

if __name__ == "__main__":
    print("Testing Kosmic K-Index Framework...")

    np.random.seed(42)

    # Test 1: Random agent
    print("\n--- Test 1: Random Agent ---")
    obs_random = np.random.randn(200, 8)
    act_random = np.random.randn(200, 2)
    result_random = compute_kosmic_index(obs_random, act_random)
    print_kosmic_report(result_random, "Random Agent")

    # Test 2: Reactive agent (action = f(observation))
    print("\n--- Test 2: Reactive Agent ---")
    obs_reactive = np.random.randn(200, 8)
    act_reactive = 0.5 * np.linalg.norm(obs_reactive, axis=1, keepdims=True) * np.ones((200, 2))
    act_reactive += 0.1 * np.random.randn(200, 2)
    result_reactive = compute_kosmic_index(obs_reactive, act_reactive)
    print_kosmic_report(result_reactive, "Reactive Agent")

    # Test 3: Predictive agent (observations follow actions)
    print("\n--- Test 3: Predictive Agent ---")
    obs_pred = np.zeros((200, 8))
    act_pred = np.random.randn(200, 2)
    for t in range(1, 200):
        obs_pred[t] = 0.8 * obs_pred[t-1] + 0.5 * np.tile(act_pred[t-1], 4) + 0.1 * np.random.randn(8)
    result_pred = compute_kosmic_index(obs_pred, act_pred)
    print_kosmic_report(result_pred, "Predictive Agent")

    # Compare all
    compare_agents([
        ("Random", result_random),
        ("Reactive", result_reactive),
        ("Predictive", result_pred),
    ])

    print("All tests completed!")
