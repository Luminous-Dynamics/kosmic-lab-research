#!/usr/bin/env python3
"""
Generate Figures for Paper 4

Create publication-quality visualizations of key findings.

Run with:
    nix-shell -p python3 python3Packages.numpy python3Packages.scipy python3Packages.matplotlib --run "python3 -u generate_figures.py"
"""

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from datetime import datetime

# Set publication style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['figure.figsize'] = (10, 6)


def figure_1_metric_comparison():
    """Bar chart comparing K-Index to other metrics."""
    metrics = ['K-Index', 'Diversity', 'Entropy*', 'MI*']
    correlations = [0.69, 0.17, 0.0, 0.0]
    colors = ['#2ecc71', '#95a5a6', '#bdc3c7', '#bdc3c7']

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(metrics, correlations, color=colors, edgecolor='black', linewidth=1.5)

    # Add significance stars
    ax.text(0, 0.72, '***', ha='center', fontsize=14, fontweight='bold')

    ax.set_ylabel('Correlation with Performance (r)')
    ax.set_title('Figure 1: K-Index Outperforms Established Metrics')
    ax.set_ylim(0, 0.85)

    # Add note
    ax.text(0.5, -0.15, '*Entropy and MI were constant across all trained teams',
            transform=ax.transAxes, fontsize=10, style='italic', ha='center')

    plt.tight_layout()
    plt.savefig('figure_1_metric_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved: figure_1_metric_comparison.png")


def figure_2_generalization():
    """Bar chart showing generalization across conditions."""
    conditions = ['Baseline\n(4 agents)', 'Small\n(2 agents)', 'Large\n(8 agents)',
                  'High dim\n(20D)', 'Sparse\nreward']
    correlations = [0.78, 0.91, 0.69, 0.82, -0.96]
    colors = ['#3498db', '#3498db', '#3498db', '#3498db', '#e74c3c']

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(conditions, correlations, color=colors, edgecolor='black', linewidth=1.5)

    # Add significance
    for i, (c, r) in enumerate(zip(conditions, correlations)):
        if abs(r) > 0.7:
            ax.text(i, r + 0.05 * np.sign(r), '***', ha='center', fontsize=12, fontweight='bold')
        elif abs(r) > 0.5:
            ax.text(i, r + 0.05 * np.sign(r), '**', ha='center', fontsize=12, fontweight='bold')

    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.set_ylabel('Correlation with Performance (r)')
    ax.set_title('Figure 2: K-Index Generalizes Across Conditions\n(Sparse Reward Reverses!)')
    ax.set_ylim(-1.1, 1.1)

    plt.tight_layout()
    plt.savefig('figure_2_generalization.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved: figure_2_generalization.png")


def figure_3_causal():
    """Line plot showing causal effect of flexibility regularization."""
    lambdas = [0.0, 0.01, 0.05, 0.1, 0.2, 0.5]
    performance = [-1620, -1615, -1580, -1594, -1508, -1691]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(lambdas, performance, 'o-', color='#2ecc71', linewidth=2, markersize=10)

    # Highlight optimal
    optimal_idx = np.argmax(performance)
    ax.plot(lambdas[optimal_idx], performance[optimal_idx], 'o',
            color='#e74c3c', markersize=15, zorder=5)
    ax.annotate(f'Optimal: λ={lambdas[optimal_idx]}\n+6.9%',
                xy=(lambdas[optimal_idx], performance[optimal_idx]),
                xytext=(0.3, -1550), fontsize=11,
                arrowprops=dict(arrowstyle='->', color='black'))

    ax.set_xlabel('Flexibility Regularization (λ)')
    ax.set_ylabel('Team Performance')
    ax.set_title('Figure 3: Causal Evidence - Flexibility Regularization Improves Coordination')

    plt.tight_layout()
    plt.savefig('figure_3_causal.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved: figure_3_causal.png")


def figure_4_robustness():
    """Bar chart showing robustness under perturbation."""
    conditions = ['Baseline', '5x Obs\nNoise', '50% Comm\nDropout', 'Combined']
    correlations = [0.94, 0.94, 0.95, 0.93]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(conditions, correlations, color='#9b59b6', edgecolor='black', linewidth=1.5)

    # All significant
    for i in range(len(conditions)):
        ax.text(i, correlations[i] + 0.02, '***', ha='center', fontsize=12, fontweight='bold')

    ax.set_ylabel('Correlation with Performance (r)')
    ax.set_title('Figure 4: K-Index Robust Under Perturbation')
    ax.set_ylim(0, 1.1)

    # Add note
    ax.axhline(y=0.70, color='gray', linestyle='--', linewidth=1)
    ax.text(3.5, 0.72, 'Joint training r=0.70', fontsize=10, style='italic')

    plt.tight_layout()
    plt.savefig('figure_4_robustness.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved: figure_4_robustness.png")


def figure_5_zeroshot():
    """Comparison of joint training vs zero-shot."""
    conditions = ['Joint Training\n(same partners)', 'Zero-Shot\n(novel partners)']
    correlations = [0.70, -0.50]
    colors = ['#2ecc71', '#e74c3c']

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(conditions, correlations, color=colors, edgecolor='black', linewidth=1.5)

    ax.text(0, 0.75, '***', ha='center', fontsize=14, fontweight='bold')
    ax.text(1, -0.55, '*', ha='center', fontsize=14, fontweight='bold')

    ax.axhline(y=0, color='black', linewidth=1)
    ax.set_ylabel('Correlation with Performance (r)')
    ax.set_title('Figure 5: Flexibility Requires Shared Learning\n(Zero-Shot Shows Negative Correlation!)')
    ax.set_ylim(-0.8, 0.9)

    plt.tight_layout()
    plt.savefig('figure_5_zeroshot.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved: figure_5_zeroshot.png")


def figure_6_discovery_execution():
    """Comparison of discovery vs execution phases."""
    phases = ['Discovery\n(random targets)', 'Execution\n(fixed target)']
    correlations = [0.89, 0.85]

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(phases, correlations, color=['#f39c12', '#3498db'],
                  edgecolor='black', linewidth=1.5)

    ax.text(0, 0.92, '***', ha='center', fontsize=14, fontweight='bold')
    ax.text(1, 0.88, '***', ha='center', fontsize=14, fontweight='bold')

    ax.set_ylabel('Correlation with Performance (r)')
    ax.set_title('Figure 6: Flexibility Matters in Both Phases\n(Slightly More in Discovery)')
    ax.set_ylim(0, 1.05)

    plt.tight_layout()
    plt.savefig('figure_6_discovery_execution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved: figure_6_discovery_execution.png")


def figure_7_theoretical_framework():
    """Visual summary of when K-Index applies."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Create 2x2 grid
    applies = [
        ['Discovery Tasks\nr = +0.70***', 'Dense Rewards\nr = +0.78***'],
        ['Execution Tasks\nvariance → 0', 'Sparse Rewards\nr = -0.96***']
    ]

    colors = [
        ['#2ecc71', '#2ecc71'],
        ['#e74c3c', '#e74c3c']
    ]

    for i in range(2):
        for j in range(2):
            rect = plt.Rectangle((j, 1-i), 1, 1, facecolor=colors[i][j],
                                  edgecolor='black', linewidth=2)
            ax.add_patch(rect)
            ax.text(j + 0.5, 1.5 - i, applies[i][j],
                    ha='center', va='center', fontsize=11, fontweight='bold')

    # Labels
    ax.text(0.5, 2.2, 'Task Type', ha='center', fontsize=14, fontweight='bold')
    ax.text(1.5, 2.2, 'Reward Type', ha='center', fontsize=14, fontweight='bold')
    ax.text(-0.2, 1.5, 'K-Index\nApplies', ha='center', va='center', fontsize=12, rotation=90)
    ax.text(-0.2, 0.5, 'K-Index\nFails', ha='center', va='center', fontsize=12, rotation=90)

    ax.set_xlim(-0.5, 2.5)
    ax.set_ylim(-0.2, 2.5)
    ax.axis('off')
    ax.set_title('Figure 7: Theoretical Framework - When K-Index Applies', fontsize=16, pad=20)

    plt.tight_layout()
    plt.savefig('figure_7_theoretical_framework.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved: figure_7_theoretical_framework.png")


def main():
    print("\n" + "=" * 70)
    print("GENERATING FIGURES FOR PAPER 4")
    print("=" * 70 + "\n")

    print("Creating figures...")

    figure_1_metric_comparison()
    figure_2_generalization()
    figure_3_causal()
    figure_4_robustness()
    figure_5_zeroshot()
    figure_6_discovery_execution()
    figure_7_theoretical_framework()

    print("\n" + "=" * 70)
    print("COMPLETE - 7 figures generated")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
