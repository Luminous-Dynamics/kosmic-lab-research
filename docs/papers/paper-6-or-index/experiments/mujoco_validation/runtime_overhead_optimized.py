#!/usr/bin/env python3
"""
Runtime Overhead Optimization Experiments for O/R Index.

Tests multiple optimization strategies:
1. Less frequent computation (every 5 updates)
2. Dynamic bin selection (adaptive k based on data diversity)
3. Sub-sampling (512 vs 2048 steps)
4. Combined optimizations

Target: <1% overhead to prove ultra-low-cost tracking is possible.
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
    exp_name: str = "runtime_overhead_optimized"
    seed: int = 42
    torch_deterministic: bool = True
    cuda: bool = True
    env_name: str = "Ant-v4"
    total_timesteps: int = 10_000
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


def estimate_optimal_bins(data: np.ndarray, max_bins: int = 20) -> int:
    """
    Dynamically estimate optimal number of bins based on data diversity.

    Uses Sturges' rule with adjustments for high-dimensional data.
    """
    n_samples = len(data)

    # Flatten if multi-dimensional
    if data.ndim > 1:
        data_flat = data.mean(axis=1)  # Project to 1D
    else:
        data_flat = data

    # Sturges' rule: k = 1 + log2(n)
    sturges_k = int(np.ceil(1 + np.log2(n_samples)))

    # Rice rule: k = 2 * n^(1/3)
    rice_k = int(np.ceil(2 * (n_samples ** (1/3))))

    # Use minimum to avoid over-binning
    optimal_k = min(sturges_k, rice_k, max_bins)

    # Ensure at least 5 bins for meaningful discretization
    return max(5, optimal_k)


def discretize_uniform_dynamic(data: np.ndarray, max_bins: int = 20) -> np.ndarray:
    """
    Discretize with dynamically selected number of bins.
    """
    if data.ndim == 1:
        data = data.reshape(-1, 1)

    # Determine optimal number of bins
    k = estimate_optimal_bins(data, max_bins)

    # Project multi-dimensional data to 1D
    if data.shape[1] > 1:
        data_1d = data.mean(axis=1)
    else:
        data_1d = data.squeeze()

    # Uniform binning
    min_val = data_1d.min()
    max_val = data_1d.max()
    bins = np.linspace(min_val, max_val + 1e-10, k + 1)
    labels = np.digitize(data_1d, bins) - 1
    labels = np.clip(labels, 0, k - 1)

    return labels


def discretize_uniform(data: np.ndarray, k: int = 20) -> np.ndarray:
    """
    Standard uniform discretization with fixed k.
    """
    if data.ndim == 1:
        data = data.reshape(-1, 1)

    if data.shape[1] > 1:
        data_1d = data.mean(axis=1)
    else:
        data_1d = data.squeeze()

    min_val = data_1d.min()
    max_val = data_1d.max()
    bins = np.linspace(min_val, max_val + 1e-10, k + 1)
    labels = np.digitize(data_1d, bins) - 1
    labels = np.clip(labels, 0, k - 1)

    return labels


def compute_or_index_uniform(observations: np.ndarray, rewards: np.ndarray,
                             k: int = 20, dynamic_bins: bool = False) -> float:
    """Compute O/R Index with uniform discretization."""
    obs_flat = observations.reshape(observations.shape[0], -1)

    if dynamic_bins:
        obs_bins = discretize_uniform_dynamic(obs_flat, max_bins=k)
        reward_bins = discretize_uniform_dynamic(rewards.reshape(-1, 1), max_bins=k)
    else:
        obs_bins = discretize_uniform(obs_flat, k)
        reward_bins = discretize_uniform(rewards.reshape(-1, 1), k)

    n_samples = len(obs_bins)
    _, counts_obs = np.unique(obs_bins, return_counts=True)
    p_obs = counts_obs / n_samples
    O_consistency = np.sum(p_obs ** 2)

    _, counts_reward = np.unique(reward_bins, return_counts=True)
    p_reward = counts_reward / n_samples
    R_consistency = np.sum(p_reward ** 2)

    return np.log(R_consistency / (O_consistency + 1e-10))


def train_ppo(args: Args, enable_or_tracking: bool = False,
              or_frequency: int = 1, subsample_size: int = None,
              dynamic_bins: bool = False) -> Tuple[float, Dict]:
    """
    Train PPO with configurable O/R tracking.

    Args:
        enable_or_tracking: Enable O/R Index computation
        or_frequency: Compute O/R every N updates (1 = every update)
        subsample_size: Use only N samples for O/R (None = use all)
        dynamic_bins: Use dynamic bin selection
    """
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

        # O/R Index tracking (with optimizations)
        if enable_or_tracking and (update + 1) % or_frequency == 0:
            obs_array = np.array(rollout_obs)
            reward_array = np.array(rollout_rewards)

            # Sub-sample if requested
            if subsample_size is not None and subsample_size < len(obs_array):
                indices = np.random.choice(len(obs_array), subsample_size, replace=False)
                obs_array = obs_array[indices]
                reward_array = reward_array[indices]

            or_index = compute_or_index_uniform(obs_array, reward_array, k=20,
                                               dynamic_bins=dynamic_bins)
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


def run_optimization_experiments(num_trials: int = 5) -> Dict:
    """Run comprehensive optimization experiments."""
    print("=" * 80)
    print("RUNTIME OVERHEAD OPTIMIZATION EXPERIMENTS")
    print("=" * 80)
    print(f"\nTesting multiple optimization strategies:")
    print(f"  1. Baseline (every update, fixed bins)")
    print(f"  2. Less frequent (every 5 updates)")
    print(f"  3. Dynamic bins (adaptive k)")
    print(f"  4. Sub-sampling (512 samples)")
    print(f"  5. Combined (every 5 + dynamic + subsample)")
    print(f"\nTrials: {num_trials} per configuration")
    print(f"Target: <1% overhead")
    print("")

    results = {}

    # Baseline (already have this from Day 3, but re-run for consistency)
    print("1️⃣  Baseline: Every update, k=20, full rollout")
    print("-" * 80)
    baseline_times = []
    treatment_baseline = []
    for trial in range(num_trials):
        print(f"  Baseline trial {trial + 1}/{num_trials}...", end=" ", flush=True)
        args = Args()
        elapsed, _ = train_ppo(args, enable_or_tracking=False)
        baseline_times.append(elapsed)
        print(f"{elapsed:.2f}s")

    for trial in range(num_trials):
        print(f"  Treatment trial {trial + 1}/{num_trials}...", end=" ", flush=True)
        args = Args()
        elapsed, info = train_ppo(args, enable_or_tracking=True, or_frequency=1)
        treatment_baseline.append(elapsed)
        print(f"{elapsed:.2f}s (O/R: {len(info['or_measurements'])})")

    results["baseline"] = {
        "baseline_times": baseline_times,
        "treatment_times": treatment_baseline,
        "baseline_mean": float(np.mean(baseline_times)),
        "treatment_mean": float(np.mean(treatment_baseline)),
        "overhead_percent": float((np.mean(treatment_baseline) - np.mean(baseline_times)) / np.mean(baseline_times) * 100),
        "config": "Every update, k=20 fixed, full rollout"
    }
    print(f"  → Overhead: {results['baseline']['overhead_percent']:.2f}%\n")

    # Optimization 1: Less frequent computation
    print("2️⃣  Optimization 1: Every 5 updates")
    print("-" * 80)
    treatment_freq5 = []
    for trial in range(num_trials):
        print(f"  Trial {trial + 1}/{num_trials}...", end=" ", flush=True)
        args = Args()
        elapsed, info = train_ppo(args, enable_or_tracking=True, or_frequency=5)
        treatment_freq5.append(elapsed)
        print(f"{elapsed:.2f}s (O/R: {len(info['or_measurements'])})")

    results["freq5"] = {
        "baseline_times": baseline_times,
        "treatment_times": treatment_freq5,
        "baseline_mean": float(np.mean(baseline_times)),
        "treatment_mean": float(np.mean(treatment_freq5)),
        "overhead_percent": float((np.mean(treatment_freq5) - np.mean(baseline_times)) / np.mean(baseline_times) * 100),
        "config": "Every 5 updates, k=20 fixed, full rollout"
    }
    print(f"  → Overhead: {results['freq5']['overhead_percent']:.2f}%\n")

    # Optimization 2: Dynamic bins
    print("3️⃣  Optimization 2: Dynamic bins")
    print("-" * 80)
    treatment_dynamic = []
    for trial in range(num_trials):
        print(f"  Trial {trial + 1}/{num_trials}...", end=" ", flush=True)
        args = Args()
        elapsed, info = train_ppo(args, enable_or_tracking=True, or_frequency=1, dynamic_bins=True)
        treatment_dynamic.append(elapsed)
        print(f"{elapsed:.2f}s (O/R: {len(info['or_measurements'])})")

    results["dynamic_bins"] = {
        "baseline_times": baseline_times,
        "treatment_times": treatment_dynamic,
        "baseline_mean": float(np.mean(baseline_times)),
        "treatment_mean": float(np.mean(treatment_dynamic)),
        "overhead_percent": float((np.mean(treatment_dynamic) - np.mean(baseline_times)) / np.mean(baseline_times) * 100),
        "config": "Every update, dynamic k, full rollout"
    }
    print(f"  → Overhead: {results['dynamic_bins']['overhead_percent']:.2f}%\n")

    # Optimization 3: Sub-sampling
    print("4️⃣  Optimization 3: Sub-sampling (512 samples)")
    print("-" * 80)
    treatment_subsample = []
    for trial in range(num_trials):
        print(f"  Trial {trial + 1}/{num_trials}...", end=" ", flush=True)
        args = Args()
        elapsed, info = train_ppo(args, enable_or_tracking=True, or_frequency=1, subsample_size=512)
        treatment_subsample.append(elapsed)
        print(f"{elapsed:.2f}s (O/R: {len(info['or_measurements'])})")

    results["subsample"] = {
        "baseline_times": baseline_times,
        "treatment_times": treatment_subsample,
        "baseline_mean": float(np.mean(baseline_times)),
        "treatment_mean": float(np.mean(treatment_subsample)),
        "overhead_percent": float((np.mean(treatment_subsample) - np.mean(baseline_times)) / np.mean(baseline_times) * 100),
        "config": "Every update, k=20 fixed, 512 samples"
    }
    print(f"  → Overhead: {results['subsample']['overhead_percent']:.2f}%\n")

    # Optimization 4: Combined (all optimizations)
    print("5️⃣  Optimization 4: Combined (every 5 + dynamic + subsample)")
    print("-" * 80)
    treatment_combined = []
    for trial in range(num_trials):
        print(f"  Trial {trial + 1}/{num_trials}...", end=" ", flush=True)
        args = Args()
        elapsed, info = train_ppo(args, enable_or_tracking=True, or_frequency=5,
                                 dynamic_bins=True, subsample_size=512)
        treatment_combined.append(elapsed)
        print(f"{elapsed:.2f}s (O/R: {len(info['or_measurements'])})")

    results["combined"] = {
        "baseline_times": baseline_times,
        "treatment_times": treatment_combined,
        "baseline_mean": float(np.mean(baseline_times)),
        "treatment_mean": float(np.mean(treatment_combined)),
        "overhead_percent": float((np.mean(treatment_combined) - np.mean(baseline_times)) / np.mean(baseline_times) * 100),
        "config": "Every 5 updates, dynamic k, 512 samples"
    }
    print(f"  → Overhead: {results['combined']['overhead_percent']:.2f}%\n")

    # Summary table
    print("=" * 80)
    print("OPTIMIZATION SUMMARY")
    print("=" * 80)
    print(f"{'Configuration':<40} {'Overhead':<15} {'Status':<15}")
    print("-" * 80)

    for name, data in results.items():
        overhead = data['overhead_percent']
        status = "✅ <1%" if overhead < 1.0 else "⚠️ <5%" if overhead < 5.0 else "❌ >5%"
        display_name = data['config'][:38]
        print(f"{display_name:<40} {overhead:>6.2f}% {status:<15}")

    print("=" * 80)

    # Best configuration
    best_config = min(results.items(), key=lambda x: x[1]['overhead_percent'])
    print(f"\n🏆 Best configuration: {best_config[0]}")
    print(f"   Overhead: {best_config[1]['overhead_percent']:.2f}%")
    print(f"   Config: {best_config[1]['config']}")

    return results


def main():
    """Main execution."""
    output_path = Path("results/runtime_overhead_optimized.json")
    output_path.parent.mkdir(exist_ok=True)

    # Run experiments
    results = run_optimization_experiments(num_trials=5)

    # Save results
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Results saved to: {output_path}")


if __name__ == "__main__":
    main()
