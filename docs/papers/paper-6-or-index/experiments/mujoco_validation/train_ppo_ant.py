#!/usr/bin/env python3
"""
Simple PPO training on Gymnasium Ant-v4 for binning sensitivity validation.

This script trains a basic PPO policy on Ant-v4 for 50K steps to generate
a checkpoint suitable for binning sensitivity ablation.

Training time: ~2-4 hours on CPU, ~30-60 minutes on GPU.
"""

import os
import time
from dataclasses import dataclass
from pathlib import Path

import gymnasium as gym
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions.normal import Normal


@dataclass
class Args:
    """Training hyperparameters for PPO on Ant-v4."""
    exp_name: str = "ppo_ant_binning"
    seed: int = 42
    torch_deterministic: bool = True
    cuda: bool = True

    # Environment
    env_name: str = "Ant-v4"

    # Training
    total_timesteps: int = 50_000
    learning_rate: float = 3e-4
    num_steps: int = 2048  # Steps per rollout
    num_epochs: int = 10  # PPO epochs per update
    num_minibatches: int = 32

    # PPO hyperparameters
    gamma: float = 0.99
    gae_lambda: float = 0.95
    clip_coef: float = 0.2
    ent_coef: float = 0.01
    vf_coef: float = 0.5
    max_grad_norm: float = 0.5

    # Logging
    checkpoint_freq: int = 10_000
    checkpoint_dir: str = "checkpoints"
    log_dir: str = "logs"


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


def train_ppo():
    """Train PPO on Ant-v4."""
    args = Args()

    # Setup
    run_name = f"{args.exp_name}__{args.seed}__{int(time.time())}"
    os.makedirs(args.checkpoint_dir, exist_ok=True)
    os.makedirs(args.log_dir, exist_ok=True)

    # Seeding
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.backends.cudnn.deterministic = args.torch_deterministic

    device = torch.device("cuda" if torch.cuda.is_available() and args.cuda else "cpu")
    print(f"Using device: {device}")

    # Environment
    env = gym.make(args.env_name)
    obs_dim = np.prod(env.observation_space.shape)
    action_dim = np.prod(env.action_space.shape)

    print(f"Environment: {args.env_name}")
    print(f"Observation dim: {obs_dim}, Action dim: {action_dim}")

    # Agent
    agent = Agent(obs_dim, action_dim).to(device)
    optimizer = optim.Adam(agent.parameters(), lr=args.learning_rate, eps=1e-5)

    # Storage
    batch_size = args.num_steps
    obs = torch.zeros((args.num_steps,) + env.observation_space.shape).to(device)
    actions = torch.zeros((args.num_steps,) + env.action_space.shape).to(device)
    logprobs = torch.zeros(args.num_steps).to(device)
    rewards = torch.zeros(args.num_steps).to(device)
    dones = torch.zeros(args.num_steps).to(device)
    values = torch.zeros(args.num_steps).to(device)

    # Training
    global_step = 0
    start_time = time.time()
    next_obs, _ = env.reset(seed=args.seed)
    next_obs = torch.Tensor(next_obs).to(device)
    next_done = torch.zeros(1).to(device)
    num_updates = args.total_timesteps // args.num_steps

    print(f"\nStarting training for {args.total_timesteps} steps ({num_updates} updates)...")
    print(f"Expected time: ~{num_updates * 2 / 60:.1f} minutes on CPU")

    for update in range(1, num_updates + 1):
        # Collect rollout
        for step in range(args.num_steps):
            global_step += 1
            obs[step] = next_obs
            dones[step] = next_done

            with torch.no_grad():
                action, logprob, _, value = agent.get_action_and_value(next_obs.unsqueeze(0))
                values[step] = value.flatten()
            actions[step] = action
            logprobs[step] = logprob

            next_obs, reward, terminated, truncated, _ = env.step(action.cpu().numpy()[0])  # Remove batch dimension
            done = terminated or truncated
            rewards[step] = torch.tensor(reward).to(device).view(-1)
            next_obs = torch.Tensor(next_obs).to(device)
            next_done = torch.Tensor([done]).to(device)

            if done:
                next_obs, _ = env.reset()
                next_obs = torch.Tensor(next_obs).to(device)

        # Compute advantages using GAE
        with torch.no_grad():
            next_value = agent.get_value(next_obs.unsqueeze(0)).flatten()
            advantages = torch.zeros_like(rewards).to(device)
            lastgaelam = 0
            for t in reversed(range(args.num_steps)):
                if t == args.num_steps - 1:
                    nextnonterminal = 1.0 - next_done
                    nextvalues = next_value
                else:
                    nextnonterminal = 1.0 - dones[t + 1]
                    nextvalues = values[t + 1]
                delta = rewards[t] + args.gamma * nextvalues * nextnonterminal - values[t]
                advantages[t] = lastgaelam = delta + args.gamma * args.gae_lambda * nextnonterminal * lastgaelam
            returns = advantages + values

        # Flatten batch
        b_obs = obs.reshape((-1,) + env.observation_space.shape)
        b_logprobs = logprobs.reshape(-1)
        b_actions = actions.reshape((-1,) + env.action_space.shape)
        b_advantages = advantages.reshape(-1)
        b_returns = returns.reshape(-1)
        b_values = values.reshape(-1)

        # Optimize policy and value network
        b_inds = np.arange(batch_size)
        minibatch_size = batch_size // args.num_minibatches

        for epoch in range(args.num_epochs):
            np.random.shuffle(b_inds)
            for start in range(0, batch_size, minibatch_size):
                end = start + minibatch_size
                mb_inds = b_inds[start:end]

                _, newlogprob, entropy, newvalue = agent.get_action_and_value(
                    b_obs[mb_inds], b_actions[mb_inds]
                )
                logratio = newlogprob - b_logprobs[mb_inds]
                ratio = logratio.exp()

                mb_advantages = b_advantages[mb_inds]
                mb_advantages = (mb_advantages - mb_advantages.mean()) / (mb_advantages.std() + 1e-8)

                # Policy loss
                pg_loss1 = -mb_advantages * ratio
                pg_loss2 = -mb_advantages * torch.clamp(ratio, 1 - args.clip_coef, 1 + args.clip_coef)
                pg_loss = torch.max(pg_loss1, pg_loss2).mean()

                # Value loss
                newvalue = newvalue.view(-1)
                v_loss = 0.5 * ((newvalue - b_returns[mb_inds]) ** 2).mean()

                # Entropy loss
                entropy_loss = entropy.mean()

                # Total loss
                loss = pg_loss - args.ent_coef * entropy_loss + v_loss * args.vf_coef

                optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(agent.parameters(), args.max_grad_norm)
                optimizer.step()

        # Logging
        if update % 5 == 0:
            elapsed = time.time() - start_time
            steps_per_sec = global_step / elapsed
            eta = (args.total_timesteps - global_step) / steps_per_sec / 60
            print(f"Update {update}/{num_updates} | Step {global_step:,}/{args.total_timesteps:,} | "
                  f"Reward: {rewards.mean().item():.2f} | "
                  f"SPS: {steps_per_sec:.0f} | ETA: {eta:.1f}min")

        # Save checkpoint
        if global_step % args.checkpoint_freq == 0 or update == num_updates:
            checkpoint_path = Path(args.checkpoint_dir) / f"ppo_ant_checkpoint_{global_step}.pt"
            torch.save({
                'agent_state_dict': agent.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'args': args,
                'global_step': global_step,
            }, checkpoint_path)
            print(f"✅ Checkpoint saved: {checkpoint_path}")

    env.close()
    print(f"\n✅ Training complete! Total time: {(time.time() - start_time) / 60:.1f} minutes")
    print(f"Final checkpoint: {args.checkpoint_dir}/ppo_ant_checkpoint_{global_step}.pt")


if __name__ == "__main__":
    train_ppo()
