#!/usr/bin/env python3
"""
Real Agent Dimensionality Analysis

Critical validation: Test K-vector dimension independence on REAL trained agents
from Track L experiments, not synthetic trajectories.

This addresses the concern that synthetic agents showed K_R-K_A correlation of 0.949,
while the paper claims mean |r| = 0.109 independence.
"""

import numpy as np
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from scipy.stats import pearsonr
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "paper-8-unified-indices"))


def load_track_l_results() -> List[Dict]:
    """Load K-vector results from Track L experiments."""
    log_dir = Path("logs/track_l")

    results = []

    # Look for L6 results (comprehensive K-vector validation)
    for log_file in sorted(log_dir.glob("track_l_l6_*.json")):
        try:
            with open(log_file) as f:
                data = json.load(f)

            # Extract per-agent K-vectors from agent_results array
            if "agent_results" in data:
                for agent in data["agent_results"]:
                    results.append({
                        "type": agent.get("agent_type", "unknown"),
                        "K_R": agent.get("K_R", 0),
                        "K_A": agent.get("K_A", 0),
                        "K_I": agent.get("K_I", 0),
                        "K_P": agent.get("K_P", 0),
                        "K_M": agent.get("K_M", 0),
                        "K_S": agent.get("K_S", 0),
                        "K_H": agent.get("K_H", 0),
                        "reward": agent.get("total_reward", 0),
                        "environment": data.get("environment", "unknown"),
                    })
        except Exception as e:
            print(f"Warning: Could not load {log_file}: {e}")

    # Also load L4 results
    for log_file in sorted(log_dir.glob("track_l_l4*.json")):
        try:
            with open(log_file) as f:
                data = json.load(f)

            if "agent_results" in data:
                for agent in data["agent_results"]:
                    results.append({
                        "type": agent.get("agent_type", "unknown"),
                        "K_R": agent.get("K_R", 0),
                        "K_A": agent.get("K_A", 0),
                        "K_I": agent.get("K_I", 0),
                        "K_P": agent.get("K_P", 0),
                        "K_M": agent.get("K_M", 0),
                        "K_S": agent.get("K_S", 0),
                        "K_H": agent.get("K_H", 0),
                        "reward": agent.get("total_reward", 0),
                        "environment": data.get("environment", "unknown"),
                    })
        except Exception as e:
            print(f"Warning: Could not load {log_file}: {e}")

    # Also load L1 results
    for log_file in sorted(log_dir.glob("track_l_l1_*.json")):
        try:
            with open(log_file) as f:
                data = json.load(f)

            if "agent_results" in data:
                for agent in data["agent_results"]:
                    results.append({
                        "type": agent.get("agent_type", "unknown"),
                        "K_R": agent.get("K_R", 0),
                        "K_A": agent.get("K_A", 0),
                        "K_I": agent.get("K_I", 0),
                        "K_P": agent.get("K_P", 0),
                        "K_M": agent.get("K_M", 0),
                        "K_S": agent.get("K_S", 0),
                        "K_H": agent.get("K_H", 0),
                        "reward": agent.get("total_reward", 0),
                        "environment": data.get("environment", "unknown"),
                    })
        except Exception as e:
            print(f"Warning: Could not load {log_file}: {e}")

    return results


def run_environment_experiments(n_episodes: int = 30) -> List[Dict]:
    """
    Run fresh experiments across environments to get K-vectors.
    """
    from coordination_environment import CoordinationEnvironment

    results = []

    # Agent types to test
    agent_configs = [
        ("random", lambda obs: np.random.randn(2)),
        ("reactive", lambda obs: obs[:2] * 0.5 if len(obs) >= 2 else np.zeros(2)),
        ("linear", lambda obs: np.tanh(obs[:2]) if len(obs) >= 2 else np.zeros(2)),
    ]

    for agent_name, agent_policy in agent_configs:
        print(f"  Testing {agent_name} agent...")

        for episode in range(n_episodes):
            env = CoordinationEnvironment()
            obs = env.reset()

            observations = [obs.copy()]
            actions = []
            total_reward = 0

            for step in range(100):
                action = np.array(agent_policy(obs))
                actions.append(action.copy())

                obs, reward, done, _ = env.step(action)
                observations.append(obs.copy())
                total_reward += reward

                if done:
                    break

            # Compute K-vector
            obs_arr = np.array(observations[:-1])
            act_arr = np.array(actions)

            if len(obs_arr) > 10 and len(act_arr) > 10:
                k_vector = compute_k_vector(obs_arr, act_arr)
                k_vector["type"] = agent_name
                k_vector["reward"] = total_reward
                k_vector["episode"] = episode
                results.append(k_vector)

    return results


def compute_k_vector(observations: np.ndarray, actions: np.ndarray) -> Dict:
    """Compute full K-vector for a trajectory."""

    obs_mags = np.linalg.norm(observations, axis=1)
    act_mags = np.linalg.norm(actions, axis=1)

    # K_R: Reactivity
    if np.std(obs_mags) > 1e-10 and np.std(act_mags) > 1e-10:
        corr = np.corrcoef(obs_mags, act_mags)[0, 1]
        k_r = 2 * abs(corr) if not np.isnan(corr) else 0.0
    else:
        k_r = 0.0

    # K_A: Agency
    if len(observations) > 1:
        delta_obs = np.diff(obs_mags)
        if np.std(delta_obs) > 1e-10 and np.std(act_mags[:-1]) > 1e-10:
            corr = np.corrcoef(act_mags[:-1], delta_obs)[0, 1]
            k_a = abs(corr) if not np.isnan(corr) else 0.0
        else:
            k_a = 0.0
    else:
        k_a = 0.0

    # K_I: Integration (entropy matching)
    def entropy(data, bins=32):
        if len(data) < 2 or np.std(data) < 1e-10:
            return 0.0
        hist, _ = np.histogram(data, bins=bins, density=True)
        p = hist / (np.sum(hist) + 1e-12)
        p = p[p > 0]
        return -np.sum(p * np.log(p + 1e-12)) if len(p) > 0 else 0.0

    h_o = entropy(obs_mags)
    h_a = entropy(act_mags)
    k_i = 2 * min(h_o, h_a) / (h_o + h_a + 1e-10) if (h_o + h_a) > 0 else 0.0

    # K_P: Prediction accuracy (using autoregressive model)
    if len(observations) > 2:
        # Simple: how predictable is next observation from current?
        pred_errors = []
        for t in range(1, len(observations)):
            # Naive prediction: next = current
            pred = observations[t-1]
            actual = observations[t]
            pred_errors.append(np.linalg.norm(actual - pred))

        mean_error = np.mean(pred_errors)
        baseline = np.std(obs_mags) + 1e-10
        k_p = max(0, 1 - mean_error / (2 * baseline))
    else:
        k_p = 0.0

    # K_M: Memory utilization
    history_len = 5
    if len(actions) > history_len + 5:
        markov_errors = []
        history_errors = []

        for t in range(history_len, len(actions)):
            # Markov: predict action from current obs
            markov_pred = observations[t][:actions.shape[1]] if observations.shape[1] >= actions.shape[1] else np.zeros(actions.shape[1])

            # History: predict from average of past
            hist_obs = observations[t-history_len:t]
            hist_avg = np.mean(hist_obs[:, :actions.shape[1]], axis=0) if hist_obs.shape[1] >= actions.shape[1] else np.zeros(actions.shape[1])

            actual = actions[t]
            markov_errors.append(np.linalg.norm(actual - markov_pred[:len(actual)]))
            history_errors.append(np.linalg.norm(actual - hist_avg[:len(actual)]))

        l_markov = np.mean(markov_errors)
        l_history = np.mean(history_errors)
        k_m = max(0, min(1, (l_markov - l_history) / (l_markov + 1e-10)))
    else:
        k_m = 0.0

    return {
        "K_R": float(np.clip(k_r, 0, 2)),
        "K_A": float(np.clip(k_a, 0, 1)),
        "K_I": float(np.clip(k_i, 0, 1)),
        "K_P": float(np.clip(k_p, 0, 1)),
        "K_M": float(np.clip(k_m, 0, 1)),
    }


def analyze_dimension_independence(results: List[Dict]) -> Dict:
    """
    Analyze independence between K-vector dimensions.
    """
    dimensions = ["K_R", "K_A", "K_I", "K_P", "K_M", "K_S", "K_H"]

    # Extract values
    k_matrix = []
    for r in results:
        row = [r.get(dim, 0) for dim in dimensions]
        if not any(np.isnan(row)):
            k_matrix.append(row)

    if len(k_matrix) < 10:
        return {"error": "Not enough valid data points"}

    k_matrix = np.array(k_matrix)
    n_dims = len(dimensions)

    # Correlation matrix
    corr_matrix = np.zeros((n_dims, n_dims))
    p_matrix = np.zeros((n_dims, n_dims))

    for i in range(n_dims):
        for j in range(n_dims):
            if i == j:
                corr_matrix[i, j] = 1.0
                p_matrix[i, j] = 0.0
            else:
                col_i = k_matrix[:, i]
                col_j = k_matrix[:, j]

                # Check for constant columns
                if np.std(col_i) < 1e-10 or np.std(col_j) < 1e-10:
                    corr_matrix[i, j] = np.nan
                    p_matrix[i, j] = np.nan
                else:
                    r, p = pearsonr(col_i, col_j)
                    corr_matrix[i, j] = r
                    p_matrix[i, j] = p

    # Mean absolute correlation (excluding diagonal and NaN)
    off_diag = []
    for i in range(n_dims):
        for j in range(i+1, n_dims):
            if not np.isnan(corr_matrix[i, j]):
                off_diag.append(abs(corr_matrix[i, j]))

    mean_abs_corr = np.mean(off_diag) if off_diag else np.nan

    # PCA
    k_centered = k_matrix - np.mean(k_matrix, axis=0)

    # Handle constant columns
    for i in range(k_centered.shape[1]):
        if np.std(k_centered[:, i]) < 1e-10:
            k_centered[:, i] = np.random.randn(len(k_centered)) * 1e-6

    cov = np.cov(k_centered.T)
    eigenvalues, _ = np.linalg.eigh(cov)
    eigenvalues = np.sort(eigenvalues)[::-1]

    total_var = np.sum(eigenvalues)
    explained = eigenvalues / total_var if total_var > 0 else eigenvalues
    cumulative = np.cumsum(explained)

    n_95 = np.argmax(cumulative >= 0.95) + 1 if any(cumulative >= 0.95) else len(dimensions)

    return {
        "n_samples": len(k_matrix),
        "dimensions": dimensions,
        "correlation_matrix": corr_matrix.tolist(),
        "p_value_matrix": p_matrix.tolist(),
        "mean_abs_correlation": float(mean_abs_corr) if not np.isnan(mean_abs_corr) else None,
        "eigenvalues": eigenvalues.tolist(),
        "explained_variance": explained.tolist(),
        "cumulative_variance": cumulative.tolist(),
        "n_components_95": int(n_95),
        "dimension_means": np.mean(k_matrix, axis=0).tolist(),
        "dimension_stds": np.std(k_matrix, axis=0).tolist(),
    }


def run_real_agent_analysis(verbose: bool = True) -> Dict:
    """
    Run comprehensive analysis on real trained agents.
    """
    print("=" * 70)
    print("📊 REAL AGENT K-VECTOR DIMENSIONALITY ANALYSIS")
    print("=" * 70)
    print()
    print("Purpose: Validate dimension independence on REAL trained agents")
    print("         (not synthetic trajectories)")
    print()

    # Try to load existing Track L results
    print("Loading Track L experimental results...")
    results = load_track_l_results()

    print(f"Loaded {len(results)} results from Track L logs.")

    print(f"Total data points: {len(results)}")

    if len(results) < 10:
        print("ERROR: Not enough data for analysis")
        return {"error": "Insufficient data"}

    # Analyze by agent type
    agent_types = set(r.get("type", "unknown") for r in results)
    print(f"Agent types: {agent_types}")
    print()

    # Overall analysis
    print("-" * 70)
    print("📈 DIMENSION INDEPENDENCE ANALYSIS")
    print("-" * 70)

    analysis = analyze_dimension_independence(results)

    if "error" in analysis:
        print(f"Error: {analysis['error']}")
        return analysis

    # Print correlation matrix
    print()
    print("Correlation Matrix:")
    dims = analysis["dimensions"]
    corr = np.array(analysis["correlation_matrix"])

    print(f"{'':>8}", end="")
    for d in dims:
        print(f"{d:>8}", end="")
    print()

    for i, d in enumerate(dims):
        print(f"{d:>8}", end="")
        for j in range(len(dims)):
            r = corr[i, j]
            if i == j:
                print(f"{'1.000':>8}", end="")
            elif np.isnan(r):
                print(f"{'nan':>8}", end="")
            elif abs(r) > 0.5:
                print(f"\033[91m{r:>8.3f}\033[0m", end="")  # Red
            elif abs(r) > 0.3:
                print(f"\033[93m{r:>8.3f}\033[0m", end="")  # Yellow
            else:
                print(f"\033[92m{r:>8.3f}\033[0m", end="")  # Green
        print()

    print()
    print(f"Mean |correlation| (off-diagonal): {analysis['mean_abs_correlation']:.3f}"
          if analysis['mean_abs_correlation'] else "Mean |correlation|: N/A")
    print(f"Components for 95% variance: {analysis['n_components_95']}")

    # Dimension statistics
    print()
    print("Dimension Statistics:")
    print(f"{'Dim':<8} {'Mean':>10} {'Std':>10}")
    print("-" * 30)
    for i, d in enumerate(dims):
        print(f"{d:<8} {analysis['dimension_means'][i]:>10.3f} {analysis['dimension_stds'][i]:>10.3f}")

    # Conclusions
    print()
    print("-" * 70)
    print("📋 CONCLUSIONS")
    print("-" * 70)

    mean_corr = analysis['mean_abs_correlation']
    if mean_corr is not None:
        if mean_corr < 0.2:
            print("✓ Dimensions are INDEPENDENT (mean |r| < 0.2)")
            print("  Paper claim of orthogonality SUPPORTED")
        elif mean_corr < 0.3:
            print("~ Dimensions are REASONABLY independent (mean |r| < 0.3)")
            print("  Paper claim partially supported")
        else:
            print("⚠ Dimensions show CORRELATION (mean |r| >= 0.3)")
            print("  Paper claim needs revision")

    n_95 = analysis['n_components_95']
    if n_95 >= 4:
        print(f"✓ {n_95}D needed for 95% variance - multidimensionality justified")
    else:
        print(f"⚠ Only {n_95}D needed for 95% variance - may be reducible")

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "n_samples": len(results),
        "agent_types": list(agent_types),
        "analysis": analysis,
    }

    log_dir = Path("logs/dimensionality")
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"real_agent_dimensionality_{timestamp}.json"

    with open(log_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n💾 Results saved → {log_file}")

    return output


if __name__ == "__main__":
    results = run_real_agent_analysis(verbose=True)
