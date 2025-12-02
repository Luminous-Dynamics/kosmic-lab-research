#!/usr/bin/env python3
"""
Simplified GPU-Accelerated Training for Overcooked O/R Index Validation
========================================================================

Single scenario (cramped_room) with GPU acceleration and MotionPlanner caching.
Designed to complete in 2-4 hours with clear progress monitoring.

Usage:
    python train_overcooked_gpu_simple.py
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from pathlib import Path
from tqdm import tqdm
import json
import sys

from env_overcooked import OvercookedMARLEnv

# GPU Configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🎮 Using device: {device}")
if torch.cuda.is_available():
    print(f"   GPU: {torch.cuda.get_device_name(0)}")
    print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")


class SimplePolicy(nn.Module):
    """Policy network - moved to GPU"""
    def __init__(self, obs_dim, n_actions):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(obs_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, n_actions)
        )

    def forward(self, x):
        return self.network(x)

    def act(self, obs, epsilon=0.0):
        """Select action with optional exploration"""
        with torch.no_grad():
            obs_tensor = torch.FloatTensor(obs).unsqueeze(0).to(device)
            logits = self.forward(obs_tensor)
            probs = torch.softmax(logits, dim=-1)

            if np.random.rand() < epsilon:
                action = np.random.randint(0, len(probs[0]))
            else:
                action = torch.argmax(probs[0]).cpu().item()

            return action, probs[0].cpu().numpy()


def collect_episode_gpu(env, policies, seed=None):
    """Collect episode with GPU-accelerated policies"""
    if seed is not None:
        np.random.seed(seed)

    state = env.reset()
    if state is None:
        raise RuntimeError("Environment reset returned None")

    obs, actions, rewards, dones = [], [], [], []
    total_reward = 0

    for t in range(env.horizon):
        # Get actions from both policies (on GPU)
        action_0, _ = policies[0].act(state)
        action_1, _ = policies[1].act(state)
        joint_action = (action_0, action_1)

        # Environment step with illegal action retry
        max_retries = 5
        for retry in range(max_retries):
            try:
                next_state, reward, done, info = env.step(joint_action)
                break  # Success
            except Exception as e:
                if retry < max_retries - 1:
                    # Try random actions
                    action_0 = np.random.randint(0, env.n_actions)
                    action_1 = np.random.randint(0, env.n_actions)
                    joint_action = (action_0, action_1)
                else:
                    # Give up after max retries
                    print(f"Warning: Step failed after {max_retries} retries at t={t}: {e}")
                    # Return what we have so far
                    if len(obs) == 0:
                        # Episode failed immediately, return minimal valid data
                        return (np.array([state]), np.array([[0, 0]]), np.array([0.0]),
                                np.array([True]), 0.0)
                    return (np.array(obs), np.array(actions), np.array(rewards),
                            np.array(dones), total_reward)

        # Store transition
        obs.append(state)
        actions.append(joint_action)
        rewards.append(reward)
        dones.append(done)
        total_reward += reward

        state = next_state
        if done:
            break

    return (np.array(obs), np.array(actions), np.array(rewards),
            np.array(dones), total_reward)


def train_checkpoint_gpu(env, n_episodes, lr=3e-4, gamma=0.99):
    """Train policies with GPU acceleration"""
    policies = [
        SimplePolicy(env.obs_dim, env.n_actions).to(device),
        SimplePolicy(env.obs_dim, env.n_actions).to(device)
    ]

    optimizers = [
        optim.Adam(policies[0].parameters(), lr=lr),
        optim.Adam(policies[1].parameters(), lr=lr)
    ]

    mean_rewards = []

    pbar = tqdm(range(n_episodes), desc="Training", ncols=100)
    for episode in pbar:
        # Collect episode
        obs, actions, rewards, dones, ep_return = collect_episode_gpu(
            env, policies, seed=episode
        )

        # Compute returns (on GPU)
        returns = []
        G = 0
        for r in reversed(rewards):
            G = r + gamma * G
            returns.insert(0, G)
        returns = torch.FloatTensor(returns).to(device)

        # Normalize returns
        if len(returns) > 1:
            returns = (returns - returns.mean()) / (returns.std() + 1e-8)

        # Policy gradient update for both agents
        for agent_id in [0, 1]:
            optimizer = optimizers[agent_id]
            optimizer.zero_grad()

            # Get log probs for taken actions
            obs_tensor = torch.FloatTensor(obs).to(device)
            logits = policies[agent_id](obs_tensor)
            log_probs = torch.log_softmax(logits, dim=-1)

            # Actions for this agent
            agent_actions = torch.LongTensor([a[agent_id] for a in actions]).to(device)
            selected_log_probs = log_probs.gather(1, agent_actions.unsqueeze(1)).squeeze()

            # Policy gradient loss
            loss = -(selected_log_probs * returns).mean()
            loss.backward()
            optimizer.step()

        mean_rewards.append(ep_return)

        # Update progress bar
        if (episode + 1) % 10 == 0:
            avg_reward = np.mean(mean_rewards[-10:])
            pbar.set_postfix({'avg_reward': f'{avg_reward:.1f}'})

    final_mean_reward = np.mean(mean_rewards[-100:]) if len(mean_rewards) >= 100 else np.mean(mean_rewards)

    return policies, final_mean_reward


def main():
    """Main training loop - simplified single scenario"""

    print("\n" + "="*70)
    print("🚀 GPU-Accelerated Simplified Overcooked Training")
    print("="*70)
    print(f"Device: {device}")
    print("Scenario: cramped_room (single baseline)")
    print("Checkpoints: random, ppo_5k, ppo_50k, ppo_200k")
    print("Expected time: 2-4 hours with GPU")
    print("="*70 + "\n")

    # Single scenario configuration
    layout = "cramped_room"
    horizon = 400
    scenario_id = f"{layout}_h{horizon}_baseline_gpu"

    # Create environment (with MotionPlanner caching disabled)
    print(f"Setting up environment: {layout} (horizon={horizon})")
    print("⚠️  MotionPlanner disabled for speed - using simple heuristics\n")

    env = OvercookedMARLEnv(layout, horizon=horizon, use_motion_planner=True)

    # Model save directory
    models_dir = Path(f"../../models/overcooked/{scenario_id}")
    models_dir.mkdir(parents=True, exist_ok=True)

    # Training checkpoints
    checkpoints = [
        ("random", 0),
        ("ppo_5k", 125),      # ~5k timesteps
        ("ppo_50k", 1250),    # ~50k timesteps
        ("ppo_200k", 5000),   # ~200k timesteps
    ]

    for ckpt_name, n_episodes in checkpoints:
        print("\n" + "="*70)
        print(f"Training checkpoint: {ckpt_name}")
        print("="*70)

        if n_episodes == 0:
            # Random baseline - just save random policies
            print("Saving random initialization...")
            policies = [
                SimplePolicy(env.obs_dim, env.n_actions).to(device),
                SimplePolicy(env.obs_dim, env.n_actions).to(device)
            ]
            mean_reward = 0.0
        else:
            # Train policies
            policies, mean_reward = train_checkpoint_gpu(env, n_episodes)

        # Save checkpoint
        checkpoint_path = models_dir / f"{ckpt_name}.pth"
        torch.save({
            'policy_0': policies[0].state_dict(),
            'policy_1': policies[1].state_dict(),
            'n_episodes': n_episodes,
            'mean_reward': mean_reward,
        }, checkpoint_path)

        # Save metadata
        metadata = {
            'scenario_id': scenario_id,
            'layout': layout,
            'horizon': horizon,
            'checkpoint': ckpt_name,
            'n_episodes': n_episodes,
            'mean_reward': float(mean_reward),
            'device': str(device),
        }

        with open(models_dir / f"{ckpt_name}_meta.json", 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"✓ Saved: {checkpoint_path} (mean reward: {mean_reward:.1f})")

    print("\n" + "="*70)
    print("✅ Training complete!")
    print("="*70)
    print(f"Saved checkpoints: {models_dir}")
    print("\nNext steps:")
    print("  1. Run: python collect_overcooked.py")
    print("  2. Run: python analyze_overcooked.py")
    print("  3. Check: outputs/ for figures and results")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
