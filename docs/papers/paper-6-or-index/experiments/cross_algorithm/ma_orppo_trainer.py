"""
OR-PPO: O/R Index-Guided Proximal Policy Optimization for MPE

This implements OR-PPO for MPE simple_spread, testing whether O/R-guided
adaptive hyperparameters improve coordination compared to vanilla PPO.

Key differences from Overcooked:
- Simpler environment where baseline PPO succeeds
- Shorter episodes (25 steps vs 400)
- Continuous observations directly binned for O/R computation

Adaptive hyperparameter formula:
    delta_t = tanh((OR_t - OR_target) / sigma)
    epsilon_t = epsilon_0 * (1 - k_epsilon * delta_t)
    alpha_t = alpha_0 * (1 - k_alpha * delta_t)

High O/R (observation-dependent) -> conservative updates
Low O/R (consistent) -> allow larger updates
"""

import argparse
import os
import random
import time
from dataclasses import dataclass
from collections import defaultdict
import json

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions.categorical import Categorical
from pettingzoo.mpe import simple_spread_v3


@dataclass
class Args:
    """Training arguments"""
    exp_name: str = "ma_orppo"
    seed: int = 42
    torch_deterministic: bool = True
    cuda: bool = True

    # Environment
    num_agents: int = 3
    max_cycles: int = 25
    local_ratio: float = 0.5

    # Training
    total_episodes: int = 1000
    learning_rate: float = 3e-4
    num_epochs: int = 4
    num_minibatches: int = 4
    gamma: float = 0.99
    gae_lambda: float = 0.95

    # PPO specific
    clip_coef: float = 0.2
    ent_coef: float = 0.01
    vf_coef: float = 0.5
    max_grad_norm: float = 0.5

    # OR-PPO specific
    use_or_guidance: bool = True  # If False, runs vanilla PPO
    k_clip: float = 0.5           # Clip adaptation strength
    k_lr: float = 0.3             # LR adaptation strength
    target_or: float = 0.0        # Target O/R Index
    sigma: float = 2.0            # Scaling for tanh (MPE O/R typically in [-1, 3])
    or_update_freq: int = 10      # Episodes between O/R recomputation

    # Logging
    save_freq: int = 100
    log_dir: str = "logs/orppo"
    checkpoint_dir: str = "checkpoints/orppo"


class Agent(nn.Module):
    """Combined actor-critic network"""
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
        probs = Categorical(logits=logits)

        if action is None:
            action = probs.sample()

        return action, probs.log_prob(action), probs.entropy(), self.critic(features)


class RolloutBuffer:
    """Store trajectories for on-policy learning"""
    def __init__(self, size, obs_dim):
        self.size = size
        self.ptr = 0
        self.full = False

        self.observations = np.zeros((size, obs_dim), dtype=np.float32)
        self.actions = np.zeros(size, dtype=np.int64)
        self.logprobs = np.zeros(size, dtype=np.float32)
        self.rewards = np.zeros(size, dtype=np.float32)
        self.dones = np.zeros(size, dtype=np.float32)
        self.values = np.zeros(size, dtype=np.float32)

    def add(self, obs, action, logprob, reward, done, value):
        self.observations[self.ptr] = obs
        self.actions[self.ptr] = action
        self.logprobs[self.ptr] = logprob
        self.rewards[self.ptr] = reward
        self.dones[self.ptr] = done
        self.values[self.ptr] = value

        self.ptr = (self.ptr + 1) % self.size
        if self.ptr == 0:
            self.full = True

    def get(self):
        size = self.size if self.full else self.ptr
        data = {
            'observations': self.observations[:size].copy(),
            'actions': self.actions[:size].copy(),
            'logprobs': self.logprobs[:size].copy(),
            'rewards': self.rewards[:size].copy(),
            'dones': self.dones[:size].copy(),
            'values': self.values[:size].copy(),
        }
        self.ptr = 0
        self.full = False
        return data


def compute_gae(rewards, values, dones, next_value, gamma, gae_lambda):
    """Compute Generalized Advantage Estimation"""
    advantages = np.zeros_like(rewards)
    lastgaelam = 0

    for t in reversed(range(len(rewards))):
        if t == len(rewards) - 1:
            nextnonterminal = 1.0 - dones[t]
            nextvalues = next_value
        else:
            nextnonterminal = 1.0 - dones[t]
            nextvalues = values[t + 1]

        delta = rewards[t] + gamma * nextvalues * nextnonterminal - values[t]
        advantages[t] = lastgaelam = delta + gamma * gae_lambda * nextnonterminal * lastgaelam

    returns = advantages + values
    return advantages, returns


def compute_or_index(trajectories, n_bins=10):
    """
    Compute O/R Index from trajectory data.

    O/R = Var[P(a|o)] / Var[P(a)] - 1

    Args:
        trajectories: dict mapping agent -> list of {'obs': ..., 'action': ...}
        n_bins: number of observation bins

    Returns:
        float: O/R Index (averaged across agents)
    """
    agent_or_indices = []

    for agent, agent_traj in trajectories.items():
        if len(agent_traj) < 10:
            continue

        observations = np.array([t['obs'] for t in agent_traj])
        actions = np.array([t['action'] for t in agent_traj])

        # Discretize observations using first PC
        if observations.shape[1] > 1:
            # Simple binning: use first dimension or PCA
            obs_1d = observations[:, 0]  # Use position x as proxy
        else:
            obs_1d = observations.squeeze()

        # Create bins
        min_val, max_val = obs_1d.min(), obs_1d.max()
        if max_val - min_val < 1e-8:
            agent_or_indices.append(0.0)
            continue

        bin_edges = np.linspace(min_val - 1e-8, max_val + 1e-8, n_bins + 1)
        bin_indices = np.digitize(obs_1d, bin_edges[1:-1], right=True)

        # Compute P(a) - unconditional action distribution
        n_actions = 5  # MPE has 5 actions
        action_counts = np.bincount(actions, minlength=n_actions)
        p_a = action_counts / len(actions)
        var_p_a = np.var(p_a)

        if var_p_a < 1e-9:
            agent_or_indices.append(0.0)
            continue

        # Compute P(a|o) variances for each bin
        obs_action_map = defaultdict(list)
        for bin_idx, action in zip(bin_indices, actions):
            obs_action_map[bin_idx].append(action)

        conditional_variances = []
        for bin_idx, bin_actions in obs_action_map.items():
            if len(bin_actions) >= 2:
                obs_action_counts = np.bincount(bin_actions, minlength=n_actions)
                p_a_given_o = obs_action_counts / len(bin_actions)
                var_p_a_given_o = np.var(p_a_given_o)
                conditional_variances.append(var_p_a_given_o)

        if len(conditional_variances) == 0:
            agent_or_indices.append(0.0)
            continue

        mean_var_conditional = np.mean(conditional_variances)
        or_index = mean_var_conditional / var_p_a - 1
        agent_or_indices.append(or_index)

    return np.mean(agent_or_indices) if agent_or_indices else 0.0


class MultiAgentORPPO:
    """OR-PPO with adaptive hyperparameters based on O/R Index"""

    def __init__(self, env, args):
        self.env = env
        self.args = args
        self.agents = env.possible_agents

        self.device = torch.device(
            "cuda" if args.cuda and torch.cuda.is_available() else "cpu"
        )
        print(f"Using device: {self.device}")

        sample_agent = self.agents[0]
        self.obs_dim = env.observation_space(sample_agent).shape[0]
        self.action_dim = env.action_space(sample_agent).n

        # Create agent networks
        self.agent_networks = {}
        self.optimizers = {}
        self.rollout_buffers = {}

        for agent in self.agents:
            self.agent_networks[agent] = Agent(self.obs_dim, self.action_dim).to(self.device)
            self.optimizers[agent] = optim.Adam(
                self.agent_networks[agent].parameters(),
                lr=args.learning_rate,
                eps=1e-5
            )
            self.rollout_buffers[agent] = RolloutBuffer(args.max_cycles * 10, self.obs_dim)

        # OR-PPO adaptive parameters
        self.current_clip = args.clip_coef
        self.current_lr = args.learning_rate
        self.current_or = 0.0

        # Trajectory storage for O/R computation
        self.recent_trajectories = {agent: [] for agent in self.agents}

        # History tracking
        self.or_history = []
        self.clip_history = []
        self.lr_history = []
        self.reward_history = []

        self.global_step = 0
        self.episode = 0

    def compute_adaptive_params(self, current_or):
        """Compute adaptive hyperparameters based on O/R feedback"""
        if not self.args.use_or_guidance:
            return self.args.clip_coef, self.args.learning_rate

        # Normalize with tanh
        delta = np.tanh((current_or - self.args.target_or) / self.args.sigma)

        # High O/R -> smaller clip, smaller LR (conservative)
        clip_range = self.args.clip_coef * (1 - self.args.k_clip * delta)
        learning_rate = self.args.learning_rate * (1 - self.args.k_lr * delta)

        # Ensure positive
        clip_range = max(0.01, clip_range)
        learning_rate = max(1e-5, learning_rate)

        return clip_range, learning_rate

    def update_hyperparameters(self, current_or):
        """Update clip range and learning rate based on O/R"""
        self.current_or = current_or
        self.current_clip, self.current_lr = self.compute_adaptive_params(current_or)

        # Update optimizer learning rates
        for agent in self.agents:
            for param_group in self.optimizers[agent].param_groups:
                param_group['lr'] = self.current_lr

        # Track history
        self.or_history.append(current_or)
        self.clip_history.append(self.current_clip)
        self.lr_history.append(self.current_lr)

    def get_action_and_value(self, agent, obs):
        with torch.no_grad():
            obs_tensor = torch.FloatTensor(obs).unsqueeze(0).to(self.device)
            action, logprob, _, value = self.agent_networks[agent].get_action_and_value(obs_tensor)
            return action.item(), logprob.item(), value.item()

    def update(self, agent):
        """PPO update with adaptive clip range"""
        data = self.rollout_buffers[agent].get()

        if len(data['rewards']) < 10:
            return None, None, None

        b_obs = torch.FloatTensor(data['observations']).to(self.device)
        b_actions = torch.LongTensor(data['actions']).to(self.device)
        b_logprobs = torch.FloatTensor(data['logprobs']).to(self.device)
        b_values = torch.FloatTensor(data['values']).to(self.device)

        with torch.no_grad():
            next_value = self.agent_networks[agent].get_value(
                torch.FloatTensor(data['observations'][-1:]).to(self.device)
            ).item()

        advantages, returns = compute_gae(
            data['rewards'], data['values'], data['dones'],
            next_value, self.args.gamma, self.args.gae_lambda
        )

        b_advantages = torch.FloatTensor(advantages).to(self.device)
        b_returns = torch.FloatTensor(returns).to(self.device)

        b_advantages = (b_advantages - b_advantages.mean()) / (b_advantages.std() + 1e-8)

        batch_size = len(b_obs)
        minibatch_size = max(1, batch_size // self.args.num_minibatches)

        total_pg_loss = 0
        total_v_loss = 0
        total_entropy = 0
        num_updates = 0

        # Use adaptive clip range from OR guidance
        clip_coef = self.current_clip

        for epoch in range(self.args.num_epochs):
            indices = np.random.permutation(batch_size)

            for start in range(0, batch_size, minibatch_size):
                end = start + minibatch_size
                mb_indices = indices[start:end]

                _, newlogprob, entropy, newvalue = self.agent_networks[agent].get_action_and_value(
                    b_obs[mb_indices], b_actions[mb_indices]
                )

                logratio = newlogprob - b_logprobs[mb_indices]
                ratio = logratio.exp()

                mb_advantages = b_advantages[mb_indices]
                pg_loss1 = -mb_advantages * ratio
                pg_loss2 = -mb_advantages * torch.clamp(ratio, 1 - clip_coef, 1 + clip_coef)
                pg_loss = torch.max(pg_loss1, pg_loss2).mean()

                newvalue = newvalue.view(-1)
                v_loss = 0.5 * ((newvalue - b_returns[mb_indices]) ** 2).mean()

                entropy_loss = entropy.mean()

                loss = pg_loss - self.args.ent_coef * entropy_loss + self.args.vf_coef * v_loss

                self.optimizers[agent].zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(self.agent_networks[agent].parameters(), self.args.max_grad_norm)
                self.optimizers[agent].step()

                total_pg_loss += pg_loss.item()
                total_v_loss += v_loss.item()
                total_entropy += entropy_loss.item()
                num_updates += 1

        return (
            total_pg_loss / num_updates if num_updates > 0 else 0,
            total_v_loss / num_updates if num_updates > 0 else 0,
            total_entropy / num_updates if num_updates > 0 else 0
        )

    def save_checkpoint(self, episode):
        checkpoint_path = os.path.join(self.args.checkpoint_dir, f"episode_{episode}")
        os.makedirs(checkpoint_path, exist_ok=True)

        for agent in self.agents:
            torch.save({
                'agent': self.agent_networks[agent].state_dict(),
                'optimizer': self.optimizers[agent].state_dict(),
                'episode': episode,
                'or_history': self.or_history,
                'clip_history': self.clip_history,
                'lr_history': self.lr_history,
            }, os.path.join(checkpoint_path, f"{agent}.pt"))

        print(f"Checkpoint saved at episode {episode}")


def train(args):
    """Main training loop"""
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    os.makedirs(args.log_dir, exist_ok=True)
    os.makedirs(args.checkpoint_dir, exist_ok=True)

    env = simple_spread_v3.parallel_env(
        N=args.num_agents,
        local_ratio=args.local_ratio,
        max_cycles=args.max_cycles,
        continuous_actions=False,
    )

    ma_ppo = MultiAgentORPPO(env, args)

    mode = "OR-PPO" if args.use_or_guidance else "Vanilla PPO"
    print(f"Starting {mode} training: {args.total_episodes} episodes")
    print(f"Agents: {ma_ppo.agents}")
    print(f"OR guidance: {args.use_or_guidance}, k_clip={args.k_clip}, k_lr={args.k_lr}")

    all_rewards = []
    all_or_values = []

    for episode in range(args.total_episodes):
        obs, _ = env.reset(seed=args.seed + episode)
        episode_rewards = {agent: 0 for agent in ma_ppo.agents}

        done = False
        step = 0

        while not done:
            actions = {}
            logprobs = {}
            values = {}

            for agent in env.agents:
                if agent in obs:
                    action, logprob, value = ma_ppo.get_action_and_value(agent, obs[agent])
                    actions[agent] = action
                    logprobs[agent] = logprob
                    values[agent] = value

            next_obs, rewards, terminations, truncations, _ = env.step(actions)

            for agent in env.agents:
                if agent in obs and agent in next_obs:
                    done_flag = float(terminations[agent] or truncations[agent])
                    ma_ppo.rollout_buffers[agent].add(
                        obs[agent], actions[agent], logprobs[agent],
                        rewards[agent], done_flag, values[agent]
                    )
                    episode_rewards[agent] += rewards[agent]

                    # Store for O/R computation
                    ma_ppo.recent_trajectories[agent].append({
                        'obs': obs[agent].copy(),
                        'action': actions[agent]
                    })

            obs = next_obs
            ma_ppo.global_step += 1
            step += 1

            done = all(terminations.values()) or all(truncations.values()) or step >= args.max_cycles

        # PPO update
        for agent in ma_ppo.agents:
            ma_ppo.update(agent)

        ma_ppo.episode = episode

        # Compute and update O/R every or_update_freq episodes
        if episode > 0 and episode % args.or_update_freq == 0:
            current_or = compute_or_index(ma_ppo.recent_trajectories)
            ma_ppo.update_hyperparameters(current_or)
            all_or_values.append((episode, current_or))

            # Clear trajectories for next window
            ma_ppo.recent_trajectories = {agent: [] for agent in ma_ppo.agents}

        # Track rewards
        mean_reward = np.mean([episode_rewards[agent] for agent in ma_ppo.agents])
        all_rewards.append(mean_reward)
        ma_ppo.reward_history.append(mean_reward)

        # Logging
        if episode % 10 == 0 or episode == args.total_episodes - 1:
            print(f"Episode {episode:4d} | Reward: {mean_reward:7.2f} | "
                  f"O/R: {ma_ppo.current_or:.3f} | clip: {ma_ppo.current_clip:.3f} | "
                  f"lr: {ma_ppo.current_lr:.6f}")

        # Save checkpoint
        if episode > 0 and episode % args.save_freq == 0:
            ma_ppo.save_checkpoint(episode)

    ma_ppo.save_checkpoint(args.total_episodes)

    # Save results
    results = {
        'exp_name': args.exp_name,
        'use_or_guidance': args.use_or_guidance,
        'seed': args.seed,
        'total_episodes': args.total_episodes,
        'final_reward_mean': np.mean(all_rewards[-100:]),
        'final_reward_std': np.std(all_rewards[-100:]),
        'final_or': ma_ppo.or_history[-1] if ma_ppo.or_history else 0.0,
        'or_history': ma_ppo.or_history,
        'clip_history': ma_ppo.clip_history,
        'lr_history': ma_ppo.lr_history,
        'reward_history': all_rewards,
        'k_clip': args.k_clip,
        'k_lr': args.k_lr,
    }

    results_file = os.path.join(args.log_dir, f"results_seed{args.seed}.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {results_file}")
    print(f"Final reward: {results['final_reward_mean']:.2f} +/- {results['final_reward_std']:.2f}")
    print(f"Final O/R: {results['final_or']:.3f}")

    env.close()
    return results


def run_comparison(args):
    """Run both PPO and OR-PPO for comparison"""
    print("=" * 70)
    print("OR-PPO vs PPO Comparison on MPE Simple Spread")
    print("=" * 70)

    all_results = {}

    for use_or in [False, True]:
        mode = "OR-PPO" if use_or else "PPO"
        print(f"\n{'='*70}")
        print(f"Training {mode}")
        print(f"{'='*70}")

        mode_results = []
        for seed in [42, 123, 456]:
            args.seed = seed
            args.use_or_guidance = use_or
            args.exp_name = f"ma_{'orppo' if use_or else 'ppo'}"
            args.log_dir = f"logs/{'orppo' if use_or else 'ppo'}"
            args.checkpoint_dir = f"checkpoints/{'orppo' if use_or else 'ppo'}"

            result = train(args)
            mode_results.append(result)

        # Aggregate across seeds
        all_results[mode] = {
            'reward_mean': np.mean([r['final_reward_mean'] for r in mode_results]),
            'reward_std': np.std([r['final_reward_mean'] for r in mode_results]),
            'or_mean': np.mean([r['final_or'] for r in mode_results]),
            'or_std': np.std([r['final_or'] for r in mode_results]),
            'per_seed': mode_results,
        }

    # Summary
    print("\n" + "=" * 70)
    print("COMPARISON SUMMARY")
    print("=" * 70)

    ppo = all_results['PPO']
    orppo = all_results['OR-PPO']

    print(f"\nPPO:")
    print(f"  Reward: {ppo['reward_mean']:.2f} +/- {ppo['reward_std']:.2f}")
    print(f"  O/R Index: {ppo['or_mean']:.3f} +/- {ppo['or_std']:.3f}")

    print(f"\nOR-PPO:")
    print(f"  Reward: {orppo['reward_mean']:.2f} +/- {orppo['reward_std']:.2f}")
    print(f"  O/R Index: {orppo['or_mean']:.3f} +/- {orppo['or_std']:.3f}")

    reward_diff = orppo['reward_mean'] - ppo['reward_mean']
    or_diff = orppo['or_mean'] - ppo['or_mean']

    print(f"\nDifference:")
    print(f"  Reward: {reward_diff:+.2f} ({100*reward_diff/abs(ppo['reward_mean']):+.1f}%)")
    print(f"  O/R Index: {or_diff:+.3f}")

    # Save comparison
    comparison_file = "logs/orppo_vs_ppo_comparison.json"
    os.makedirs("logs", exist_ok=True)
    with open(comparison_file, 'w') as f:
        json.dump(all_results, f, indent=2, default=float)
    print(f"\nComparison saved to {comparison_file}")

    return all_results


if __name__ == "__main__":
    import sys
    # Unbuffered output
    sys.stdout = open(sys.stdout.fileno(), mode='w', buffering=1)
    sys.stderr = open(sys.stderr.fileno(), mode='w', buffering=1)

    parser = argparse.ArgumentParser()
    parser.add_argument("--exp-name", type=str, default="ma_orppo")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--cuda", action="store_true", default=True)
    parser.add_argument("--total-episodes", type=int, default=1000)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--save-freq", type=int, default=100)
    parser.add_argument("--use-or-guidance", action="store_true", default=True)
    parser.add_argument("--comparison", action="store_true", help="Run PPO vs OR-PPO comparison")
    parser.add_argument("--k-clip", type=float, default=0.5)
    parser.add_argument("--k-lr", type=float, default=0.3)

    parsed_args = parser.parse_args()

    # Create Args with proper handling of comparison flag
    args = Args()
    args.exp_name = parsed_args.exp_name
    args.seed = parsed_args.seed
    args.cuda = parsed_args.cuda
    args.total_episodes = parsed_args.total_episodes
    args.learning_rate = parsed_args.learning_rate
    args.save_freq = parsed_args.save_freq
    args.use_or_guidance = parsed_args.use_or_guidance
    args.k_clip = parsed_args.k_clip
    args.k_lr = parsed_args.k_lr

    if parsed_args.comparison:
        run_comparison(args)
    else:
        train(args)
