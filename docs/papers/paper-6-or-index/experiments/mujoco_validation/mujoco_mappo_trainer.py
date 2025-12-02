"""
Multi-Agent PPO for Multi-Agent MuJoCo (Continuous Control)
Adapted from discrete MAPPO for continuous action spaces with O/R Index computation

Key Differences from Discrete MAPPO:
- Normal distribution instead of Categorical
- Continuous action sampling and storage
- Multi-Agent MuJoCo environments (Ant, Swimmer, etc.)
- Integrated O/R Index computation at checkpoints
"""

import argparse
import os
import random
import time
import json
from dataclasses import dataclass
from datetime import datetime

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions.normal import Normal

# Import ContinuousORMetric
import sys
sys.path.insert(0, os.path.dirname(__file__))
from mujoco_or_trainer import ContinuousORMetric


@dataclass
class Args:
    """Training arguments"""
    exp_name: str = "mujoco_mappo"
    seed: int = 42
    torch_deterministic: bool = True
    cuda: bool = True

    # Environment
    env_name: str = "ManyAgentAnt"  # or "ManyAgentSwimmer"
    env_version: str = "v0"
    num_agents: int = 2
    agent_conf: str = "2x4"  # For Ant: 2 agents, 4 legs each
    max_cycles: int = 1000

    # Training
    total_timesteps: int = 500_000  # 500K steps for Week 1
    learning_rate: float = 3e-4
    num_epochs: int = 10  # PPO update epochs
    num_minibatches: int = 32
    gamma: float = 0.99
    gae_lambda: float = 0.95

    # PPO specific
    clip_coef: float = 0.2
    ent_coef: float = 0.01
    vf_coef: float = 0.5
    max_grad_norm: float = 0.5

    # O/R computation
    or_checkpoint_freq: int = 50_000  # Compute O/R every 50K steps
    or_window_size: int = 10_000  # Use last 10K transitions

    # Logging
    save_freq: int = 50_000
    log_dir: str = "logs"
    checkpoint_dir: str = "checkpoints"
    results_dir: str = "results"


class ContinuousAgent(nn.Module):
    """Actor-critic network for continuous actions"""
    def __init__(self, obs_dim, action_dim):
        super().__init__()

        # Shared feature extractor
        self.network = nn.Sequential(
            nn.Linear(obs_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
        )

        # Actor head (Gaussian policy)
        self.actor_mean = nn.Linear(256, action_dim)
        self.actor_logstd = nn.Parameter(torch.zeros(action_dim))

        # Critic head (value function)
        self.critic = nn.Linear(256, 1)

    def get_value(self, x):
        """Get state value"""
        features = self.network(x)
        return self.critic(features)

    def get_action_and_value(self, x, action=None):
        """Get action distribution and value"""
        features = self.network(x)

        # Gaussian policy
        action_mean = self.actor_mean(features)
        action_std = torch.clamp(self.actor_logstd.exp(), min=1e-3, max=1.0)
        probs = Normal(action_mean, action_std)

        if action is None:
            action = probs.sample()

        return action, probs.log_prob(action).sum(-1), probs.entropy().sum(-1), self.critic(features)


class ContinuousRolloutBuffer:
    """Store trajectories for on-policy learning (continuous actions)"""
    def __init__(self, size, obs_dim, action_dim):
        self.size = size
        self.obs_dim = obs_dim
        self.action_dim = action_dim
        self.ptr = 0
        self.full = False

        # Buffers
        self.observations = np.zeros((size, obs_dim), dtype=np.float32)
        self.actions = np.zeros((size, action_dim), dtype=np.float32)  # Changed to float32
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


class MultiAgentMuJoCoTrainer:
    """MAPPO trainer for Multi-Agent MuJoCo with O/R Index computation"""

    def __init__(self, args):
        self.args = args

        # Create directories
        os.makedirs(args.log_dir, exist_ok=True)
        os.makedirs(args.checkpoint_dir, exist_ok=True)
        os.makedirs(args.results_dir, exist_ok=True)

        # Setup device
        self.device = torch.device(
            "cuda" if args.cuda and torch.cuda.is_available() else "cpu"
        )
        print(f"Using device: {self.device}")
        if self.device.type == "cuda":
            print(f"GPU: {torch.cuda.get_device_name(0)}")

        # Initialize environment
        print(f"Loading {args.env_name}-{args.env_version} environment...")
        self.env = self._create_env()

        # Get dimensions from actual observations (space metadata is unreliable)
        sample_obs = self.env.reset()
        if isinstance(sample_obs, list):
            self.obs_dim = sample_obs[0].shape[0]
        else:
            self.obs_dim = sample_obs.shape[0]

        # Get action dimensions from space (handle tuple/list/single space)
        if isinstance(self.env.action_space, (tuple, list)):
            # Multi-agent: tuple or list of spaces, extract from first agent
            self.action_dim = self.env.action_space[0].shape[0]
        else:
            # Single-agent: single space
            self.action_dim = self.env.action_space.shape[0]

        print(f"Observation dim: {self.obs_dim}")
        print(f"Action dim: {self.action_dim}")
        print(f"Number of agents: {args.num_agents}")

        # Create agent networks
        self.agent_networks = {}
        self.optimizers = {}
        self.rollout_buffers = {}

        for i in range(args.num_agents):
            agent_id = f"agent_{i}"
            self.agent_networks[agent_id] = ContinuousAgent(
                self.obs_dim,
                self.action_dim
            ).to(self.device)

            self.optimizers[agent_id] = optim.Adam(
                self.agent_networks[agent_id].parameters(),
                lr=args.learning_rate,
                eps=1e-5
            )

            # Buffer size = max_cycles * 10 episodes
            buffer_size = args.max_cycles * 10
            self.rollout_buffers[agent_id] = ContinuousRolloutBuffer(
                buffer_size,
                self.obs_dim,
                self.action_dim
            )

        # O/R metric tracker
        self.or_metric = ContinuousORMetric(n_bins=10)
        self.or_history = []

        # Training state
        self.global_step = 0
        self.episode = 0
        self.episode_rewards = []

    def _create_env(self):
        """Create Multi-Agent MuJoCo environment"""
        try:
            import gymnasium as gym
            from multiagent_mujoco.mujoco_multi import MujocoMulti

            env_args = {
                "scenario": self.args.env_name,
                "agent_conf": self.args.agent_conf,
                "agent_obsk": 1,  # Each agent observes other agents
                "episode_limit": self.args.max_cycles,
            }

            env = MujocoMulti(env_args=env_args)
            return env

        except ImportError as e:
            print(f"Error loading Multi-Agent MuJoCo: {e}")
            print("Please install: pip install git+https://github.com/schroederdewitt/multiagent_mujoco")
            raise

    def get_action_and_value(self, agent_id, obs):
        """Sample action from policy and get value"""
        with torch.no_grad():
            obs_tensor = torch.FloatTensor(obs).unsqueeze(0).to(self.device)
            action, logprob, _, value = self.agent_networks[agent_id].get_action_and_value(obs_tensor)
            return action.cpu().numpy()[0], logprob.item(), value.item()

    def update(self, agent_id):
        """PPO update for one agent"""
        data = self.rollout_buffers[agent_id].get()

        if len(data['rewards']) < 100:  # Need minimum data
            return None, None, None

        # Convert to tensors
        b_obs = torch.FloatTensor(data['observations']).to(self.device)
        b_actions = torch.FloatTensor(data['actions']).to(self.device)
        b_logprobs = torch.FloatTensor(data['logprobs']).to(self.device)
        b_values = torch.FloatTensor(data['values']).to(self.device)

        # Compute advantages
        with torch.no_grad():
            next_value = self.agent_networks[agent_id].get_value(
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

        # PPO update
        batch_size = len(b_obs)
        minibatch_size = batch_size // self.args.num_minibatches

        total_pg_loss = 0
        total_v_loss = 0
        total_entropy = 0
        num_updates = 0

        for epoch in range(self.args.num_epochs):
            indices = np.random.permutation(batch_size)

            for start in range(0, batch_size, minibatch_size):
                end = start + minibatch_size
                mb_indices = indices[start:end]

                _, newlogprob, entropy, newvalue = self.agent_networks[agent_id].get_action_and_value(
                    b_obs[mb_indices],
                    b_actions[mb_indices]
                )

                # Policy loss
                logratio = newlogprob - b_logprobs[mb_indices]
                ratio = logratio.exp()

                mb_advantages = b_advantages[mb_indices]
                pg_loss1 = -mb_advantages * ratio
                pg_loss2 = -mb_advantages * torch.clamp(
                    ratio, 1 - self.args.clip_coef, 1 + self.args.clip_coef
                )
                pg_loss = torch.max(pg_loss1, pg_loss2).mean()

                # Value loss
                newvalue = newvalue.view(-1)
                v_loss = 0.5 * ((newvalue - b_returns[mb_indices]) ** 2).mean()

                # Entropy bonus
                entropy_loss = entropy.mean()

                # Total loss
                loss = pg_loss - self.args.ent_coef * entropy_loss + self.args.vf_coef * v_loss

                # Optimize
                self.optimizers[agent_id].zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(
                    self.agent_networks[agent_id].parameters(),
                    self.args.max_grad_norm
                )
                self.optimizers[agent_id].step()

                total_pg_loss += pg_loss.item()
                total_v_loss += v_loss.item()
                total_entropy += entropy_loss.item()
                num_updates += 1

        return (
            total_pg_loss / num_updates if num_updates > 0 else 0,
            total_v_loss / num_updates if num_updates > 0 else 0,
            total_entropy / num_updates if num_updates > 0 else 0
        )

    def compute_or_index(self):
        """Compute O/R Index from recent transitions"""
        result = self.or_metric.compute()

        if 'error' not in result:
            self.or_history.append({
                'timestep': self.global_step,
                'or_index': result['or_index'],
                'observation_consistency': result['observation_consistency'],
                'reward_consistency': result['reward_consistency'],
                'n_samples': result['n_samples']
            })

            print(f"\nO/R Index @ {self.global_step:,} steps:")
            print(f"  O/R: {result['or_index']:.4f}")
            print(f"  O: {result['observation_consistency']:.4f}")
            print(f"  R: {result['reward_consistency']:.4f}")
            print(f"  Samples: {result['n_samples']}")

        # Reset metric for next window
        self.or_metric = ContinuousORMetric(n_bins=10)

        return result

    def save_checkpoint(self, filename):
        """Save model checkpoint"""
        checkpoint = {
            'global_step': self.global_step,
            'episode': self.episode,
            'agent_networks': {
                agent_id: net.state_dict()
                for agent_id, net in self.agent_networks.items()
            },
            'optimizers': {
                agent_id: opt.state_dict()
                for agent_id, opt in self.optimizers.items()
            },
            'or_history': self.or_history,
            'args': self.args
        }

        path = os.path.join(self.args.checkpoint_dir, filename)
        torch.save(checkpoint, path)
        print(f"Checkpoint saved: {path}")

    def save_results(self):
        """Save O/R measurements to JSON"""
        results = {
            'env_name': f"{self.args.env_name}-{self.args.env_version}",
            'seed': self.args.seed,
            'total_timesteps': self.global_step,
            'or_measurements': self.or_history,
            'final_or': self.or_history[-1]['or_index'] if self.or_history else None,
            'timestamp': datetime.now().isoformat()
        }

        filename = f"or_results_seed{self.args.seed}_{self.global_step}steps.json"
        path = os.path.join(self.args.results_dir, filename)

        with open(path, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\nResults saved: {path}")
        print(f"Total O/R measurements: {len(self.or_history)}")

    def train(self):
        """Main training loop"""
        print("=" * 80)
        print("Starting Multi-Agent MuJoCo Training with O/R Index")
        print("=" * 80)
        print()

        start_time = time.time()
        episode_start_time = start_time

        while self.global_step < self.args.total_timesteps:
            # Reset environment
            obs = self.env.reset()
            episode_reward = 0
            done = False
            step = 0

            while not done and step < self.args.max_cycles:
                # Get actions for all agents
                actions = []
                for i in range(self.args.num_agents):
                    agent_id = f"agent_{i}"
                    action, logprob, value = self.get_action_and_value(agent_id, obs[i])
                    actions.append(action)

                    # Store in buffer
                    # (We'll add the reward and done after step)

                # Environment step (Multi-Agent MuJoCo returns: reward, done, info)
                reward, done, info = self.env.step(actions)
                next_obs = self.env.get_obs()  # Get observations separately

                # Convert scalar reward/done to per-agent (all agents share same reward/done)
                rewards = [reward] * self.args.num_agents
                dones = [done] * self.args.num_agents

                # Store transitions
                for i in range(self.args.num_agents):
                    agent_id = f"agent_{i}"
                    action, logprob, value = self.get_action_and_value(agent_id, obs[i])

                    self.rollout_buffers[agent_id].add(
                        obs[i], action, logprob, rewards[i],
                        float(dones[i]), value
                    )

                    # Add to O/R metric
                    self.or_metric.add_transition(obs[i], action)

                episode_reward += sum(rewards)
                obs = next_obs
                # done is already a scalar bool
                step += 1
                self.global_step += 1

                # PPO update
                if self.global_step % 2048 == 0:
                    for i in range(self.args.num_agents):
                        agent_id = f"agent_{i}"
                        pg_loss, v_loss, entropy = self.update(agent_id)

                # Compute O/R at checkpoints
                if self.global_step % self.args.or_checkpoint_freq == 0:
                    self.compute_or_index()

                # Save checkpoint
                if self.global_step % self.args.save_freq == 0:
                    self.save_checkpoint(f"checkpoint_{self.global_step}.pt")

            # Episode complete
            self.episode += 1
            self.episode_rewards.append(episode_reward)

            elapsed = time.time() - episode_start_time
            print(f"Episode {self.episode:,} | Steps: {self.global_step:,}/{self.args.total_timesteps:,} | "
                  f"Reward: {episode_reward:.2f} | Time: {elapsed:.1f}s")
            episode_start_time = time.time()

        # Training complete
        total_time = time.time() - start_time
        print()
        print("=" * 80)
        print("Training Complete!")
        print("=" * 80)
        print(f"Total steps: {self.global_step:,}")
        print(f"Total episodes: {self.episode:,}")
        print(f"Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
        print(f"Average reward: {np.mean(self.episode_rewards[-100:]):.2f}")

        # Final O/R computation
        if len(self.or_history) == 0 or self.or_history[-1]['timestep'] < self.global_step:
            print("\nComputing final O/R Index...")
            self.compute_or_index()

        # Save final results
        self.save_results()


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--exp-name", type=str, default="mujoco_mappo")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--cuda", action="store_true", default=True)

    # Environment
    parser.add_argument("--env-name", type=str, default="Ant-v2")
    parser.add_argument("--num-agents", type=int, default=2)
    parser.add_argument("--agent-conf", type=str, default="2x4")

    # Training
    parser.add_argument("--total-timesteps", type=int, default=500_000)
    parser.add_argument("--learning-rate", type=float, default=3e-4)

    return parser.parse_args()


def main():
    """Entry point"""
    args_dict = parse_args()
    args = Args(**vars(args_dict))

    # Set random seeds
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if args.torch_deterministic:
        torch.backends.cudnn.deterministic = True

    # Create trainer and train
    trainer = MultiAgentMuJoCoTrainer(args)
    trainer.train()


if __name__ == "__main__":
    main()
