"""
Multi-Agent QMIX for MPE Cooperative Navigation
QMIX: Monotonic Value Function Factorisation for Decentralised Multi-Agent RL

Based on the original QMIX paper (Rashid et al., ICML 2018)
Key innovation: Mixing network with positive weights ensures Individual-Global-Max (IGM) principle
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
    exp_name: str = "ma_qmix"
    seed: int = 42
    torch_deterministic: bool = True
    cuda: bool = True  # QMIX benefits from GPU for mixing network

    # Environment
    num_agents: int = 3
    max_cycles: int = 25
    local_ratio: float = 0.5
    continuous_actions: bool = False

    # Training
    total_episodes: int = 1000
    learning_rate: float = 5e-4
    buffer_size: int = 10000
    gamma: float = 0.99
    target_network_frequency: int = 200
    batch_size: int = 32  # Smaller batch for joint updates
    start_e: float = 1.0
    end_e: float = 0.05
    exploration_fraction: float = 0.5
    learning_starts: int = 1000
    train_frequency: int = 1  # Update more frequently

    # QMIX-specific
    mixing_embed_dim: int = 32  # Mixing network hidden dimension
    hypernet_layers: int = 2  # Hypernetwork depth
    hypernet_embed: int = 64  # Hypernetwork hidden dimension

    # Logging
    save_freq: int = 100
    log_dir: str = "logs"
    checkpoint_dir: str = "checkpoints"


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


class MultiAgentReplayBuffer:
    """Replay buffer storing joint transitions for QMIX"""
    def __init__(self, capacity, num_agents):
        self.buffer = deque(maxlen=capacity)
        self.num_agents = num_agents

    def push(self, obs_dict, actions_dict, rewards_dict, next_obs_dict, dones_dict, state, next_state):
        """
        Store joint transition

        Args:
            obs_dict: {agent_id: obs} observations for all agents
            actions_dict: {agent_id: action} actions taken
            rewards_dict: {agent_id: reward} individual rewards
            next_obs_dict: {agent_id: next_obs} next observations
            dones_dict: {agent_id: done} done flags
            state: global state (concatenated observations)
            next_state: next global state
        """
        self.buffer.append((obs_dict, actions_dict, rewards_dict, next_obs_dict, dones_dict, state, next_state))

    def sample(self, batch_size):
        """Sample batch of joint transitions"""
        if len(self.buffer) < batch_size:
            return None

        indices = np.random.choice(len(self.buffer), batch_size, replace=False)
        batch = [self.buffer[i] for i in indices]

        # Unpack batch
        obs_dicts, actions_dicts, rewards_dicts, next_obs_dicts, dones_dicts, states, next_states = zip(*batch)

        # Convert to tensors
        # obs: (batch, num_agents, obs_dim)
        obs_batch = torch.FloatTensor(np.array([[obs_dicts[i][f'agent_{j}'] for j in range(self.num_agents)]
                                                 for i in range(batch_size)]))

        actions_batch = torch.LongTensor(np.array([[actions_dicts[i][f'agent_{j}'] for j in range(self.num_agents)]
                                                     for i in range(batch_size)]))

        # Use team reward (sum of individual rewards)
        rewards_batch = torch.FloatTensor(np.array([sum(rewards_dicts[i].values()) for i in range(batch_size)]))

        next_obs_batch = torch.FloatTensor(np.array([[next_obs_dicts[i][f'agent_{j}'] for j in range(self.num_agents)]
                                                       for i in range(batch_size)]))

        # Done if any agent is done
        dones_batch = torch.FloatTensor(np.array([any(dones_dicts[i].values()) for i in range(batch_size)]))

        states_batch = torch.FloatTensor(np.array(states))
        next_states_batch = torch.FloatTensor(np.array(next_states))

        return obs_batch, actions_batch, rewards_batch, next_obs_batch, dones_batch, states_batch, next_states_batch

    def __len__(self):
        return len(self.buffer)


def train_qmix(args):
    """Train QMIX agents"""
    # Set random seeds
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if args.torch_deterministic:
        torch.backends.cudnn.deterministic = True

    device = torch.device("cuda" if torch.cuda.is_available() and args.cuda else "cpu")
    print(f"Using device: {device}")

    # Create environment
    env = simple_spread_v3.parallel_env(
        N=args.num_agents,
        local_ratio=args.local_ratio,
        max_cycles=args.max_cycles,
        continuous_actions=args.continuous_actions,
    )

    # Get dimensions
    agent_list = env.possible_agents
    obs_dim = env.observation_space(agent_list[0]).shape[0]
    action_dim = env.action_space(agent_list[0]).n
    state_dim = obs_dim * args.num_agents  # Concatenated observations as state

    print(f"Agents: {args.num_agents}, Obs dim: {obs_dim}, Action dim: {action_dim}, State dim: {state_dim}")

    # Create agent Q-networks (one per agent)
    agent_networks = [AgentQNetwork(obs_dim, action_dim).to(device) for _ in range(args.num_agents)]
    target_agent_networks = [AgentQNetwork(obs_dim, action_dim).to(device) for _ in range(args.num_agents)]

    # Copy initial weights
    for agent_net, target_net in zip(agent_networks, target_agent_networks):
        target_net.load_state_dict(agent_net.state_dict())

    # Create mixing networks
    mixer = QMixerNetwork(args.num_agents, state_dim, args.mixing_embed_dim, args.hypernet_embed).to(device)
    target_mixer = QMixerNetwork(args.num_agents, state_dim, args.mixing_embed_dim, args.hypernet_embed).to(device)
    target_mixer.load_state_dict(mixer.state_dict())

    # Optimizer for all parameters
    params = list(mixer.parameters())
    for agent_net in agent_networks:
        params += list(agent_net.parameters())
    optimizer = optim.Adam(params, lr=args.learning_rate)

    # Replay buffer
    replay_buffer = MultiAgentReplayBuffer(args.buffer_size, args.num_agents)

    # Create directories
    os.makedirs(args.log_dir, exist_ok=True)
    checkpoint_base = os.path.join(args.checkpoint_dir, "qmix", f"seed_{args.seed}")
    os.makedirs(checkpoint_base, exist_ok=True)

    # Training loop
    global_step = 0
    episode_rewards = []

    for episode in range(1, args.total_episodes + 1):
        obs, infos = env.reset(seed=args.seed + episode)
        episode_reward = 0
        episode_steps = 0

        # Compute initial state
        state = np.concatenate([obs[agent] for agent in agent_list])

        for step in range(args.max_cycles):
            # Epsilon-greedy action selection
            epsilon = np.interp(global_step,
                                [0, args.exploration_fraction * args.total_episodes * args.max_cycles],
                                [args.start_e, args.end_e])

            actions = {}
            for i, agent in enumerate(agent_list):
                if random.random() < epsilon:
                    actions[agent] = env.action_space(agent).sample()
                else:
                    obs_tensor = torch.FloatTensor(obs[agent]).unsqueeze(0).to(device)
                    with torch.no_grad():
                        q_values = agent_networks[i](obs_tensor)
                    actions[agent] = q_values.argmax(dim=1).item()

            # Step environment
            next_obs, rewards, dones, truncations, infos = env.step(actions)

            # Compute next state
            next_state = np.concatenate([next_obs[agent] for agent in agent_list])

            # Store transition
            replay_buffer.push(obs, actions, rewards, next_obs, dones, state, next_state)

            episode_reward += sum(rewards.values())
            episode_steps += 1
            global_step += 1

            # Update
            obs = next_obs
            state = next_state

            # Training update
            if global_step > args.learning_starts and global_step % args.train_frequency == 0:
                batch = replay_buffer.sample(args.batch_size)
                if batch is not None:
                    obs_batch, actions_batch, rewards_batch, next_obs_batch, dones_batch, states_batch, next_states_batch = batch

                    # Move to device
                    obs_batch = obs_batch.to(device)
                    actions_batch = actions_batch.to(device)
                    rewards_batch = rewards_batch.to(device).unsqueeze(1)
                    next_obs_batch = next_obs_batch.to(device)
                    dones_batch = dones_batch.to(device).unsqueeze(1)
                    states_batch = states_batch.to(device)
                    next_states_batch = next_states_batch.to(device)

                    # Compute current Q-values for taken actions
                    agent_qs = []
                    for i in range(args.num_agents):
                        q_values = agent_networks[i](obs_batch[:, i, :])
                        taken_q = q_values.gather(1, actions_batch[:, i].unsqueeze(1))
                        agent_qs.append(taken_q)
                    agent_qs = torch.cat(agent_qs, dim=1)  # (batch, num_agents)

                    # Mix Q-values
                    q_tot = mixer(agent_qs, states_batch)  # (batch, 1)

                    # Compute target Q-values
                    with torch.no_grad():
                        target_agent_qs = []
                        for i in range(args.num_agents):
                            target_q_values = target_agent_networks[i](next_obs_batch[:, i, :])
                            target_agent_qs.append(target_q_values.max(dim=1, keepdim=True)[0])
                        target_agent_qs = torch.cat(target_agent_qs, dim=1)

                        target_q_tot = target_mixer(target_agent_qs, next_states_batch)
                        target = rewards_batch + args.gamma * (1 - dones_batch) * target_q_tot

                    # Compute loss
                    loss = F.mse_loss(q_tot, target)

                    # Optimize
                    optimizer.zero_grad()
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(params, 10.0)  # Gradient clipping
                    optimizer.step()

            # Update target networks
            if global_step % args.target_network_frequency == 0:
                for agent_net, target_net in zip(agent_networks, target_agent_networks):
                    target_net.load_state_dict(agent_net.state_dict())
                target_mixer.load_state_dict(mixer.state_dict())

            # Check if episode done
            if any(dones.values()) or any(truncations.values()):
                break

        episode_rewards.append(episode_reward)
        avg_reward = np.mean(episode_rewards[-100:])

        # Logging
        if episode % 10 == 0:
            print(f"Episode {episode}/{args.total_episodes} | "
                  f"Steps: {episode_steps} | "
                  f"Reward: {episode_reward:.2f} | "
                  f"Avg(100): {avg_reward:.2f} | "
                  f"Epsilon: {epsilon:.3f} | "
                  f"Buffer: {len(replay_buffer)}")

        # Save checkpoint
        if episode % args.save_freq == 0:
            checkpoint_path = os.path.join(checkpoint_base, f"episode_{episode}")
            os.makedirs(checkpoint_path, exist_ok=True)

            # Save all agent networks
            for i, agent_net in enumerate(agent_networks):
                torch.save(agent_net.state_dict(),
                          os.path.join(checkpoint_path, f"agent_{i}_qnet.pt"))

            # Save mixer
            torch.save(mixer.state_dict(),
                      os.path.join(checkpoint_path, "mixer.pt"))

            # Save training state
            torch.save({
                'episode': episode,
                'global_step': global_step,
                'optimizer_state_dict': optimizer.state_dict(),
                'avg_reward': avg_reward,
            }, os.path.join(checkpoint_path, "training_state.pt"))

            print(f"Checkpoint saved at episode {episode}")

    env.close()
    print(f"Training complete! Final avg reward: {np.mean(episode_rewards[-100:]):.2f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--cuda", action="store_true", default=True)
    parser.add_argument("--total-episodes", type=int, default=1000)
    parser.add_argument("--save-freq", type=int, default=100)

    args_dict = vars(parser.parse_args())
    args = Args(**args_dict)

    train_qmix(args)
