#!/usr/bin/env python3
"""
Simplified O/R Index Analysis for GPU-trained policies
Analyzes single-scenario validation results
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy.stats import pearsonr
from sklearn.decomposition import PCA
from tqdm import tqdm
import json


def compute_or_index(observations, actions, n_bins=10):
    """
    Compute O/R Index from trajectory data.

    Args:
        observations: (T, obs_dim) - observation vectors
        actions: (T, n_agents) - discrete action indices
        n_bins: number of observation bins

    Returns:
        or_index: scalar O/R value
    """
    T, obs_dim = observations.shape
    n_agents = actions.shape[1]

    # Project observations to 1D via PCA if needed
    if obs_dim > 1:
        pca = PCA(n_components=1)
        obs_1d = pca.fit_transform(observations).squeeze()
    else:
        obs_1d = observations.squeeze()

    # Create bins using quantiles
    bin_edges = np.quantile(obs_1d, np.linspace(0, 1, n_bins + 1))
    bin_indices = np.digitize(obs_1d, bin_edges[1:-1], right=True)

    # Convert actions to one-hot vectors for variance computation
    # Average over agents to get team-level action representation
    n_actions = int(actions.max()) + 1
    action_onehot = np.zeros((T, n_actions))

    for t in range(T):
        for agent_action in actions[t]:
            action_onehot[t, agent_action] += 1.0 / n_agents

    # Compute total variance (marginal action variance)
    action_mean = action_onehot.mean(axis=0)
    var_total = np.mean(np.sum((action_onehot - action_mean)**2, axis=1))

    # Compute within-bin variances
    bin_vars = []
    for b in range(n_bins):
        mask = (bin_indices == b)
        if np.sum(mask) < 2:
            continue  # Skip bins with too few samples

        actions_bin = action_onehot[mask]
        action_mean_bin = actions_bin.mean(axis=0)
        var_bin = np.mean(np.sum((actions_bin - action_mean_bin)**2, axis=1))
        bin_vars.append(var_bin)

    if len(bin_vars) == 0:
        return 0.0  # Fallback if no bins have enough samples

    var_conditional = np.mean(bin_vars)

    # Handle edge case: constant actions
    if var_total < 1e-9:
        return -1.0

    or_index = var_conditional / var_total - 1.0
    return or_index


def compute_coordination_success(episode_return):
    """
    Normalize episode return to [0, 1] coordination score.
    Approximate baseline: random ~0, expert ~200 for cramped_room
    """
    random_baseline = 0
    expert_baseline = 200

    coord_score = (episode_return - random_baseline) / (expert_baseline - random_baseline)
    return np.clip(coord_score, 0.0, 1.0)


def analyze_scenario(scenario_id="cramped_room_h400_baseline_gpu"):
    """Analyze single scenario and generate results"""

    trajectory_dir = Path(f"./trajectories/{scenario_id}")

    if not trajectory_dir.exists():
        print(f"⚠ Trajectory directory not found: {trajectory_dir}")
        print(f"⚠ Run collect_overcooked_simple.py first!")
        return

    print(f"\n{'='*70}")
    print(f"Analyzing: {scenario_id}")
    print(f"{'='*70}\n")

    policy_types = ["random", "ppo_5k", "ppo_50k", "ppo_200k"]
    results = []

    for policy_type in policy_types:
        policy_dir = trajectory_dir / policy_type

        if not policy_dir.exists():
            print(f"  ⚠ Policy directory not found: {policy_dir}")
            continue

        print(f"Processing: {policy_type}")

        # Get all seeds
        seed_dirs = sorted([d for d in policy_dir.iterdir() if d.is_dir() and d.name.startswith("seed_")])

        for seed_dir in tqdm(seed_dirs, desc=f"  {policy_type}"):
            # Load trajectory
            traj_file = seed_dir / "trajectories.npz"
            if not traj_file.exists():
                continue

            data = np.load(traj_file)
            obs = data["obs"]
            actions = data["actions"]
            ep_return = float(data["ep_return"])
            ep_length = int(data["ep_length"])

            # Compute O/R Index
            or_index = compute_or_index(obs, actions)

            # Compute coordination success
            coord_success = compute_coordination_success(ep_return)

            # Store results
            results.append({
                "scenario_id": scenario_id,
                "policy_type": policy_type,
                "seed": int(seed_dir.name.split("_")[1]),
                "or_index": or_index,
                "coordination_success": coord_success,
                "episode_return": ep_return,
                "episode_length": ep_length,
            })

    # Create DataFrame
    df = pd.DataFrame(results)

    # Print summary statistics
    print(f"\n{'='*70}")
    print("Summary Statistics")
    print(f"{'='*70}\n")

    for policy_type in policy_types:
        policy_data = df[df["policy_type"] == policy_type]
        if len(policy_data) == 0:
            continue

        print(f"{policy_type}:")
        print(f"  O/R Index: {policy_data['or_index'].mean():.4f} ± {policy_data['or_index'].std():.4f}")
        print(f"  Coord Success: {policy_data['coordination_success'].mean():.4f} ± {policy_data['coordination_success'].std():.4f}")
        print(f"  Episode Return: {policy_data['episode_return'].mean():.2f} ± {policy_data['episode_return'].std():.2f}")
        print()

    # Correlation analysis
    print(f"{'='*70}")
    print("Correlation Analysis")
    print(f"{'='*70}\n")

    r, p = pearsonr(df["or_index"], df["coordination_success"])
    print(f"Pearson correlation: r = {r:.4f}, p = {p:.6f}")

    # Linear regression stats
    from scipy import stats
    slope, intercept, r_value, p_value, std_err = stats.linregress(df["or_index"], df["coordination_success"])
    print(f"Linear fit: y = {slope:.4f}x + {intercept:.4f}")
    print(f"R² = {r_value**2:.4f}")

    # Save results
    output_dir = Path("./outputs")
    output_dir.mkdir(exist_ok=True)

    # Save CSV
    csv_path = output_dir / "or_index_results_simple.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n✓ Saved CSV: {csv_path}")

    # Create scatter plot
    plt.figure(figsize=(8, 6))

    colors = {"random": "gray", "ppo_5k": "blue", "ppo_50k": "green", "ppo_200k": "red"}

    for policy_type in policy_types:
        policy_data = df[df["policy_type"] == policy_type]
        plt.scatter(
            policy_data["or_index"],
            policy_data["coordination_success"],
            c=colors.get(policy_type, "black"),
            label=policy_type,
            alpha=0.6,
            s=100
        )

    # Add regression line
    x = np.linspace(df["or_index"].min(), df["or_index"].max(), 100)
    y = slope * x + intercept
    plt.plot(x, y, 'k--', linewidth=2, label=f"Linear fit (R²={r_value**2:.3f})")

    plt.xlabel("O/R Index", fontsize=12)
    plt.ylabel("Coordination Success", fontsize=12)
    plt.title(f"O/R Index vs Coordination Success\n{scenario_id}", fontsize=14)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    fig_path = output_dir / "scatter_or_vs_coord_simple.pdf"
    plt.savefig(fig_path, dpi=300, bbox_inches="tight")
    print(f"✓ Saved figure: {fig_path}")

    # Create training evolution plot
    plt.figure(figsize=(8, 6))

    policy_means = df.groupby("policy_type")["or_index"].mean()
    policy_stds = df.groupby("policy_type")["or_index"].std()

    x_pos = np.arange(len(policy_types))
    plt.errorbar(
        x_pos,
        [policy_means[p] for p in policy_types],
        yerr=[policy_stds[p] for p in policy_types],
        marker='o',
        markersize=10,
        linewidth=2,
        capsize=5
    )

    plt.xticks(x_pos, policy_types)
    plt.xlabel("Training Checkpoint", fontsize=12)
    plt.ylabel("O/R Index", fontsize=12)
    plt.title("O/R Index Evolution Across Training", fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    fig_path = output_dir / "training_evolution_simple.pdf"
    plt.savefig(fig_path, dpi=300, bbox_inches="tight")
    print(f"✓ Saved figure: {fig_path}")

    print(f"\n{'='*70}")
    print("✅ Analysis complete!")
    print(f"{'='*70}")
    print(f"\nResults saved to: {output_dir}/")
    print(f"  - or_index_results_simple.csv")
    print(f"  - scatter_or_vs_coord_simple.pdf")
    print(f"  - training_evolution_simple.pdf")


if __name__ == "__main__":
    analyze_scenario()
