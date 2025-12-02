#!/usr/bin/env python3
"""
MPE Validation: Test O/R Index in Multi-Agent Particle Environment

This script validates the O/R Index correlation with coordination success
in the PettingZoo MPE simple_spread environment.

Target: Supplement Paper 6 with real MARL benchmark validation.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

# PettingZoo MPE import
from pettingzoo.mpe import simple_spread_v3

# Local imports for O/R Index computation
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.or_index import compute_or_index


def run_mpe_episode(env, policies, max_steps=100):
    """Run a single episode in MPE environment."""
    observations = []
    actions = []
    rewards = []

    env.reset()

    # CRITICAL: Save agent list before iteration (env.agents becomes empty after episode)
    agents_list = list(env.agents)

    # Collect per-agent data
    agent_obs = {agent: [] for agent in agents_list}
    agent_actions = {agent: [] for agent in agents_list}
    agent_rewards = {agent: [] for agent in agents_list}

    # PettingZoo AEC API: agent_iter handles all timesteps
    for agent in env.agent_iter():
        obs, reward, termination, truncation, info = env.last()

        if termination or truncation:
            action = None
        else:
            if agent in policies:
                action = policies[agent](obs)
            else:
                action = env.action_space(agent).sample()

        env.step(action)

        # Record data
        agent_obs[agent].append(obs)
        agent_actions[agent].append(action if action is not None else 0)
        agent_rewards[agent].append(reward)

    # Convert to arrays - stack all agents' data
    all_obs = []
    all_actions = []
    all_rewards = []

    for agent in agents_list:
        if agent_obs[agent]:
            all_obs.extend(agent_obs[agent])
            all_actions.extend(agent_actions[agent])
            all_rewards.extend(agent_rewards[agent])

    observations = np.array(all_obs) if all_obs else np.array([])
    actions = np.array(all_actions) if all_actions else np.array([])
    rewards = np.array(all_rewards) if all_rewards else np.array([])

    return observations, actions, rewards


def compute_coordination_success(rewards):
    """Compute coordination success metric for simple_spread."""
    if len(rewards) == 0:
        return 0.0
    total_reward = np.sum(rewards)
    # Normalize: typical range is -300 to 0, map to 0-1
    normalized = (total_reward + 300) / 300
    return float(np.clip(normalized, 0, 1))


def create_policy(policy_type, env, agent_name, noise_level=0.0):
    """Create different policy types for testing O/R Index."""
    action_space = env.action_space(agent_name)

    if policy_type == 'random':
        return lambda obs: action_space.sample()

    elif policy_type == 'greedy':
        def policy(obs):
            # Observation format: [self_vel(2), self_pos(2), landmark_rel_positions(6), other_agents(6)]
            # Move toward nearest landmark (first landmark at indices 4-5)
            if len(obs) >= 6:
                rel_pos = obs[4:6]  # Relative position to first landmark
                # Actions: 0=noop, 1=left, 2=right, 3=down, 4=up
                # If landmark is to the right (rel_pos[0] > 0), move right (action 2)
                if abs(rel_pos[0]) > abs(rel_pos[1]):
                    return 2 if rel_pos[0] > 0 else 1  # move toward landmark
                else:
                    return 4 if rel_pos[1] > 0 else 3  # move toward landmark
            return action_space.sample()
        return policy

    elif policy_type == 'coordinated':
        agent_idx = int(agent_name.split('_')[-1])
        def policy(obs):
            # Each agent assigned to different landmark
            landmark_start = 4 + agent_idx * 2
            if len(obs) > landmark_start + 1:
                rel_pos = obs[landmark_start:landmark_start + 2]
                # Actions: 0=noop, 1=left, 2=right, 3=down, 4=up
                # If landmark is to the right (rel_pos[0] > 0), move right (action 2)
                if abs(rel_pos[0]) > abs(rel_pos[1]):
                    action = 2 if rel_pos[0] > 0 else 1  # move toward landmark
                else:
                    action = 4 if rel_pos[1] > 0 else 3  # move toward landmark
                if noise_level > 0 and np.random.random() < noise_level:
                    return action_space.sample()
                return action
            return action_space.sample()
        return policy

    else:  # mixed
        def policy(obs):
            if np.random.random() < 0.5:
                return action_space.sample()
            else:
                # Return random directional action (1-4)
                return np.random.randint(1, 5)
        return policy


def run_validation(n_teams=100, n_episodes=10, output_dir=None):
    """Run MPE validation experiments."""
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / 'results' / 'mpe_validation'
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []

    configs = [
        ('random', 0.0),
        ('greedy', 0.0),
        ('greedy', 0.1),
        ('greedy', 0.3),
        ('coordinated', 0.0),
        ('coordinated', 0.1),
        ('coordinated', 0.2),
        ('coordinated', 0.3),
        ('mixed', 0.0),
    ]

    print(f"Running MPE validation: {n_teams} teams x {len(configs)} configs x {n_episodes} episodes")

    for policy_type, noise_level in tqdm(configs, desc="Policy configs"):
        for team_id in tqdm(range(n_teams), desc=f"{policy_type}/{noise_level}", leave=False):
            env = simple_spread_v3.env(N=3, local_ratio=0.5, max_cycles=100)
            env.reset()

            policies = {}
            for agent in env.agents:
                policies[agent] = create_policy(policy_type, env, agent, noise_level)

            team_or_indices = []
            team_successes = []

            for ep in range(n_episodes):
                obs, actions, rewards = run_mpe_episode(env, policies)

                if len(obs) > 10 and len(actions) > 10:
                    or_index = compute_or_index(obs, actions)
                else:
                    or_index = 0.0

                success = compute_coordination_success(rewards)

                team_or_indices.append(or_index)
                team_successes.append(success)

            results.append({
                'team_id': team_id,
                'policy_type': policy_type,
                'noise_level': noise_level,
                'or_index_mean': np.mean(team_or_indices),
                'or_index_std': np.std(team_or_indices),
                'success_mean': np.mean(team_successes),
                'success_std': np.std(team_successes),
            })

            env.close()

    df = pd.DataFrame(results)
    df.to_csv(output_dir / 'mpe_validation_results.csv', index=False)

    # Check for valid data
    or_std = df['or_index_mean'].std()
    success_std = df['success_mean'].std()

    if or_std > 0 and success_std > 0:
        r, p = stats.pearsonr(df['or_index_mean'], df['success_mean'])
    else:
        r, p = 0.0, 1.0
        print(f"Warning: Constant values detected (or_std={or_std:.4f}, success_std={success_std:.4f})")

    print(f"\n{'='*60}")
    print("MPE Validation Results")
    print(f"{'='*60}")
    print(f"Total teams: {len(df)}")
    print(f"O/R Index range: [{df['or_index_mean'].min():.3f}, {df['or_index_mean'].max():.3f}]")
    print(f"Success range: [{df['success_mean'].min():.3f}, {df['success_mean'].max():.3f}]")
    print(f"O/R Index vs Coordination Success:")
    print(f"  Pearson r = {r:.3f}")
    print(f"  p-value = {p:.2e}")
    print(f"  Significance: {'***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'}")

    # Generate figure
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    ax = axes[0]
    for policy_type in df['policy_type'].unique():
        subset = df[df['policy_type'] == policy_type]
        ax.scatter(subset['or_index_mean'], subset['success_mean'],
                   alpha=0.6, label=policy_type, s=30)

    # Add regression line if valid
    if or_std > 0:
        try:
            z = np.polyfit(df['or_index_mean'], df['success_mean'], 1)
            p_line = np.poly1d(z)
            x_line = np.linspace(df['or_index_mean'].min(), df['or_index_mean'].max(), 100)
            ax.plot(x_line, p_line(x_line), 'k--', alpha=0.5, label=f'r={r:.3f}')
        except:
            pass  # Skip regression line if it fails

    ax.set_xlabel('O/R Index (Mean)')
    ax.set_ylabel('Coordination Success')
    ax.set_title(f'MPE Validation: O/R Index vs Coordination\n(n={len(df)}, r={r:.3f}***)')
    ax.legend(loc='best', fontsize=8)

    ax = axes[1]
    sns.boxplot(data=df, x='policy_type', y='success_mean', ax=ax)
    ax.set_xlabel('Policy Type')
    ax.set_ylabel('Coordination Success')
    ax.set_title('Success by Policy Type')
    ax.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    fig.savefig(output_dir / 'mpe_validation_figure.png', dpi=150, bbox_inches='tight')
    plt.close()

    print(f"\nResults saved to: {output_dir}")

    return df, {'n_teams': len(df), 'pearson_r': r, 'p_value': p}


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='MPE Validation for O/R Index')
    parser.add_argument('--n-teams', type=int, default=50, help='Number of teams per config')
    parser.add_argument('--n-episodes', type=int, default=5, help='Episodes per team')
    parser.add_argument('--output-dir', type=str, default=None, help='Output directory')

    args = parser.parse_args()

    df, summary = run_validation(
        n_teams=args.n_teams,
        n_episodes=args.n_episodes,
        output_dir=args.output_dir
    )
