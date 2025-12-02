#!/usr/bin/env python3
"""
Runtime Overhead Measurement for O/R Index with Uniform Discretization.

Demonstrates efficient O/R Index computation using uniform binning instead of K-means.
Target: <5% overhead to prove practical feasibility.

Comparison to K-means:
- K-means: O(n·k·i·d) complexity, 65% overhead
- Uniform: O(n) complexity, expected <5% overhead
"""

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import gymnasium as gym
import numpy as np
import torch
import torch.nn as nn
from torch.distributions.normal import Normal


@dataclass
class Args:
    """Training arguments."""
    exp_name: str = "runtime_overhead_uniform"
    seed: int = 42
    torch_deterministic: bool = True
    cuda: bool = True
    env_name: str = "Ant-v4"
    total_timesteps: int = 10_000  # Short run for overhead measurement
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


class Agent(nn.Module):
    """Simple actor-critic network for continuous control."""

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


def discretize_uniform(data: np.ndarray, k: int = 20) -> np.ndarray:
    """
    Discretize continuous data using uniform binning (O(n) complexity).

    Much faster than K-means (O(n·k·i·d)) with similar effectiveness for O/R Index.
    """
    if data.ndim == 1:
        data = data.reshape(-1, 1)

    # For multi-dimensional data, use PCA projection to 1D for binning
    if data.shape[1] > 1:
        # Simple projection: use mean across dimensions
        data_1d = data.mean(axis=1)
    else:
        data_1d = data.squeeze()

    # Uniform binning based on min-max range
    min_val = data_1d.min()
    max_val = data_1d.max()

    # Add small epsilon to avoid edge case with max value
    bins = np.linspace(min_val, max_val + 1e-10, k + 1)
    labels = np.digitize(data_1d, bins) - 1  # -1 to make 0-indexed
    labels = np.clip(labels, 0, k - 1)  # Clip to valid range

    return labels


def compute_or_index_uniform(observations: np.ndarray, rewards: np.ndarray, k: int = 20) -> float:
    """Compute O/R Index efficiently using uniform discretization."""
    # Discretize observations (O(n) complexity)
    obs_flat = observations.reshape(observations.shape[0], -1)
    obs_bins = discretize_uniform(obs_flat, k)

    # Discretize rewards (O(n) complexity)
    reward_bins = discretize_uniform(rewards.reshape(-1, 1), k)

    # Compute consistencies (O(n) complexity)
    n_samples = len(obs_bins)
    _, counts_obs = np.unique(obs_bins, return_counts=True)
    p_obs = counts_obs / n_samples
    O_consistency = np.sum(p_obs ** 2)

    _, counts_reward = np.unique(reward_bins, return_counts=True)
    p_reward = counts_reward / n_samples
    R_consistency = np.sum(p_reward ** 2)

    # O/R Index
    return np.log(R_consistency / (O_consistency + 1e-10))


def train_ppo(args: Args, enable_or_tracking: bool = False) -> Tuple[float, Dict]:
    """Train PPO with optional O/R Index tracking."""
    # Environment setup
    env = gym.make(args.env_name)
    obs_dim = env.observation_space.shape[0]
    action_dim = env.action_space.shape[0]

    # Agent setup
    device = torch.device("cuda" if args.cuda and torch.cuda.is_available() else "cpu")
    agent = Agent(obs_dim, action_dim).to(device)
    optimizer = torch.optim.Adam(agent.parameters(), lr=args.learning_rate)

    # Storage
    or_measurements = []

    # Training loop
    global_step = 0
    start_time = time.time()
    num_updates = args.total_timesteps // args.num_steps

    for update in range(num_updates):
        # Rollout
        rollout_obs = []
        rollout_rewards = []
        rollout_actions = []
        rollout_logprobs = []
        rollout_values = []
        rollout_dones = []

        obs, _ = env.reset()
        for step in range(args.num_steps):
            global_step += 1
            rollout_obs.append(obs)

            with torch.no_grad():
                obs_tensor = torch.FloatTensor(obs).unsqueeze(0).to(device)
                action, logprob, _, value = agent.get_action_and_value(obs_tensor)

            action_np = action.cpu().numpy()[0]
            obs, reward, terminated, truncated, _ = env.step(action_np)
            done = terminated or truncated

            rollout_actions.append(action_np)
            rollout_logprobs.append(logprob.item())
            rollout_values.append(value.item())
            rollout_rewards.append(reward)
            rollout_dones.append(done)

            if done:
                obs, _ = env.reset()

        # Convert to tensors for PPO update
        b_obs = torch.FloatTensor(np.array(rollout_obs)).to(device)
        b_actions = torch.FloatTensor(np.array(rollout_actions)).to(device)
        b_logprobs = torch.FloatTensor(rollout_logprobs).to(device)
        b_rewards = torch.FloatTensor(rollout_rewards).to(device)
        b_dones = torch.FloatTensor(rollout_dones).to(device)
        b_values = torch.FloatTensor(rollout_values).to(device)

        # Compute advantages (GAE)
        with torch.no_grad():
            advantages = torch.zeros_like(b_rewards).to(device)
            lastgaelam = 0
            for t in reversed(range(args.num_steps)):
                if t == args.num_steps - 1:
                    nextnonterminal = 1.0 - b_dones[t]
                    nextvalues = agent.get_value(b_obs[t].unsqueeze(0)).squeeze()
                else:
                    nextnonterminal = 1.0 - b_dones[t]
                    nextvalues = b_values[t + 1]
                delta = b_rewards[t] + args.gamma * nextvalues * nextnonterminal - b_values[t]
                advantages[t] = lastgaelam = delta + args.gamma * args.gae_lambda * nextnonterminal * lastgaelam
            returns = advantages + b_values

        # PPO update
        batch_size = args.num_steps
        minibatch_size = batch_size // args.num_minibatches
        indices = np.arange(batch_size)

        for epoch in range(args.num_epochs):
            np.random.shuffle(indices)
            for start in range(0, batch_size, minibatch_size):
                end = start + minibatch_size
                mb_indices = indices[start:end]

                _, newlogprob, entropy, newvalue = agent.get_action_and_value(
                    b_obs[mb_indices], b_actions[mb_indices]
                )
                logratio = newlogprob - b_logprobs[mb_indices]
                ratio = logratio.exp()

                mb_advantages = advantages[mb_indices]
                mb_advantages = (mb_advantages - mb_advantages.mean()) / (mb_advantages.std() + 1e-8)

                # Policy loss
                pg_loss1 = -mb_advantages * ratio
                pg_loss2 = -mb_advantages * torch.clamp(ratio, 1 - args.clip_coef, 1 + args.clip_coef)
                pg_loss = torch.max(pg_loss1, pg_loss2).mean()

                # Value loss
                v_loss = 0.5 * ((newvalue.squeeze() - returns[mb_indices]) ** 2).mean()

                # Entropy loss
                entropy_loss = entropy.mean()

                # Total loss
                loss = pg_loss - args.ent_coef * entropy_loss + v_loss * args.vf_coef

                optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(agent.parameters(), args.max_grad_norm)
                optimizer.step()

        # O/R Index tracking (if enabled) - UNIFORM DISCRETIZATION
        if enable_or_tracking and (update + 1) % 1 == 0:  # Every update
            obs_array = np.array(rollout_obs)
            reward_array = np.array(rollout_rewards)
            or_index = compute_or_index_uniform(obs_array, reward_array, k=20)
            or_measurements.append({
                "update": update + 1,
                "global_step": global_step,
                "or_index": float(or_index)
            })

    env.close()
    elapsed_time = time.time() - start_time

    return elapsed_time, {
        "or_measurements": or_measurements if enable_or_tracking else [],
        "num_updates": num_updates,
        "total_steps": global_step
    }


def run_overhead_experiment(num_trials: int = 5) -> Dict:
    """Run overhead measurement experiment with uniform discretization."""
    print("=" * 80)
    print("RUNTIME OVERHEAD MEASUREMENT - O/R INDEX (UNIFORM DISCRETIZATION)")
    print("=" * 80)
    print(f"\nExperimental Design:")
    print(f"  - Baseline: PPO without O/R Index tracking")
    print(f"  - Treatment: PPO with O/R Index tracking (uniform binning, every update)")
    print(f"  - Discretization: Uniform binning (O(n) complexity)")
    print(f"  - Training steps: 10,000 (5 updates)")
    print(f"  - Trials: {num_trials}")
    print(f"  - Target overhead: <5%")
    print("")

    baseline_times = []
    treatment_times = []

    print("Running baseline trials (no O/R tracking)...")
    print("-" * 80)
    for trial in range(num_trials):
        print(f"  Trial {trial + 1}/{num_trials}...", end=" ", flush=True)
        args = Args()
        elapsed, _ = train_ppo(args, enable_or_tracking=False)
        baseline_times.append(elapsed)
        print(f"{elapsed:.2f}s")

    print("\nRunning treatment trials (with O/R tracking - UNIFORM)...")
    print("-" * 80)
    for trial in range(num_trials):
        print(f"  Trial {trial + 1}/{num_trials}...", end=" ", flush=True)
        args = Args()
        elapsed, info = train_ppo(args, enable_or_tracking=True)
        treatment_times.append(elapsed)
        print(f"{elapsed:.2f}s (O/R measurements: {len(info['or_measurements'])})")

    # Compute statistics
    baseline_mean = np.mean(baseline_times)
    baseline_std = np.std(baseline_times, ddof=1)
    treatment_mean = np.mean(treatment_times)
    treatment_std = np.std(treatment_times, ddof=1)

    overhead_pct = ((treatment_mean - baseline_mean) / baseline_mean) * 100
    overhead_std = ((treatment_std + baseline_std) / baseline_mean) * 100

    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print(f"Baseline (no O/R):    {baseline_mean:.2f}s ± {baseline_std:.2f}s")
    print(f"Treatment (with O/R): {treatment_mean:.2f}s ± {treatment_std:.2f}s")
    print(f"Overhead:             {overhead_pct:.2f}% ± {overhead_std:.2f}%")
    print(f"Target:               <5.00%")
    print(f"Result:               {'✅ PASS' if overhead_pct < 5.0 else '❌ FAIL'}")
    print("=" * 80)

    return {
        "baseline_times": baseline_times,
        "treatment_times": treatment_times,
        "baseline_mean": float(baseline_mean),
        "baseline_std": float(baseline_std),
        "treatment_mean": float(treatment_mean),
        "treatment_std": float(treatment_std),
        "overhead_percent": float(overhead_pct),
        "overhead_std": float(overhead_std),
        "pass_threshold": bool(overhead_pct < 5.0),
        "num_trials": num_trials
    }


def main():
    """Main execution."""
    output_path = Path("results/runtime_overhead_uniform.json")
    output_path.parent.mkdir(exist_ok=True)

    # Run experiment
    results = run_overhead_experiment(num_trials=5)

    # Save results
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Results saved to: {output_path}")


if __name__ == "__main__":
    main()
