#!/usr/bin/env python3
"""
QMIX O/R Index Computation
Evaluates QMIX checkpoints and computes O/R metrics
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
# QMIX Network Architectures
# ========================================

class AgentQNetwork(nn.Module):
    """Individual agent Q-network (observation → Q-values)"""
    def __init__(self, obs_dim, action_dim):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(obs_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim),
        )

    def forward(self, obs):
        return self.network(obs)


class QMixerNetwork(nn.Module):
    """
    QMIX Mixing Network with Hypernetworks

    Takes individual Q-values and state, outputs joint Q-value Q_tot.
    Uses hypernetworks to generate mixing network weights, ensuring monotonicity
    by constraining weights to be non-negative (via abs).
    """
    def __init__(self, num_agents, state_dim, mixing_embed_dim=32, hypernet_embed=64):
        super().__init__()
        self.num_agents = num_agents
        self.state_dim = state_dim
        self.embed_dim = mixing_embed_dim

        # Hypernetwork for first layer weights (state → weights)
        self.hyper_w1 = nn.Sequential(
            nn.Linear(state_dim, hypernet_embed),
            nn.ReLU(),
            nn.Linear(hypernet_embed, num_agents * mixing_embed_dim),
        )

        # Hypernetwork for first layer bias
        self.hyper_b1 = nn.Linear(state_dim, mixing_embed_dim)

        # Hypernetwork for second layer weights
        self.hyper_w2 = nn.Sequential(
            nn.Linear(state_dim, hypernet_embed),
            nn.ReLU(),
            nn.Linear(hypernet_embed, mixing_embed_dim),
        )

        # Hypernetwork for second layer bias (scalar)
        self.hyper_b2 = nn.Sequential(
            nn.Linear(state_dim, mixing_embed_dim),
            nn.ReLU(),
            nn.Linear(mixing_embed_dim, 1),
        )

    def forward(self, agent_qs, state):
        """
        Args:
            agent_qs: (batch_size, num_agents) - individual Q-values
            state: (batch_size, state_dim) - global state

        Returns:
            q_tot: (batch_size, 1) - joint Q-value
        """
        batch_size = agent_qs.size(0)

        # Generate weights and biases from state using hypernetworks
        # Apply abs() to ensure monotonicity (∂Qtot/∂Qi ≥ 0)
        w1 = torch.abs(self.hyper_w1(state))  # (batch, num_agents * embed_dim)
        b1 = self.hyper_b1(state)  # (batch, embed_dim)
        w1 = w1.view(batch_size, self.num_agents, self.embed_dim)

        w2 = torch.abs(self.hyper_w2(state))  # (batch, embed_dim)
        b2 = self.hyper_b2(state)  # (batch, 1)
        w2 = w2.view(batch_size, self.embed_dim, 1)

        # First layer: (batch, num_agents) @ (batch, num_agents, embed) + (batch, embed)
        # agent_qs: (batch, num_agents, 1)
        agent_qs_reshaped = agent_qs.unsqueeze(1)  # (batch, 1, num_agents)
        hidden = torch.bmm(agent_qs_reshaped, w1)  # (batch, 1, embed_dim)
        hidden = hidden.squeeze(1) + b1  # (batch, embed_dim)
        hidden = F.elu(hidden)  # Non-linear activation

        # Second layer: (batch, embed) @ (batch, embed, 1) + (batch, 1)
        hidden = hidden.unsqueeze(1)  # (batch, 1, embed)
        q_tot = torch.bmm(hidden, w2).squeeze(1) + b2  # (batch, 1)

        return q_tot


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


def evaluate_qmix_policy(agent_networks, mixer, num_episodes=10):
    """Evaluate QMIX policy and collect O/R metrics"""
    env = simple_spread_v3.parallel_env(N=3, max_cycles=25, continuous_actions=False)
    device = next(agent_networks[0].parameters()).device

    all_observations = []
    all_rewards = []
    episode_rewards = []

    for episode in range(num_episodes):
        obs, info = env.reset(seed=42 + episode)
        episode_reward = 0
        episode_obs = []

        # Store agent names at start of episode
        agent_names = list(obs.keys())

        for step in range(25):
            # Get observations for all agents
            obs_arrays = [obs[agent] for agent in agent_names if agent in obs]
            episode_obs.extend(obs_arrays)

            # Select actions using QMIX (greedy)
            actions = {}
            agent_qs_list = []

            for i, agent in enumerate(agent_names):
                if agent not in obs:
                    continue
                obs_tensor = torch.FloatTensor(obs[agent]).unsqueeze(0).to(device)
                with torch.no_grad():
                    q_values = agent_networks[i](obs_tensor)
                    action = q_values.argmax(dim=1).item()
                    actions[agent] = action
                    agent_qs_list.append(q_values.max(dim=1, keepdim=True)[0])

            # Step environment
            next_obs, rewards, terminations, truncations, infos = env.step(actions)

            # Collect rewards (use first agent's reward as team reward)
            if agent_names[0] in rewards:
                team_reward = rewards[agent_names[0]]
                all_rewards.append(team_reward)
                episode_reward += team_reward

            obs = next_obs

            if any(terminations.values()) or any(truncations.values()):
                break

        all_observations.extend(episode_obs)
        episode_rewards.append(episode_reward)

    env.close()

    # Compute O/R metrics
    O = compute_observation_consistency(all_observations)
    R = compute_reward_consistency(all_rewards)
    OR = O / (R + 1e-8) if R > 1e-8 else 0.0
    mean_reward = np.mean(episode_rewards)

    return O, R, OR, mean_reward


# ========================================
# Main Computation
# ========================================

def main():
    print("=" * 80)
    print("QMIX O/R Index Computation")
    print("=" * 80)
    print()

    # Setup
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    print()

    # Environment dimensions
    env = simple_spread_v3.parallel_env(N=3, max_cycles=25, continuous_actions=False)
    env.reset(seed=0)
    obs_dim = env.observation_space(env.agents[0]).shape[0]
    action_dim = env.action_space(env.agents[0]).n
    state_dim = obs_dim * 3  # Concatenated observations as state
    env.close()

    print(f"Observation dim: {obs_dim}, Action dim: {action_dim}")
    print(f"State dim (for mixer): {state_dim}")
    print()

    # Find all QMIX checkpoints
    checkpoint_base = Path("checkpoints/qmix")
    seeds = [42, 123, 456]
    episodes = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]

    all_metrics = []

    for seed in seeds:
        print(f"=" * 80)
        print(f"QMIX Seed {seed} Evaluation")
        print(f"=" * 80)
        print()

        for episode in episodes:
            checkpoint_path = checkpoint_base / f"seed_{seed}" / f"episode_{episode}"

            if not checkpoint_path.exists():
                print(f"  ⚠️  Checkpoint not found: {checkpoint_path}")
                continue

            # Load networks
            agent_networks = []
            for i in range(3):
                agent_net = AgentQNetwork(obs_dim, action_dim).to(device)
                agent_net.load_state_dict(
                    torch.load(checkpoint_path / f"agent_{i}_qnet.pt", map_location=device)
                )
                agent_net.eval()
                agent_networks.append(agent_net)

            # Load mixer
            mixer = QMixerNetwork(num_agents=3, state_dim=state_dim).to(device)
            mixer.load_state_dict(
                torch.load(checkpoint_path / "mixer.pt", map_location=device)
            )
            mixer.eval()

            # Evaluate
            O, R, OR, mean_reward = evaluate_qmix_policy(agent_networks, mixer)

            # Store metrics
            metrics = ORMetrics(
                observation_consistency=O,
                reward_consistency=R,
                or_index=OR,
                mean_reward=mean_reward,
                algorithm="QMIX",
                seed=seed,
                episode=episode
            )
            all_metrics.append(metrics)

            print(f"  QMIX seed {seed} episode {episode}... ✅ O={O:.3f}, R={R:.3f}, O/R={OR:.3f}, Reward={mean_reward:.2f}")

    print()
    print("=" * 80)
    print("Summary Statistics")
    print("=" * 80)
    print()

    if all_metrics:
        O_values = [m.observation_consistency for m in all_metrics]
        R_values = [m.reward_consistency for m in all_metrics]
        OR_values = [m.or_index for m in all_metrics]
        reward_values = [m.mean_reward for m in all_metrics]

        print(f"QMIX (n={len(all_metrics)}):")
        print(f"  O:   {np.mean(O_values):.3f} ± {np.std(O_values):.3f}")
        print(f"  R:   {np.mean(R_values):.3f} ± {np.std(R_values):.3f}")
        print(f"  O/R: {np.mean(OR_values):.3f} ± {np.std(OR_values):.3f}")
        print(f"  Reward: {np.mean(reward_values):.2f} ± {np.std(reward_values):.2f}")
        print()

        # Save results
        results = {
            "algorithm": "QMIX",
            "metrics": [asdict(m) for m in all_metrics],
            "summary": {
                "n": len(all_metrics),
                "O_mean": float(np.mean(O_values)),
                "O_std": float(np.std(O_values)),
                "R_mean": float(np.mean(R_values)),
                "R_std": float(np.std(R_values)),
                "OR_mean": float(np.mean(OR_values)),
                "OR_std": float(np.std(OR_values)),
                "reward_mean": float(np.mean(reward_values)),
                "reward_std": float(np.std(reward_values))
            }
        }

        output_file = "or_qmix_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"✅ Results saved to {output_file}")
        print(f"📊 Total measurements: {len(all_metrics)}")
    else:
        print("❌ No checkpoints found!")

    print()
    print("✅ QMIX O/R computation complete!")


if __name__ == "__main__":
    main()
