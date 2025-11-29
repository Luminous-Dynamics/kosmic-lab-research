#!/usr/bin/env python3
"""
K_M (Temporal Depth) Full Validation for Paper 9.

Tests hypothesis: Recurrent agents show higher K_M than feedforward agents
in environments requiring memory.
"""

import sys
sys.path.insert(0, '/srv/luminous-dynamics/kosmic-lab/docs/papers/paper-8-unified-indices')

import numpy as np
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from km_validation_environment import DelayedHintEnvironment, SequenceRecallEnvironment

# Import agent types from track_l_runner
from track_l_runner import (
    RandomAgent,
    LinearAgent,
    CMAESAgent,
    RecurrentAgent,
)


def compute_km_index(obs_history: np.ndarray, actions: np.ndarray) -> float:
    """
    Compute K_M (temporal depth) from observation history and actions.

    K_M measures how much past observations influence current actions.
    Uses mutual information approximation between action and history.

    K_M = (L_markov - L_history) / (L_markov + eps)

    Where:
    - L_markov: Loss using only current observation
    - L_history: Loss using full history
    """
    if len(actions) < 5:
        return 0.0

    # Simple approximation: variance explained by history vs current only
    # Use action magnitude as target
    action_norms = np.array([np.linalg.norm(a) for a in actions])

    if len(obs_history) != len(actions):
        return 0.0

    # Current-only prediction (Markov)
    current_obs_norms = np.array([np.linalg.norm(o) for o in obs_history])

    if np.std(action_norms) < 1e-8:
        return 0.0  # No variance to explain

    # Correlation with current observation
    if np.std(current_obs_norms) < 1e-8:
        r_markov = 0.0
    else:
        r_markov = np.corrcoef(action_norms, current_obs_norms)[0, 1]
        if np.isnan(r_markov):
            r_markov = 0.0

    # History-based prediction: use cumulative information
    # For recurrent agents, actions should correlate with historical patterns
    history_features = []
    for i in range(len(obs_history)):
        # Feature: running mean of observation norms up to this point
        if i == 0:
            running_mean = np.linalg.norm(obs_history[0])
        else:
            running_mean = np.mean([np.linalg.norm(obs_history[j]) for j in range(i+1)])
        history_features.append(running_mean)

    history_features = np.array(history_features)

    if np.std(history_features) < 1e-8:
        r_history = r_markov
    else:
        r_history = np.corrcoef(action_norms, history_features)[0, 1]
        if np.isnan(r_history):
            r_history = r_markov

    # K_M: Relative improvement from using history
    # Higher when history helps more than current-only
    L_markov = 1 - abs(r_markov)
    L_history = 1 - abs(r_history)

    eps = 1e-8
    K_M = (L_markov - L_history) / (L_markov + eps)

    # Clamp to [0, 2]
    K_M = max(0.0, min(2.0, K_M))

    return K_M


def run_episode_with_km(env, agent, compute_km: bool = True) -> Dict[str, Any]:
    """Run a single episode and compute K_M."""
    obs = env.reset()
    done = False
    total_reward = 0.0

    obs_history = [obs.copy()]
    action_history = []
    correct_actions = 0
    total_actions = 0

    while not done:
        action = agent.select_action(obs)
        action_history.append(action.copy())

        obs, reward, done, info = env.step(action)
        obs_history.append(obs.copy())
        total_reward += reward

        # Track correctness at decision points
        if "correct_action" in info:
            if np.argmax(action) == info["correct_action"]:
                correct_actions += 1
            total_actions += 1

    result = {
        "total_reward": total_reward,
        "steps": len(action_history),
        "accuracy": correct_actions / max(1, total_actions),
    }

    if compute_km and len(action_history) >= 5:
        obs_array = np.array(obs_history[:-1])  # Exclude final obs
        action_array = np.array(action_history)
        result["K_M"] = compute_km_index(obs_array, action_array)
    else:
        result["K_M"] = 0.0

    return result


def run_km_validation():
    """Run full K_M validation comparing feedforward vs recurrent agents."""

    print("=" * 70)
    print("🧠 K_M (TEMPORAL DEPTH) VALIDATION EXPERIMENTS")
    print("=" * 70)
    print()
    print("Hypothesis: Recurrent agents show higher K_M than feedforward agents")
    print("in environments requiring memory.")
    print()

    # Test configurations
    environments = [
        ("DelayedHint-5", lambda: DelayedHintEnvironment(hint_delay=5, episode_length=15)),
        ("DelayedHint-10", lambda: DelayedHintEnvironment(hint_delay=10, episode_length=20)),
        ("DelayedHint-15", lambda: DelayedHintEnvironment(hint_delay=15, episode_length=25)),
        ("SequenceRecall-3", lambda: SequenceRecallEnvironment(sequence_length=3, recall_delay=5)),
        ("SequenceRecall-5", lambda: SequenceRecallEnvironment(sequence_length=5, recall_delay=8)),
    ]

    agent_types = [
        ("Random", lambda obs_dim, act_dim: RandomAgent(act_dim)),
        ("Linear", lambda obs_dim, act_dim: LinearAgent(obs_dim, act_dim, learning_rate=0.1)),
        ("CMA-ES", lambda obs_dim, act_dim: CMAESAgent(obs_dim, act_dim, sigma=0.5)),
        ("Recurrent", lambda obs_dim, act_dim: RecurrentAgent(obs_dim, act_dim, hidden_dim=16)),
    ]

    n_episodes = 30
    all_results = []

    for env_name, env_factory in environments:
        print(f"\n{'='*60}")
        print(f"📊 Environment: {env_name}")
        print(f"{'='*60}")

        env_results = []

        for agent_name, agent_factory in agent_types:
            print(f"\n  Testing {agent_name} agent ({n_episodes} episodes)...")

            agent_episodes = []
            for i in range(n_episodes):
                env = env_factory()
                agent = agent_factory(env.obs_dim, env.action_dim)

                episode_result = run_episode_with_km(env, agent, compute_km=True)
                agent_episodes.append(episode_result)

            # Compute statistics
            km_values = [r["K_M"] for r in agent_episodes]
            rewards = [r["total_reward"] for r in agent_episodes]
            accuracies = [r["accuracy"] for r in agent_episodes]

            km_mean = np.mean(km_values)
            km_std = np.std(km_values)
            reward_mean = np.mean(rewards)
            accuracy_mean = np.mean(accuracies)

            result = {
                "environment": env_name,
                "agent": agent_name,
                "K_M_mean": km_mean,
                "K_M_std": km_std,
                "reward_mean": reward_mean,
                "accuracy_mean": accuracy_mean,
                "episodes": agent_episodes,
            }

            env_results.append(result)
            all_results.append(result)

            print(f"    K_M = {km_mean:.3f} ± {km_std:.3f}")
            print(f"    Reward = {reward_mean:.2f}, Accuracy = {accuracy_mean:.1%}")

        # Environment summary
        print(f"\n  {'-'*50}")
        print(f"  {env_name} Summary:")
        print(f"  {'Agent':<12} {'K_M (mean)':<12} {'Accuracy':<12} {'Reward':<10}")
        print(f"  {'-'*50}")
        for r in sorted(env_results, key=lambda x: -x["K_M_mean"]):
            print(f"  {r['agent']:<12} {r['K_M_mean']:<12.3f} {r['accuracy_mean']:<12.1%} {r['reward_mean']:<10.2f}")

    # Overall analysis
    print("\n" + "=" * 70)
    print("📈 OVERALL K_M VALIDATION SUMMARY")
    print("=" * 70)

    # Group by agent type
    agent_stats = {}
    for r in all_results:
        agent = r["agent"]
        if agent not in agent_stats:
            agent_stats[agent] = {"K_M": [], "reward": [], "accuracy": []}
        agent_stats[agent]["K_M"].append(r["K_M_mean"])
        agent_stats[agent]["reward"].append(r["reward_mean"])
        agent_stats[agent]["accuracy"].append(r["accuracy_mean"])

    print(f"\n{'Agent Type':<15} {'Avg K_M':<12} {'Avg Accuracy':<15} {'Avg Reward':<12}")
    print("-" * 55)

    for agent, stats in sorted(agent_stats.items(), key=lambda x: -np.mean(x[1]["K_M"])):
        avg_km = np.mean(stats["K_M"])
        avg_acc = np.mean(stats["accuracy"])
        avg_rew = np.mean(stats["reward"])
        print(f"{agent:<15} {avg_km:<12.3f} {avg_acc:<15.1%} {avg_rew:<12.2f}")

    # Hypothesis testing
    print("\n" + "-" * 60)
    print("🧪 HYPOTHESIS TESTING")
    print("-" * 60)

    recurrent_km = np.mean(agent_stats.get("Recurrent", {"K_M": [0]})["K_M"])
    feedforward_km = np.mean([
        np.mean(agent_stats.get(a, {"K_M": [0]})["K_M"])
        for a in ["Random", "Linear", "CMA-ES"]
    ])

    recurrent_acc = np.mean(agent_stats.get("Recurrent", {"accuracy": [0]})["accuracy"])
    feedforward_acc = np.mean([
        np.mean(agent_stats.get(a, {"accuracy": [0]})["accuracy"])
        for a in ["Random", "Linear", "CMA-ES"]
    ])

    print(f"\nRecurrent agents avg K_M: {recurrent_km:.3f}")
    print(f"Feedforward agents avg K_M: {feedforward_km:.3f}")
    print(f"K_M ratio (Recurrent/Feedforward): {recurrent_km / (feedforward_km + 1e-8):.2f}x")

    print(f"\nRecurrent agents avg accuracy: {recurrent_acc:.1%}")
    print(f"Feedforward agents avg accuracy: {feedforward_acc:.1%}")

    if recurrent_km > feedforward_km:
        print("\n✓ HYPOTHESIS SUPPORTED: Recurrent agents show higher K_M")
    else:
        print("\n✗ HYPOTHESIS NOT SUPPORTED: Feedforward agents show similar/higher K_M")

    if recurrent_acc > feedforward_acc:
        print("✓ TASK VALIDATION: Recurrent agents achieve higher accuracy")
    else:
        print("✗ TASK VALIDATION: Memory doesn't help accuracy (environment may be too simple)")

    # Save results
    output_dir = Path("/srv/luminous-dynamics/kosmic-lab/logs/km_validation")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"km_validation_{timestamp}.json"

    output_data = {
        "experiment": "K_M_temporal_depth_validation",
        "timestamp": timestamp,
        "n_episodes_per_config": n_episodes,
        "environments": [e[0] for e in environments],
        "agent_types": [a[0] for a in agent_types],
        "results": all_results,
        "summary": {
            "recurrent_avg_km": recurrent_km,
            "feedforward_avg_km": feedforward_km,
            "km_ratio": recurrent_km / (feedforward_km + 1e-8),
            "recurrent_avg_accuracy": recurrent_acc,
            "feedforward_avg_accuracy": feedforward_acc,
            "hypothesis_supported": recurrent_km > feedforward_km,
            "task_validated": recurrent_acc > feedforward_acc,
        },
        "agent_statistics": {
            agent: {
                "avg_K_M": np.mean(stats["K_M"]),
                "avg_accuracy": np.mean(stats["accuracy"]),
                "avg_reward": np.mean(stats["reward"]),
            }
            for agent, stats in agent_stats.items()
        }
    }

    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2, default=float)

    print(f"\n💾 Results saved → {output_file}")

    return all_results


if __name__ == "__main__":
    run_km_validation()
