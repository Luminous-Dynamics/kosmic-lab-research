"""
Multi-Agent SAC (Soft Actor-Critic) for MPE Cooperative Navigation
Based on CleanRL's SAC implementation, adapted for multi-agent settings

SAC is an off-policy actor-critic algorithm with:
- Entropy regularization for exploration
- Soft Q-learning with temperature parameter
- Automatic temperature tuning
"""

import argparse
import os
import random
import time
from collections import deque
from dataclasses import dataclass

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from pettingzoo.mpe import simple_spread_v3


@dataclass
class Args:
    """Training arguments"""
    exp_name: str = "ma_sac"
    seed: int = 42
    torch_deterministic: bool = True
    cuda: bool = False

    # Environment
    num_agents: int = 3
    max_cycles: int = 25
    local_ratio: float = 0.5

    # Training
    total_episodes: int = 1000
    learning_rate: float = 3e-4
    buffer_size: int = 10000
    gamma: float = 0.99
    tau: float = 0.005  # Soft update coefficient
    batch_size: int = 128
    learning_starts: int = 1000
    train_frequency: int = 1  # Update every step

    # SAC specific
    alpha: float = 0.2  # Entropy temperature
    autotune: bool = True  # Automatic temperature tuning
    target_entropy_scale: float = 0.89  # Scale factor for target entropy

    # Logging
    save_freq: int = 100
    log_dir: str = "logs"
    checkpoint_dir: str = "checkpoints"


class Actor(nn.Module):
    """Stochastic policy network"""
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
        x_t = normal.rsample()  # Reparameterization trick
        action = torch.tanh(x_t)
        log_prob = normal.log_prob(x_t)
        # Enforcing action bounds
        log_prob -= torch.log(1 - action.pow(2) + 1e-6)
        log_prob = log_prob.sum(1, keepdim=True)
        return action, log_prob


class SoftQNetwork(nn.Module):
    """Soft Q-network (critic)"""
    def __init__(self, obs_dim, action_dim):
        super().__init__()
        self.fc1 = nn.Linear(obs_dim + action_dim, 256)
        self.fc2 = nn.Linear(256, 256)
        self.fc3 = nn.Linear(256, 1)

    def forward(self, obs, action):
        x = torch.cat([obs, action], 1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)


class ReplayBuffer:
    """Experience replay buffer"""
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)

    def push(self, agent_id, obs, action, reward, next_obs, done):
        self.buffer.append((agent_id, obs, action, reward, next_obs, done))

    def sample(self, batch_size, agent_id=None):
        """Sample batch, optionally filtered by agent"""
        if agent_id is not None:
            agent_transitions = [t for t in self.buffer if t[0] == agent_id]
            if len(agent_transitions) < batch_size:
                return None
            indices = np.random.choice(len(agent_transitions), batch_size, replace=False)
            batch = [agent_transitions[i] for i in indices]
        else:
            indices = np.random.choice(len(self.buffer), batch_size, replace=False)
            batch = [self.buffer[i] for i in indices]

        agents, obs, actions, rewards, next_obs, dones = zip(*batch)
        return (
            agents,
            torch.FloatTensor(np.array(obs)),
            torch.FloatTensor(np.array(actions)),
            torch.FloatTensor(np.array(rewards)).unsqueeze(1),
            torch.FloatTensor(np.array(next_obs)),
            torch.FloatTensor(np.array(dones)).unsqueeze(1),
        )

    def __len__(self):
        return len(self.buffer)


class MultiAgentSAC:
    """Independent SAC for each agent"""
    def __init__(self, env, args):
        self.env = env
        self.args = args
        self.agents = env.possible_agents

        # Get dimensions (discrete actions, so we'll use a trick)
        sample_agent = self.agents[0]
        obs_space = env.observation_space(sample_agent)
        action_space = env.action_space(sample_agent)

        self.obs_dim = obs_space.shape[0]
        self.action_dim = action_space.n  # Discrete actions

        # Create networks for each agent
        self.actors = {}
        self.qf1s = {}
        self.qf2s = {}
        self.qf1_targets = {}
        self.qf2_targets = {}

        self.actor_optimizers = {}
        self.q_optimizers = {}

        # Temperature parameters
        self.log_alphas = {}
        self.alpha_optimizers = {}
        self.target_entropies = {}

        for agent in self.agents:
            # Actor
            self.actors[agent] = Actor(self.obs_dim, self.action_dim)
            self.actor_optimizers[agent] = optim.Adam(
                self.actors[agent].parameters(), lr=args.learning_rate
            )

            # Critics (double Q-learning)
            self.qf1s[agent] = SoftQNetwork(self.obs_dim, self.action_dim)
            self.qf2s[agent] = SoftQNetwork(self.obs_dim, self.action_dim)
            self.qf1_targets[agent] = SoftQNetwork(self.obs_dim, self.action_dim)
            self.qf2_targets[agent] = SoftQNetwork(self.obs_dim, self.action_dim)

            self.qf1_targets[agent].load_state_dict(self.qf1s[agent].state_dict())
            self.qf2_targets[agent].load_state_dict(self.qf2s[agent].state_dict())

            q_params = list(self.qf1s[agent].parameters()) + list(self.qf2s[agent].parameters())
            self.q_optimizers[agent] = optim.Adam(q_params, lr=args.learning_rate)

            # Temperature
            if args.autotune:
                self.target_entropies[agent] = -args.target_entropy_scale * self.action_dim
                self.log_alphas[agent] = torch.zeros(1, requires_grad=True)
                self.alpha_optimizers[agent] = optim.Adam(
                    [self.log_alphas[agent]], lr=args.learning_rate
                )
            else:
                self.log_alphas[agent] = torch.tensor(np.log(args.alpha))

        # Shared replay buffer
        self.replay_buffer = ReplayBuffer(args.buffer_size)
        self.global_step = 0

    def get_action(self, agent, obs, deterministic=False):
        """Get action from policy"""
        with torch.no_grad():
            obs_tensor = torch.FloatTensor(obs).unsqueeze(0)
            if deterministic:
                action, _ = self.actors[agent](obs_tensor)
                action = torch.tanh(action)
            else:
                action, _ = self.actors[agent].get_action(obs_tensor)

            # Convert continuous action to discrete
            action = action.cpu().numpy()[0]
            discrete_action = np.argmax(action)
            return discrete_action

    def update(self, agent):
        """Update networks for one agent"""
        if len(self.replay_buffer) < self.args.batch_size:
            return None, None, None

        batch = self.replay_buffer.sample(self.args.batch_size, agent_id=agent)
        if batch is None:
            return None, None, None

        _, obs, actions_discrete, rewards, next_obs, dones = batch

        # Convert discrete actions back to continuous for Q-network
        actions = F.one_hot(actions_discrete.long().squeeze(), self.action_dim).float()

        alpha = self.log_alphas[agent].exp()

        # Update Q-networks
        with torch.no_grad():
            next_actions, next_log_probs = self.actors[agent].get_action(next_obs)
            qf1_next_target = self.qf1_targets[agent](next_obs, next_actions)
            qf2_next_target = self.qf2_targets[agent](next_obs, next_actions)
            min_qf_next_target = torch.min(qf1_next_target, qf2_next_target) - alpha * next_log_probs
            next_q_value = rewards + (1 - dones) * self.args.gamma * min_qf_next_target

        qf1_a_values = self.qf1s[agent](obs, actions)
        qf2_a_values = self.qf2s[agent](obs, actions)
        qf1_loss = F.mse_loss(qf1_a_values, next_q_value)
        qf2_loss = F.mse_loss(qf2_a_values, next_q_value)
        qf_loss = qf1_loss + qf2_loss

        self.q_optimizers[agent].zero_grad()
        qf_loss.backward()
        self.q_optimizers[agent].step()

        # Update policy
        pi, log_pi = self.actors[agent].get_action(obs)
        qf1_pi = self.qf1s[agent](obs, pi)
        qf2_pi = self.qf2s[agent](obs, pi)
        min_qf_pi = torch.min(qf1_pi, qf2_pi)

        actor_loss = ((alpha * log_pi) - min_qf_pi).mean()

        self.actor_optimizers[agent].zero_grad()
        actor_loss.backward()
        self.actor_optimizers[agent].step()

        # Update temperature
        alpha_loss = None
        if self.args.autotune:
            with torch.no_grad():
                _, log_pi = self.actors[agent].get_action(obs)
            alpha_loss = (-self.log_alphas[agent].exp() * (log_pi + self.target_entropies[agent])).mean()

            self.alpha_optimizers[agent].zero_grad()
            alpha_loss.backward()
            self.alpha_optimizers[agent].step()

        # Soft update target networks
        for param, target_param in zip(self.qf1s[agent].parameters(), self.qf1_targets[agent].parameters()):
            target_param.data.copy_(self.args.tau * param.data + (1 - self.args.tau) * target_param.data)
        for param, target_param in zip(self.qf2s[agent].parameters(), self.qf2_targets[agent].parameters()):
            target_param.data.copy_(self.args.tau * param.data + (1 - self.args.tau) * target_param.data)

        return qf_loss.item(), actor_loss.item(), alpha_loss.item() if alpha_loss else 0.0

    def save_checkpoint(self, episode):
        """Save model checkpoints"""
        checkpoint_path = os.path.join(self.args.checkpoint_dir, f"episode_{episode}")
        os.makedirs(checkpoint_path, exist_ok=True)

        for agent in self.agents:
            torch.save({
                'actor': self.actors[agent].state_dict(),
                'qf1': self.qf1s[agent].state_dict(),
                'qf2': self.qf2s[agent].state_dict(),
                'qf1_target': self.qf1_targets[agent].state_dict(),
                'qf2_target': self.qf2_targets[agent].state_dict(),
                'actor_optimizer': self.actor_optimizers[agent].state_dict(),
                'q_optimizer': self.q_optimizers[agent].state_dict(),
                'log_alpha': self.log_alphas[agent],
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

    ma_sac = MultiAgentSAC(env, args)

    print(f"Starting SAC training: {args.total_episodes} episodes")
    print(f"Agents: {ma_sac.agents}")
    print(f"Obs dim: {ma_sac.obs_dim}, Action dim: {ma_sac.action_dim}")

    for episode in range(args.total_episodes):
        obs, _ = env.reset(seed=args.seed + episode)
        episode_rewards = {agent: 0 for agent in ma_sac.agents}

        done = False
        step = 0

        while not done:
            actions = {}
            for agent in env.agents:
                if agent in obs:
                    # Random actions for initial exploration
                    if ma_sac.global_step < args.learning_starts:
                        actions[agent] = env.action_space(agent).sample()
                    else:
                        actions[agent] = ma_sac.get_action(agent, obs[agent])

            next_obs, rewards, terminations, truncations, _ = env.step(actions)

            for agent in env.agents:
                if agent in obs and agent in next_obs:
                    done_flag = terminations[agent] or truncations[agent]
                    ma_sac.replay_buffer.push(
                        agent, obs[agent], actions[agent],
                        rewards[agent], next_obs[agent], done_flag
                    )
                    episode_rewards[agent] += rewards[agent]

            # Update networks
            if ma_sac.global_step > args.learning_starts:
                if ma_sac.global_step % args.train_frequency == 0:
                    for agent in ma_sac.agents:
                        ma_sac.update(agent)

            obs = next_obs
            ma_sac.global_step += 1
            step += 1

            done = all(terminations.values()) or all(truncations.values()) or step >= args.max_cycles

        # Logging
        if episode % 10 == 0 or episode == args.total_episodes - 1:
            mean_reward = np.mean([episode_rewards[agent] for agent in ma_sac.agents])
            alpha_values = [ma_sac.log_alphas[agent].exp().item() for agent in ma_sac.agents]
            mean_alpha = np.mean(alpha_values)
            print(f"Episode {episode:4d} | Steps: {ma_sac.global_step:6d} | "
                  f"Mean Reward: {mean_reward:7.2f} | Alpha: {mean_alpha:.3f} | "
                  f"Buffer: {len(ma_sac.replay_buffer):5d}")

        # Save checkpoint
        if episode > 0 and episode % args.save_freq == 0:
            ma_sac.save_checkpoint(episode)

    ma_sac.save_checkpoint(args.total_episodes)
    print("Training complete!")
    env.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--exp-name", type=str, default="ma_sac")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--total-episodes", type=int, default=1000)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--save-freq", type=int, default=100)
    parser.add_argument("--log-dir", type=str, default="logs")
    parser.add_argument("--checkpoint-dir", type=str, default="checkpoints")

    args = parser.parse_args()
    args = Args(**vars(args))
    train(args)
