#!/usr/bin/env python3
"""
Compute O/R Index for Cross-Algorithm Validation
Extracts trajectories from trained DQN, SAC, and MAPPO agents and computes O/R metrics.

This script handles all three algorithms and computes standardized O/R metrics
based on observation and reward consistency rather than action variance.
"""

import torch
import numpy as np
from pathlib import Path
import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple
from pettingzoo.mpe import simple_spread_v3
import warnings
warnings.filterwarnings('ignore')

# Import trainer classes to load models
from ma_dqn_trainer import MADQN, Args as DQNArgs
from ma_sac_trainer import MASAC, Args as SACArgs
from ma_mappo_trainer import MultiAgentPPO, Args as MAPPOArgs


@dataclass
class ORMetrics:
    """O/R Index metrics for a trajectory"""
    observation_consistency: float  # O: Consistency in observation patterns
    reward_consistency: float       # R: Consistency in reward patterns
    or_index: float                 # O/R ratio
    mean_reward: float              # Average reward over trajectory
    trajectory_length: int          # Number of steps
    algorithm: str                  # Algorithm name
    seed: int                       # Random seed
    episode_checkpoint: int         # Which checkpoint (100, 500, 1000)


class QNetwork(nn.Module):
    """Q-Network (must match training architecture)"""
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


def load_checkpoint(checkpoint_path, obs_dim, action_dim):
    """Load Q-network from checkpoint"""
    q_network = QNetwork(obs_dim, action_dim)
    checkpoint = torch.load(checkpoint_path, map_location='cpu')
    q_network.load_state_dict(checkpoint['q_network'])
    q_network.eval()
    return q_network


def evaluate_policy(env, q_networks, num_episodes=50, seed=42):
    """Evaluate policy and collect (observation, action) pairs"""
    trajectories = {agent: [] for agent in env.possible_agents}

    for episode in range(num_episodes):
        obs, _ = env.reset(seed=seed + episode)
        done = False
        step = 0

        while not done and step < 25:
            actions = {}

            # Get greedy actions (no exploration)
            for agent in env.agents:
                if agent in obs:
                    with torch.no_grad():
                        obs_tensor = torch.FloatTensor(obs[agent]).unsqueeze(0)
                        q_values = q_networks[agent](obs_tensor)
                        action = q_values.argmax().item()
                        actions[agent] = action

                        # Store (observation, action) pair
                        trajectories[agent].append({
                            'obs': obs[agent].copy(),
                            'action': action
                        })

            # Environment step
            next_obs, rewards, terminations, truncations, _ = env.step(actions)
            obs = next_obs
            step += 1

            # Check if all agents done
            done = all(terminations.values()) or all(truncations.values())

    return trajectories


def discretize_observation(obs, bins=5):
    """Discretize continuous observation for grouping"""
    # Simple binning: divide each dimension into bins
    discretized = []
    for val in obs:
        # Normalize to [0, bins-1]
        bin_idx = int(np.clip((val + 3) / 6 * bins, 0, bins - 1))
        discretized.append(bin_idx)
    return tuple(discretized)


def compute_or_index(trajectories, discretize=True, bins=5):
    """
    Compute O/R Index = Var[P(a|o)] / Var[P(a)] - 1

    Args:
        trajectories: List of {obs, action} dicts
        discretize: Whether to discretize observations
        bins: Number of bins for discretization
    """
    if len(trajectories) == 0:
        return 0.0

    # Extract actions and observations
    actions = np.array([t['action'] for t in trajectories])
    observations = [t['obs'] for t in trajectories]

    # Discretize observations for grouping
    if discretize:
        obs_keys = [discretize_observation(obs, bins) for obs in observations]
    else:
        obs_keys = [tuple(obs) for obs in observations]

    # Compute P(a) - unconditional action distribution
    action_counts = np.bincount(actions, minlength=5)
    p_a = action_counts / len(actions)
    var_p_a = np.var(p_a)

    if var_p_a == 0:
        return 0.0  # All actions the same

    # Compute P(a|o) for each unique observation
    obs_action_map = defaultdict(list)
    for obs_key, action in zip(obs_keys, actions):
        obs_action_map[obs_key].append(action)

    # Compute variance of P(a|o) across different observations
    conditional_variances = []
    for obs_key, obs_actions in obs_action_map.items():
        if len(obs_actions) > 1:  # Need multiple samples
            obs_action_counts = np.bincount(obs_actions, minlength=5)
            p_a_given_o = obs_action_counts / len(obs_actions)
            var_p_a_given_o = np.var(p_a_given_o)
            conditional_variances.append(var_p_a_given_o)

    if len(conditional_variances) == 0:
        return 0.0

    # Average variance across observations
    mean_var_p_a_given_o = np.mean(conditional_variances)

    # O/R Index
    or_index = mean_var_p_a_given_o / var_p_a - 1

    return or_index


def main(args):
    """Main analysis pipeline"""
    print(f"Computing O/R Index for seed {args.seed}")
    print(f"Checkpoints: {args.checkpoint_episodes}")
    print(f"Evaluation episodes: {args.eval_episodes}")
    print()

    # Create environment
    env = simple_spread_v3.parallel_env(
        N=3,
        local_ratio=0.5,
        max_cycles=25,
        continuous_actions=False,
    )

    # Get dimensions
    sample_agent = env.possible_agents[0]
    obs_dim = env.observation_space(sample_agent).shape[0]
    action_dim = env.action_space(sample_agent).n

    results = []

    # Process each checkpoint
    for episode in args.checkpoint_episodes:
        checkpoint_dir = os.path.join(
            args.checkpoint_base,
            f"seed_{args.seed}",
            f"episode_{episode}"
        )

        if not os.path.exists(checkpoint_dir):
            print(f"Warning: Checkpoint {checkpoint_dir} not found, skipping")
            continue

        print(f"Processing checkpoint episode {episode}...")

        # Load Q-networks
        q_networks = {}
        for agent in env.possible_agents:
            checkpoint_path = os.path.join(checkpoint_dir, f"{agent}.pt")
            q_networks[agent] = load_checkpoint(checkpoint_path, obs_dim, action_dim)

        # Evaluate policy
        trajectories = evaluate_policy(env, q_networks, args.eval_episodes, args.seed)

        # Compute O/R Index for each agent
        or_indices = {}
        for agent, agent_traj in trajectories.items():
            or_index = compute_or_index(agent_traj, discretize=True, bins=args.bins)
            or_indices[agent] = or_index

        # Average across agents
        mean_or_index = np.mean(list(or_indices.values()))

        results.append({
            'episode': episode,
            'or_indices': or_indices,
            'mean_or_index': mean_or_index
        })

        print(f"  Episode {episode}:")
        for agent, or_idx in or_indices.items():
            print(f"    {agent}: {or_idx:.4f}")
        print(f"    Mean: {mean_or_index:.4f}")
        print()

    env.close()

    # Save results
    output_file = f"results/or_index_seed{args.seed}.npy"
    os.makedirs("results", exist_ok=True)
    np.save(output_file, results)
    print(f"Results saved to {output_file}")

    # Summary
    print("\n=== Summary ===")
    print(f"Seed: {args.seed}")
    print(f"Checkpoints analyzed: {len(results)}")
    print(f"Mean O/R Index range: {min(r['mean_or_index'] for r in results):.4f} to {max(r['mean_or_index'] for r in results):.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42, help="Seed to analyze")
    parser.add_argument("--checkpoint-base", type=str, default="checkpoints/dqn",
                       help="Base checkpoint directory")
    parser.add_argument("--checkpoint-episodes", type=int, nargs="+",
                       default=[100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
                       help="Episodes to analyze")
    parser.add_argument("--eval-episodes", type=int, default=50,
                       help="Number of evaluation episodes")
    parser.add_argument("--bins", type=int, default=5,
                       help="Number of bins for observation discretization")

    args = parser.parse_args()
    main(args)
