"""
Collect trajectories from all 24 trained policies (6 scenarios × 4 checkpoints)

For each policy:
  - Run 30 episodes with different random seeds
  - Save (observations, actions) trajectories
  - Total: 720 trajectories

Estimated time: ~30 minutes
"""

import torch
import numpy as np
import json
from pathlib import Path
from tqdm import tqdm
from typing import List, Dict, Tuple
import sys

# Import environment and policy
from env_overcooked import OvercookedMARLEnv
from train_full_abc_validation import PolicyNetwork


def collect_trajectory(
    env: OvercookedMARLEnv,
    policy: PolicyNetwork,
    seed: int,
    device: str = "cuda"
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Collect a single trajectory (observations, actions).

    Returns:
        observations: (T, obs_dim) array
        actions: (T, 2) array of joint actions
    """
    policy.eval()

    obs = env.reset(seed=seed)
    observations = [obs]
    actions = []

    done = False
    with torch.no_grad():
        while not done:
            # Get policy actions
            obs_tensor = torch.FloatTensor(obs).unsqueeze(0).to(device)
            logits = policy(obs_tensor)

            # Split logits for two agents (parameter sharing, same as training)
            mid = len(logits[0]) // 2
            logits_a0 = logits[0, :mid]
            logits_a1 = logits[0, mid:]

            # Sample actions for each agent
            dist_a0 = torch.distributions.Categorical(logits=logits_a0)
            dist_a1 = torch.distributions.Categorical(logits=logits_a1)
            a0 = dist_a0.sample().item()
            a1 = dist_a1.sample().item()

            # Step environment (pass as list, same as training)
            obs, reward, done, info = env.step([a0, a1])

            observations.append(obs)
            actions.append([a0, a1])

    return np.array(observations[:-1]), np.array(actions)  # Remove final obs (after done)


def collect_policy_trajectories(
    scenario_id: str,
    layout_name: str,
    horizon: int,
    randomize_positions: bool,
    policy_name: str,
    model_path: Path,
    n_seeds: int = 30,
    device: str = "cuda"
) -> List[Dict]:
    """
    Collect trajectories for a single policy across multiple seeds.

    Returns:
        List of trajectory dicts with keys: observations, actions, seed, policy, scenario
    """
    # Create environment
    env = OvercookedMARLEnv(
        layout_name=layout_name,
        horizon=horizon,
        use_motion_planner=True,
        randomize_positions=randomize_positions
    )

    # Load checkpoint first to get correct architecture
    if model_path.exists():
        checkpoint = torch.load(model_path, map_location=device)

        # Get architecture from checkpoint metadata
        if isinstance(checkpoint, dict) and 'n_actions' in checkpoint:
            n_actions_ckpt = checkpoint['n_actions']
            obs_dim_ckpt = checkpoint['obs_dim']
        else:
            # Fallback to env dimensions (shouldn't happen with new checkpoints)
            n_actions_ckpt = env.n_actions
            obs_dim_ckpt = env.obs_dim

        # Create policy with correct architecture (same as training: n_actions * 2 for both agents)
        policy = PolicyNetwork(obs_dim_ckpt, n_actions_ckpt * 2).to(device)

        # Load weights
        if isinstance(checkpoint, dict) and 'policy_state_dict' in checkpoint:
            policy.load_state_dict(checkpoint['policy_state_dict'])
        else:
            # Fallback for direct state_dict
            policy.load_state_dict(checkpoint)
    else:
        # Random policy - use environment dimensions
        print(f"Warning: {model_path} not found, using random policy")
        policy = PolicyNetwork(env.obs_dim, env.n_actions * 2).to(device)

    # Collect trajectories
    trajectories = []
    for seed in tqdm(range(n_seeds), desc=f"{scenario_id}/{policy_name}", leave=False):
        obs, actions = collect_trajectory(env, policy, seed, device)

        trajectories.append({
            "observations": obs.tolist(),
            "actions": actions.tolist(),
            "seed": seed,
            "policy": policy_name,
            "scenario": scenario_id,
            "layout": layout_name,
            "horizon": horizon,
            "randomized": randomize_positions
        })

    return trajectories


def main():
    # Configuration
    scenarios = [
        # Option A: Baseline Validation
        ("cramped_room_h400_baseline", "cramped_room", 400, False),
        ("asymmetric_advantages_h400_baseline", "asymmetric_advantages", 400, False),

        # Option B: Stress Testing
        ("coordination_ring_h400_stress_spatial", "coordination_ring", 400, False),
        ("forced_coordination_h400_stress_sequential", "forced_coordination", 400, False),
        ("cramped_room_h800_stress_temporal", "cramped_room", 800, False),

        # Option C: Many-Agent Simulation
        ("cramped_room_h400_multiagent_sim", "cramped_room", 400, True),
    ]

    policies = ["random", "ppo_5k", "ppo_50k", "ppo_200k"]
    n_seeds = 30

    base_dir = Path("models/overcooked")
    output_dir = Path("trajectories/full_abc")
    output_dir.mkdir(parents=True, exist_ok=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    print(f"Collecting {len(scenarios)} scenarios × {len(policies)} policies × {n_seeds} seeds = {len(scenarios) * len(policies) * n_seeds} trajectories\n")

    # Collect all trajectories
    all_trajectories = []

    for scenario_id, layout_name, horizon, randomize_positions in scenarios:
        print(f"\n{'='*70}")
        print(f"Scenario: {scenario_id}")
        print(f"{'='*70}")

        for policy_name in policies:
            model_path = base_dir / scenario_id / f"{policy_name}.pth"

            trajectories = collect_policy_trajectories(
                scenario_id=scenario_id,
                layout_name=layout_name,
                horizon=horizon,
                randomize_positions=randomize_positions,
                policy_name=policy_name,
                model_path=model_path,
                n_seeds=n_seeds,
                device=device
            )

            all_trajectories.extend(trajectories)

            # Save individual policy trajectories
            policy_output = output_dir / f"{scenario_id}_{policy_name}.json"
            with open(policy_output, 'w') as f:
                json.dump(trajectories, f)

            print(f"  ✓ {policy_name}: {len(trajectories)} trajectories → {policy_output}")

    # Save combined file
    combined_output = output_dir / "all_trajectories.json"
    with open(combined_output, 'w') as f:
        json.dump(all_trajectories, f)

    print(f"\n{'='*70}")
    print(f"✅ Collection complete!")
    print(f"Total trajectories: {len(all_trajectories)}")
    print(f"Output directory: {output_dir}")
    print(f"Combined file: {combined_output}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
