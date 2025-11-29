"""
Train Overcooked policies at 4 checkpoints using simple REINFORCE
Designed to be lightweight and NixOS-friendly (no heavy frameworks)
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical
from pathlib import Path
import json
from tqdm import tqdm
from env_overcooked import OvercookedMARLEnv


class SimplePolicy(nn.Module):
    """Simple feedforward policy network"""

    def __init__(self, obs_dim: int, n_actions: int, hidden_dim: int = 128):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(obs_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, n_actions),
        )

    def forward(self, obs):
        logits = self.network(obs)
        return Categorical(logits=logits)

    def act(self, obs, deterministic=False):
        """Sample action from policy"""
        dist = self.forward(obs)
        if deterministic:
            action = torch.argmax(dist.logits)
        else:
            action = dist.sample()
        return action.item(), dist.log_prob(action)


def compute_returns(rewards, gamma=0.99):
    """Compute discounted returns"""
    returns = []
    R = 0
    for r in reversed(rewards):
        R = r + gamma * R
        returns.insert(0, R)
    return torch.tensor(returns, dtype=torch.float32)


def train_episode(env, policies, optimizers, gamma=0.99):
    """Run one episode and update policies"""
    obs = env.reset()
    obs_tensor = torch.from_numpy(obs).float()

    trajectory = {"obs": [], "actions": [], "log_probs": [], "rewards": []}

    done = False
    while not done:
        # Each agent acts independently (IPPO-style)
        actions = []
        log_probs = []

        for agent_id, policy in enumerate(policies):
            action, log_prob = policy.act(obs_tensor)
            actions.append(action)
            log_probs.append(log_prob)

        # Step environment
        obs_next, reward, done, info = env.step(actions)

        # Store trajectory
        trajectory["obs"].append(obs)
        trajectory["actions"].append(actions)
        trajectory["log_probs"].append(torch.stack(log_probs))
        trajectory["rewards"].append(reward)

        obs = obs_next
        obs_tensor = torch.from_numpy(obs).float()

    # Compute returns
    returns = compute_returns(trajectory["rewards"], gamma)

    # Update each policy
    for agent_id, (policy, optimizer) in enumerate(zip(policies, optimizers)):
        # Extract this agent's log probs
        log_probs = torch.stack([lp[agent_id] for lp in trajectory["log_probs"]])

        # Policy gradient loss
        loss = -(log_probs * returns).mean()

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    return sum(trajectory["rewards"])


def train_checkpoint(
    layout: str,
    checkpoint_name: str,
    n_episodes: int,
    save_path: Path,
    random_init: bool = False,
):
    """Train policies for a specific checkpoint"""

    print(f"\n{'='*60}")
    print(f"Training {checkpoint_name} on {layout}")
    print(f"{'='*60}")

    # Create environment
    env = OvercookedMARLEnv(layout, horizon=400)

    # Create policies (one per agent, parameter-shared in practice)
    policies = [
        SimplePolicy(env.obs_dim, env.n_actions) for _ in range(2)
    ]

    if random_init:
        # Save random policy without training
        print("Saving random initialization...")
        save_checkpoint(policies, save_path, checkpoint_name, 0, 0.0)
        return

    # Create optimizers
    optimizers = [
        optim.Adam(policy.parameters(), lr=3e-4) for policy in policies
    ]

    # Training loop
    episode_rewards = []
    for episode in tqdm(range(n_episodes), desc="Training"):
        episode_reward = train_episode(env, policies, optimizers, gamma=0.99)
        episode_rewards.append(episode_reward)

        # Log progress
        if (episode + 1) % 100 == 0:
            mean_reward = np.mean(episode_rewards[-100:])
            print(f"  Episode {episode+1}/{n_episodes}: Mean reward = {mean_reward:.2f}")

    # Save checkpoint
    final_mean_reward = np.mean(episode_rewards[-100:])
    save_checkpoint(policies, save_path, checkpoint_name, n_episodes, final_mean_reward)

    print(f"✓ Saved {checkpoint_name} (final mean reward: {final_mean_reward:.2f})")


def save_checkpoint(policies, save_path, checkpoint_name, n_episodes, mean_reward):
    """Save policy checkpoint with metadata"""
    save_path.mkdir(parents=True, exist_ok=True)

    # Save policy weights
    checkpoint = {
        "policy_0": policies[0].state_dict(),
        "policy_1": policies[1].state_dict(),
        "n_episodes": n_episodes,
        "mean_reward": mean_reward,
    }
    torch.save(checkpoint, save_path / f"{checkpoint_name}.pth")

    # Save metadata JSON
    meta = {
        "checkpoint_name": checkpoint_name,
        "n_episodes": n_episodes,
        "mean_reward": float(mean_reward),
    }
    with open(save_path / f"{checkpoint_name}_meta.json", "w") as f:
        json.dump(meta, f, indent=2)


def main():
    """Train all checkpoints for both layouts"""

    # Configuration
    layouts = ["cramped_room", "asymmetric_advantages"]
    checkpoints = [
        ("random", 0, True),         # Random initialization
        ("ppo_5k", 125, False),      # ~5k timesteps (125 episodes × 40 steps avg)
        ("ppo_50k", 1250, False),    # ~50k timesteps
        ("ppo_200k", 5000, False),   # ~200k timesteps
    ]

    base_path = Path("../../models/overcooked")

    for layout in layouts:
        print(f"\n{'#'*60}")
        print(f"# Training policies for layout: {layout}")
        print(f"{'#'*60}")

        save_path = base_path / layout

        for checkpoint_name, n_episodes, is_random in checkpoints:
            train_checkpoint(
                layout=layout,
                checkpoint_name=checkpoint_name,
                n_episodes=n_episodes,
                save_path=save_path,
                random_init=is_random,
            )

    print("\n" + "="*60)
    print("✓ All training complete!")
    print("="*60)
    print(f"\nCheckpoints saved to: {base_path}")
    print("\nNext steps:")
    print("  1. Run collect_overcooked.py to generate trajectories")
    print("  2. Run analyze_overcooked.py to compute O/R and generate plots")


if __name__ == "__main__":
    main()
