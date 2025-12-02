#!/usr/bin/env python3
"""
O/R Index vs Performance Correlation Analysis for Overcooked-AI

This script:
1. Loads O/R Index data from outputs/full_abc_or_index_results.csv
2. Extracts episode returns from trajectory files
3. Computes Pearson correlation with significance testing
4. Generates publication-quality scatter plot with regression line
5. Saves correlation statistics and figure

Created: November 22, 2025
Purpose: Complete empirical validation by demonstrating O/R Index predictive relationship
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats
from typing import Dict, List, Tuple

# Publication-quality plotting
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12


def extract_episode_returns_from_trajectory(traj_file: Path) -> List[float]:
    """
    Extract episode returns from trajectory JSON file.

    The Overcooked environment provides sparse rewards:
    +20 for delivering a completed dish.

    Since trajectories don't explicitly store returns, we need to:
    1. Load the trajectory JSON (list of 30 episodes)
    2. Compute return as the number of timesteps (proxy for efficiency)
       OR count reward events if available

    For now, we'll use episode length as an inverse proxy:
    - Shorter episodes with same deliveries = more efficient = better performance
    - Longer episodes = less efficient coordination = worse performance

    Args:
        traj_file: Path to trajectory JSON file

    Returns:
        List of episode returns (using -length as proxy since lower is better for fixed deliveries)
    """
    with open(traj_file, 'r') as f:
        trajectories = json.load(f)

    # Each trajectory is a dict with 'observations' and 'actions'
    # Episode length = number of timesteps
    episode_lengths = []
    for traj in trajectories:
        # observations is a list of [timestep][agent_obs]
        # Length of observations list = episode length
        episode_length = len(traj['observations'])
        episode_lengths.append(episode_length)

    # Return negative length as proxy for performance
    # (shorter episodes with same task = better performance)
    # This makes correlation directionally consistent with MPE:
    # Lower O/R → Higher performance (less negative = higher)
    return [-length for length in episode_lengths]


def load_or_index_data(csv_path: Path) -> pd.DataFrame:
    """Load O/R Index data from CSV."""
    df = pd.DataFrame(columns=[])
    df = pd.read_csv(csv_path)
    return df


def match_trajectory_files(df: pd.DataFrame, traj_dir: Path) -> pd.DataFrame:
    """
    Match trajectory files to O/R Index data and extract performance metrics.

    Args:
        df: DataFrame with O/R Index data (scenario, policy, checkpoint, or_index)
        traj_dir: Directory containing trajectory JSON files

    Returns:
        DataFrame with added 'mean_return' and 'std_return' columns
    """
    mean_returns = []
    std_returns = []

    for _, row in df.iterrows():
        # Construct trajectory filename from row data
        scenario = row['scenario']
        policy = row['policy']

        # File naming pattern: {scenario}_{policy}.json
        traj_file = traj_dir / f"{scenario}_{policy}.json"

        if not traj_file.exists():
            print(f"Warning: Trajectory file not found: {traj_file}")
            mean_returns.append(np.nan)
            std_returns.append(np.nan)
            continue

        # Extract returns
        returns = extract_episode_returns_from_trajectory(traj_file)
        mean_returns.append(np.mean(returns))
        std_returns.append(np.std(returns))

    df['mean_return'] = mean_returns
    df['std_return'] = std_returns

    return df


def compute_correlation(df: pd.DataFrame) -> Dict:
    """
    Compute Pearson correlation between O/R Index and performance.

    Args:
        df: DataFrame with 'or_index' and 'mean_return' columns

    Returns:
        Dictionary with correlation statistics
    """
    # Remove any NaN values
    clean_df = df.dropna(subset=['or_index', 'mean_return'])

    if len(clean_df) < 3:
        raise ValueError("Insufficient data points for correlation analysis")

    # Pearson correlation
    r, p_value = stats.pearsonr(clean_df['or_index'], clean_df['mean_return'])

    # Effect size interpretation (Cohen's guidelines for correlation)
    if abs(r) < 0.1:
        effect_size = "negligible"
    elif abs(r) < 0.3:
        effect_size = "small"
    elif abs(r) < 0.5:
        effect_size = "medium"
    else:
        effect_size = "large"

    # Significance stars
    if p_value < 0.001:
        significance = "***"
    elif p_value < 0.01:
        significance = "**"
    elif p_value < 0.05:
        significance = "*"
    else:
        significance = "ns"

    return {
        'pearson_r': r,
        'p_value': p_value,
        'n_points': len(clean_df),
        'effect_size': effect_size,
        'significance': significance
    }


def create_correlation_scatter_plot(df: pd.DataFrame, stats_dict: Dict, output_path: Path):
    """
    Create publication-quality scatter plot with regression line.

    Args:
        df: DataFrame with correlation data
        stats_dict: Dictionary with correlation statistics
        output_path: Path to save figure
    """
    fig, ax = plt.subplots(figsize=(8, 6), dpi=600)

    # Remove NaN values
    clean_df = df.dropna(subset=['or_index', 'mean_return'])

    # Color by checkpoint
    checkpoint_colors = {
        0: '#1f77b4',  # blue (random)
        5000: '#ff7f0e',  # orange (5K)
        50000: '#2ca02c',  # green (50K)
        200000: '#d62728'  # red (200K)
    }

    # Scatter plot with checkpoint colors
    for checkpoint, color in checkpoint_colors.items():
        mask = clean_df['checkpoint'] == checkpoint
        ax.scatter(
            clean_df[mask]['or_index'],
            clean_df[mask]['mean_return'],
            c=color,
            s=100,
            alpha=0.7,
            edgecolors='black',
            linewidth=0.5,
            label=f"{checkpoint // 1000}K episodes" if checkpoint > 0 else "Random"
        )

    # Regression line
    x = clean_df['or_index'].values
    y = clean_df['mean_return'].values
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    x_line = np.linspace(x.min(), x.max(), 100)
    ax.plot(x_line, p(x_line), 'k--', alpha=0.8, linewidth=2, label='Linear fit')

    # Labels and formatting
    ax.set_xlabel('O/R Index (Observation-Response Coupling)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Mean Episode Return (Proxy: -Episode Length)', fontsize=14, fontweight='bold')

    # Correlation statistics in title
    r = stats_dict['pearson_r']
    p = stats_dict['p_value']
    sig = stats_dict['significance']
    ax.set_title(
        f"O/R Index vs Performance in Overcooked-AI\n"
        f"r = {r:.3f}{sig}, p = {p:.4f}, n = {stats_dict['n_points']}",
        fontsize=14,
        fontweight='bold',
        pad=20
    )

    # Legend
    ax.legend(loc='best', frameon=True, fancybox=True, shadow=True, fontsize=11)

    # Grid
    ax.grid(True, alpha=0.3, linestyle='--')

    # Tight layout
    plt.tight_layout()

    # Save
    plt.savefig(output_path, dpi=600, bbox_inches='tight')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight')
    print(f"✓ Saved correlation scatter plot: {output_path}")
    print(f"✓ Saved vector version: {output_path.with_suffix('.pdf')}")


def main():
    """Main correlation analysis pipeline."""
    print("="*80)
    print("O/R Index vs Performance Correlation Analysis")
    print("="*80)

    # Paths
    base_dir = Path(__file__).parent
    or_index_csv = base_dir / "outputs" / "full_abc_or_index_results.csv"
    traj_dir = base_dir / "trajectories" / "full_abc"
    output_dir = base_dir / "outputs"

    # Load O/R Index data
    print("\n[1/5] Loading O/R Index data...")
    df = load_or_index_data(or_index_csv)
    print(f"  ✓ Loaded {len(df)} policy evaluations")

    # Match trajectory files and extract performance
    print("\n[2/5] Extracting episode returns from trajectory files...")
    df = match_trajectory_files(df, traj_dir)
    print(f"  ✓ Extracted returns for {df['mean_return'].notna().sum()}/{len(df)} policies")

    # Compute correlation
    print("\n[3/5] Computing Pearson correlation...")
    corr_stats = compute_correlation(df)
    print(f"  ✓ Pearson r = {corr_stats['pearson_r']:.3f}")
    print(f"  ✓ p-value = {corr_stats['p_value']:.4f} ({corr_stats['significance']})")
    print(f"  ✓ Effect size: {corr_stats['effect_size']}")
    print(f"  ✓ Sample size: n = {corr_stats['n_points']}")

    # Create scatter plot
    print("\n[4/5] Creating publication-quality scatter plot...")
    scatter_path = output_dir / "or_index_performance_correlation.png"
    create_correlation_scatter_plot(df, corr_stats, scatter_path)

    # Save correlation data
    print("\n[5/5] Saving correlation data...")

    # Save merged DataFrame
    merged_csv = output_dir / "or_index_with_performance.csv"
    df.to_csv(merged_csv, index=False)
    print(f"  ✓ Saved merged data: {merged_csv}")

    # Save correlation statistics
    corr_json = output_dir / "correlation_statistics.json"
    with open(corr_json, 'w') as f:
        json.dump(corr_stats, f, indent=2)
    print(f"  ✓ Saved correlation stats: {corr_json}")

    # Summary
    print("\n" + "="*80)
    print("CORRELATION ANALYSIS COMPLETE")
    print("="*80)
    print(f"\n📊 Key Finding:")
    print(f"   Pearson r = {corr_stats['pearson_r']:.3f}{corr_stats['significance']}")
    print(f"   p-value = {corr_stats['p_value']:.4f}")
    print(f"   Effect size: {corr_stats['effect_size']}")

    if corr_stats['p_value'] < 0.05:
        direction = "negative" if corr_stats['pearson_r'] < 0 else "positive"
        print(f"\n   ✓ Statistically significant {direction} correlation detected!")
    else:
        print(f"\n   ⚠ Correlation not statistically significant (p >= 0.05)")

    print(f"\n📁 Output Files:")
    print(f"   - {scatter_path}")
    print(f"   - {scatter_path.with_suffix('.pdf')}")
    print(f"   - {merged_csv}")
    print(f"   - {corr_json}")
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
