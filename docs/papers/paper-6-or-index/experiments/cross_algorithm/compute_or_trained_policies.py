#!/usr/bin/env python3
"""
Compute O/R Index for Trained Policies Across Algorithms
Loads checkpoints from DQN, SAC, and MAPPO and evaluates O/R metrics
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from pettingzoo.mpe import simple_spread_v3
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


# ========================================
# Network Architectures (must match trainers)
# ========================================

class QNetwork(nn.Module):
    """DQN Q-Network (from ma_dqn_trainer.py)"""
    def __init__(self, obs_dim, action_dim):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(obs_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, action_dim),
        )

    def forward(self, x):
        return self.network(x)


class Actor(nn.Module):
    """SAC Actor Network (from ma_sac_trainer.py)"""
    def __init__(self, obs_dim, action_dim):
        super().__init__()
        self.fc1 = nn.Linear(obs_dim, 256)
        self.fc2 = nn.Linear(256, 256)
        self.mean = nn.Linear(256, action_dim)
        self.log_std = nn.Linear(256, action_dim)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        mean = self.mean(x)
        log_std = self.log_std(x)
        log_std = torch.clamp(log_std, -20, 2)
        return mean, log_std

    def get_action(self, obs):
        """Sample action from policy"""
        mean, log_std = self(obs)
        std = log_std.exp()
        normal = torch.distributions.Normal(mean, std)
        x_t = normal.rsample()
        action = torch.tanh(x_t)
        log_prob = normal.log_prob(x_t)
        log_prob -= torch.log(1 - action.pow(2) + 1e-6)
        log_prob = log_prob.sum(1, keepdim=True)
        return action, log_prob


class Agent(nn.Module):
    """MAPPO Agent Network (from ma_mappo_trainer.py)"""
    def __init__(self, obs_dim, action_dim):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(obs_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
        )
        self.actor = nn.Linear(128, action_dim)
        self.critic = nn.Linear(128, 1)

    def get_value(self, x):
        features = self.network(x)
        return self.critic(features)

    def get_action_and_value(self, x, action=None):
        features = self.network(x)
        logits = self.actor(features)
        probs = torch.distributions.Categorical(logits=logits)
        if action is None:
            action = probs.sample()
        return action, probs.log_prob(action), probs.entropy(), self.critic(features)


# ========================================
# O/R Metrics
# ========================================

@dataclass
class ORMetrics:
    """O/R Index metrics"""
    observation_consistency: float
    reward_consistency: float
    or_index: float
    mean_reward: float
    algorithm: str
    seed: int
    episode: int


def compute_observation_consistency(observations):
    """O = 1 - mean(|| obs[t] - obs[t-1] || / || obs[t] ||)"""
    if len(observations) < 2:
        return 0.0

    differences = []
    for t in range(1, len(observations)):
        obs_prev, obs_curr = observations[t-1], observations[t]
        diff_norm = np.linalg.norm(obs_curr - obs_prev)
        obs_norm = np.linalg.norm(obs_curr)
        if obs_norm > 1e-8:
            differences.append(diff_norm / obs_norm)

    return max(0.0, 1.0 - np.mean(differences)) if differences else 0.0


def compute_reward_consistency(rewards):
    """R = 1 - (std(rewards) / (|mean(rewards)| + epsilon))"""
    if len(rewards) < 2:
        return 0.0

    std_reward = np.std(rewards)
    mean_reward = np.mean(rewards)
    normalized_std = std_reward / (abs(mean_reward) + 1e-8)

    return max(0.0, 1.0 - normalized_std)


# ========================================
# Checkpoint Loading
# ========================================

def load_dqn_checkpoint(seed, episode, obs_dim, action_dim):
    """Load DQN checkpoint from checkpoints/dqn/seed_X/episode_Y/"""
    checkpoint_dir = Path(f"checkpoints/dqn/seed_{seed}/episode_{episode}")

    if not checkpoint_dir.exists():
        print(f"  Warning: DQN checkpoint not found at {checkpoint_dir}")
        return None

    q_networks = {}
    for agent_id in range(3):
        agent_name = f"agent_{agent_id}"
        checkpoint_path = checkpoint_dir / f"{agent_name}.pt"

        if not checkpoint_path.exists():
            print(f"  Warning: Missing {checkpoint_path}")
            return None

        # Load checkpoint
        checkpoint = torch.load(checkpoint_path, map_location='cpu')

        # Create network and load weights
        q_network = QNetwork(obs_dim, action_dim)
        q_network.load_state_dict(checkpoint['q_network'])
        q_network.eval()

        q_networks[agent_name] = q_network

    return q_networks


def load_sac_checkpoint(seed, episode, obs_dim, action_dim):
    """Load SAC checkpoint from checkpoints/sac_cpu_backup/seed_X/episode_Y/"""
    checkpoint_dir = Path(f"checkpoints/sac_cpu_backup/seed_{seed}/episode_{episode}")

    if not checkpoint_dir.exists():
        print(f"  Warning: SAC checkpoint not found at {checkpoint_dir}")
        return None

    actors = {}
    for agent_id in range(3):
        agent_name = f"agent_{agent_id}"
        checkpoint_path = checkpoint_dir / f"{agent_name}.pt"

        if not checkpoint_path.exists():
            print(f"  Warning: Missing {checkpoint_path}")
            return None

        # Load checkpoint
        checkpoint = torch.load(checkpoint_path, map_location='cpu')

        # Create actor and load weights
        actor = Actor(obs_dim, action_dim)
        actor.load_state_dict(checkpoint['actor'])
        actor.eval()

        actors[agent_name] = actor

    return actors


def load_mappo_checkpoint(seed, episode, obs_dim, action_dim):
    """Load MAPPO checkpoint from checkpoints/episode_Y/"""
    # Note: MAPPO checkpoints don't have seed subdirectory
    # We'll use the episode checkpoint and assume it's from the requested seed
    checkpoint_dir = Path(f"checkpoints/episode_{episode}")

    if not checkpoint_dir.exists():
        print(f"  Warning: MAPPO checkpoint not found at {checkpoint_dir}")
        return None

    agents = {}
    for agent_id in range(3):
        agent_name = f"agent_{agent_id}"
        checkpoint_path = checkpoint_dir / f"{agent_name}.pt"

        if not checkpoint_path.exists():
            print(f"  Warning: Missing {checkpoint_path}")
            return None

        # Load checkpoint
        checkpoint = torch.load(checkpoint_path, map_location='cpu')

        # Create agent and load weights
        agent = Agent(obs_dim, action_dim)
        agent.load_state_dict(checkpoint['agent'])
        agent.eval()

        agents[agent_name] = agent

    return agents


# ========================================
# Policy Evaluation
# ========================================

def evaluate_dqn_policy(q_networks, num_episodes=10, seed=42):
    """Evaluate DQN policy deterministically"""
    env = simple_spread_v3.parallel_env(N=3, max_cycles=25, continuous_actions=False)

    all_observations = []
    all_rewards = []

    for ep in range(num_episodes):
        observations_dict, info = env.reset(seed=seed + ep)
        agents = env.possible_agents
        done = False

        while not done:
            # Store concatenated observations
            obs_concat = np.concatenate([observations_dict[agent] for agent in agents])
            all_observations.append(obs_concat)

            # Get greedy actions (no exploration)
            actions = {}
            for agent in agents:
                with torch.no_grad():
                    obs_tensor = torch.FloatTensor(observations_dict[agent]).unsqueeze(0)
                    q_values = q_networks[agent](obs_tensor)
                    action = q_values.argmax().item()
                    actions[agent] = action

            # Environment step
            observations_dict, rewards_dict, terminations, truncations, _ = env.step(actions)

            mean_reward = np.mean([rewards_dict[agent] for agent in agents])
            all_rewards.append(mean_reward)

            done = all(terminations.values()) or all(truncations.values())

    env.close()
    return all_observations, all_rewards


def evaluate_sac_policy(actors, num_episodes=10, seed=42):
    """Evaluate SAC policy deterministically (use mean, not sample)"""
    env = simple_spread_v3.parallel_env(N=3, max_cycles=25, continuous_actions=False)

    all_observations = []
    all_rewards = []

    for ep in range(num_episodes):
        observations_dict, info = env.reset(seed=seed + ep)
        agents = env.possible_agents
        done = False

        while not done:
            # Store concatenated observations
            obs_concat = np.concatenate([observations_dict[agent] for agent in agents])
            all_observations.append(obs_concat)

            # Get deterministic actions (use mean, not sample)
            actions = {}
            for agent in agents:
                with torch.no_grad():
                    obs_tensor = torch.FloatTensor(observations_dict[agent]).unsqueeze(0)
                    mean, _ = actors[agent](obs_tensor)
                    action = torch.tanh(mean)
                    # Convert continuous action to discrete (argmax over action dimensions)
                    discrete_action = action.squeeze(0).argmax().item()
                    actions[agent] = discrete_action

            # Environment step
            observations_dict, rewards_dict, terminations, truncations, _ = env.step(actions)

            mean_reward = np.mean([rewards_dict[agent] for agent in agents])
            all_rewards.append(mean_reward)

            done = all(terminations.values()) or all(truncations.values())

    env.close()
    return all_observations, all_rewards


def evaluate_mappo_policy(agents, num_episodes=10, seed=42):
    """Evaluate MAPPO policy deterministically (greedy action)"""
    env = simple_spread_v3.parallel_env(N=3, max_cycles=25, continuous_actions=False)

    all_observations = []
    all_rewards = []

    for ep in range(num_episodes):
        observations_dict, info = env.reset(seed=seed + ep)
        agent_names = env.possible_agents
        done = False

        while not done:
            # Store concatenated observations
            obs_concat = np.concatenate([observations_dict[agent] for agent in agent_names])
            all_observations.append(obs_concat)

            # Get greedy actions (argmax of logits)
            actions = {}
            for agent_name in agent_names:
                with torch.no_grad():
                    obs_tensor = torch.FloatTensor(observations_dict[agent_name]).unsqueeze(0)
                    features = agents[agent_name].network(obs_tensor)
                    logits = agents[agent_name].actor(features)
                    action = logits.argmax().item()
                    actions[agent_name] = action

            # Environment step
            observations_dict, rewards_dict, terminations, truncations, _ = env.step(actions)

            mean_reward = np.mean([rewards_dict[agent] for agent in agent_names])
            all_rewards.append(mean_reward)

            done = all(terminations.values()) or all(truncations.values())

    env.close()
    return all_observations, all_rewards


# ========================================
# Main Evaluation
# ========================================

def main():
    """Evaluate trained policies and compute O/R metrics"""
    print("=" * 80)
    print("Cross-Algorithm O/R Index Computation (Trained Policies)")
    print("=" * 80)

    # Get environment dimensions
    env = simple_spread_v3.parallel_env(N=3, max_cycles=25, continuous_actions=False)
    sample_agent = env.possible_agents[0]
    obs_dim = env.observation_space(sample_agent).shape[0]
    action_dim = env.action_space(sample_agent).n
    env.close()

    print(f"\nEnvironment: simple_spread_v3")
    print(f"Observation dim: {obs_dim}")
    print(f"Action dim: {action_dim}")
    print(f"Agents: 3")

    # Configuration
    algorithms = ["DQN", "SAC", "MAPPO"]
    seeds = [42, 123, 456]
    episodes = [100, 500, 1000]  # Early, mid, late training

    all_metrics = []

    # Evaluate each algorithm
    for algo in algorithms:
        print(f"\n{'=' * 80}")
        print(f"{algo} Policy Evaluation")
        print("=" * 80)

        for seed in seeds:
            for ep in episodes:
                print(f"\n  Loading {algo} seed {seed} episode {ep}...")

                # Load checkpoint
                if algo == "DQN":
                    networks = load_dqn_checkpoint(seed, ep, obs_dim, action_dim)
                    evaluate_fn = evaluate_dqn_policy
                elif algo == "SAC":
                    networks = load_sac_checkpoint(seed, ep, obs_dim, action_dim)
                    evaluate_fn = evaluate_sac_policy
                else:  # MAPPO
                    networks = load_mappo_checkpoint(seed, ep, obs_dim, action_dim)
                    evaluate_fn = evaluate_mappo_policy

                if networks is None:
                    print(f"  ⚠️  Skipping {algo} seed {seed} episode {ep} (checkpoint not found)")
                    continue

                # Evaluate policy
                print(f"  Running evaluation episodes...")
                observations, rewards = evaluate_fn(networks, num_episodes=10, seed=seed)

                # Compute O/R metrics
                O = compute_observation_consistency(observations)
                R = compute_reward_consistency(rewards)
                OR = O / (R + 1e-8) if R > 1e-8 else 0.0

                metrics = ORMetrics(
                    observation_consistency=O,
                    reward_consistency=R,
                    or_index=OR,
                    mean_reward=np.mean(rewards),
                    algorithm=algo,
                    seed=seed,
                    episode=ep
                )

                all_metrics.append(metrics)
                print(f"  ✅ O={O:.3f}, R={R:.3f}, O/R={OR:.3f}, Reward={np.mean(rewards):.2f}")

    # Save results
    results_file = "or_trained_policies.json"
    results = {
        "metadata": {
            "note": "Trained policy O/R metrics for cross-algorithm validation",
            "algorithms": algorithms,
            "seeds": seeds,
            "episodes": episodes,
            "total_measurements": len(all_metrics)
        },
        "metrics": [asdict(m) for m in all_metrics]
    }

    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Results saved to {results_file}")
    print(f"📊 Total measurements: {len(all_metrics)}")

    # Summary by algorithm
    print("\n" + "=" * 80)
    print("Summary by Algorithm:")
    print("=" * 80)

    for algo in algorithms:
        algo_metrics = [m for m in all_metrics if m.algorithm == algo]
        if not algo_metrics:
            print(f"\n{algo}: No data")
            continue

        all_O = [m.observation_consistency for m in algo_metrics]
        all_R = [m.reward_consistency for m in algo_metrics]
        all_OR = [m.or_index for m in algo_metrics]
        all_rew = [m.mean_reward for m in algo_metrics]

        print(f"\n{algo} (n={len(algo_metrics)}):")
        print(f"  O (Observation Consistency): {np.mean(all_O):.3f} ± {np.std(all_O):.3f}")
        print(f"  R (Reward Consistency):       {np.mean(all_R):.3f} ± {np.std(all_R):.3f}")
        print(f"  O/R Index:                    {np.mean(all_OR):.3f} ± {np.std(all_OR):.3f}")
        print(f"  Mean Reward:                  {np.mean(all_rew):.2f} ± {np.std(all_rew):.2f}")

    # Comparison to random baseline
    print("\n" + "=" * 80)
    print("Comparison to Random Baseline:")
    print("=" * 80)
    print("\nRandom Policy Baseline (from or_random_baseline.json):")
    print("  O = 0.788 ± 0.015")
    print("  R = 0.657 ± 0.087")
    print("  O/R = 1.222 ± 0.176")

    if all_metrics:
        trained_O = np.mean([m.observation_consistency for m in all_metrics])
        trained_R = np.mean([m.reward_consistency for m in all_metrics])
        trained_OR = np.mean([m.or_index for m in all_metrics])

        print(f"\nTrained Policies Average (all algorithms):")
        print(f"  O = {trained_O:.3f}")
        print(f"  R = {trained_R:.3f}")
        print(f"  O/R = {trained_OR:.3f}")

        print(f"\nDifference (Trained - Random):")
        print(f"  ΔO = {trained_O - 0.788:+.3f}")
        print(f"  ΔR = {trained_R - 0.657:+.3f}")
        print(f"  ΔO/R = {trained_OR - 1.222:+.3f}")

    print("\n✅ Cross-algorithm O/R computation complete!")
    print("📋 Next: Statistical analysis and Section 5.7 writing")


if __name__ == "__main__":
    main()
