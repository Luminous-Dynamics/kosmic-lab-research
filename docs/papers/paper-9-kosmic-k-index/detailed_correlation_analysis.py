#!/usr/bin/env python3
"""
Detailed Correlation Analysis by Environment and Agent Type

Following up on the critical finding that mean |r| = 0.455 (not 0.109 as claimed).
This analysis breaks down correlations to understand:
1. Are correlations environment-specific?
2. Are correlations agent-type specific?
3. Which dimensions are truly independent?
"""

import numpy as np
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from scipy.stats import pearsonr
from collections import defaultdict


def load_track_l_results() -> List[Dict]:
    """Load K-vector results from Track L experiments."""
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


def compute_correlations(data: List[Dict], dimensions: List[str]) -> Dict:
    """Compute correlation matrix for a subset of data."""
    k_matrix = []
    for r in data:
        row = [r.get(dim, 0) for dim in dimensions]
        if not any(np.isnan(row)):
            k_matrix.append(row)

    if len(k_matrix) < 10:
        return {"error": "Insufficient data", "n": len(k_matrix)}

    k_matrix = np.array(k_matrix)
    n_dims = len(dimensions)

    corr_matrix = np.zeros((n_dims, n_dims))
    p_matrix = np.zeros((n_dims, n_dims))

    for i in range(n_dims):
        for j in range(n_dims):
            if i == j:
                corr_matrix[i, j] = 1.0
            else:
                col_i = k_matrix[:, i]
                col_j = k_matrix[:, j]
                if np.std(col_i) < 1e-10 or np.std(col_j) < 1e-10:
                    corr_matrix[i, j] = np.nan
                else:
                    r, p = pearsonr(col_i, col_j)
                    corr_matrix[i, j] = r
                    p_matrix[i, j] = p

    # Mean absolute off-diagonal
    off_diag = []
    for i in range(n_dims):
        for j in range(i+1, n_dims):
            if not np.isnan(corr_matrix[i, j]):
                off_diag.append(abs(corr_matrix[i, j]))

    return {
        "n": len(k_matrix),
        "correlation_matrix": corr_matrix.tolist(),
        "mean_abs_correlation": np.mean(off_diag) if off_diag else np.nan,
        "off_diagonal_correlations": off_diag,
    }


def run_detailed_analysis():
    """Run detailed correlation analysis."""
    print("=" * 70)
    print("📊 DETAILED CORRELATION ANALYSIS")
    print("=" * 70)
    print()
    print("Investigating the discrepancy between claimed (0.109) and")
    print("observed (0.455) mean dimension correlation")
    print()

    results = load_track_l_results()
    print(f"Loaded {len(results)} data points")

    # Active dimensions (excluding K_S which is always 0)
    active_dims = ["K_R", "K_A", "K_I", "K_P", "K_M", "K_H"]

    # Group by environment
    by_env = defaultdict(list)
    for r in results:
        by_env[r["environment"]].append(r)

    # Group by agent type
    by_type = defaultdict(list)
    for r in results:
        by_type[r["type"]].append(r)

    print("-" * 70)
    print("📈 CORRELATIONS BY ENVIRONMENT")
    print("-" * 70)

    env_results = {}
    for env, data in sorted(by_env.items()):
        corr = compute_correlations(data, active_dims)
        env_results[env] = corr

        print(f"\n{env} (n={corr.get('n', 0)}):")
        if "mean_abs_correlation" in corr and not np.isnan(corr["mean_abs_correlation"]):
            print(f"  Mean |r| = {corr['mean_abs_correlation']:.3f}")

            # Top correlations
            matrix = np.array(corr["correlation_matrix"])
            pairs = []
            for i in range(len(active_dims)):
                for j in range(i+1, len(active_dims)):
                    if not np.isnan(matrix[i, j]):
                        pairs.append((active_dims[i], active_dims[j], abs(matrix[i, j])))
            pairs.sort(key=lambda x: -x[2])

            if pairs:
                print(f"  Highest: {pairs[0][0]}-{pairs[0][1]} = {pairs[0][2]:.3f}")
                if len(pairs) > 1:
                    print(f"  2nd:     {pairs[1][0]}-{pairs[1][1]} = {pairs[1][2]:.3f}")

    print()
    print("-" * 70)
    print("📊 CORRELATIONS BY AGENT TYPE")
    print("-" * 70)

    type_results = {}
    for agent_type, data in sorted(by_type.items()):
        corr = compute_correlations(data, active_dims)
        type_results[agent_type] = corr

        print(f"\n{agent_type} (n={corr.get('n', 0)}):")
        if "mean_abs_correlation" in corr and not np.isnan(corr["mean_abs_correlation"]):
            print(f"  Mean |r| = {corr['mean_abs_correlation']:.3f}")

    # Look at pairwise correlations across ALL data
    print()
    print("-" * 70)
    print("📈 PAIRWISE CORRELATIONS (ALL DATA)")
    print("-" * 70)
    print()

    all_corr = compute_correlations(results, active_dims)
    matrix = np.array(all_corr["correlation_matrix"])

    print("Full correlation matrix (excluding K_S):")
    print()
    print(f"{'':>8}", end="")
    for d in active_dims:
        print(f"{d:>8}", end="")
    print()

    for i, d in enumerate(active_dims):
        print(f"{d:>8}", end="")
        for j in range(len(active_dims)):
            r = matrix[i, j]
            if np.isnan(r):
                print(f"{'nan':>8}", end="")
            elif i == j:
                print(f"{'1.000':>8}", end="")
            else:
                # Color code
                if abs(r) > 0.5:
                    print(f"\033[91m{r:>8.3f}\033[0m", end="")  # Red
                elif abs(r) > 0.3:
                    print(f"\033[93m{r:>8.3f}\033[0m", end="")  # Yellow
                else:
                    print(f"\033[92m{r:>8.3f}\033[0m", end="")  # Green
        print()

    # Identify independent dimensions
    print()
    print("-" * 70)
    print("📋 DIMENSION INDEPENDENCE ASSESSMENT")
    print("-" * 70)
    print()

    independent_pairs = []
    correlated_pairs = []

    for i in range(len(active_dims)):
        for j in range(i+1, len(active_dims)):
            r = matrix[i, j]
            if not np.isnan(r):
                pair = f"{active_dims[i]}-{active_dims[j]}"
                if abs(r) < 0.3:
                    independent_pairs.append((pair, r))
                else:
                    correlated_pairs.append((pair, r))

    print("✅ INDEPENDENT PAIRS (|r| < 0.3):")
    for pair, r in sorted(independent_pairs, key=lambda x: abs(x[1])):
        print(f"   {pair}: r = {r:.3f}")

    print()
    print("⚠️  CORRELATED PAIRS (|r| >= 0.3):")
    for pair, r in sorted(correlated_pairs, key=lambda x: -abs(x[1])):
        print(f"   {pair}: r = {r:.3f}")

    # Summary statistics
    print()
    print("-" * 70)
    print("📋 SUMMARY")
    print("-" * 70)
    print()
    print(f"Total pairs analyzed: {len(independent_pairs) + len(correlated_pairs)}")
    print(f"Independent pairs (|r| < 0.3): {len(independent_pairs)}")
    print(f"Correlated pairs (|r| >= 0.3): {len(correlated_pairs)}")
    print(f"Mean |r| overall: {all_corr['mean_abs_correlation']:.3f}")
    print()

    # Recommendations
    print("-" * 70)
    print("💡 RECOMMENDATIONS FOR PAPER")
    print("-" * 70)
    print()

    if all_corr["mean_abs_correlation"] > 0.3:
        print("⚠️  The current claim of mean |r| = 0.109 is NOT supported.")
        print(f"   Actual value: mean |r| = {all_corr['mean_abs_correlation']:.3f}")
        print()
        print("Options to address:")
        print("1. Revise the claim to match actual data")
        print("2. Clarify that some dimensions are inherently related")
        print("3. Focus on the dimensions that ARE independent (K_M)")
        print("4. Argue that correlation doesn't mean redundancy")
        print("   (dimensions can be correlated but measure different things)")

    # Variance analysis
    print()
    print("-" * 70)
    print("📊 DIMENSION VARIANCE ANALYSIS")
    print("-" * 70)
    print()

    for dim in active_dims:
        values = [r.get(dim, 0) for r in results]
        values = [v for v in values if not np.isnan(v)]
        if values:
            print(f"{dim}: mean={np.mean(values):.4f}, std={np.std(values):.4f}, "
                  f"range=[{np.min(values):.4f}, {np.max(values):.4f}]")

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "n_samples": len(results),
        "overall_mean_abs_correlation": float(all_corr["mean_abs_correlation"])
            if not np.isnan(all_corr["mean_abs_correlation"]) else None,
        "environment_results": {k: {
            "n": v.get("n", 0),
            "mean_abs_correlation": float(v.get("mean_abs_correlation", 0))
                if not np.isnan(v.get("mean_abs_correlation", 0)) else None
        } for k, v in env_results.items()},
        "agent_type_results": {k: {
            "n": v.get("n", 0),
            "mean_abs_correlation": float(v.get("mean_abs_correlation", 0))
                if not np.isnan(v.get("mean_abs_correlation", 0)) else None
        } for k, v in type_results.items()},
        "independent_pairs": [{"pair": p, "r": float(r)} for p, r in independent_pairs],
        "correlated_pairs": [{"pair": p, "r": float(r)} for p, r in correlated_pairs],
    }

    log_dir = Path("logs/dimensionality")
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"detailed_correlation_analysis_{timestamp}.json"

    with open(log_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n💾 Results saved → {log_file}")

    return output


if __name__ == "__main__":
    run_detailed_analysis()
