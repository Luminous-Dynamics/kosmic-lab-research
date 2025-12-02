#!/usr/bin/env python3
"""
Environment-Dependent Independence Analysis

Investigates why dimension independence varies by environment:
- Commons: mean |r| = 0.252 (good)
- Delayed: mean |r| = 0.251 (good)
- Simple: mean |r| = 0.401 (moderate)
- Unknown: mean |r| = 0.533 (high)

Hypothesis: Independence is better in environments that require
diverse behavioral strategies (sustainability, memory, etc.)
"""

import numpy as np
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from scipy.stats import pearsonr
from collections import defaultdict


def load_all_results() -> List[Dict]:
    """Load all Track L results with environment labels."""
    log_dir = Path("logs/track_l")
    results = []

    for pattern in ["track_l_l6_*.json", "track_l_l4*.json", "track_l_l1_*.json"]:
        for log_file in sorted(log_dir.glob(pattern)):
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


def compute_environment_stats(results: List[Dict], env_name: str) -> Dict:
    """Compute correlation statistics for a specific environment."""
    env_data = [r for r in results if r["environment"] == env_name]

    if len(env_data) < 10:
        return {"n": len(env_data), "error": "Insufficient data"}

    dimensions = ["K_R", "K_A", "K_I", "K_P", "K_M", "K_H"]

    # Build matrix
    k_matrix = []
    for r in env_data:
        row = [r.get(dim, 0) for dim in dimensions]
        if not any(np.isnan(row)):
            k_matrix.append(row)

    k_matrix = np.array(k_matrix)
    n_dims = len(dimensions)

    # Correlation matrix
    corr_matrix = np.zeros((n_dims, n_dims))
    for i in range(n_dims):
        for j in range(n_dims):
            if i == j:
                corr_matrix[i, j] = 1.0
            else:
                col_i = k_matrix[:, i]
                col_j = k_matrix[:, j]
                if np.std(col_i) > 1e-10 and np.std(col_j) > 1e-10:
                    r, _ = pearsonr(col_i, col_j)
                    corr_matrix[i, j] = r if not np.isnan(r) else 0
                else:
                    corr_matrix[i, j] = np.nan

    # Mean absolute off-diagonal
    off_diag = []
    for i in range(n_dims):
        for j in range(i+1, n_dims):
            if not np.isnan(corr_matrix[i, j]):
                off_diag.append(abs(corr_matrix[i, j]))

    mean_abs_corr = np.mean(off_diag) if off_diag else np.nan

    # Dimension means and stds
    dim_stats = {}
    for i, dim in enumerate(dimensions):
        values = k_matrix[:, i]
        dim_stats[dim] = {
            "mean": float(np.mean(values)),
            "std": float(np.std(values)),
        }

    # Reward statistics
    rewards = [r["reward"] for r in env_data]

    return {
        "n": len(k_matrix),
        "mean_abs_correlation": float(mean_abs_corr) if not np.isnan(mean_abs_corr) else None,
        "correlation_matrix": corr_matrix.tolist(),
        "dimensions": dimensions,
        "dimension_stats": dim_stats,
        "reward_mean": float(np.mean(rewards)),
        "reward_std": float(np.std(rewards)),
    }


def analyze_environment_characteristics(stats: Dict, env_name: str) -> Dict:
    """Analyze what makes an environment produce independent dimensions."""
    characteristics = {
        "requires_memory": False,
        "requires_sustainability": False,
        "has_delayed_reward": False,
        "behavioral_diversity": 0.0,
        "dimension_spread": 0.0,
    }

    if "dimension_stats" in stats:
        # Behavioral diversity: variance across dimension means
        means = [stats["dimension_stats"][d]["mean"] for d in ["K_R", "K_A", "K_I", "K_P", "K_M", "K_H"]]
        characteristics["behavioral_diversity"] = float(np.std(means))

        # Dimension spread: average std across dimensions
        stds = [stats["dimension_stats"][d]["std"] for d in ["K_R", "K_A", "K_I", "K_P", "K_M", "K_H"]]
        characteristics["dimension_spread"] = float(np.mean(stds))

        # Infer environment properties
        if stats["dimension_stats"]["K_M"]["std"] > 0.02:
            characteristics["requires_memory"] = True

        if stats["dimension_stats"]["K_H"]["std"] > 0.1:
            characteristics["requires_sustainability"] = True

    # Known environment characteristics
    if env_name == "commons":
        characteristics["requires_sustainability"] = True
        characteristics["has_delayed_reward"] = True
    elif env_name == "delayed":
        characteristics["requires_memory"] = True
        characteristics["has_delayed_reward"] = True
    elif env_name == "simple":
        pass  # Baseline
    elif env_name == "coordination":
        characteristics["requires_memory"] = True

    return characteristics


def run_environment_independence_analysis():
    """Run comprehensive environment independence analysis."""
    print("=" * 70)
    print("📊 ENVIRONMENT-DEPENDENT INDEPENDENCE ANALYSIS")
    print("=" * 70)
    print()
    print("Investigating why dimension independence varies by environment")
    print()

    results = load_all_results()
    print(f"Loaded {len(results)} total data points")

    # Group by environment
    envs = set(r["environment"] for r in results)
    print(f"Environments found: {envs}")
    print()

    env_analysis = {}

    print("-" * 70)
    print("📈 CORRELATION BY ENVIRONMENT")
    print("-" * 70)
    print()
    print(f"{'Environment':<15} {'N':>6} {'Mean |r|':>10} {'Dim Spread':>12} {'Reward μ':>10}")
    print("-" * 60)

    for env in sorted(envs):
        stats = compute_environment_stats(results, env)
        characteristics = analyze_environment_characteristics(stats, env)

        env_analysis[env] = {
            "stats": stats,
            "characteristics": characteristics,
        }

        if stats.get("mean_abs_correlation") is not None:
            print(f"{env:<15} {stats['n']:>6} {stats['mean_abs_correlation']:>10.3f} "
                  f"{characteristics['dimension_spread']:>12.3f} {stats['reward_mean']:>10.2f}")
        else:
            print(f"{env:<15} {stats.get('n', 0):>6} {'N/A':>10} {'N/A':>12} {'N/A':>10}")

    # Analyze correlation vs characteristics
    print()
    print("-" * 70)
    print("📊 CORRELATION PREDICTORS")
    print("-" * 70)
    print()

    # Collect data for regression-like analysis
    mean_corrs = []
    dim_spreads = []
    behavioral_divs = []
    requires_memory = []
    requires_sustain = []

    for env, data in env_analysis.items():
        if data["stats"].get("mean_abs_correlation") is not None:
            mean_corrs.append(data["stats"]["mean_abs_correlation"])
            dim_spreads.append(data["characteristics"]["dimension_spread"])
            behavioral_divs.append(data["characteristics"]["behavioral_diversity"])
            requires_memory.append(1 if data["characteristics"]["requires_memory"] else 0)
            requires_sustain.append(1 if data["characteristics"]["requires_sustainability"] else 0)

    if len(mean_corrs) >= 3:
        # Correlation between mean |r| and characteristics
        print("Factors associated with LOWER dimension correlation (more independence):")
        print()

        if len(set(dim_spreads)) > 1:
            r, p = pearsonr(mean_corrs, dim_spreads)
            direction = "↑ spread → ↓ correlation (GOOD)" if r < 0 else "↑ spread → ↑ correlation"
            print(f"  Dimension spread: r = {r:+.3f}, p = {p:.4f}")
            print(f"    {direction}")

        if len(set(behavioral_divs)) > 1:
            r, p = pearsonr(mean_corrs, behavioral_divs)
            direction = "↑ diversity → ↓ correlation (GOOD)" if r < 0 else "↑ diversity → ↑ correlation"
            print(f"  Behavioral diversity: r = {r:+.3f}, p = {p:.4f}")
            print(f"    {direction}")

        if len(set(requires_memory)) > 1:
            memory_corrs = [c for c, m in zip(mean_corrs, requires_memory) if m == 1]
            no_memory_corrs = [c for c, m in zip(mean_corrs, requires_memory) if m == 0]
            if memory_corrs and no_memory_corrs:
                print(f"  Memory requirement: memory envs = {np.mean(memory_corrs):.3f}, "
                      f"no-memory = {np.mean(no_memory_corrs):.3f}")
                if np.mean(memory_corrs) < np.mean(no_memory_corrs):
                    print("    Memory environments show BETTER independence")

    # Per-environment detailed breakdown
    print()
    print("-" * 70)
    print("📋 DETAILED ENVIRONMENT BREAKDOWN")
    print("-" * 70)

    for env in sorted(envs):
        data = env_analysis[env]
        stats = data["stats"]

        if stats.get("mean_abs_correlation") is None:
            continue

        print(f"\n{env.upper()} (n={stats['n']}):")
        print(f"  Mean |r|: {stats['mean_abs_correlation']:.3f}")

        # Top correlations
        if "correlation_matrix" in stats:
            matrix = np.array(stats["correlation_matrix"])
            dims = stats["dimensions"]
            pairs = []
            for i in range(len(dims)):
                for j in range(i+1, len(dims)):
                    if not np.isnan(matrix[i, j]):
                        pairs.append((dims[i], dims[j], matrix[i, j]))
            pairs.sort(key=lambda x: -abs(x[2]))

            print("  Top correlations:")
            for d1, d2, r in pairs[:3]:
                status = "⚠️" if abs(r) > 0.5 else "✅" if abs(r) < 0.3 else "~"
                print(f"    {d1}-{d2}: r = {r:+.3f} {status}")

        print(f"  Characteristics:")
        chars = data["characteristics"]
        print(f"    Requires memory: {chars['requires_memory']}")
        print(f"    Requires sustainability: {chars['requires_sustainability']}")
        print(f"    Dimension spread: {chars['dimension_spread']:.3f}")

    # Conclusions
    print()
    print("-" * 70)
    print("📋 CONCLUSIONS")
    print("-" * 70)
    print()

    # Rank environments by independence
    ranked = sorted(
        [(env, data["stats"]["mean_abs_correlation"])
         for env, data in env_analysis.items()
         if data["stats"].get("mean_abs_correlation") is not None],
        key=lambda x: x[1]
    )

    print("Environments ranked by independence (lower = better):")
    for i, (env, corr) in enumerate(ranked, 1):
        status = "✅ Good" if corr < 0.3 else "⚠️ High" if corr > 0.4 else "~ Moderate"
        print(f"  {i}. {env}: mean |r| = {corr:.3f} {status}")

    if ranked:
        best_env = ranked[0][0]
        worst_env = ranked[-1][0]

        print()
        print(f"Best for independence: {best_env}")
        print(f"Worst for independence: {worst_env}")

        best_chars = env_analysis[best_env]["characteristics"]
        worst_chars = env_analysis[worst_env]["characteristics"]

        if best_chars["requires_sustainability"] and not worst_chars["requires_sustainability"]:
            print("  → Sustainability requirement improves independence")
        if best_chars["requires_memory"] and not worst_chars["requires_memory"]:
            print("  → Memory requirement improves independence")

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "n_total": len(results),
        "environments": {
            env: {
                "n": data["stats"].get("n", 0),
                "mean_abs_correlation": data["stats"].get("mean_abs_correlation"),
                "characteristics": data["characteristics"],
                "dimension_stats": data["stats"].get("dimension_stats", {}),
            }
            for env, data in env_analysis.items()
        },
        "ranking": [
            {"environment": env, "mean_abs_correlation": corr}
            for env, corr in ranked
        ],
    }

    log_dir = Path("logs/environment_analysis")
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"environment_independence_{timestamp}.json"

    with open(log_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n💾 Results saved → {log_file}")

    return output


if __name__ == "__main__":
    run_environment_independence_analysis()
