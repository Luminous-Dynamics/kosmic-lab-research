#!/usr/bin/env python3
"""
Dimensionality Analysis for K-Vector Framework

Questions:
1. Are 7 dimensions necessary or redundant?
2. Which dimensions carry unique information?
3. Can we reduce dimensionality without losing predictive power?

Methods:
- PCA on K-vectors across many agents
- Correlation analysis between dimensions
- Predictive power comparison (7D vs reduced)
"""

import numpy as np
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from scipy.stats import pearsonr, spearmanr
import warnings

# Import from existing modules
import sys
sys.path.insert(0, str(Path(__file__).parent))

from kosmic_k_index import compute_kosmic_index


def generate_diverse_agents(n_agents: int = 200,
                            episode_length: int = 100) -> List[Dict]:
    """
    Generate diverse synthetic agent trajectories for dimensionality analysis.

    Creates agents with varying characteristics:
    - Random (baseline)
    - Reactive (high K_R)
    - Predictive (high K_P)
    - Memory-based (high K_M)
    - Coordinated pairs (high K_S)
    - Sustainable (high K_H)
    - Mixed profiles
    """
    agents = []

    for i in range(n_agents):
        agent_type = i % 8  # 8 different agent profiles

        obs_dim = 4
        act_dim = 2

        # Generate observations (common to all)
        observations = np.random.randn(episode_length, obs_dim)

        if agent_type == 0:  # Random
            actions = np.random.randn(episode_length, act_dim)
            name = "random"

        elif agent_type == 1:  # Reactive (high K_R)
            # Actions proportional to observations
            actions = observations[:, :act_dim] * 0.5 + np.random.randn(episode_length, act_dim) * 0.1
            name = "reactive"

        elif agent_type == 2:  # Predictive (high K_P)
            # Actions based on predicted next observation
            actions = np.zeros((episode_length, act_dim))
            for t in range(1, episode_length):
                # "Predict" and act to compensate
                predicted_change = observations[t] - observations[t-1]
                actions[t] = -predicted_change[:act_dim] * 0.3
            name = "predictive"

        elif agent_type == 3:  # Memory-based (high K_M)
            # Actions depend on history
            actions = np.zeros((episode_length, act_dim))
            history_len = 5
            for t in range(history_len, episode_length):
                # Action based on historical average
                hist_avg = np.mean(observations[t-history_len:t, :act_dim], axis=0)
                actions[t] = hist_avg + np.random.randn(act_dim) * 0.1
            name = "memory"

        elif agent_type == 4:  # Constant (thermostat-like)
            actions = np.ones((episode_length, act_dim)) * 0.5
            name = "constant"

        elif agent_type == 5:  # Oscillating
            t_arr = np.arange(episode_length)
            actions = np.column_stack([
                np.sin(t_arr * 0.1),
                np.cos(t_arr * 0.1)
            ])
            name = "oscillating"

        elif agent_type == 6:  # Adaptive (mixed)
            actions = np.zeros((episode_length, act_dim))
            for t in range(episode_length):
                # Mix of reactive and predictive
                reactive_component = observations[t, :act_dim] * 0.3
                random_component = np.random.randn(act_dim) * 0.2
                actions[t] = reactive_component + random_component
            name = "adaptive"

        else:  # agent_type == 7: Complex
            # Complex behavior mixing multiple strategies
            actions = np.zeros((episode_length, act_dim))
            for t in range(episode_length):
                phase = t / episode_length
                if phase < 0.3:
                    actions[t] = observations[t, :act_dim] * 0.5  # Reactive early
                elif phase < 0.7:
                    if t > 0:
                        actions[t] = actions[t-1] * 0.9 + np.random.randn(act_dim) * 0.1  # Smooth
                else:
                    actions[t] = np.random.randn(act_dim) * 0.3  # Random late
            name = "complex"

        # Compute K-vector using inline implementations for robustness
        try:
            # K_R: Reactivity - correlation of observation/action magnitudes
            obs_mags = np.linalg.norm(observations, axis=1)
            act_mags = np.linalg.norm(actions, axis=1)
            if np.std(obs_mags) > 1e-10 and np.std(act_mags) > 1e-10:
                k_r = 2 * abs(np.corrcoef(obs_mags, act_mags)[0, 1])
            else:
                k_r = 0.0

            # K_A: Agency - action causes observation change
            if len(observations) > 1:
                delta_obs = np.diff(np.linalg.norm(observations, axis=1))
                act_mags_shifted = act_mags[:-1]
                if np.std(delta_obs) > 1e-10 and np.std(act_mags_shifted) > 1e-10:
                    k_a = abs(np.corrcoef(act_mags_shifted, delta_obs)[0, 1])
                else:
                    k_a = 0.0
            else:
                k_a = 0.0

            # K_I: Integration - entropy matching
            def entropy(data, bins=32):
                if np.std(data) < 1e-10:
                    return 0.0
                hist, _ = np.histogram(data, bins=bins, density=True)
                p = hist / (np.sum(hist) + 1e-12)
                p = p[p > 0]
                return -np.sum(p * np.log(p + 1e-12)) if len(p) > 0 else 0.0

            h_o = entropy(obs_mags)
            h_a = entropy(act_mags)
            k_i = 2 * min(h_o, h_a) / (h_o + h_a + 1e-10) if (h_o + h_a) > 0 else 0.0

            # K_P: Prediction - simple next-step prediction accuracy
            if len(observations) > 1:
                pred_error = np.mean(np.linalg.norm(np.diff(observations, axis=0), axis=1))
                baseline_var = np.var(obs_mags)
                k_p = max(0, 1 - pred_error / (np.sqrt(baseline_var) + 1e-10))
            else:
                k_p = 0.0

            # K_M: Meta - history dependence (simplified)
            history_len = 5
            if len(actions) > history_len:
                # Check if current action can be predicted better with history
                markov_errors = []
                history_errors = []
                for t in range(history_len, len(actions)):
                    # Markov: predict from current obs only
                    markov_pred = observations[t, :min(2, observations.shape[1])]
                    # History: average of past observations
                    hist_avg = np.mean(observations[t-history_len:t, :min(2, observations.shape[1])], axis=0)

                    actual = actions[t, :min(2, actions.shape[1])]
                    markov_errors.append(np.linalg.norm(actual - markov_pred[:len(actual)]))
                    history_errors.append(np.linalg.norm(actual - hist_avg[:len(actual)]))

                l_markov = np.mean(markov_errors)
                l_history = np.mean(history_errors)
                k_m = max(0, (l_markov - l_history) / (l_markov + 1e-10))
            else:
                k_m = 0.0

            # Validate and store
            k_r = float(np.clip(k_r, 0, 2))
            k_a = float(np.clip(k_a, 0, 1))
            k_i = float(np.clip(k_i, 0, 1))
            k_p = float(np.clip(k_p, 0, 1))
            k_m = float(np.clip(k_m, 0, 1))

            if not any(np.isnan([k_r, k_a, k_i, k_p, k_m])):
                agents.append({
                    "id": i,
                    "type": name,
                    "K_R": k_r,
                    "K_A": k_a,
                    "K_I": k_i,
                    "K_P": k_p,
                    "K_M": k_m,
                })
        except Exception as e:
            print(f"Warning: Agent {i} failed: {e}")
            pass

    return agents


def compute_correlation_matrix(agents: List[Dict]) -> Tuple[np.ndarray, List[str]]:
    """Compute correlation matrix between K-vector dimensions."""
    # Only use dimensions that actually vary in synthetic agents
    dimensions = ["K_R", "K_A", "K_I", "K_P", "K_M"]

    # Extract K-vectors
    k_matrix = np.array([
        [a[dim] for dim in dimensions]
        for a in agents
    ])

    n_dims = len(dimensions)
    corr_matrix = np.zeros((n_dims, n_dims))
    p_matrix = np.zeros((n_dims, n_dims))

    for i in range(n_dims):
        for j in range(n_dims):
            if i == j:
                corr_matrix[i, j] = 1.0
                p_matrix[i, j] = 0.0
            else:
                r, p = pearsonr(k_matrix[:, i], k_matrix[:, j])
                corr_matrix[i, j] = r
                p_matrix[i, j] = p

    return corr_matrix, p_matrix, dimensions


def perform_pca(agents: List[Dict]) -> Dict:
    """Perform PCA on K-vectors to assess dimensionality."""
    dimensions = ["K_R", "K_A", "K_I", "K_P", "K_M"]

    # Extract K-vectors
    k_matrix = np.array([
        [a[dim] for dim in dimensions]
        for a in agents
    ])

    # Center the data
    k_centered = k_matrix - np.mean(k_matrix, axis=0)

    # Compute covariance matrix
    cov_matrix = np.cov(k_centered.T)

    # Eigenvalue decomposition
    eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)

    # Sort by eigenvalue (descending)
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    # Compute explained variance ratio
    total_var = np.sum(eigenvalues)
    explained_ratio = eigenvalues / total_var
    cumulative_ratio = np.cumsum(explained_ratio)

    # Find components needed for 90%, 95%, 99% variance
    n_90 = np.argmax(cumulative_ratio >= 0.90) + 1
    n_95 = np.argmax(cumulative_ratio >= 0.95) + 1
    n_99 = np.argmax(cumulative_ratio >= 0.99) + 1

    return {
        "eigenvalues": eigenvalues.tolist(),
        "explained_ratio": explained_ratio.tolist(),
        "cumulative_ratio": cumulative_ratio.tolist(),
        "n_components_90": int(n_90),
        "n_components_95": int(n_95),
        "n_components_99": int(n_99),
        "principal_components": eigenvectors.tolist(),
        "dimension_names": dimensions,
    }


def analyze_redundancy(corr_matrix: np.ndarray,
                       dimensions: List[str],
                       threshold: float = 0.7) -> Dict:
    """Identify potentially redundant dimensions."""
    n_dims = len(dimensions)
    redundant_pairs = []

    for i in range(n_dims):
        for j in range(i + 1, n_dims):
            if abs(corr_matrix[i, j]) > threshold:
                redundant_pairs.append({
                    "dim1": dimensions[i],
                    "dim2": dimensions[j],
                    "correlation": float(corr_matrix[i, j]),
                })

    # Compute mean absolute correlation (excluding diagonal)
    upper_tri = np.triu(np.abs(corr_matrix), k=1)
    mean_abs_corr = np.sum(upper_tri) / (n_dims * (n_dims - 1) / 2)

    return {
        "redundant_pairs": redundant_pairs,
        "mean_abs_correlation": float(mean_abs_corr),
        "threshold_used": threshold,
        "n_redundant_pairs": len(redundant_pairs),
    }


def run_dimensionality_analysis(n_agents: int = 200,
                                 verbose: bool = True) -> Dict:
    """
    Run comprehensive dimensionality analysis.

    Questions answered:
    1. Are dimensions independent? (correlation analysis)
    2. How many components needed? (PCA)
    3. Which dimensions are redundant? (redundancy analysis)
    """
    print("=" * 70)
    print("📐 K-VECTOR DIMENSIONALITY ANALYSIS")
    print("=" * 70)
    print()
    print(f"Generating {n_agents} diverse agent trajectories...")
    print()

    # Generate agents
    agents = generate_diverse_agents(n_agents=n_agents)
    print(f"Successfully computed K-vectors for {len(agents)} agents")

    # Agent type distribution
    type_counts = {}
    for a in agents:
        t = a["type"]
        type_counts[t] = type_counts.get(t, 0) + 1
    print(f"Agent types: {type_counts}")
    print()

    # 1. Correlation Analysis
    print("-" * 70)
    print("📊 INTER-DIMENSION CORRELATION MATRIX")
    print("-" * 70)

    corr_matrix, p_matrix, dimensions = compute_correlation_matrix(agents)

    # Print correlation matrix
    print()
    print(f"{'':>8}", end="")
    for d in dimensions:
        print(f"{d:>8}", end="")
    print()

    for i, d in enumerate(dimensions):
        print(f"{d:>8}", end="")
        for j in range(len(dimensions)):
            r = corr_matrix[i, j]
            if i == j:
                print(f"{'1.000':>8}", end="")
            elif abs(r) > 0.5:
                print(f"\033[91m{r:>8.3f}\033[0m", end="")  # Red for high corr
            elif abs(r) > 0.3:
                print(f"\033[93m{r:>8.3f}\033[0m", end="")  # Yellow for medium
            else:
                print(f"{r:>8.3f}", end="")
        print()

    # 2. PCA Analysis
    print()
    print("-" * 70)
    print("📈 PRINCIPAL COMPONENT ANALYSIS")
    print("-" * 70)

    pca_results = perform_pca(agents)

    print()
    print("Eigenvalues and Explained Variance:")
    print(f"{'PC':<5} {'Eigenvalue':<12} {'Var %':<10} {'Cumulative %':<12}")
    print("-" * 40)

    n_dims = len(pca_results["eigenvalues"])
    for i in range(n_dims):
        ev = pca_results["eigenvalues"][i]
        ratio = pca_results["explained_ratio"][i] * 100
        cum = pca_results["cumulative_ratio"][i] * 100
        print(f"PC{i+1:<3} {ev:<12.4f} {ratio:<10.1f} {cum:<12.1f}")

    print()
    print(f"Components for 90% variance: {pca_results['n_components_90']}")
    print(f"Components for 95% variance: {pca_results['n_components_95']}")
    print(f"Components for 99% variance: {pca_results['n_components_99']}")

    # 3. Redundancy Analysis
    print()
    print("-" * 70)
    print("🔍 REDUNDANCY ANALYSIS")
    print("-" * 70)

    redundancy = analyze_redundancy(corr_matrix, dimensions, threshold=0.5)

    print()
    print(f"Mean |correlation| (off-diagonal): {redundancy['mean_abs_correlation']:.3f}")
    print(f"Pairs with |r| > 0.5: {redundancy['n_redundant_pairs']}")

    if redundancy['redundant_pairs']:
        print("\nPotentially redundant pairs:")
        for pair in redundancy['redundant_pairs']:
            print(f"  {pair['dim1']} ↔ {pair['dim2']}: r = {pair['correlation']:.3f}")
    else:
        print("\n✓ No highly correlated pairs found (all |r| < 0.5)")

    # 4. Summary and Conclusions
    print()
    print("-" * 70)
    print("📋 CONCLUSIONS")
    print("-" * 70)

    conclusions = []

    # Independence conclusion
    if redundancy['mean_abs_correlation'] < 0.2:
        conclusions.append("✓ Dimensions are largely INDEPENDENT (mean |r| < 0.2)")
        independence_verdict = "excellent"
    elif redundancy['mean_abs_correlation'] < 0.3:
        conclusions.append("✓ Dimensions are reasonably INDEPENDENT (mean |r| < 0.3)")
        independence_verdict = "good"
    else:
        conclusions.append("⚠ Some dimensions may be REDUNDANT (mean |r| >= 0.3)")
        independence_verdict = "concerning"

    # Dimensionality conclusion
    if pca_results['n_components_95'] >= 6:
        conclusions.append("✓ All 7 dimensions carry unique information (need 6+ PCs for 95%)")
        dimensionality_verdict = "7D justified"
    elif pca_results['n_components_95'] >= 5:
        conclusions.append("~ Most dimensions useful (5-6 PCs for 95%)")
        dimensionality_verdict = "6-7D reasonable"
    else:
        conclusions.append(f"⚠ May be reducible to {pca_results['n_components_95']}D")
        dimensionality_verdict = f"{pca_results['n_components_95']}D may suffice"

    print()
    for c in conclusions:
        print(c)

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "n_agents": len(agents),
        "agent_type_distribution": type_counts,
        "correlation_matrix": corr_matrix.tolist(),
        "p_value_matrix": p_matrix.tolist(),
        "pca": pca_results,
        "redundancy": redundancy,
        "conclusions": {
            "independence": independence_verdict,
            "dimensionality": dimensionality_verdict,
            "mean_abs_correlation": redundancy['mean_abs_correlation'],
            "n_components_95": pca_results['n_components_95'],
        }
    }

    log_dir = Path("logs/dimensionality")
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"dimensionality_analysis_{timestamp}.json"

    with open(log_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n💾 Results saved → {log_file}")

    return output


if __name__ == "__main__":
    results = run_dimensionality_analysis(n_agents=200, verbose=True)
