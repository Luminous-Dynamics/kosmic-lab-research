#!/usr/bin/env python3
"""
Generate Supplementary Figures for Paper 6

Create publication-quality visualizations of supplementary findings.

Run with:
    nix-shell -p python3 python3Packages.numpy python3Packages.scipy python3Packages.matplotlib --run "python3 -u generate_supplementary_figures.py"
"""

import numpy as np
import matplotlib.pyplot as plt

# Set publication style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['figure.figsize'] = (10, 6)


def figure_s1_algorithm_comparison():
    """Bar chart comparing algorithms."""
    algorithms = ['REINFORCE', 'A2C', 'PPO']
    correlations = [0.71, 0.88, 0.34]
    colors = ['#3498db', '#2ecc71', '#e74c3c']

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(algorithms, correlations, color=colors, edgecolor='black', linewidth=1.5)

    # Add significance
    ax.text(0, 0.74, '***', ha='center', fontsize=14, fontweight='bold')
    ax.text(1, 0.91, '***', ha='center', fontsize=14, fontweight='bold')
    ax.text(2, 0.37, 'ns', ha='center', fontsize=10, style='italic')

    ax.set_ylabel('Correlation with Performance (r)')
    ax.set_title('Figure S1: O/R Index Generalizes Across Algorithms')
    ax.set_ylim(0, 1.05)

    # Add baseline reference
    ax.axhline(y=0.70, color='gray', linestyle='--', linewidth=1)
    ax.text(2.5, 0.72, 'Baseline r=0.70', fontsize=10, style='italic')

    plt.tight_layout()
    plt.savefig('figure_s1_algorithms.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved: figure_s1_algorithms.png")


def figure_s2_temporal_dynamics():
    """Line plot showing O/R Index evolution during training."""
    episodes = [0, 5, 10, 20, 30, 40, 49]
    kindex = [-0.41, -1.05, -1.07, -1.07, -1.07, -1.07, -1.07]
    correlation = [0.59, 0.89, 0.73, 0.75, 0.73, 0.73, 0.69]

    fig, ax1 = plt.subplots(figsize=(10, 5))

    # O/R Index evolution
    color1 = '#3498db'
    ax1.set_xlabel('Training Episode')
    ax1.set_ylabel('Mean O/R Index', color=color1)
    line1 = ax1.plot(episodes, kindex, 'o-', color=color1, linewidth=2, markersize=8, label='O/R Index')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_ylim(-1.2, 0)

    # Correlation with performance
    ax2 = ax1.twinx()
    color2 = '#e74c3c'
    ax2.set_ylabel('Correlation with Performance (r)', color=color2)
    line2 = ax2.plot(episodes, correlation, 's--', color=color2, linewidth=2, markersize=8, label='r with perf')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(0, 1.0)

    # Legend
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='center right')

    ax1.set_title('Figure S2: O/R Index Evolution During Training')

    plt.tight_layout()
    plt.savefig('figure_s2_temporal.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved: figure_s2_temporal.png")


def figure_s3_ablations():
    """Grouped bar chart for ablation studies."""
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))

    # History window
    ax = axes[0]
    windows = ['25', '50', '100']
    r_vals = [0.71, 0.71, 0.69]
    bars = ax.bar(windows, r_vals, color='#9b59b6', edgecolor='black')
    ax.set_ylabel('Correlation (r)')
    ax.set_xlabel('History Window')
    ax.set_title('History Window')
    ax.set_ylim(0.6, 0.8)
    for i in range(3):
        ax.text(i, r_vals[i] + 0.01, '***', ha='center', fontsize=10)

    # Message dimension
    ax = axes[1]
    dims = ['3', '5', '10']
    r_vals = [0.75, 0.71, 0.73]
    bars = ax.bar(dims, r_vals, color='#f39c12', edgecolor='black')
    ax.set_xlabel('Message Dimension')
    ax.set_title('Message Dimension')
    ax.set_ylim(0.6, 0.8)
    for i in range(3):
        ax.text(i, r_vals[i] + 0.01, '***', ha='center', fontsize=10)

    # Observation noise
    ax = axes[2]
    noise = ['0.05', '0.1', '0.3', '0.5']
    r_vals = [0.70, 0.71, 0.80, 0.84]
    bars = ax.bar(noise, r_vals, color='#1abc9c', edgecolor='black')
    ax.set_xlabel('Observation Noise')
    ax.set_title('Observation Noise')
    ax.set_ylim(0.6, 0.9)
    for i in range(4):
        ax.text(i, r_vals[i] + 0.01, '***', ha='center', fontsize=10)

    fig.suptitle('Figure S3: O/R Index Robust to Hyperparameters', fontsize=16, y=1.02)

    plt.tight_layout()
    plt.savefig('figure_s3_ablations.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved: figure_s3_ablations.png")


def figure_s4_power_analysis():
    """Power analysis visualization."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Power by sample size
    ax = axes[0]
    n_vals = [10, 20, 30, 50, 100]
    power = [68.3, 95.4, 99.2, 100, 100]

    ax.bar(range(len(n_vals)), power, color='#3498db', edgecolor='black')
    ax.set_xticks(range(len(n_vals)))
    ax.set_xticklabels(n_vals)
    ax.set_xlabel('Sample Size (n)')
    ax.set_ylabel('Statistical Power (%)')
    ax.set_title('Power by Sample Size (r = 0.70)')
    ax.axhline(y=80, color='red', linestyle='--', linewidth=2, label='80% threshold')
    ax.legend()
    ax.set_ylim(0, 110)

    # Highlight our n=30
    ax.bar(2, 99.2, color='#2ecc71', edgecolor='black', linewidth=2)
    ax.text(2, 102, 'Our study', ha='center', fontsize=10, fontweight='bold')

    # Required n by effect size
    ax = axes[1]
    effects = [0.30, 0.50, 0.70, 0.80, 0.90]
    required_n = [85, 30, 14, 10, 7]

    ax.bar(range(len(effects)), required_n, color='#e74c3c', edgecolor='black')
    ax.set_xticks(range(len(effects)))
    ax.set_xticklabels(effects)
    ax.set_xlabel('Effect Size (r)')
    ax.set_ylabel('Required n for 80% Power')
    ax.set_title('Sample Size Requirements')

    # Highlight our effect
    ax.bar(2, 14, color='#2ecc71', edgecolor='black', linewidth=2)
    ax.text(2, 17, 'Our effect', ha='center', fontsize=10, fontweight='bold')

    fig.suptitle('Figure S4: Statistical Power Analysis', fontsize=16, y=1.02)

    plt.tight_layout()
    plt.savefig('figure_s4_power.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved: figure_s4_power.png")


def figure_s5_summary():
    """Summary figure showing all key results."""
    fig = plt.figure(figsize=(14, 8))

    # Create grid
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)

    # 1. Main effect
    ax1 = fig.add_subplot(gs[0, 0])
    metrics = ['O/R Index', 'Diversity', 'Entropy']
    r_vals = [0.69, 0.17, 0.0]
    colors = ['#2ecc71', '#95a5a6', '#bdc3c7']
    ax1.bar(metrics, r_vals, color=colors, edgecolor='black')
    ax1.set_title('A. Metric Comparison')
    ax1.set_ylabel('r')
    ax1.set_ylim(0, 0.8)

    # 2. Generalization
    ax2 = fig.add_subplot(gs[0, 1])
    conditions = ['Base', 'Small', 'Large', 'High-D', 'Sparse']
    r_vals = [0.78, 0.91, 0.69, 0.82, -0.96]
    colors = ['#3498db', '#3498db', '#3498db', '#3498db', '#e74c3c']
    ax2.bar(conditions, r_vals, color=colors, edgecolor='black')
    ax2.axhline(y=0, color='black', linewidth=0.5)
    ax2.set_title('B. Generalization')
    ax2.set_ylabel('r')
    ax2.set_ylim(-1.1, 1.0)

    # 3. Causal
    ax3 = fig.add_subplot(gs[0, 2])
    lambdas = [0.0, 0.1, 0.2, 0.5]
    perf = [-1620, -1594, -1508, -1691]
    ax3.plot(lambdas, perf, 'o-', color='#2ecc71', linewidth=2, markersize=8)
    ax3.plot(0.2, -1508, 'o', color='#e74c3c', markersize=12)
    ax3.set_title('C. Causal Evidence')
    ax3.set_xlabel('λ')
    ax3.set_ylabel('Performance')

    # 4. Robustness
    ax4 = fig.add_subplot(gs[1, 0])
    conditions = ['Base', 'Noise', 'Dropout', 'Both']
    r_vals = [0.94, 0.94, 0.95, 0.93]
    ax4.bar(conditions, r_vals, color='#9b59b6', edgecolor='black')
    ax4.set_title('D. Robustness')
    ax4.set_ylabel('r')
    ax4.set_ylim(0.8, 1.0)

    # 5. Zero-shot
    ax5 = fig.add_subplot(gs[1, 1])
    settings = ['Joint', 'Zero-shot']
    r_vals = [0.70, -0.50]
    colors = ['#2ecc71', '#e74c3c']
    ax5.bar(settings, r_vals, color=colors, edgecolor='black')
    ax5.axhline(y=0, color='black', linewidth=0.5)
    ax5.set_title('E. Zero-Shot')
    ax5.set_ylabel('r')
    ax5.set_ylim(-0.7, 0.9)

    # 6. Algorithms
    ax6 = fig.add_subplot(gs[1, 2])
    algos = ['REINFORCE', 'A2C', 'PPO']
    r_vals = [0.71, 0.88, 0.34]
    colors = ['#3498db', '#2ecc71', '#e74c3c']
    ax6.bar(algos, r_vals, color=colors, edgecolor='black')
    ax6.set_title('F. Algorithms')
    ax6.set_ylabel('r')
    ax6.set_ylim(0, 1.0)

    fig.suptitle('Figure S5: Summary of O/R Index Findings', fontsize=18, y=1.02)

    plt.tight_layout()
    plt.savefig('figure_s5_summary.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved: figure_s5_summary.png")


def main():
    print("\n" + "=" * 70)
    print("GENERATING SUPPLEMENTARY FIGURES")
    print("=" * 70 + "\n")

    print("Creating figures...")

    figure_s1_algorithm_comparison()
    figure_s2_temporal_dynamics()
    figure_s3_ablations()
    figure_s4_power_analysis()
    figure_s5_summary()

    print("\n" + "=" * 70)
    print("COMPLETE - 5 supplementary figures generated")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
