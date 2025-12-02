#!/usr/bin/env python3
"""
Binning Sensitivity Ablation for PPO Ant-v4.

Tests O/R Index stability across different discretization granularities (k bins).
This validates that the metric is robust to binning choice.

Target: CV < 0.20 across k ∈ {5, 10, 20, 50, 100}
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import gymnasium as gym
import numpy as np
import torch
import torch.nn as nn
from torch.distributions.normal import Normal
from sklearn.cluster import KMeans


@dataclass
class Args:
    """Training arguments (needed for unpickling checkpoint)."""
    exp_name: str = "ppo_ant_binning"
    seed: int = 42
    torch_deterministic: bool = True
    cuda: bool = True
    env_name: str = "Ant-v4"
    total_timesteps: int = 50_000
    learning_rate: float = 3e-4
    num_steps: int = 2048
    num_epochs: int = 10
    num_minibatches: int = 32
    gamma: float = 0.99
    gae_lambda: float = 0.95
    clip_coef: float = 0.2
    ent_coef: float = 0.01
    vf_coef: float = 0.5
    max_grad_norm: float = 0.5
    checkpoint_freq: int = 10_000
    checkpoint_dir: str = "checkpoints"
    log_dir: str = "logs"


class Agent(nn.Module):
    """Simple actor-critic network for continuous control (from train_ppo_ant.py)."""

    def __init__(self, obs_dim: int, action_dim: int, hidden_dim: int = 256):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(obs_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
        )
        self.actor_mean = nn.Linear(hidden_dim, action_dim)
        self.actor_logstd = nn.Parameter(torch.zeros(action_dim))
        self.critic = nn.Linear(hidden_dim, 1)

    def get_value(self, x):
        return self.critic(self.network(x))

    def get_action_and_value(self, x, action=None):
        hidden = self.network(x)
        action_mean = self.actor_mean(hidden)
        action_std = self.actor_logstd.exp()
        probs = Normal(action_mean, action_std)
        if action is None:
            action = probs.sample()
        return action, probs.log_prob(action).sum(1), probs.entropy().sum(1), self.critic(hidden)


def load_checkpoint(checkpoint_path: str) -> Tuple[torch.nn.Module, int, int]:
    """Load PPO checkpoint."""
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)

    # Extract dimensions from saved args
    # For Ant-v4: obs_dim=27, action_dim=8
    obs_dim = 27
    action_dim = 8

    # Create agent and load weights
    agent = Agent(obs_dim, action_dim)
    agent.load_state_dict(checkpoint['agent_state_dict'])
    agent.eval()

    print(f"Loaded checkpoint from {checkpoint_path}")
    print(f"Observation dim: {obs_dim}, Action dim: {action_dim}")

    return agent, obs_dim, action_dim


def collect_trajectories(env, agent, num_episodes: int = 50) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Collect observation, action, and reward data from policy rollouts."""
    observations = []
    actions = []
    rewards = []

    for episode in range(num_episodes):
        obs, _ = env.reset()
        episode_obs = [obs]
        episode_actions = []
        episode_rewards = []

        done = False
        while not done:
            obs_tensor = torch.FloatTensor(obs).unsqueeze(0)
            with torch.no_grad():
                action, _, _, _ = agent.get_action_and_value(obs_tensor)
            action_np = action.cpu().numpy()[0]

            obs, reward, terminated, truncated, _ = env.step(action_np)
            done = terminated or truncated

            episode_obs.append(obs)
            episode_actions.append(action_np)
            episode_rewards.append(reward)

        observations.extend(episode_obs[:-1])  # Don't include terminal observation
        actions.extend(episode_actions)
        rewards.extend(episode_rewards)

        if (episode + 1) % 10 == 0:
            print(f"  Collected {episode + 1}/{num_episodes} episodes...")

    return np.array(observations), np.array(actions), np.array(rewards)


def discretize_with_kmeans(data: np.ndarray, k: int) -> np.ndarray:
    """Discretize continuous data using K-means clustering."""
    if data.ndim == 1:
        data = data.reshape(-1, 1)

    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(data)
    return labels


def compute_or_index(obs_bins: np.ndarray, reward_bins: np.ndarray) -> float:
    """Compute O/R Index = log(R_consistency / O_consistency)."""
    n_samples = len(obs_bins)

    # Observation consistency
    unique_obs, counts_obs = np.unique(obs_bins, return_counts=True)
    p_obs = counts_obs / n_samples
    O_consistency = np.sum(p_obs ** 2)  # Concentration measure

    # Reward consistency
    unique_reward, counts_reward = np.unique(reward_bins, return_counts=True)
    p_reward = counts_reward / n_samples
    R_consistency = np.sum(p_reward ** 2)

    # O/R Index
    or_index = np.log(R_consistency / (O_consistency + 1e-10))

    return or_index


def run_binning_sensitivity(checkpoint_path: str, bin_counts: List[int]) -> Dict:
    """Run binning sensitivity ablation."""
    print("=" * 80)
    print("BINNING SENSITIVITY ABLATION - PPO ANT-V4")
    print("=" * 80)

    # Load checkpoint
    agent, obs_dim, action_dim = load_checkpoint(checkpoint_path)

    # Create environment
    env = gym.make("Ant-v4")

    print("\nCollecting trajectories...")
    observations, actions, rewards = collect_trajectories(env, agent, num_episodes=50)
    env.close()

    print(f"\nCollected {len(observations)} steps")
    print(f"Observations shape: {observations.shape}")
    print(f"Actions shape: {actions.shape}")
    print(f"Rewards shape: {rewards.shape}")

    # Run ablation for different bin counts
    results = []
    print(f"\nTesting bin counts: {bin_counts}")
    print("-" * 80)

    for k in bin_counts:
        print(f"\nBin count k={k}:")

        # Discretize observations (use all dimensions combined)
        obs_flat = observations.reshape(observations.shape[0], -1)
        obs_bins = discretize_with_kmeans(obs_flat, k)

        # Discretize rewards
        reward_bins = discretize_with_kmeans(rewards, k)

        # Compute O/R Index
        or_index = compute_or_index(obs_bins, reward_bins)

        print(f"  O/R Index: {or_index:.4f}")

        results.append({
            "k": k,
            "or_index": float(or_index),
            "n_samples": len(observations)
        })

    # Compute statistics
    or_values = [r["or_index"] for r in results]
    mean_or = np.mean(or_values)
    std_or = np.std(or_values, ddof=1)
    cv = std_or / abs(mean_or) if mean_or != 0 else float('inf')

    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print(f"Mean O/R: {mean_or:.4f}")
    print(f"Std O/R: {std_or:.4f}")
    print(f"Coefficient of Variation: {cv:.4f}")
    print(f"Target: CV < 0.20 → {'✅ PASS' if cv < 0.20 else '❌ FAIL'}")
    print("=" * 80)

    return {
        "checkpoint": str(checkpoint_path),
        "bin_counts": bin_counts,
        "results": results,
        "statistics": {
            "mean_or": float(mean_or),
            "std_or": float(std_or),
            "cv": float(cv),
            "pass_threshold": bool(cv < 0.20)  # Convert numpy bool_ to Python bool
        }
    }


def main():
    """Main execution."""
    checkpoint_path = Path("checkpoints/ppo_ant_checkpoint_49152.pt")
    output_path = Path("results/binning_sensitivity_ppo_ant.json")
    output_path.parent.mkdir(exist_ok=True)

    # Bin counts to test
    bin_counts = [5, 10, 20, 50, 100]

    # Run ablation
    results = run_binning_sensitivity(checkpoint_path, bin_counts)

    # Save results
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Results saved to: {output_path}")


if __name__ == "__main__":
    main()
