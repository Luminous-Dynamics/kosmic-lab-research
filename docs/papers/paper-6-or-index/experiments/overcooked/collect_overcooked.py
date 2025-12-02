"""
Collect Overcooked trajectories from trained policies
Saves in standardized NPZ format for O/R analysis
"""

import numpy as np
import torch
import json
from pathlib import Path
from tqdm import tqdm
from env_overcooked import OvercookedMARLEnv
from train_overcooked import SimplePolicy


def load_checkpoint(checkpoint_path: Path, env):
    """Load trained policy checkpoint"""
    checkpoint = torch.load(checkpoint_path, map_location="cpu")

    policies = [
        SimplePolicy(env.obs_dim, env.n_actions) for _ in range(2)
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
    obs = env.reset(seed=seed)
    obs_tensor = torch.from_numpy(obs).float()

    obs_list = []
    actions_list = []
    rewards_list = []
    dones_list = []

    done = False
    while not done:
        # Get actions from each policy
        with torch.no_grad():
            actions = []
            for policy in policies:
                action, _ = policy.act(obs_tensor, deterministic=False)
                actions.append(action)

        # Step environment
        obs_next, reward, done, info = env.step(actions)

        # Store trajectory
        obs_list.append(obs)
        actions_list.append(actions)
        rewards_list.append(reward)
        dones_list.append(done)

        obs = obs_next
        obs_tensor = torch.from_numpy(obs).float()

    episode_return = sum(rewards_list)

    return (
        np.array(obs_list),
        np.array(actions_list),
        np.array(rewards_list),
        np.array(dones_list),
        episode_return,
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

    # Create environment with matching horizon
    env = OvercookedMARLEnv(layout, horizon=horizon)

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
    """Collect all trajectories for all scenarios and policy types - A+B+C Comprehensive Validation"""

    # Match training configuration from train_overcooked.py
    # Format: (layout_name, horizon, scenario_type)
    scenarios = [
        # OPTION A: Standard validation (2 layouts, normal difficulty)
        ("cramped_room", 400, "baseline"),
        ("asymmetric_advantages", 400, "baseline"),

        # OPTION B: Stress tests (harder coordination scenarios)
        ("coordination_ring", 400, "stress_spatial"),
        ("forced_coordination", 400, "stress_sequential"),
        ("cramped_room", 800, "stress_temporal"),

        # OPTION C: "Many-agent simulation" via rapid role-switching
        ("cramped_room", 400, "multiagent_sim"),
    ]

    policy_types = ["random", "ppo_5k", "ppo_50k", "ppo_200k"]
    models_path = Path("../../models/overcooked")

    print("="*60)
    print("Collecting Overcooked Trajectories - A+B+C Validation")
    print("="*60)
    print(f"Scenarios: {len(scenarios)}")
    print(f"Checkpoints per scenario: {len(policy_types)}")
    print(f"Seeds per checkpoint: 30")
    print(f"Total trajectories: {len(scenarios) * len(policy_types) * 30}")

    for layout_name, horizon, scenario_type in scenarios:
        # Match training's scenario_id format
        scenario_id = f"{layout_name}_h{horizon}_{scenario_type}"

        print(f"\n{'#'*60}")
        print(f"# Scenario: {scenario_id}")
        print(f"#   Layout: {layout_name}, Horizon: {horizon}, Type: {scenario_type}")
        print(f"{'#'*60}")

        for policy_type in policy_types:
            checkpoint_path = models_path / scenario_id / f"{policy_type}.pth"

            if not checkpoint_path.exists():
                print(f"  ⚠ Checkpoint not found: {checkpoint_path}")
                print(f"  ⚠ Training may still be in progress or failed")
                continue

            collect_trajectories(
                layout=layout_name,
                scenario_id=scenario_id,
                policy_type=policy_type,
                checkpoint_path=checkpoint_path,
                horizon=horizon,
                n_seeds=30,
            )

    print("\n" + "="*60)
    print("✓ All trajectory collection complete!")
    print("="*60)
    print("\nNext step: Run analyze_overcooked.py to compute O/R and generate plots")


if __name__ == "__main__":
    main()
