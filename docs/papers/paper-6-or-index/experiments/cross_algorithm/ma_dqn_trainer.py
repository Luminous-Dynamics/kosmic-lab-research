"""
Multi-Agent DQN for MPE Cooperative Navigation
Based on CleanRL's DQN implementation, adapted for multi-agent settings
"""

import argparse
import os
import random
import time
from collections import deque
from dataclasses import dataclass

import gymnasium as gym
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from pettingzoo.mpe import simple_spread_v3


@dataclass
class Args:
    """Training arguments"""
    exp_name: str = "ma_dqn"
    seed: int = 42
    torch_deterministic: bool = True
    cuda: bool = False  # Use CPU for now

    # Environment
    num_agents: int = 3
    max_cycles: int = 25
    local_ratio: float = 0.5
    continuous_actions: bool = False

    # Training
    total_episodes: int = 1000
    learning_rate: float = 2.5e-4
    buffer_size: int = 10000
    gamma: float = 0.99
    tau: float = 1.0  # Target network update frequency
    target_network_frequency: int = 500
    batch_size: int = 128
    start_e: float = 1.0
    end_e: float = 0.05
    exploration_fraction: float = 0.5
    learning_starts: int = 1000
    train_frequency: int = 10

    # Logging
    save_freq: int = 100
    log_dir: str = "logs"
    checkpoint_dir: str = "checkpoints"


class QNetwork(nn.Module):
    """Q-Network for discrete actions"""
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


class ReplayBuffer:
    """Simple replay buffer for multi-agent experience"""
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)

    def push(self, agent_id, obs, action, reward, next_obs, done):
        """Store transition"""
        self.buffer.append((agent_id, obs, action, reward, next_obs, done))

    def sample(self, batch_size, agent_id=None):
        """Sample batch of transitions, optionally filtered by agent"""
        if agent_id is not None:
            agent_transitions = [t for t in self.buffer if t[0] == agent_id]
            if len(agent_transitions) < batch_size:
                return None
            indices = np.random.choice(len(agent_transitions), batch_size, replace=False)
            batch = [agent_transitions[i] for i in indices]
        else:
            indices = np.random.choice(len(self.buffer), batch_size, replace=False)
            batch = [self.buffer[i] for i in indices]

        # Unpack batch
        agents, obs, actions, rewards, next_obs, dones = zip(*batch)
        return (
            agents,
            torch.FloatTensor(np.array(obs)),
            torch.LongTensor(np.array(actions)),
            torch.FloatTensor(np.array(rewards)),
            torch.FloatTensor(np.array(next_obs)),
            torch.FloatTensor(np.array(dones)),
        )

    def __len__(self):
        return len(self.buffer)


class MultiAgentDQN:
    """Independent DQN for each agent"""
    def __init__(self, env, args):
        self.env = env
        self.args = args
        self.agents = env.possible_agents

        # Get observation and action spaces
        sample_agent = self.agents[0]
        obs_space = env.observation_space(sample_agent)
        action_space = env.action_space(sample_agent)

        self.obs_dim = obs_space.shape[0]
        self.action_dim = action_space.n

        # Create Q-networks for each agent
        self.q_networks = {}
        self.target_networks = {}
        self.optimizers = {}

        for agent in self.agents:
            self.q_networks[agent] = QNetwork(self.obs_dim, self.action_dim)
            self.target_networks[agent] = QNetwork(self.obs_dim, self.action_dim)
            self.target_networks[agent].load_state_dict(self.q_networks[agent].state_dict())
            self.optimizers[agent] = optim.Adam(
                self.q_networks[agent].parameters(),
                lr=args.learning_rate
            )

        # Shared replay buffer
        self.replay_buffer = ReplayBuffer(args.buffer_size)

        # Training state
        self.global_step = 0
        self.episode_rewards = {agent: [] for agent in self.agents}

    def get_action(self, agent, obs, epsilon):
        """Epsilon-greedy action selection"""
        if random.random() < epsilon:
            return random.randint(0, self.action_dim - 1)
        else:
            with torch.no_grad():
                obs_tensor = torch.FloatTensor(obs).unsqueeze(0)
                q_values = self.q_networks[agent](obs_tensor)
                return q_values.argmax().item()

    def update(self, agent):
        """Update Q-network for one agent"""
        if len(self.replay_buffer) < self.args.batch_size:
            return None

        # Sample batch for this agent
        batch = self.replay_buffer.sample(self.args.batch_size, agent_id=agent)
        if batch is None:
            return None

        agents, obs, actions, rewards, next_obs, dones = batch

        # Current Q values
        current_q_values = self.q_networks[agent](obs).gather(1, actions.unsqueeze(1)).squeeze()

        # Target Q values
        with torch.no_grad():
            next_q_values = self.target_networks[agent](next_obs).max(1)[0]
            target_q_values = rewards + self.args.gamma * next_q_values * (1 - dones)

        # Compute loss
        loss = F.mse_loss(current_q_values, target_q_values)

        # Optimize
        self.optimizers[agent].zero_grad()
        loss.backward()
        self.optimizers[agent].step()

        return loss.item()

    def update_target_networks(self):
        """Update target networks for all agents"""
        for agent in self.agents:
            self.target_networks[agent].load_state_dict(self.q_networks[agent].state_dict())

    def save_checkpoint(self, episode):
        """Save model checkpoints"""
        checkpoint_path = os.path.join(self.args.checkpoint_dir, f"episode_{episode}")
        os.makedirs(checkpoint_path, exist_ok=True)

        for agent in self.agents:
            torch.save(
                {
                    'q_network': self.q_networks[agent].state_dict(),
                    'target_network': self.target_networks[agent].state_dict(),
                    'optimizer': self.optimizers[agent].state_dict(),
                    'episode': episode,
                    'global_step': self.global_step,
                },
                os.path.join(checkpoint_path, f"{agent}.pt")
            )

        print(f"Checkpoint saved at episode {episode}")


def train(args):
    """Main training loop"""
    # Set seeds
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    # Create directories
    os.makedirs(args.log_dir, exist_ok=True)
    os.makedirs(args.checkpoint_dir, exist_ok=True)

    # Create environment
    env = simple_spread_v3.parallel_env(
        N=args.num_agents,
        local_ratio=args.local_ratio,
        max_cycles=args.max_cycles,
        continuous_actions=args.continuous_actions,
    )

    # Initialize multi-agent DQN
    ma_dqn = MultiAgentDQN(env, args)

    # Training loop
    print(f"Starting training: {args.total_episodes} episodes")
    print(f"Agents: {ma_dqn.agents}")
    print(f"Obs dim: {ma_dqn.obs_dim}, Action dim: {ma_dqn.action_dim}")

    for episode in range(args.total_episodes):
        obs, _ = env.reset(seed=args.seed + episode)
        episode_rewards = {agent: 0 for agent in ma_dqn.agents}
        episode_lengths = {agent: 0 for agent in ma_dqn.agents}

        # Compute epsilon for exploration
        epsilon = max(
            args.end_e,
            args.start_e - (args.start_e - args.end_e) * episode / (args.total_episodes * args.exploration_fraction)
        )

        done = False
        step = 0

        while not done:
            # Get actions for all agents
            actions = {}
            for agent in env.agents:
                if agent in obs:
                    actions[agent] = ma_dqn.get_action(agent, obs[agent], epsilon)

            # Environment step
            next_obs, rewards, terminations, truncations, infos = env.step(actions)

            # Store transitions
            for agent in env.agents:
                if agent in obs and agent in next_obs:
                    done_flag = terminations[agent] or truncations[agent]
                    ma_dqn.replay_buffer.push(
                        agent,
                        obs[agent],
                        actions[agent],
                        rewards[agent],
                        next_obs[agent],
                        done_flag
                    )
                    episode_rewards[agent] += rewards[agent]
                    episode_lengths[agent] += 1

            # Update networks
            if ma_dqn.global_step > args.learning_starts and ma_dqn.global_step % args.train_frequency == 0:
                for agent in ma_dqn.agents:
                    loss = ma_dqn.update(agent)

            # Update target networks
            if ma_dqn.global_step % args.target_network_frequency == 0:
                ma_dqn.update_target_networks()

            obs = next_obs
            ma_dqn.global_step += 1
            step += 1

            # Check if all agents are done
            done = all(terminations.values()) or all(truncations.values()) or step >= args.max_cycles

        # Logging
        if episode % 10 == 0 or episode == args.total_episodes - 1:
            mean_reward = np.mean([episode_rewards[agent] for agent in ma_dqn.agents])
            print(f"Episode {episode:4d} | Steps: {ma_dqn.global_step:6d} | "
                  f"Epsilon: {epsilon:.3f} | Mean Reward: {mean_reward:7.2f} | "
                  f"Buffer: {len(ma_dqn.replay_buffer):5d}")

        # Save checkpoint
        if episode > 0 and episode % args.save_freq == 0:
            ma_dqn.save_checkpoint(episode)

    # Final checkpoint
    ma_dqn.save_checkpoint(args.total_episodes)

    print(f"Training complete!")
    env.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--exp-name", type=str, default="ma_dqn")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--total-episodes", type=int, default=1000)
    parser.add_argument("--learning-rate", type=float, default=2.5e-4)
    parser.add_argument("--save-freq", type=int, default=100)
    parser.add_argument("--log-dir", type=str, default="logs")
    parser.add_argument("--checkpoint-dir", type=str, default="checkpoints")

    args = parser.parse_args()
    args = Args(**vars(args))  # Convert to dataclass

    train(args)
