"""
Full A+B+C Validation: Train policies on 6 Overcooked scenarios

Scenarios:
  A. cramped_room (h=400, h=800)
  B. asymmetric_advantages (h=400, h=800)
  C. coordination_ring (h=400, h=800)

For each scenario:
  - Train 4 checkpoints: random, ppo_5k, ppo_50k, ppo_200k
  - Collect 30 seeds per checkpoint
  - Total: 6 scenarios × 4 policies × 30 seeds = 720 trajectories

Estimated time: 6-8 hours (training) + 5-10 minutes (collection) + 5-10 minutes (analysis)
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import json
from pathlib import Path
from tqdm import tqdm
import sys
from typing import List, Tuple

# Import environment wrapper
from env_overcooked import OvercookedMARLEnv


class PolicyNetwork(nn.Module):
    """Simple feedforward policy for both agents (parameter sharing)"""

    def __init__(self, obs_dim: int, n_actions: int = 6, hidden_size: int = 256):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(obs_dim, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Linear(hidden_size // 2, n_actions)
        )

    def forward(self, obs):
        logits = self.network(obs)
        return logits


def train_reinforce(
    env: OvercookedMARLEnv,
    policy: PolicyNetwork,
    optimizer: optim.Optimizer,
    n_episodes: int,
    gamma: float = 0.99,
    entropy_beta: float = 0.01,
    device: str = "cuda",
    save_every: int = 250,
    save_path: Path = None,
    scenario_name: str = "default"
) -> List[float]:
    """
    Train a policy using REINFORCE with entropy regularization.

    Returns:
        List of episode returns
    """
    returns = []
    policy.train()

    for episode in tqdm(range(n_episodes), desc=f"Training {scenario_name}"):
        # Collect episode
        obs = env.reset()
        log_probs = []
        rewards = []
        entropies = []

        done = False
        while not done:
            # Policy forward pass
            obs_tensor = torch.FloatTensor(obs).unsqueeze(0).to(device)
            logits = policy(obs_tensor)

            # Split logits for two agents (assume parameter sharing)
            mid = len(logits[0]) // 2  # Split in half
            logits_a0 = logits[0, :mid]
            logits_a1 = logits[0, mid:]

            # Sample actions
            dist_a0 = torch.distributions.Categorical(logits=logits_a0)
            dist_a1 = torch.distributions.Categorical(logits=logits_a1)

            a0 = dist_a0.sample()
            a1 = dist_a1.sample()

            # Log probabilities and entropy
            log_probs.append(dist_a0.log_prob(a0) + dist_a1.log_prob(a1))
            entropies.append(dist_a0.entropy() + dist_a1.entropy())

            # Environment step
            obs, reward, done, _ = env.step([a0.item(), a1.item()])
            rewards.append(reward)

        # Compute returns
        G = 0
        returns_episode = []
        for r in reversed(rewards):
            G = r + gamma * G
            returns_episode.insert(0, G)

        returns.append(sum(rewards))

        # Policy gradient update
        returns_tensor = torch.FloatTensor(returns_episode).to(device)
        returns_tensor = (returns_tensor - returns_tensor.mean()) / (returns_tensor.std() + 1e-8)

        policy_loss = []
        for log_prob, G, entropy in zip(log_probs, returns_tensor, entropies):
            policy_loss.append(-log_prob * G - entropy_beta * entropy)

        optimizer.zero_grad()
        loss = torch.stack(policy_loss).sum()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(policy.parameters(), 0.5)
        optimizer.step()

        # Save checkpoint
        if save_path and (episode + 1) % save_every == 0:
            save_path.mkdir(parents=True, exist_ok=True)  # Fix: Create directory
            checkpoint_path = save_path / f"checkpoint_{episode + 1}.pth"
            torch.save({
                'policy_state_dict': policy.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'episode': episode + 1,
                'mean_return': np.mean(returns[-100:]) if len(returns) >= 100 else np.mean(returns)
            }, checkpoint_path)
            print(f"Saved checkpoint: {checkpoint_path}")

    return returns


def train_scenario(
    scenario_id: str,
    layout_name: str,
    horizon: int,
    randomize_positions: bool = False,
    base_dir: Path = Path("models/overcooked"),
    device: str = "cuda"
):
    """Train all 4 checkpoints for a single scenario"""

    print(f"\n{'='*70}")
    print(f"Training scenario: {scenario_id}")
    print(f"{'='*70}\n")

    # Create environment
    env = OvercookedMARLEnv(layout_name, horizon=horizon, use_motion_planner=True, randomize_positions=randomize_positions)
    obs_dim = env.obs_dim
    n_actions = env.n_actions

    print(f"Environment: {layout_name}")
    print(f"  Observation dim: {obs_dim}")
    print(f"  Action space: {n_actions}")
    print(f"  Horizon: {horizon}")
    print(f"  Randomize positions: {randomize_positions}")

    # Create save directory
    save_dir = base_dir / scenario_id
    save_dir.mkdir(parents=True, exist_ok=True)

    # Training configurations
    checkpoints = [
        ("random", 0, None),  # No training
        ("ppo_5k", 125, 3e-4),  # Minimal training
        ("ppo_50k", 1250, 3e-4),  # Medium training
        ("ppo_200k", 5000, 3e-4),  # Full training
    ]

    for checkpoint_name, n_episodes, lr in checkpoints:
        print(f"\n--- Training {checkpoint_name} ({n_episodes} episodes) ---")

        # Initialize policy
        policy = PolicyNetwork(obs_dim, n_actions * 2).to(device)  # *2 for both agents

        if n_episodes == 0:
            # Random policy - no training
            print("Random policy (no training)")
        else:
            # Train policy
            optimizer = optim.Adam(policy.parameters(), lr=lr)
            returns = train_reinforce(
                env, policy, optimizer, n_episodes,
                gamma=0.99, entropy_beta=0.01, device=device,
                save_every=n_episodes // 4,  # Save 4 intermediate checkpoints
                save_path=save_dir / "checkpoints" / checkpoint_name,
                scenario_name=f"{scenario_id}/{checkpoint_name}"
            )

            print(f"Training complete!")
            print(f"  Mean return (last 100): {np.mean(returns[-100:]):.4f}")
            print(f"  Min return: {np.min(returns):.4f}")
            print(f"  Max return: {np.max(returns):.4f}")

        # Save final policy
        final_path = save_dir / f"{checkpoint_name}.pth"
        torch.save({
            'policy_state_dict': policy.state_dict(),
            'obs_dim': obs_dim,
            'n_actions': n_actions,
            'scenario': scenario_id,
            'checkpoint': checkpoint_name,
            'n_episodes': n_episodes
        }, final_path)
        print(f"Saved: {final_path}")

        # Save metadata
        meta_path = save_dir / f"{checkpoint_name}_meta.json"
        with open(meta_path, 'w') as f:
            json.dump({
                'scenario': scenario_id,
                'layout': layout_name,
                'horizon': horizon,
                'randomize_positions': randomize_positions,
                'checkpoint': checkpoint_name,
                'n_episodes': n_episodes,
                'obs_dim': obs_dim,
                'n_actions': n_actions,
                'learning_rate': lr,
                'gamma': 0.99,
                'entropy_beta': 0.01
            }, f, indent=2)

    print(f"\n✓ Scenario {scenario_id} complete!\n")


def main():
    """Train all 6 scenarios (A+B+C validation)"""

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    if device == "cpu":
        print("WARNING: No GPU detected! Training will be VERY slow (20-30 hours).")
        response = input("Continue anyway? [y/N]: ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)

    # Define all 6 scenarios matching paper specification (EXPERIMENTAL_DESIGN.md)
    # Format: (scenario_id, layout_name, horizon, randomize_positions)
    scenarios = [
        # Option A: Baseline Validation
        ("cramped_room_h400_baseline", "cramped_room", 400, False),
        ("asymmetric_advantages_h400_baseline", "asymmetric_advantages", 400, False),

        # Option B: Stress Testing
        ("coordination_ring_h400_stress_spatial", "coordination_ring", 400, False),
        ("forced_coordination_h400_stress_sequential", "forced_coordination", 400, False),
        ("cramped_room_h800_stress_temporal", "cramped_room", 800, False),

        # Option C: Many-Agent Simulation
        ("cramped_room_h400_multiagent_sim", "cramped_room", 400, True),  # Randomized positions
    ]

    print("\n" + "="*70)
    print("FULL A+B+C VALIDATION")
    print("="*70)
    print(f"\nScenarios to train: {len(scenarios)}")
    print(f"Checkpoints per scenario: 4 (random, ppo_5k, ppo_50k, ppo_200k)")
    print(f"Total training runs: {len(scenarios) * 4} = {len(scenarios) * 4}")
    print(f"\nEstimated time:")
    print(f"  GPU: ~6-8 hours total")
    print(f"  CPU: ~120-180 hours total (NOT RECOMMENDED)")
    print("\nPress Ctrl+C at any time to abort.\n")
    print("Starting training automatically (no prompt for background execution)...\n")

    # Train all scenarios
    for scenario_id, layout_name, horizon, randomize_positions in scenarios:
        try:
            train_scenario(
                scenario_id=scenario_id,
                layout_name=layout_name,
                horizon=horizon,
                randomize_positions=randomize_positions,
                device=device
            )
        except KeyboardInterrupt:
            print("\n\nTraining interrupted by user!")
            print("Partial results have been saved.")
            sys.exit(0)
        except Exception as e:
            print(f"\nERROR in scenario {scenario_id}: {e}")
            print("Continuing with next scenario...")
            continue

    print("\n" + "="*70)
    print("✅ ALL TRAINING COMPLETE!")
    print("="*70)
    print(f"\nTotal scenarios trained: {len(scenarios)}")
    print(f"Next steps:")
    print(f"  1. Run: python collect_full_abc.py")
    print(f"  2. Run: python analyze_full_abc.py")
    print(f"  3. Check outputs/ for results and figures")
    print()


if __name__ == "__main__":
    main()
