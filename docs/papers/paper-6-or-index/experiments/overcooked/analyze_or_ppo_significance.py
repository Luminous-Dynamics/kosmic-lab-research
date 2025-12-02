#!/usr/bin/env python3
"""
Statistical Analysis for OR-PPO Results

Generates:
1. Statistical significance tests (t-tests, Mann-Whitney U)
2. Effect size calculations (Cohen's d)
3. Correlation analysis (O/R Index vs. performance)
4. Supplementary figures for deeper insights
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
from scipy.ndimage import uniform_filter1d

# Publication style
plt.rcParams.update({
    'font.size': 10,
    'font.family': 'serif',
    'figure.figsize': (7, 5),
    'axes.labelsize': 10,
    'axes.titlesize': 10,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'lines.linewidth': 1.5,
})

def load_metrics(base_path, algorithm, seed):
    """Load metrics for a specific algorithm and seed."""
    path = base_path / f"seed_{seed}" / algorithm / f"{algorithm}_metrics.json"
    with open(path) as f:
        return json.load(f)

def cohens_d(group1, group2):
    """Calculate Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    return (np.mean(group1) - np.mean(group2)) / pooled_std

def main():
    base_path = Path("models/overcooked/or_ppo_comparison")

    print("="*70)
    print("OR-PPO STATISTICAL ANALYSIS")
    print("="*70)

    # Load all data
    print("\nLoading data...")
    ppo_final_or = []
    or_ppo_final_or = []
    ppo_final_reward = []
    or_ppo_final_reward = []

    ppo_or_trajectories = []
    or_ppo_or_trajectories = []

    for seed in range(3):
        # PPO
        ppo_metrics = load_metrics(base_path, 'ppo', seed)
        # Use average of last 100 episodes (more stable than single final value)
        ppo_final_or.append(np.mean(ppo_metrics['or_indices'][-100:]))
        ppo_final_reward.append(np.mean(ppo_metrics['episode_rewards'][-100:]))
        ppo_or_trajectories.append(np.array(ppo_metrics['or_indices']))

        # OR-PPO
        or_ppo_metrics = load_metrics(base_path, 'or_ppo', seed)
        or_ppo_final_or.append(np.mean(or_ppo_metrics['or_indices'][-100:]))
        or_ppo_final_reward.append(np.mean(or_ppo_metrics['episode_rewards'][-100:]))
        or_ppo_or_trajectories.append(np.array(or_ppo_metrics['or_indices']))

    print(f"✓ Loaded 3 seeds for PPO and OR-PPO")

    # ========================================================================
    # 1. Statistical Significance Tests
    # ========================================================================
    print("\n" + "="*70)
    print("1. STATISTICAL SIGNIFICANCE TESTS")
    print("="*70)

    # T-test for O/R Index
    t_stat, p_value = stats.ttest_ind(or_ppo_final_or, ppo_final_or)
    print(f"\nO/R Index Comparison:")
    print(f"  PPO:     {np.mean(ppo_final_or):.6f} ± {np.std(ppo_final_or, ddof=1):.6f}")
    print(f"  OR-PPO:  {np.mean(or_ppo_final_or):.6f} ± {np.std(or_ppo_final_or, ddof=1):.6f}")
    print(f"  t-statistic: {t_stat:.4f}")
    print(f"  p-value: {p_value:.4f}")

    if p_value < 0.05:
        print(f"  ✓ SIGNIFICANT at α=0.05 (p={p_value:.4f})")
    else:
        print(f"  ✗ NOT significant at α=0.05 (p={p_value:.4f})")

    # Mann-Whitney U test (non-parametric alternative)
    u_stat, p_value_mw = stats.mannwhitneyu(or_ppo_final_or, ppo_final_or, alternative='greater')
    print(f"\n  Mann-Whitney U test (non-parametric):")
    print(f"  U-statistic: {u_stat:.4f}")
    print(f"  p-value: {p_value_mw:.4f}")

    # ========================================================================
    # 2. Effect Size Analysis
    # ========================================================================
    print("\n" + "="*70)
    print("2. EFFECT SIZE ANALYSIS")
    print("="*70)

    d = cohens_d(or_ppo_final_or, ppo_final_or)
    print(f"\nCohen's d: {d:.4f}")

    # Interpret effect size
    if abs(d) < 0.2:
        interpretation = "negligible"
    elif abs(d) < 0.5:
        interpretation = "small"
    elif abs(d) < 0.8:
        interpretation = "medium"
    else:
        interpretation = "large"

    print(f"Interpretation: {interpretation} effect size")

    # Percentage improvement
    ppo_mean = np.mean(ppo_final_or)
    or_ppo_mean = np.mean(or_ppo_final_or)
    improvement = ((or_ppo_mean - ppo_mean) / abs(ppo_mean)) * 100
    print(f"Percentage improvement: {improvement:.2f}%")

    # ========================================================================
    # 3. Variance Analysis
    # ========================================================================
    print("\n" + "="*70)
    print("3. VARIANCE ANALYSIS")
    print("="*70)

    ppo_var = np.var(ppo_final_or, ddof=1)
    or_ppo_var = np.var(or_ppo_final_or, ddof=1)

    print(f"\nO/R Index Variance:")
    print(f"  PPO:     {ppo_var:.8f}")
    print(f"  OR-PPO:  {or_ppo_var:.8f}")
    print(f"  Reduction: {((ppo_var - or_ppo_var) / ppo_var) * 100:.2f}%")

    # F-test for variance equality
    f_stat = ppo_var / or_ppo_var if ppo_var > or_ppo_var else or_ppo_var / ppo_var
    df1, df2 = (2, 2)  # degrees of freedom
    p_value_f = 1 - stats.f.cdf(f_stat, df1, df2)
    print(f"\n  F-test for variance equality:")
    print(f"  F-statistic: {f_stat:.4f}")
    print(f"  p-value: {p_value_f:.4f}")

    # ========================================================================
    # 4. Convergence Analysis
    # ========================================================================
    print("\n" + "="*70)
    print("4. CONVERGENCE ANALYSIS")
    print("="*70)

    # Analyze convergence speed (episodes to reach 90% of final value)
    def episodes_to_convergence(trajectory, threshold=0.9):
        """Calculate episodes to reach threshold of final value."""
        trajectory = np.array(trajectory)  # Ensure numpy array
        final_val = np.mean(trajectory[-100:])  # Average of last 100 episodes
        target = threshold * abs(final_val)

        # Find first episode where we're within threshold
        for i, val in enumerate(trajectory):
            if abs(val) >= abs(target):
                return i
        return len(trajectory)

    ppo_conv = [episodes_to_convergence(traj) for traj in ppo_or_trajectories]
    or_ppo_conv = [episodes_to_convergence(traj) for traj in or_ppo_or_trajectories]

    print(f"\nEpisodes to convergence (90% of final O/R Index):")
    print(f"  PPO:     {np.mean(ppo_conv):.0f} ± {np.std(ppo_conv, ddof=1):.0f}")
    print(f"  OR-PPO:  {np.mean(or_ppo_conv):.0f} ± {np.std(or_ppo_conv, ddof=1):.0f}")
    print(f"  Speedup: {(np.mean(ppo_conv) / np.mean(or_ppo_conv)):.2f}x")

    # ========================================================================
    # 5. Generate Supplementary Figures
    # ========================================================================
    print("\n" + "="*70)
    print("5. GENERATING SUPPLEMENTARY FIGURES")
    print("="*70)

    figures_dir = Path("figures/supplementary")
    figures_dir.mkdir(exist_ok=True, parents=True)

    # Figure S1: Distribution comparison
    print("\nGenerating Figure S1: Distribution comparison...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 3))

    # Left: Box plots
    data_to_plot = [ppo_final_or, or_ppo_final_or]
    bp = ax1.boxplot(data_to_plot, labels=['PPO', 'OR-PPO'], patch_artist=True)
    bp['boxes'][0].set_facecolor('#1f77b4')
    bp['boxes'][1].set_facecolor('#d62728')
    ax1.set_ylabel('Final O/R Index')
    ax1.set_title('Distribution Comparison')
    ax1.grid(True, alpha=0.3, linestyle='--', axis='y')

    # Right: Scatter plot with individual seeds
    x_ppo = np.random.normal(1, 0.04, len(ppo_final_or))
    x_or_ppo = np.random.normal(2, 0.04, len(or_ppo_final_or))

    ax2.scatter(x_ppo, ppo_final_or, s=100, c='#1f77b4', alpha=0.6,
                edgecolors='black', linewidths=1.5, label='PPO')
    ax2.scatter(x_or_ppo, or_ppo_final_or, s=100, c='#d62728', alpha=0.6,
                edgecolors='black', linewidths=1.5, label='OR-PPO')

    # Add means
    ax2.hlines(np.mean(ppo_final_or), 0.7, 1.3, colors='#1f77b4',
               linestyles='--', linewidth=2, label='PPO mean')
    ax2.hlines(np.mean(or_ppo_final_or), 1.7, 2.3, colors='#d62728',
               linestyles='--', linewidth=2, label='OR-PPO mean')

    ax2.set_xlim(0.5, 2.5)
    ax2.set_xticks([1, 2])
    ax2.set_xticklabels(['PPO', 'OR-PPO'])
    ax2.set_ylabel('Final O/R Index')
    ax2.set_title('Individual Seeds')
    ax2.grid(True, alpha=0.3, linestyle='--', axis='y')

    plt.tight_layout()
    plt.savefig(figures_dir / "or_ppo_distribution.pdf", dpi=300, bbox_inches='tight')
    plt.savefig(figures_dir / "or_ppo_distribution.png", dpi=150, bbox_inches='tight')
    print(f"  ✓ Saved: {figures_dir / 'or_ppo_distribution.pdf'}")
    plt.close()

    # Figure S2: Convergence comparison
    print("\nGenerating Figure S2: Convergence analysis...")
    fig, ax = plt.subplots(figsize=(7, 4))

    episodes = np.arange(2000)

    # Plot all seeds with different transparencies
    for i, traj in enumerate(ppo_or_trajectories):
        ax.plot(episodes, traj, color='#1f77b4', alpha=0.3, linewidth=1)

    for i, traj in enumerate(or_ppo_or_trajectories):
        ax.plot(episodes, traj, color='#d62728', alpha=0.3, linewidth=1)

    # Plot means
    ppo_mean_traj = np.mean(ppo_or_trajectories, axis=0)
    or_ppo_mean_traj = np.mean(or_ppo_or_trajectories, axis=0)

    # Smooth for visibility
    window = 50
    ppo_smooth = uniform_filter1d(ppo_mean_traj, size=window, mode='nearest')
    or_ppo_smooth = uniform_filter1d(or_ppo_mean_traj, size=window, mode='nearest')

    ax.plot(episodes, ppo_smooth, color='#1f77b4', linewidth=2.5, label='PPO (mean)')
    ax.plot(episodes, or_ppo_smooth, color='#d62728', linewidth=2.5, label='OR-PPO (mean)')

    # Add convergence markers
    for conv_ep in ppo_conv:
        ax.axvline(conv_ep, color='#1f77b4', linestyle=':', alpha=0.5, linewidth=1)
    for conv_ep in or_ppo_conv:
        ax.axvline(conv_ep, color='#d62728', linestyle=':', alpha=0.5, linewidth=1)

    ax.set_xlabel('Episode')
    ax.set_ylabel('O/R Index')
    ax.set_title('Convergence Comparison (all seeds)')
    ax.legend(loc='lower right', framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.axhline(y=0, color='black', linestyle=':', linewidth=0.8, alpha=0.5)

    plt.tight_layout()
    plt.savefig(figures_dir / "or_ppo_convergence.pdf", dpi=300, bbox_inches='tight')
    plt.savefig(figures_dir / "or_ppo_convergence.png", dpi=150, bbox_inches='tight')
    print(f"  ✓ Saved: {figures_dir / 'or_ppo_convergence.pdf'}")
    plt.close()

    # ========================================================================
    # 6. Summary Report
    # ========================================================================
    print("\n" + "="*70)
    print("SUMMARY REPORT")
    print("="*70)

    report = f"""
OR-PPO Statistical Analysis Summary
====================================

Sample Size: 3 seeds per algorithm (6 total)

Primary Result:
  OR-PPO achieves {improvement:.2f}% higher O/R Index than PPO
  PPO:     {np.mean(ppo_final_or):.6f} ± {np.std(ppo_final_or, ddof=1):.6f}
  OR-PPO:  {np.mean(or_ppo_final_or):.6f} ± {np.std(or_ppo_final_or, ddof=1):.6f}

Statistical Significance:
  Independent t-test: t={t_stat:.4f}, p={p_value:.4f}
  Mann-Whitney U: U={u_stat:.4f}, p={p_value_mw:.4f}
  Result: {'SIGNIFICANT' if p_value < 0.05 else 'NOT SIGNIFICANT'} at α=0.05

Effect Size:
  Cohen's d: {d:.4f} ({interpretation} effect)

Variance Reduction:
  PPO variance:     {ppo_var:.8f}
  OR-PPO variance:  {or_ppo_var:.8f}
  Reduction: {((ppo_var - or_ppo_var) / ppo_var) * 100:.2f}%

Convergence Speed:
  PPO:     {np.mean(ppo_conv):.0f} ± {np.std(ppo_conv, ddof=1):.0f} episodes
  OR-PPO:  {np.mean(or_ppo_conv):.0f} ± {np.std(or_ppo_conv, ddof=1):.0f} episodes
  Speedup: {(np.mean(ppo_conv) / np.mean(or_ppo_conv)):.2f}x

Interpretation:
  OR-PPO demonstrates {'statistically significant' if p_value < 0.05 else 'measurable but not statistically significant'}
  improvement in policy organization (O/R Index) with {'substantial' if ((ppo_var - or_ppo_var) / ppo_var) * 100 > 10 else 'moderate'}
  variance reduction, suggesting more consistent learning across seeds.

  The {interpretation} effect size (Cohen's d={d:.4f}) indicates {'meaningful' if abs(d) >= 0.5 else 'modest'}
  practical significance beyond statistical testing.
"""

    print(report)

    # Save report
    with open(figures_dir / "statistical_analysis_report.txt", "w") as f:
        f.write(report)
    print(f"\n✓ Saved: {figures_dir / 'statistical_analysis_report.txt'}")

    print("\n" + "="*70)
    print("✓ Statistical analysis complete!")
    print("="*70)

if __name__ == "__main__":
    main()
