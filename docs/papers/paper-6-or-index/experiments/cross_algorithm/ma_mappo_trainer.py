"""
Multi-Agent PPO (Proximal Policy Optimization) for MPE Cooperative Navigation
Based on CleanRL's PPO implementation, adapted for multi-agent settings

MAPPO is an on-policy actor-critic algorithm with:
- Centralized critic, decentralized actors
- Clipped policy updates for stability
- Generalized Advantage Estimation (GAE)
- Multiple epochs of minibatch updates
"""

import argparse
import os
import random
import time
from dataclasses import dataclass

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions.categorical import Categorical
from pettingzoo.mpe import simple_spread_v3


@dataclass
class Args:
    """Training arguments"""
    exp_name: str = "ma_mappo"
    seed: int = 42
    torch_deterministic: bool = True
    cuda: bool = True  # Use GPU by default (automatically falls back to CPU if unavailable)

    # Environment
    num_agents: int = 3
    max_cycles: int = 25
    local_ratio: float = 0.5

    # Training
    total_episodes: int = 1000
    learning_rate: float = 3e-4
    num_epochs: int = 4  # PPO update epochs
    num_minibatches: int = 4
    gamma: float = 0.99
    gae_lambda: float = 0.95  # GAE parameter

    # PPO specific
    clip_coef: float = 0.2  # PPO clipping parameter
    ent_coef: float = 0.01  # Entropy coefficient
    vf_coef: float = 0.5  # Value function coefficient
    max_grad_norm: float = 0.5  # Gradient clipping

    # Logging
    save_freq: int = 100
    log_dir: str = "logs"
    checkpoint_dir: str = "checkpoints"


class Agent(nn.Module):
    """Combined actor-critic network"""
    def __init__(self, obs_dim, action_dim):
        super().__init__()

        # Shared feature extractor
        self.network = nn.Sequential(
            nn.Linear(obs_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
        )

        # Actor head (policy)
        self.actor = nn.Linear(128, action_dim)

        # Critic head (value function)
        self.critic = nn.Linear(128, 1)

    def get_value(self, x):
        """Get state value"""
        features = self.network(x)
        return self.critic(features)

    def get_action_and_value(self, x, action=None):
        """Get action distribution and value"""
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

        # Buffers
        self.observations = np.zeros((size, obs_dim), dtype=np.float32)
        self.actions = np.zeros(size, dtype=np.int64)
        self.logprobs = np.zeros(size, dtype=np.float32)
        self.rewards = np.zeros(size, dtype=np.float32)
        self.dones = np.zeros(size, dtype=np.float32)
        self.values = np.zeros(size, dtype=np.float32)

    def add(self, obs, action, logprob, reward, done, value):
        """Add transition"""
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
        """Get all data and reset"""
        size = self.size if self.full else self.ptr
        data = {
            'observations': self.observations[:size],
            'actions': self.actions[:size],
            'logprobs': self.logprobs[:size],
            'rewards': self.rewards[:size],
            'dones': self.dones[:size],
            'values': self.values[:size],
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


class MultiAgentPPO:
    """Independent PPO for each agent"""
    def __init__(self, env, args):
        self.env = env
        self.args = args
        self.agents = env.possible_agents

        # Setup device (GPU if available and requested)
        self.device = torch.device(
            "cuda" if args.cuda and torch.cuda.is_available() else "cpu"
        )
        print(f"Using device: {self.device}")
        if self.device.type == "cuda":
            print(f"GPU: {torch.cuda.get_device_name(0)}")

        # Get dimensions
        sample_agent = self.agents[0]
        obs_space = env.observation_space(sample_agent)
        action_space = env.action_space(sample_agent)

        self.obs_dim = obs_space.shape[0]
        self.action_dim = action_space.n

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
            # Buffer size = max_cycles (one episode worth)
            self.rollout_buffers[agent] = RolloutBuffer(args.max_cycles * 10, self.obs_dim)

        self.global_step = 0
        self.episode = 0

    def get_action_and_value(self, agent, obs):
        """Sample action from policy and get value"""
        with torch.no_grad():
            obs_tensor = torch.FloatTensor(obs).unsqueeze(0).to(self.device)
            action, logprob, _, value = self.agent_networks[agent].get_action_and_value(obs_tensor)
            return action.item(), logprob.item(), value.item()

    def update(self, agent):
        """PPO update for one agent"""
        # Get rollout data
        data = self.rollout_buffers[agent].get()

        if len(data['rewards']) < 10:  # Not enough data
            return None, None, None

        # Convert to tensors
        b_obs = torch.FloatTensor(data['observations']).to(self.device)
        b_actions = torch.LongTensor(data['actions']).to(self.device)
        b_logprobs = torch.FloatTensor(data['logprobs']).to(self.device)
        b_values = torch.FloatTensor(data['values']).to(self.device)

        # Compute advantages with GAE
        with torch.no_grad():
            next_value = self.agent_networks[agent].get_value(
                torch.FloatTensor(data['observations'][-1:]).to(self.device)
            ).item()

        advantages, returns = compute_gae(
            data['rewards'],
            data['values'],
            data['dones'],
            next_value,
            self.args.gamma,
            self.args.gae_lambda
        )

        b_advantages = torch.FloatTensor(advantages).to(self.device)
        b_returns = torch.FloatTensor(returns).to(self.device)

        # Normalize advantages
        b_advantages = (b_advantages - b_advantages.mean()) / (b_advantages.std() + 1e-8)

        # PPO update loop
        batch_size = len(b_obs)
        minibatch_size = batch_size // self.args.num_minibatches

        total_pg_loss = 0
        total_v_loss = 0
        total_entropy = 0
        num_updates = 0

        for epoch in range(self.args.num_epochs):
            # Shuffle data
            indices = np.random.permutation(batch_size)

            for start in range(0, batch_size, minibatch_size):
                end = start + minibatch_size
                mb_indices = indices[start:end]

                # Get minibatch
                _, newlogprob, entropy, newvalue = self.agent_networks[agent].get_action_and_value(
                    b_obs[mb_indices],
                    b_actions[mb_indices]
                )

                # Policy loss with clipping
                logratio = newlogprob - b_logprobs[mb_indices]
                ratio = logratio.exp()

                mb_advantages = b_advantages[mb_indices]
                pg_loss1 = -mb_advantages * ratio
                pg_loss2 = -mb_advantages * torch.clamp(ratio, 1 - self.args.clip_coef, 1 + self.args.clip_coef)
                pg_loss = torch.max(pg_loss1, pg_loss2).mean()

                # Value loss
                newvalue = newvalue.view(-1)
                v_loss = 0.5 * ((newvalue - b_returns[mb_indices]) ** 2).mean()

                # Entropy bonus
                entropy_loss = entropy.mean()

                # Total loss
                loss = pg_loss - self.args.ent_coef * entropy_loss + self.args.vf_coef * v_loss

                # Optimize
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
        """Save model checkpoints"""
        checkpoint_path = os.path.join(self.args.checkpoint_dir, f"episode_{episode}")
        os.makedirs(checkpoint_path, exist_ok=True)

        for agent in self.agents:
            torch.save({
                'agent': self.agent_networks[agent].state_dict(),
                'optimizer': self.optimizers[agent].state_dict(),
                'episode': episode,
                'global_step': self.global_step,
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

    ma_ppo = MultiAgentPPO(env, args)

    print(f"Starting MAPPO training: {args.total_episodes} episodes")
    print(f"Agents: {ma_ppo.agents}")
    print(f"Obs dim: {ma_ppo.obs_dim}, Action dim: {ma_ppo.action_dim}")

    for episode in range(args.total_episodes):
        obs, _ = env.reset(seed=args.seed + episode)
        episode_rewards = {agent: 0 for agent in ma_ppo.agents}

        done = False
        step = 0

        while not done:
            actions = {}
            logprobs = {}
            values = {}

            # Collect actions for all agents
            for agent in env.agents:
                if agent in obs:
                    action, logprob, value = ma_ppo.get_action_and_value(agent, obs[agent])
                    actions[agent] = action
                    logprobs[agent] = logprob
                    values[agent] = value

            next_obs, rewards, terminations, truncations, _ = env.step(actions)

            # Store transitions
            for agent in env.agents:
                if agent in obs and agent in next_obs:
                    done_flag = float(terminations[agent] or truncations[agent])
                    ma_ppo.rollout_buffers[agent].add(
                        obs[agent], actions[agent], logprobs[agent],
                        rewards[agent], done_flag, values[agent]
                    )
                    episode_rewards[agent] += rewards[agent]

            obs = next_obs
            ma_ppo.global_step += 1
            step += 1

            done = all(terminations.values()) or all(truncations.values()) or step >= args.max_cycles

        # PPO update after each episode
        for agent in ma_ppo.agents:
            ma_ppo.update(agent)

        ma_ppo.episode = episode

        # Logging
        if episode % 10 == 0 or episode == args.total_episodes - 1:
            mean_reward = np.mean([episode_rewards[agent] for agent in ma_ppo.agents])
            print(f"Episode {episode:4d} | Steps: {ma_ppo.global_step:6d} | "
                  f"Mean Reward: {mean_reward:7.2f}")

        # Save checkpoint
        if episode > 0 and episode % args.save_freq == 0:
            ma_ppo.save_checkpoint(episode)

    ma_ppo.save_checkpoint(args.total_episodes)
    print("Training complete!")
    env.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--exp-name", type=str, default="ma_mappo")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--cuda", action="store_true", default=True, help="Use GPU if available")
    parser.add_argument("--total-episodes", type=int, default=1000)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--save-freq", type=int, default=100)
    parser.add_argument("--log-dir", type=str, default="logs")
    parser.add_argument("--checkpoint-dir", type=str, default="checkpoints")

    args = parser.parse_args()
    args = Args(**vars(args))
    train(args)
