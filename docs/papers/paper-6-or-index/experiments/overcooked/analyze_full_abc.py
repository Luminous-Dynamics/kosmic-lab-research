"""
Analyze O/R Index for all 24 trained policies (6 scenarios × 4 checkpoints).

O/R Index Formula: Var(P(a|o)) / Var(P(a)) - 1

Computes:
  - Per-policy O/R Index
  - Scenario-wise statistics
  - Policy progression (random → 5k → 50k → 200k)
  - CSV output + visualization
"""

import torch
import numpy as np
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple
from tqdm import tqdm


def compute_or_index(trajectories: List[Dict]) -> float:
    """
    Compute O/R Index from trajectories.

    O/R Index = E_o[Var(P(a|o))] / Var(P(a)) - 1

    This measures how much action variance is explained by observation conditioning.
    - O/R = -1: Perfectly deterministic (Var(P(a|o)) = 0 for all o)
    - O/R = 0: No observation dependence (Var(P(a|o)) = Var(P(a)))
    - O/R > 0: Action distributions vary more within observations than marginally

    Where:
    - P(a|o): Probability distribution over actions given observation o
    - P(a): Marginal probability distribution over actions
    - Var(): Variance over the action space

    Args:
        trajectories: List of dicts with 'observations' and 'actions' keys

    Returns:
        O/R Index value in range [-1, ∞)
    """
    # Collect all (observation, action) pairs
    obs_action_pairs = []
    all_actions = []

    for traj in trajectories:
        obs = np.array(traj['observations'])  # (T, obs_dim)
        actions = np.array(traj['actions'])    # (T, 2)

        for o, a in zip(obs, actions):
            # Use joint action (a0, a1) as single action
            obs_action_pairs.append((tuple(o), tuple(a)))
            all_actions.append(tuple(a))

    if len(obs_action_pairs) == 0:
        return 0.0

    # Count occurrences
    obs_action_counts = defaultdict(lambda: defaultdict(int))
    obs_counts = defaultdict(int)
    action_counts = defaultdict(int)

    for obs, action in obs_action_pairs:
        obs_action_counts[obs][action] += 1
        obs_counts[obs] += 1
        action_counts[action] += 1

    # Get all unique actions (defines the action space)
    all_unique_actions = list(action_counts.keys())
    n_actions = len(all_unique_actions)
    total_samples = len(all_actions)

    if n_actions <= 1:
        return 0.0  # Only one action, no variance possible

    # Compute P(a) - marginal action distribution over all actions
    marginal_probs = np.array([action_counts.get(a, 0) / total_samples
                               for a in all_unique_actions])
    var_marginal = np.var(marginal_probs)

    if var_marginal < 1e-10:
        return 0.0  # Uniform marginal, no structure to explain

    # Compute E_o[Var(P(a|o))] - expected variance of conditional distributions
    # For each observation, compute P(a|o) over ALL actions, then take variance
    expected_conditional_var = 0.0
    total_obs_weight = 0.0

    for obs in obs_action_counts:
        obs_count = obs_counts[obs]
        obs_weight = obs_count / total_samples  # P(o)

        # Compute P(a|o) for ALL actions (including zeros for unseen actions)
        conditional_probs = np.array([obs_action_counts[obs].get(a, 0) / obs_count
                                      for a in all_unique_actions])

        # Variance of P(a|o) over action space
        var_conditional = np.var(conditional_probs)

        # Weight by observation probability P(o)
        expected_conditional_var += obs_weight * var_conditional
        total_obs_weight += obs_weight

    # O/R Index: E_o[Var(P(a|o))] / Var(P(a)) - 1
    or_index = (expected_conditional_var / var_marginal) - 1
    return float(or_index)


def load_trajectories(file_path: Path) -> List[Dict]:
    """Load trajectories from JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)


def analyze_all_policies(trajectory_dir: Path) -> pd.DataFrame:
    """
    Analyze O/R Index for all 24 policies.

    Returns:
        DataFrame with columns: scenario, policy, checkpoint, or_index, n_trajectories
    """
    results = []

    # Find all trajectory files
    trajectory_files = sorted(trajectory_dir.glob("*.json"))
    trajectory_files = [f for f in trajectory_files if f.name != "all_trajectories.json"]

    print(f"Found {len(trajectory_files)} trajectory files")

    for file_path in tqdm(trajectory_files, desc="Analyzing policies"):
        # Parse filename: {scenario}_{policy}.json
        filename = file_path.stem

        # Known policy names (check these first, from longest to shortest)
        known_policies = ['ppo_200k', 'ppo_50k', 'ppo_5k', 'random']

        policy = None
        scenario = None
        for p in known_policies:
            if filename.endswith('_' + p):
                policy = p
                scenario = filename[:-len('_' + p)]
                break

        if policy is None:
            print(f"Skipping {filename} (unknown policy)")
            continue

        # Load trajectories
        trajectories = load_trajectories(file_path)

        # Compute O/R Index
        or_index = compute_or_index(trajectories)

        # Map policy name to checkpoint count
        checkpoint_map = {
            'random': 0,
            'ppo_5k': 5000,
            'ppo_50k': 50000,
            'ppo_200k': 200000
        }
        checkpoint = checkpoint_map.get(policy, 0)

        results.append({
            'scenario': scenario,
            'policy': policy,
            'checkpoint': checkpoint,
            'or_index': or_index,
            'n_trajectories': len(trajectories)
        })

        print(f"  {scenario:50s} | {policy:10s} | O/R Index: {or_index:8.4f}")

    return pd.DataFrame(results)


def generate_summary_statistics(df: pd.DataFrame) -> Dict:
    """Generate summary statistics for the results."""
    stats = {}

    # Overall statistics
    stats['overall'] = {
        'mean': df['or_index'].mean(),
        'std': df['or_index'].std(),
        'min': df['or_index'].min(),
        'max': df['or_index'].max(),
        'median': df['or_index'].median()
    }

    # Per-scenario statistics
    stats['by_scenario'] = df.groupby('scenario')['or_index'].agg(['mean', 'std', 'count']).to_dict('index')

    # Per-checkpoint statistics
    stats['by_checkpoint'] = df.groupby('checkpoint')['or_index'].agg(['mean', 'std', 'count']).to_dict('index')

    # Training progression
    stats['progression'] = df.groupby('policy')['or_index'].mean().to_dict()

    return stats


def create_visualizations(df: pd.DataFrame, output_dir: Path):
    """Create visualization figures."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Set style
    sns.set_theme(style="whitegrid")
    plt.rcParams['figure.figsize'] = (14, 10)

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # 1. O/R Index by Policy (Training Progression)
    ax1 = axes[0, 0]
    policy_order = ['random', 'ppo_5k', 'ppo_50k', 'ppo_200k']
    sns.boxplot(data=df, x='policy', y='or_index', order=policy_order, ax=ax1)
    ax1.set_title('O/R Index by Training Checkpoint', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Policy Checkpoint', fontsize=12)
    ax1.set_ylabel('O/R Index', fontsize=12)
    ax1.grid(True, alpha=0.3)

    # 2. O/R Index by Scenario
    ax2 = axes[0, 1]
    scenario_order = df.groupby('scenario')['or_index'].mean().sort_values(ascending=False).index
    sns.boxplot(data=df, x='scenario', y='or_index', order=scenario_order, ax=ax2)
    ax2.set_title('O/R Index by Scenario', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Scenario', fontsize=12)
    ax2.set_ylabel('O/R Index', fontsize=12)
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3)

    # 3. Heatmap: Scenario × Policy
    ax3 = axes[1, 0]
    pivot_table = df.pivot_table(values='or_index', index='scenario', columns='policy', aggfunc='mean')
    pivot_table = pivot_table[policy_order]  # Reorder columns
    sns.heatmap(pivot_table, annot=True, fmt='.3f', cmap='viridis', ax=ax3, cbar_kws={'label': 'O/R Index'})
    ax3.set_title('O/R Index Heatmap (Scenario × Policy)', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Policy Checkpoint', fontsize=12)
    ax3.set_ylabel('Scenario', fontsize=12)

    # 4. Training Progression Line Plot
    ax4 = axes[1, 1]
    for scenario in df['scenario'].unique():
        scenario_df = df[df['scenario'] == scenario].sort_values('checkpoint')
        ax4.plot(scenario_df['checkpoint'], scenario_df['or_index'], marker='o', label=scenario, alpha=0.7)

    ax4.set_title('O/R Index Training Progression', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Training Episodes', fontsize=12)
    ax4.set_ylabel('O/R Index', fontsize=12)
    ax4.legend(fontsize=8, loc='best')
    ax4.grid(True, alpha=0.3)
    ax4.set_xscale('symlog')  # Log scale for better visualization

    plt.tight_layout()
    plt.savefig(output_dir / 'full_abc_or_index_analysis.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved figure: {output_dir / 'full_abc_or_index_analysis.png'}")
    plt.close()


def main():
    # Paths
    trajectory_dir = Path("trajectories/full_abc")
    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("="*80)
    print("O/R Index Analysis - Full A+B+C Validation")
    print("="*80)

    # Analyze all policies
    print("\nComputing O/R Index for all 24 policies...")
    df = analyze_all_policies(trajectory_dir)

    # Save CSV
    csv_path = output_dir / "full_abc_or_index_results.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n✓ Saved results: {csv_path}")

    # Generate statistics
    stats = generate_summary_statistics(df)

    # Save statistics
    stats_path = output_dir / "full_abc_or_index_statistics.json"
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"✓ Saved statistics: {stats_path}")

    # Print summary
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    print(f"\nOverall O/R Index:")
    print(f"  Mean:   {stats['overall']['mean']:.4f}")
    print(f"  Std:    {stats['overall']['std']:.4f}")
    print(f"  Median: {stats['overall']['median']:.4f}")
    print(f"  Range:  [{stats['overall']['min']:.4f}, {stats['overall']['max']:.4f}]")

    print(f"\nTraining Progression (Mean O/R Index):")
    for policy in ['random', 'ppo_5k', 'ppo_50k', 'ppo_200k']:
        if policy in stats['progression']:
            print(f"  {policy:10s}: {stats['progression'][policy]:.4f}")

    # Create visualizations
    print("\nGenerating visualizations...")
    create_visualizations(df, output_dir)

    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE!")
    print("="*80)
    print(f"\nOutputs:")
    print(f"  - CSV:         {csv_path}")
    print(f"  - Statistics:  {stats_path}")
    print(f"  - Figure:      {output_dir / 'full_abc_or_index_analysis.png'}")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
