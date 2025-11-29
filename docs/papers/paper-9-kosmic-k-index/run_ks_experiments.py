#!/usr/bin/env python3
"""
K_S (Social Coherence) Multi-Agent Experiments for Paper 9.

Tests hypothesis: Coordinated agent pairs show higher K_S than independent pairs.
"""

import sys
sys.path.insert(0, '/srv/luminous-dynamics/kosmic-lab/docs/papers/paper-8-unified-indices')

import numpy as np
import json
from datetime import datetime
from pathlib import Path
from scipy.stats import pearsonr

from track_l_runner import (
    CoordinationEnvironment,
    RandomAgent,
    LinearAgent,
    CMAESAgent,
    RecurrentAgent,
    run_multiagent_episode,
)

def run_ks_validation():
    """Run K_S validation experiments with different agent pairings."""

    print("=" * 70)
    print("🤝 K_S (SOCIAL COHERENCE) MULTI-AGENT EXPERIMENTS")
    print("=" * 70)
    print()
    print("Hypothesis: Trained agent pairs show higher K_S than random pairs")
    print()

    # Create environment
    env = CoordinationEnvironment(obs_dim=8, action_dim=4)
    obs_dim = env.obs_dim
    action_dim = env.action_dim

    # Define agent pairings to test
    pairings = [
        ("random-random", lambda: RandomAgent(action_dim), lambda: RandomAgent(action_dim)),
        ("linear-linear",
         lambda: LinearAgent(obs_dim, action_dim, learning_rate=0.01),
         lambda: LinearAgent(obs_dim, action_dim, learning_rate=0.01)),
        ("cmaes-cmaes",
         lambda: CMAESAgent(obs_dim, action_dim, sigma=0.5),
         lambda: CMAESAgent(obs_dim, action_dim, sigma=0.5)),
        ("recurrent-recurrent",
         lambda: RecurrentAgent(obs_dim, action_dim, hidden_dim=16),
         lambda: RecurrentAgent(obs_dim, action_dim, hidden_dim=16)),
        # Mixed pairings (should show lower K_S)
        ("random-cmaes", lambda: RandomAgent(action_dim),
         lambda: CMAESAgent(obs_dim, action_dim, sigma=0.5)),
        ("linear-recurrent",
         lambda: LinearAgent(obs_dim, action_dim, learning_rate=0.01),
         lambda: RecurrentAgent(obs_dim, action_dim, hidden_dim=16)),
    ]

    n_episodes = 20
    results = []

    for pairing_name, agent_A_factory, agent_B_factory in pairings:
        print(f"\n📊 Testing {pairing_name} pairing ({n_episodes} episodes)...")

        pairing_results = []
        for i in range(n_episodes):
            agent_A = agent_A_factory()
            agent_B = agent_B_factory()

            episode_result = run_multiagent_episode(env, agent_A, agent_B, compute_kosmic=True)

            pairing_results.append({
                "episode": i,
                "K_S": episode_result.get("K_S", 0.0),
                "K_R_A": episode_result.get("K_R_A", 0.0),
                "K_R_B": episode_result.get("K_R_B", 0.0),
                "total_reward": episode_result.get("total_reward", 0.0),
            })

        # Compute statistics
        ks_values = [r["K_S"] for r in pairing_results]
        rewards = [r["total_reward"] for r in pairing_results]

        ks_mean = np.mean(ks_values)
        ks_std = np.std(ks_values)
        reward_mean = np.mean(rewards)

        results.append({
            "pairing": pairing_name,
            "K_S_mean": ks_mean,
            "K_S_std": ks_std,
            "reward_mean": reward_mean,
            "episodes": pairing_results,
        })

        print(f"  K_S = {ks_mean:.3f} ± {ks_std:.3f}, Reward = {reward_mean:.2f}")

    # Summary table
    print("\n" + "-" * 60)
    print("📈 K_S VALIDATION SUMMARY")
    print("-" * 60)
    print(f"{'Pairing':<25} {'K_S (mean)':<12} {'K_S (std)':<12} {'Reward':<10}")
    print("-" * 60)

    for r in sorted(results, key=lambda x: -x["K_S_mean"]):
        print(f"{r['pairing']:<25} {r['K_S_mean']:<12.3f} {r['K_S_std']:<12.3f} {r['reward_mean']:<10.2f}")

    # Hypothesis testing
    print("\n" + "-" * 60)
    print("🧪 HYPOTHESIS TESTING")
    print("-" * 60)

    # Compare same-type vs mixed pairings
    same_type = [r for r in results if "-" in r["pairing"] and r["pairing"].split("-")[0] == r["pairing"].split("-")[1]]
    mixed_type = [r for r in results if "-" in r["pairing"] and r["pairing"].split("-")[0] != r["pairing"].split("-")[1]]

    same_ks = np.mean([r["K_S_mean"] for r in same_type])
    mixed_ks = np.mean([r["K_S_mean"] for r in mixed_type])

    print(f"Same-type pairings avg K_S: {same_ks:.3f}")
    print(f"Mixed pairings avg K_S: {mixed_ks:.3f}")

    if same_ks > mixed_ks:
        print("✓ HYPOTHESIS SUPPORTED: Same-type pairs show higher coordination")
    else:
        print("✗ HYPOTHESIS NOT SUPPORTED: Mixed pairs show similar/higher coordination")

    # Save results
    output_dir = Path("/srv/luminous-dynamics/kosmic-lab/logs/track_l")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"ks_multiagent_{timestamp}.json"

    output_data = {
        "experiment": "K_S_multiagent_validation",
        "timestamp": timestamp,
        "n_episodes": n_episodes,
        "results": results,
        "summary": {
            "same_type_avg_ks": same_ks,
            "mixed_avg_ks": mixed_ks,
            "hypothesis_supported": same_ks > mixed_ks,
        }
    }

    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2, default=float)

    print(f"\n💾 Results saved → {output_file}")

    return results


if __name__ == "__main__":
    run_ks_validation()
