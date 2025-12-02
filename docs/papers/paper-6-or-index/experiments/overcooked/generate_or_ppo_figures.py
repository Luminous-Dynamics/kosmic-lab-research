#!/usr/bin/env python3
"""
Generate publication-quality figures for OR-PPO results.

Creates two figures:
1. Learning curves: Reward and O/R Index evolution
2. Hyperparameter adaptation: Clip range and learning rate trajectories
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.ndimage import uniform_filter1d

# Set publication style
plt.rcParams.update({
    'font.size': 10,
    'font.family': 'serif',
    'font.serif': ['Times New Roman'],
    'text.usetex': False,  # Set to True if LaTeX is available
    'figure.figsize': (7, 3),
    'axes.labelsize': 10,
    'axes.titlesize': 10,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'lines.linewidth': 1.5,
})

def smooth_curve(data, window=50):
    """Apply moving average smoothing."""
    return uniform_filter1d(data, size=window, mode='nearest')

def load_metrics(base_path, algorithm, seed):
    """Load metrics for a specific algorithm and seed."""
    path = base_path / f"seed_{seed}" / algorithm / f"{algorithm}_metrics.json"
    with open(path) as f:
        return json.load(f)

def compute_statistics(data_list):
    """Compute mean and std across seeds."""
    data_array = np.array(data_list)
    return data_array.mean(axis=0), data_array.std(axis=0)

def main():
    # Paths
    base_path = Path("models/overcooked/or_ppo_comparison")
    figures_dir = Path("figures")
    figures_dir.mkdir(exist_ok=True)

    # Load all data
    print("Loading training metrics...")
    ppo_data = {
        'rewards': [],
        'or_indices': []
    }
    or_ppo_data = {
        'rewards': [],
        'or_indices': [],
        'clip': [],
        'lr': []
    }

    for seed in range(3):
        # PPO
        ppo_metrics = load_metrics(base_path, 'ppo', seed)
        ppo_data['rewards'].append(ppo_metrics['episode_rewards'])
        ppo_data['or_indices'].append(ppo_metrics['or_indices'])

        # OR-PPO
        or_ppo_metrics = load_metrics(base_path, 'or_ppo', seed)
        or_ppo_data['rewards'].append(or_ppo_metrics['episode_rewards'])
        or_ppo_data['or_indices'].append(or_ppo_metrics['or_indices'])
        or_ppo_data['clip'].append(or_ppo_metrics['clip_history'])
        or_ppo_data['lr'].append(or_ppo_metrics['lr_history'])

    print(f"Loaded {len(ppo_data['rewards'])} PPO seeds")
    print(f"Loaded {len(or_ppo_data['rewards'])} OR-PPO seeds")

    # Compute statistics
    print("\nComputing statistics across seeds...")
    ppo_reward_mean, ppo_reward_std = compute_statistics(ppo_data['rewards'])
    ppo_or_mean, ppo_or_std = compute_statistics(ppo_data['or_indices'])

    or_ppo_reward_mean, or_ppo_reward_std = compute_statistics(or_ppo_data['rewards'])
    or_ppo_or_mean, or_ppo_or_std = compute_statistics(or_ppo_data['or_indices'])

    or_ppo_clip_mean, or_ppo_clip_std = compute_statistics(or_ppo_data['clip'])
    or_ppo_lr_mean, or_ppo_lr_std = compute_statistics(or_ppo_data['lr'])

    episodes = np.arange(len(ppo_reward_mean))

    # Apply smoothing for better visualization
    smooth_window = 50
    print(f"Applying smoothing (window={smooth_window})...")

    ppo_reward_smooth = smooth_curve(ppo_reward_mean, smooth_window)
    or_ppo_reward_smooth = smooth_curve(or_ppo_reward_mean, smooth_window)
    ppo_or_smooth = smooth_curve(ppo_or_mean, smooth_window)
    or_ppo_or_smooth = smooth_curve(or_ppo_or_mean, smooth_window)

    # ========================================================================
    # Figure 1: Learning Curves (Reward + O/R Index)
    # ========================================================================
    print("\nGenerating Figure 1: Learning curves...")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 2.8))

    # Left panel: Reward curves
    ax1.plot(episodes, ppo_reward_smooth, color='#1f77b4', label='PPO', linewidth=1.5)
    ax1.fill_between(episodes,
                     ppo_reward_mean - ppo_reward_std,
                     ppo_reward_mean + ppo_reward_std,
                     color='#1f77b4', alpha=0.2)

    ax1.plot(episodes, or_ppo_reward_smooth, color='#d62728', label='OR-PPO', linewidth=1.5)
    ax1.fill_between(episodes,
                     or_ppo_reward_mean - or_ppo_reward_std,
                     or_ppo_reward_mean + or_ppo_reward_std,
                     color='#d62728', alpha=0.2)

    ax1.set_xlabel('Episode')
    ax1.set_ylabel('Total Reward')
    ax1.set_title('Reward Learning Curves')
    ax1.legend(loc='lower right', framealpha=0.9)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_ylim([0, 5])

    # Right panel: O/R Index evolution
    ax2.plot(episodes, ppo_or_smooth, color='#1f77b4', label='PPO', linewidth=1.5)
    ax2.fill_between(episodes,
                     ppo_or_mean - ppo_or_std,
                     ppo_or_mean + ppo_or_std,
                     color='#1f77b4', alpha=0.2)

    ax2.plot(episodes, or_ppo_or_smooth, color='#d62728', label='OR-PPO', linewidth=1.5)
    ax2.fill_between(episodes,
                     or_ppo_or_mean - or_ppo_or_std,
                     or_ppo_or_mean + or_ppo_or_std,
                     color='#d62728', alpha=0.2)

    ax2.set_xlabel('Episode')
    ax2.set_ylabel('O/R Index')
    ax2.set_title('O/R Index Evolution')
    ax2.legend(loc='lower right', framealpha=0.9)
    ax2.grid(True, alpha=0.3, linestyle='--')

    # Add horizontal line at 0 for reference
    ax2.axhline(y=0, color='black', linestyle=':', linewidth=0.8, alpha=0.5)

    plt.tight_layout()

    # Save
    output_path = figures_dir / "or_ppo_comparison.pdf"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")

    # Also save as PNG for preview
    output_path_png = figures_dir / "or_ppo_comparison.png"
    plt.savefig(output_path_png, dpi=150, bbox_inches='tight')
    print(f"✓ Saved: {output_path_png}")

    plt.close()

    # ========================================================================
    # Figure 2: Hyperparameter Adaptation
    # ========================================================================
    print("\nGenerating Figure 2: Hyperparameter adaptation...")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 2.8))

    # Hyperparameters are logged every K episodes, not every episode
    # Create correct episode indices for hyperparameter history
    hyperparam_episodes = np.arange(0, len(or_ppo_clip_mean) * 10, 10)  # Updated every 10 episodes

    # Smooth hyperparameter trajectories
    clip_smooth = smooth_curve(or_ppo_clip_mean, max(1, smooth_window // 10))
    lr_smooth = smooth_curve(or_ppo_lr_mean, max(1, smooth_window // 10))

    # Left panel: Clip range
    ax1.plot(hyperparam_episodes, clip_smooth, color='#2ca02c', linewidth=1.5)
    ax1.fill_between(hyperparam_episodes,
                     or_ppo_clip_mean - or_ppo_clip_std,
                     or_ppo_clip_mean + or_ppo_clip_std,
                     color='#2ca02c', alpha=0.2)

    # Base value line
    ax1.axhline(y=0.2, color='black', linestyle='--', linewidth=1.0,
                label=r'Base: $\epsilon_0 = 0.2$', alpha=0.7)

    ax1.set_xlabel('Episode')
    ax1.set_ylabel('Clip Range ($\\epsilon_t$)')
    ax1.set_title('Adaptive Clip Range')
    ax1.legend(loc='best', framealpha=0.9)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_ylim([0.15, 0.25])

    # Right panel: Learning rate
    ax2.plot(hyperparam_episodes, lr_smooth * 1e4, color='#ff7f0e', linewidth=1.5)  # Scale for readability
    ax2.fill_between(hyperparam_episodes,
                     (or_ppo_lr_mean - or_ppo_lr_std) * 1e4,
                     (or_ppo_lr_mean + or_ppo_lr_std) * 1e4,
                     color='#ff7f0e', alpha=0.2)

    # Base value line
    ax2.axhline(y=3.0, color='black', linestyle='--', linewidth=1.0,
                label=r'Base: $\alpha_0 = 3 \times 10^{-4}$', alpha=0.7)

    ax2.set_xlabel('Episode')
    ax2.set_ylabel('Learning Rate ($\\alpha_t \\times 10^{4}$)')
    ax2.set_title('Adaptive Learning Rate')
    ax2.legend(loc='best', framealpha=0.9)
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.set_ylim([2.5, 3.5])

    plt.tight_layout()

    # Save
    output_path = figures_dir / "or_ppo_hyperparameters.pdf"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")

    # Also save as PNG for preview
    output_path_png = figures_dir / "or_ppo_hyperparameters.png"
    plt.savefig(output_path_png, dpi=150, bbox_inches='tight')
    print(f"✓ Saved: {output_path_png}")

    plt.close()

    # ========================================================================
    # Summary Statistics
    # ========================================================================
    print("\n" + "="*70)
    print("SUMMARY STATISTICS")
    print("="*70)

    print(f"\nFinal Rewards (last 100 episodes average):")
    print(f"  PPO:     {ppo_reward_mean[-100:].mean():.4f} ± {ppo_reward_std[-100:].mean():.4f}")
    print(f"  OR-PPO:  {or_ppo_reward_mean[-100:].mean():.4f} ± {or_ppo_reward_std[-100:].mean():.4f}")

    print(f"\nFinal O/R Index (last 100 episodes average):")
    print(f"  PPO:     {ppo_or_mean[-100:].mean():.6f} ± {ppo_or_std[-100:].mean():.6f}")
    print(f"  OR-PPO:  {or_ppo_or_mean[-100:].mean():.6f} ± {or_ppo_or_std[-100:].mean():.6f}")

    print(f"\nFinal Hyperparameters (last 100 episodes average):")
    print(f"  Clip range: {or_ppo_clip_mean[-100:].mean():.4f} ± {or_ppo_clip_std[-100:].mean():.4f}")
    print(f"  Learn rate: {or_ppo_lr_mean[-100:].mean():.6f} ± {or_ppo_lr_std[-100:].mean():.6f}")

    print("\n" + "="*70)
    print("✓ Figure generation complete!")
    print("="*70)

if __name__ == "__main__":
    main()
