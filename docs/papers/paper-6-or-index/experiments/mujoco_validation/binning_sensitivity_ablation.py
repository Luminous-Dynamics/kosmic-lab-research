#!/usr/bin/env python3
"""
Binning Sensitivity Ablation for O/R Index

Tests whether O/R Index is robust to discretization choices by evaluating
correlation with performance across k ∈ {5, 10, 20, 50, 100} bins.

Critical for Best Paper: Eliminates #1 methodological vulnerability.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass

import gymnasium as gym
import numpy as np
import torch
import torch.nn as nn
from torch.distributions.normal import Normal
from scipy import stats
from sklearn.cluster import KMeans


# ============================================================================
# Classes needed for checkpoint loading (from mujoco_mappo_trainer.py)
# ============================================================================

@dataclass
class Args:
    """Training arguments (needed for unpickling checkpoint)"""
    exp_name: str = "mujoco_mappo"
    seed: int = 42
    torch_deterministic: bool = True
    cuda: bool = True
    env_name: str = "ManyAgentAnt"
    env_version: str = "v0"
    num_agents: int = 2
    agent_conf: str = "2x4"
    max_cycles: int = 1000
    total_timesteps: int = 500_000
    learning_rate: float = 3e-4
    num_epochs: int = 10
    num_minibatches: int = 32
    gamma: float = 0.99
    gae_lambda: float = 0.95
    clip_coef: float = 0.2
    ent_coef: float = 0.01
    vf_coef: float = 0.5
    max_grad_norm: float = 0.5
    or_checkpoint_freq: int = 50_000
    or_window_size: int = 10_000
    save_freq: int = 50_000
    log_dir: str = "logs"
    checkpoint_dir: str = "checkpoints"
    results_dir: str = "results"


class ContinuousAgent(nn.Module):
    """Actor-critic network for continuous actions (needed for checkpoint loading)"""
    def __init__(self, obs_dim, action_dim):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(obs_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
        )
        self.actor_mean = nn.Linear(256, action_dim)
        self.actor_logstd = nn.Parameter(torch.zeros(action_dim))
        self.critic = nn.Linear(256, 1)

    def get_value(self, x):
        features = self.network(x)
        return self.critic(features)

    def get_action_and_value(self, x, action=None):
        features = self.network(x)
        action_mean = self.actor_mean(features)
        action_std = torch.clamp(self.actor_logstd.exp(), min=1e-3, max=1.0)
        probs = Normal(action_mean, action_std)
        if action is None:
            action = probs.sample()
        return action, probs.log_prob(action).sum(-1), probs.entropy().sum(-1), self.critic(features)

# ============================================================================


def load_checkpoint(checkpoint_path: str) -> Tuple[torch.nn.Module, Dict]:
    """Load trained policy from checkpoint."""
    # PyTorch 2.7+ requires weights_only=False for checkpoints with custom classes
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    return checkpoint


def collect_evaluation_trajectories(
    env_name: str,
    policy,
    n_episodes: int = 50,
    seed: int = 42
) -> Dict[str, np.ndarray]:
    """
    Collect evaluation trajectories for O/R computation.

    Returns:
        observations: (n_timesteps, obs_dim)
        actions: (n_timesteps, action_dim)
        rewards: (n_timesteps,)
    """
    env = gym.make(env_name)
    env.reset(seed=seed)

    all_observations = []
    all_actions = []
    all_rewards = []

    for episode in range(n_episodes):
        obs, _ = env.reset(seed=seed + episode)
        done = False
        truncated = False

        while not (done or truncated):
            # Get action from policy
            with torch.no_grad():
                obs_tensor = torch.FloatTensor(obs).unsqueeze(0)
                action = policy(obs_tensor).squeeze(0).numpy()

            # Step environment
            next_obs, reward, done, truncated, _ = env.step(action)

            # Store data
            all_observations.append(obs)
            all_actions.append(action)
            all_rewards.append(reward)

            obs = next_obs

    env.close()

    return {
        "observations": np.array(all_observations),
        "actions": np.array(all_actions),
        "rewards": np.array(all_rewards)
    }


def discretize_space(data: np.ndarray, k_bins: int, seed: int = 42) -> np.ndarray:
    """
    Discretize continuous space using K-means clustering.

    Args:
        data: (n_samples, dim) continuous values
        k_bins: number of bins (clusters)
        seed: random seed for reproducibility

    Returns:
        bin_indices: (n_samples,) discrete bin assignments
    """
    if len(data) < k_bins:
        # Fallback: simple quantile binning
        percentiles = np.linspace(0, 100, k_bins + 1)
        bins = np.percentile(data, percentiles)
        bin_indices = np.digitize(data[:, 0], bins[:-1])  # Use first dimension
        return bin_indices - 1  # Make 0-indexed

    kmeans = KMeans(n_clusters=k_bins, random_state=seed, n_init=10)
    bin_indices = kmeans.fit_predict(data)
    return bin_indices


def compute_or_index_with_bins(
    observations: np.ndarray,
    actions: np.ndarray,
    rewards: np.ndarray,
    k_bins_obs: int,
    k_bins_action: int,
    seed: int = 42
) -> Dict[str, float]:
    """
    Compute O/R Index with specified bin counts.

    Returns:
        or_index: O/R Index value
        obs_consistency: Observation consistency (O)
        reward_consistency: Reward consistency (R)
    """
    # Discretize observations and actions
    obs_bins = discretize_space(observations, k_bins_obs, seed=seed)
    action_bins = discretize_space(actions, k_bins_action, seed=seed)

    # Compute observation consistency (O)
    # Variance of action patterns across observation bins
    obs_action_variance = []
    for obs_bin in range(k_bins_obs):
        mask = obs_bins == obs_bin
        if np.sum(mask) < 2:  # Need at least 2 samples
            continue
        actions_in_bin = action_bins[mask]
        variance = np.var(actions_in_bin)
        obs_action_variance.append(variance)

    if len(obs_action_variance) == 0:
        return {"or_index": np.nan, "obs_consistency": np.nan, "reward_consistency": np.nan}

    obs_consistency = np.mean(obs_action_variance)

    # Compute reward consistency (R)
    # Variance of rewards across action bins
    action_reward_variance = []
    for action_bin in range(k_bins_action):
        mask = action_bins == action_bin
        if np.sum(mask) < 2:
            continue
        rewards_in_bin = rewards[mask]
        variance = np.var(rewards_in_bin)
        action_reward_variance.append(variance)

    if len(action_reward_variance) == 0:
        return {"or_index": np.nan, "obs_consistency": np.nan, "reward_consistency": np.nan}

    reward_consistency = np.mean(action_reward_variance)

    # Compute O/R Index
    # O/R = (Var(actions | obs) / Var(actions)) - 1
    # Approximation: use variance ratios
    overall_action_variance = np.var(action_bins)
    if overall_action_variance == 0:
        return {"or_index": np.nan, "obs_consistency": np.nan, "reward_consistency": np.nan}

    or_index = (obs_consistency / overall_action_variance) - 1

    return {
        "or_index": float(or_index),
        "obs_consistency": float(obs_consistency),
        "reward_consistency": float(reward_consistency)
    }


def binning_sensitivity_analysis(
    observations: np.ndarray,
    actions: np.ndarray,
    rewards: np.ndarray,
    k_values: List[int] = [5, 10, 20, 50, 100],
    seed: int = 42
) -> Dict:
    """
    Perform binning sensitivity analysis across different k values.

    Returns:
        results: Dictionary with O/R values for each k and stability metrics
    """
    results = {
        "k_values": k_values,
        "or_indices": [],
        "obs_consistencies": [],
        "reward_consistencies": []
    }

    for k in k_values:
        print(f"Computing O/R with k={k} bins...")

        or_result = compute_or_index_with_bins(
            observations, actions, rewards,
            k_bins_obs=k,
            k_bins_action=k,
            seed=seed
        )

        results["or_indices"].append(or_result["or_index"])
        results["obs_consistencies"].append(or_result["obs_consistency"])
        results["reward_consistencies"].append(or_result["reward_consistency"])

        print(f"  O/R = {or_result['or_index']:.4f}")

    # Compute stability metrics
    or_values = np.array(results["or_indices"])
    valid_or = or_values[~np.isnan(or_values)]

    if len(valid_or) > 1:
        results["mean_or"] = float(np.mean(valid_or))
        results["std_or"] = float(np.std(valid_or))
        results["coefficient_of_variation"] = float(np.std(valid_or) / np.abs(np.mean(valid_or)))
        results["min_or"] = float(np.min(valid_or))
        results["max_or"] = float(np.max(valid_or))
        results["range_or"] = float(np.max(valid_or) - np.min(valid_or))
    else:
        results["mean_or"] = np.nan
        results["std_or"] = np.nan
        results["coefficient_of_variation"] = np.nan

    return results


def evaluate_performance(env_name: str, policy, n_episodes: int = 50, seed: int = 42) -> Dict:
    """
    Evaluate policy performance (average return).
    """
    env = gym.make(env_name)

    episode_returns = []
    for episode in range(n_episodes):
        obs, _ = env.reset(seed=seed + episode)
        done = False
        truncated = False
        episode_return = 0.0

        while not (done or truncated):
            with torch.no_grad():
                obs_tensor = torch.FloatTensor(obs).unsqueeze(0)
                action = policy(obs_tensor).squeeze(0).numpy()

            obs, reward, done, truncated, _ = env.step(action)
            episode_return += reward

        episode_returns.append(episode_return)

    env.close()

    return {
        "mean_return": float(np.mean(episode_returns)),
        "std_return": float(np.std(episode_returns)),
        "n_episodes": n_episodes
    }


def main():
    """
    Main binning sensitivity ablation experiment.

    Steps:
    1. Load trained checkpoint(s)
    2. Collect evaluation trajectories
    3. Compute O/R with k ∈ {5, 10, 20, 50, 100}
    4. Analyze stability
    5. Compute correlation with performance
    6. Generate report
    """
    print("=" * 80)
    print("BINNING SENSITIVITY ABLATION")
    print("=" * 80)

    # Configuration
    env_name = "Ant-v2-v0"  # Or "HalfCheetah-v2-v0"
    checkpoint_dir = Path("checkpoints")
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    k_values = [5, 10, 20, 50, 100]
    n_eval_episodes = 50
    seed = 42

    # Find available checkpoints
    checkpoints = sorted(checkpoint_dir.glob("*.pt"))
    if not checkpoints:
        print("ERROR: No checkpoints found!")
        print(f"Looked in: {checkpoint_dir.absolute()}")
        return

    print(f"Found {len(checkpoints)} checkpoint(s):")
    for ckpt in checkpoints:
        print(f"  - {ckpt.name}")

    all_results = []

    for checkpoint_path in checkpoints:
        print(f"\nProcessing checkpoint: {checkpoint_path.name}")
        print("-" * 80)

        # Load checkpoint
        try:
            checkpoint = load_checkpoint(str(checkpoint_path))
            print(f"Checkpoint loaded successfully")
        except Exception as e:
            print(f"ERROR loading checkpoint: {e}")
            continue

        # Extract policy (this depends on checkpoint structure)
        # For now, create a simple dummy policy for demonstration
        class DummyPolicy(torch.nn.Module):
            def __init__(self, obs_dim, action_dim):
                super().__init__()
                self.fc = torch.nn.Linear(obs_dim, action_dim)

            def forward(self, x):
                return torch.tanh(self.fc(x))

        # Determine dimensions from environment
        env_temp = gym.make(env_name)
        obs_dim = env_temp.observation_space.shape[0]
        action_dim = env_temp.action_space.shape[0]
        env_temp.close()

        policy = DummyPolicy(obs_dim, action_dim)

        # TODO: Load actual policy weights from checkpoint
        # policy.load_state_dict(checkpoint['policy_state_dict'])
        policy.eval()

        # Evaluate performance
        print(f"\nEvaluating performance...")
        performance = evaluate_performance(env_name, policy, n_eval_episodes, seed)
        print(f"Mean Return: {performance['mean_return']:.2f} ± {performance['std_return']:.2f}")

        # Collect trajectories
        print(f"\nCollecting {n_eval_episodes} evaluation trajectories...")
        trajectories = collect_evaluation_trajectories(env_name, policy, n_eval_episodes, seed)
        print(f"Collected {len(trajectories['observations'])} timesteps")
        print(f"  Observations: {trajectories['observations'].shape}")
        print(f"  Actions: {trajectories['actions'].shape}")
        print(f"  Rewards: {trajectories['rewards'].shape}")

        # Binning sensitivity analysis
        print(f"\nRunning binning sensitivity analysis...")
        binning_results = binning_sensitivity_analysis(
            trajectories["observations"],
            trajectories["actions"],
            trajectories["rewards"],
            k_values=k_values,
            seed=seed
        )

        # Combine results
        result = {
            "checkpoint": checkpoint_path.name,
            "environment": env_name,
            "performance": performance,
            "binning_sensitivity": binning_results,
            "n_trajectories": len(trajectories["observations"]),
            "seed": seed
        }

        all_results.append(result)

        # Print summary
        print(f"\nBinning Sensitivity Results:")
        print(f"  Mean O/R: {binning_results['mean_or']:.4f} ± {binning_results['std_or']:.4f}")
        print(f"  Coefficient of Variation: {binning_results['coefficient_of_variation']:.4f}")
        print(f"  Range: [{binning_results['min_or']:.4f}, {binning_results['max_or']:.4f}]")
        print(f"\n  O/R by k:")
        for k, or_val in zip(k_values, binning_results["or_indices"]):
            print(f"    k={k:3d}: O/R = {or_val:.4f}")

    # Save results
    output_path = results_dir / "binning_sensitivity_results.json"
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    # Statistical analysis
    print("\n" + "=" * 80)
    print("STATISTICAL ANALYSIS")
    print("=" * 80)

    if len(all_results) > 0:
        # Aggregate across checkpoints
        all_or_by_k = {k: [] for k in k_values}
        all_performances = []

        for result in all_results:
            all_performances.append(result["performance"]["mean_return"])
            for k, or_val in zip(k_values, result["binning_sensitivity"]["or_indices"]):
                if not np.isnan(or_val):
                    all_or_by_k[k].append(or_val)

        print(f"\nAggregated Results Across {len(all_results)} Checkpoint(s):")
        print(f"\n{'k':<10} {'Mean O/R':<12} {'Std O/R':<12} {'n':<8}")
        print("-" * 50)
        for k in k_values:
            if len(all_or_by_k[k]) > 0:
                mean_or = np.mean(all_or_by_k[k])
                std_or = np.std(all_or_by_k[k])
                n = len(all_or_by_k[k])
                print(f"{k:<10} {mean_or:<12.4f} {std_or:<12.4f} {n:<8}")

        # Correlation analysis
        print(f"\nCorrelation with Performance:")
        print(f"Performance range: [{np.min(all_performances):.2f}, {np.max(all_performances):.2f}]")

        if len(all_performances) > 1:
            for k in k_values:
                if len(all_or_by_k[k]) > 1:
                    # Match O/R values with performances
                    or_vals = all_or_by_k[k]
                    perf_vals = all_performances[:len(or_vals)]  # Truncate if needed

                    if len(or_vals) == len(perf_vals) and len(or_vals) > 1:
                        r, p = stats.pearsonr(or_vals, perf_vals)
                        print(f"  k={k:3d}: r = {r:.4f}, p = {p:.4f}")
        else:
            print("  (Need multiple checkpoints for correlation analysis)")

        # Stability assessment
        print(f"\nStability Assessment:")
        all_or_values = []
        for k in k_values:
            all_or_values.extend(all_or_by_k[k])

        if len(all_or_values) > 1:
            cv = np.std(all_or_values) / np.abs(np.mean(all_or_values))
            print(f"  Overall Coefficient of Variation: {cv:.4f}")
            if cv < 0.20:
                print(f"  ✅ STABLE: O/R shows low sensitivity to binning (CV < 0.20)")
            elif cv < 0.40:
                print(f"  ⚠️  MODERATE: O/R shows moderate sensitivity (0.20 ≤ CV < 0.40)")
            else:
                print(f"  ❌ UNSTABLE: O/R shows high sensitivity to binning (CV ≥ 0.40)")

    print("\n" + "=" * 80)
    print("ABLATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
