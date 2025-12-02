#!/usr/bin/env python3
"""
Compute O/R Index for Available Checkpoints
Works with the actual checkpoint organization (mixed DQN/SAC/MAPPO)
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from pettingzoo.mpe import simple_spread_v3
import warnings
warnings.filterwarnings('ignore')


# ========================================
# Network Architectures
# ========================================

class QNetwork(nn.Module):
    """DQN Q-Network"""
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
    """SAC Actor Network"""
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


class Agent(nn.Module):
    """MAPPO Agent Network"""
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


# ========================================
# Metrics and Evaluation
# ========================================

@dataclass
class ORMetrics:
    observation_consistency: float
    reward_consistency: float
    or_index: float
    mean_reward: float
    algorithm: str
    seed: int
    episode: int


def compute_observation_consistency(observations):
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
    if len(rewards) < 2:
        return 0.0
    std_reward = np.std(rewards)
    mean_reward = np.mean(rewards)
    normalized_std = std_reward / (abs(mean_reward) + 1e-8)
    return max(0.0, 1.0 - normalized_std)


def evaluate_dqn_policy(q_networks, num_episodes=10, seed=42):
    env = simple_spread_v3.parallel_env(N=3, max_cycles=25, continuous_actions=False)
    all_observations, all_rewards = [], []

    for ep in range(num_episodes):
        observations_dict, info = env.reset(seed=seed + ep)
        agents = env.possible_agents
        done = False

        while not done:
            obs_concat = np.concatenate([observations_dict[agent] for agent in agents])
            all_observations.append(obs_concat)

            actions = {}
            for agent in agents:
                with torch.no_grad():
                    obs_tensor = torch.FloatTensor(observations_dict[agent]).unsqueeze(0)
                    q_values = q_networks[agent](obs_tensor)
                    action = q_values.argmax().item()
                    actions[agent] = action

            observations_dict, rewards_dict, terminations, truncations, _ = env.step(actions)
            mean_reward = np.mean([rewards_dict[agent] for agent in agents])
            all_rewards.append(mean_reward)
            done = all(terminations.values()) or all(truncations.values())

    env.close()
    return all_observations, all_rewards


def evaluate_sac_policy(actors, num_episodes=10, seed=42):
    env = simple_spread_v3.parallel_env(N=3, max_cycles=25, continuous_actions=False)
    all_observations, all_rewards = [], []

    for ep in range(num_episodes):
        observations_dict, info = env.reset(seed=seed + ep)
        agents = env.possible_agents
        done = False

        while not done:
            obs_concat = np.concatenate([observations_dict[agent] for agent in agents])
            all_observations.append(obs_concat)

            actions = {}
            for agent in agents:
                with torch.no_grad():
                    obs_tensor = torch.FloatTensor(observations_dict[agent]).unsqueeze(0)
                    mean, _ = actors[agent](obs_tensor)
                    action = torch.tanh(mean)
                    discrete_action = action.squeeze(0).argmax().item()
                    actions[agent] = discrete_action

            observations_dict, rewards_dict, terminations, truncations, _ = env.step(actions)
            mean_reward = np.mean([rewards_dict[agent] for agent in agents])
            all_rewards.append(mean_reward)
            done = all(terminations.values()) or all(truncations.values())

    env.close()
    return all_observations, all_rewards


def evaluate_mappo_policy(agents, num_episodes=10, seed=42):
    env = simple_spread_v3.parallel_env(N=3, max_cycles=25, continuous_actions=False)
    all_observations, all_rewards = [], []

    for ep in range(num_episodes):
        observations_dict, info = env.reset(seed=seed + ep)
        agent_names = env.possible_agents
        done = False

        while not done:
            obs_concat = np.concatenate([observations_dict[agent] for agent in agent_names])
            all_observations.append(obs_concat)

            actions = {}
            for agent_name in agent_names:
                with torch.no_grad():
                    obs_tensor = torch.FloatTensor(observations_dict[agent_name]).unsqueeze(0)
                    features = agents[agent_name].network(obs_tensor)
                    logits = agents[agent_name].actor(features)
                    action = logits.argmax().item()
                    actions[agent_name] = action

            observations_dict, rewards_dict, terminations, truncations, _ = env.step(actions)
            mean_reward = np.mean([rewards_dict[agent] for agent in agent_names])
            all_rewards.append(mean_reward)
            done = all(terminations.values()) or all(truncations.values())

    env.close()
    return all_observations, all_rewards


# ========================================
# Checkpoint Loading
# ========================================

def load_dqn_checkpoint(seed, episode, obs_dim, action_dim):
    checkpoint_dir = Path(f"checkpoints/dqn/seed_{seed}/episode_{episode}")
    if not checkpoint_dir.exists():
        return None

    q_networks = {}
    for agent_id in range(3):
        agent_name = f"agent_{agent_id}"
        checkpoint_path = checkpoint_dir / f"{agent_name}.pt"
        if not checkpoint_path.exists():
            return None

        checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
        q_network = QNetwork(obs_dim, action_dim)
        q_network.load_state_dict(checkpoint['q_network'])
        q_network.eval()
        q_networks[agent_name] = q_network

    return q_networks


def load_sac_checkpoint_from_backup(seed, obs_dim, action_dim):
    """Load SAC checkpoint from CPU backup (episode 100 only)"""
    checkpoint_dir = Path(f"checkpoints/sac_cpu_backup/seed_{seed}/episode_100")
    if not checkpoint_dir.exists():
        return None

    actors = {}
    for agent_id in range(3):
        agent_name = f"agent_{agent_id}"
        checkpoint_path = checkpoint_dir / f"{agent_name}.pt"
        if not checkpoint_path.exists():
            return None

        checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
        actor = Actor(obs_dim, action_dim)
        actor.load_state_dict(checkpoint['actor'])
        actor.eval()
        actors[agent_name] = actor

    return actors


def load_sac_checkpoint_from_gpu(episode, obs_dim, action_dim):
    """Load SAC checkpoint from GPU training (episodes 500/1000, seed 456 only)"""
    checkpoint_dir = Path(f"checkpoints/episode_{episode}")
    if not checkpoint_dir.exists():
        return None

    # Check if it's actually SAC (not MAPPO)
    test_ckpt = torch.load(checkpoint_dir / "agent_0.pt", map_location='cpu', weights_only=False)
    if 'actor' not in test_ckpt:
        return None  # This is MAPPO, not SAC

    actors = {}
    for agent_id in range(3):
        agent_name = f"agent_{agent_id}"
        checkpoint_path = checkpoint_dir / f"{agent_name}.pt"
        if not checkpoint_path.exists():
            return None

        checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
        actor = Actor(obs_dim, action_dim)
        actor.load_state_dict(checkpoint['actor'])
        actor.eval()
        actors[agent_name] = actor

    return actors


def load_mappo_checkpoint(episode, obs_dim, action_dim):
    """Load MAPPO checkpoint (episodes 100/200, seed 456 only)"""
    checkpoint_dir = Path(f"checkpoints/episode_{episode}")
    if not checkpoint_dir.exists():
        return None

    # Check if it's actually MAPPO (not SAC)
    test_ckpt = torch.load(checkpoint_dir / "agent_0.pt", map_location='cpu', weights_only=False)
    if 'agent' not in test_ckpt or 'actor' in test_ckpt:
        return None  # This is SAC, not MAPPO

    agents = {}
    for agent_id in range(3):
        agent_name = f"agent_{agent_id}"
        checkpoint_path = checkpoint_dir / f"{agent_name}.pt"
        if not checkpoint_path.exists():
            return None

        checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
        agent = Agent(obs_dim, action_dim)
        agent.load_state_dict(checkpoint['agent'])
        agent.eval()
        agents[agent_name] = agent

    return agents


# ========================================
# Main Evaluation
# ========================================

def main():
    print("=" * 80)
    print("Cross-Algorithm O/R Index Computation (Available Checkpoints)")
    print("=" * 80)

    env = simple_spread_v3.parallel_env(N=3, max_cycles=25, continuous_actions=False)
    sample_agent = env.possible_agents[0]
    obs_dim = env.observation_space(sample_agent).shape[0]
    action_dim = env.action_space(sample_agent).n
    env.close()

    print(f"\nEnvironment: simple_spread_v3")
    print(f"Observation dim: {obs_dim}, Action dim: {action_dim}\n")

    all_metrics = []

    # ========================================
    # DQN (3 seeds × 3 episodes)
    # ========================================
    print("=" * 80)
    print("DQN Policy Evaluation (3 seeds × 3 episodes)")
    print("=" * 80)

    for seed in [42, 123, 456]:
        for ep in [100, 500, 1000]:
            print(f"\n  DQN seed {seed} episode {ep}...", end=" ")
            networks = load_dqn_checkpoint(seed, ep, obs_dim, action_dim)

            if networks is None:
                print("❌ Not found")
                continue

            observations, rewards = evaluate_dqn_policy(networks, num_episodes=10, seed=seed)
            O = compute_observation_consistency(observations)
            R = compute_reward_consistency(rewards)
            OR = O / (R + 1e-8) if R > 1e-8 else 0.0

            metrics = ORMetrics(O, R, OR, np.mean(rewards), "DQN", seed, ep)
            all_metrics.append(metrics)
            print(f"✅ O={O:.3f}, R={R:.3f}, O/R={OR:.3f}, Reward={np.mean(rewards):.2f}")

    # ========================================
    # SAC (3 seeds × episode 100 + seed 456 × episodes 500, 1000)
    # ========================================
    print("\n" + "=" * 80)
    print("SAC Policy Evaluation")
    print("=" * 80)

    # Episode 100 from all 3 seeds (CPU backup)
    for seed in [42, 123, 456]:
        print(f"\n  SAC seed {seed} episode 100 (CPU backup)...", end=" ")
        actors = load_sac_checkpoint_from_backup(seed, obs_dim, action_dim)

        if actors is None:
            print("❌ Not found")
            continue

        observations, rewards = evaluate_sac_policy(actors, num_episodes=10, seed=seed)
        O = compute_observation_consistency(observations)
        R = compute_reward_consistency(rewards)
        OR = O / (R + 1e-8) if R > 1e-8 else 0.0

        metrics = ORMetrics(O, R, OR, np.mean(rewards), "SAC", seed, 100)
        all_metrics.append(metrics)
        print(f"✅ O={O:.3f}, R={R:.3f}, O/R={OR:.3f}, Reward={np.mean(rewards):.2f}")

    # Episodes 500, 1000 from seed 456 (GPU training)
    for ep in [500, 1000]:
        print(f"\n  SAC seed 456 episode {ep} (GPU)...", end=" ")
        actors = load_sac_checkpoint_from_gpu(ep, obs_dim, action_dim)

        if actors is None:
            print("❌ Not found")
            continue

        observations, rewards = evaluate_sac_policy(actors, num_episodes=10, seed=456)
        O = compute_observation_consistency(observations)
        R = compute_reward_consistency(rewards)
        OR = O / (R + 1e-8) if R > 1e-8 else 0.0

        metrics = ORMetrics(O, R, OR, np.mean(rewards), "SAC", 456, ep)
        all_metrics.append(metrics)
        print(f"✅ O={O:.3f}, R={R:.3f}, O/R={OR:.3f}, Reward={np.mean(rewards):.2f}")

    # ========================================
    # MAPPO (seed 456 × episodes 100, 200)
    # ========================================
    print("\n" + "=" * 80)
    print("MAPPO Policy Evaluation (seed 456 only)")
    print("=" * 80)

    for ep in [100, 200]:
        print(f"\n  MAPPO seed 456 episode {ep}...", end=" ")
        agents = load_mappo_checkpoint(ep, obs_dim, action_dim)

        if agents is None:
            print("❌ Not found")
            continue

        observations, rewards = evaluate_mappo_policy(agents, num_episodes=10, seed=456)
        O = compute_observation_consistency(observations)
        R = compute_reward_consistency(rewards)
        OR = O / (R + 1e-8) if R > 1e-8 else 0.0

        metrics = ORMetrics(O, R, OR, np.mean(rewards), "MAPPO", 456, ep)
        all_metrics.append(metrics)
        print(f"✅ O={O:.3f}, R={R:.3f}, O/R={OR:.3f}, Reward={np.mean(rewards):.2f}")

    # ========================================
    # Save and Summarize
    # ========================================
    results_file = "or_cross_algorithm_results.json"
    results = {
        "metadata": {
            "note": "Cross-algorithm O/R validation with available checkpoints",
            "total_measurements": len(all_metrics),
            "dqn_measurements": len([m for m in all_metrics if m.algorithm == "DQN"]),
            "sac_measurements": len([m for m in all_metrics if m.algorithm == "SAC"]),
            "mappo_measurements": len([m for m in all_metrics if m.algorithm == "MAPPO"])
        },
        "metrics": [asdict(m) for m in all_metrics]
    }

    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 80)
    print("Summary by Algorithm")
    print("=" * 80)

    for algo in ["DQN", "SAC", "MAPPO"]:
        algo_metrics = [m for m in all_metrics if m.algorithm == algo]
        if not algo_metrics:
            continue

        all_O = [m.observation_consistency for m in algo_metrics]
        all_R = [m.reward_consistency for m in algo_metrics]
        all_OR = [m.or_index for m in algo_metrics]
        all_rew = [m.mean_reward for m in algo_metrics]

        print(f"\n{algo} (n={len(algo_metrics)}):")
        print(f"  O:   {np.mean(all_O):.3f} ± {np.std(all_O):.3f}")
        print(f"  R:   {np.mean(all_R):.3f} ± {np.std(all_R):.3f}")
        print(f"  O/R: {np.mean(all_OR):.3f} ± {np.std(all_OR):.3f}")
        print(f"  Reward: {np.mean(all_rew):.2f} ± {np.std(all_rew):.2f}")

    print(f"\n✅ Results saved to {results_file}")
    print(f"📊 Total measurements: {len(all_metrics)}")
    print("\n✅ Cross-algorithm O/R computation complete!")


if __name__ == "__main__":
    main()
