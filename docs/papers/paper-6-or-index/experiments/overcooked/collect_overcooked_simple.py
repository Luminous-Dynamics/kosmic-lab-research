#!/usr/bin/env python3
"""
Simplified Overcooked Trajectory Collection for GPU-trained policies
Collects trajectories from the simplified single-scenario validation
"""

import numpy as np
import torch
import json
from pathlib import Path
from tqdm import tqdm
from env_overcooked import OvercookedMARLEnv
from train_overcooked_gpu_simple import SimplePolicy


def load_checkpoint(checkpoint_path: Path, env):
    """Load trained policy checkpoint"""
    # Use GPU for fast inference (policies were trained on GPU)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # weights_only=False is safe here - we're loading our own checkpoints
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)

    policies = [
        SimplePolicy(env.obs_dim, env.n_actions).to(device) for _ in range(2)
    ]

    policies[0].load_state_dict(checkpoint["policy_0"])
    policies[1].load_state_dict(checkpoint["policy_1"])

    # Set to eval mode
    for policy in policies:
        policy.eval()

    return policies


def collect_episode(env, policies, seed: int):
    """
    Collect one episode trajectory
    Returns: obs_list, actions_list, rewards_list, dones_list, episode_return
    """
    np.random.seed(seed)
    obs = env.reset(seed=seed)

    obs_list = []
    actions_list = []
    rewards_list = []
    dones_list = []

    total_reward = 0
    for t in range(env.horizon):
        # Get actions from each policy (epsilon-greedy for robustness to illegal actions)
        action_0, _ = policies[0].act(obs, epsilon=0.2)
        action_1, _ = policies[1].act(obs, epsilon=0.2)
        joint_action = (action_0, action_1)

        # Environment step with illegal action retry
        max_retries = 5
        for retry in range(max_retries):
            try:
                obs_next, reward, done, info = env.step(joint_action)
                break  # Success
            except Exception as e:
                if retry < max_retries - 1:
                    # Try random actions
                    action_0 = np.random.randint(0, env.n_actions)
                    action_1 = np.random.randint(0, env.n_actions)
                    joint_action = (action_0, action_1)
                else:
                    # Give up after max retries - end episode
                    if len(obs_list) == 0:
                        # Episode failed immediately, return minimal valid data
                        return (
                            np.array([obs]),
                            np.array([[0, 0]]),
                            np.array([0.0]),
                            np.array([True]),
                            0.0,
                        )
                    # Return what we have so far
                    return (
                        np.array(obs_list),
                        np.array(actions_list),
                        np.array(rewards_list),
                        np.array(dones_list),
                        total_reward,
                    )

        # Store trajectory
        obs_list.append(obs)
        actions_list.append(joint_action)
        rewards_list.append(reward)
        dones_list.append(done)
        total_reward += reward

        obs = obs_next
        if done:
            break

    return (
        np.array(obs_list),
        np.array(actions_list),
        np.array(rewards_list),
        np.array(dones_list),
        total_reward,
    )


def collect_trajectories(
    layout: str,
    scenario_id: str,
    policy_type: str,
    checkpoint_path: Path,
    horizon: int,
    n_seeds: int = 30,
):
    """Collect trajectories for a given policy and save"""

    print(f"\nCollecting trajectories: {scenario_id} / {policy_type}")
    print(f"  Checkpoint: {checkpoint_path}")
    print(f"  Layout: {layout}, Horizon: {horizon}")

    # Create environment with matching horizon (MotionPlanner enabled for proper action validation)
    env = OvercookedMARLEnv(layout, horizon=horizon, use_motion_planner=True)

    # Load policies
    policies = load_checkpoint(checkpoint_path, env)

    # Output directory matches training structure
    output_dir = Path(f"./trajectories/{scenario_id}/{policy_type}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Collect trajectories for each seed
    for seed in tqdm(range(n_seeds), desc=f"  {policy_type}"):
        # Collect episode
        obs, actions, rewards, dones, ep_return = collect_episode(
            env, policies, seed
        )

        # Create seed directory
        seed_dir = output_dir / f"seed_{seed:03d}"
        seed_dir.mkdir(parents=True, exist_ok=True)

        # Save trajectory NPZ
        np.savez(
            seed_dir / "trajectories.npz",
            obs=obs,                      # (T, obs_dim)
            actions=actions,              # (T, 2) - two agents
            rewards=rewards,              # (T,)
            dones=dones,                  # (T,)
            ep_return=ep_return,
            ep_length=len(rewards),
        )

        # Save metadata JSON
        meta = {
            "scenario_id": scenario_id,
            "layout": layout,
            "horizon": horizon,
            "policy_type": policy_type,
            "seed": seed,
            "episode_return": float(ep_return),
            "episode_length": int(len(rewards)),
            "checkpoint_path": str(checkpoint_path),
        }

        with open(seed_dir / "meta.json", "w") as f:
            json.dump(meta, f, indent=2)

    print(f"  ✓ Saved {n_seeds} trajectories to {output_dir}")


def main():
    """Collect trajectories for simplified single-scenario validation"""

    layout = "cramped_room"
    horizon = 400
    scenario_id = f"{layout}_h{horizon}_baseline_gpu"
    policy_types = ["random", "ppo_5k", "ppo_50k", "ppo_200k"]
    models_path = Path("../../models/overcooked")

    print("="*70)
    print("🚀 GPU-Accelerated Simplified Overcooked Trajectory Collection")
    print("="*70)
    print(f"Scenario: {scenario_id}")
    print(f"Checkpoints: {len(policy_types)}")
    print(f"Seeds per checkpoint: 30")
    print(f"Total trajectories: {len(policy_types) * 30}")
    print("="*70)

    for policy_type in policy_types:
        checkpoint_path = models_path / scenario_id / f"{policy_type}.pth"

        if not checkpoint_path.exists():
            print(f"  ⚠ Checkpoint not found: {checkpoint_path}")
            print(f"  ⚠ Skipping {policy_type}")
            continue

        collect_trajectories(
            layout=layout,
            scenario_id=scenario_id,
            policy_type=policy_type,
            checkpoint_path=checkpoint_path,
            horizon=horizon,
            n_seeds=30,
        )

    print("\n" + "="*70)
    print("✅ All trajectory collection complete!")
    print("="*70)
    print("\nNext step: Run analyze_overcooked.py to compute O/R and generate plots")


if __name__ == "__main__":
    main()
