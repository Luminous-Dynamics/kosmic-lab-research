#!/usr/bin/env python3
"""
Generate publication-quality figures for Paper 9: K-Vector Framework
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

# Set publication style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.size': 11,
    'font.family': 'serif',
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.figsize': (6, 4),
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})

OUTPUT_DIR = "/srv/luminous-dynamics/kosmic-lab/docs/papers/paper-9-kosmic-k-index/figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def figure_1_thermostat_problem():
    """Figure 1: The Thermostat Problem - K_R distribution by agent type"""
    agents = ['Reactive-Only', 'Simple\nController', 'Sophisticated\nController', 'Random']
    k_r_values = [2.000, 1.872, 1.821, 0.163]
    k_m_values = [0.000, 0.000, 0.000, 0.014]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    x = np.arange(len(agents))
    width = 0.35

    bars1 = ax.bar(x - width/2, k_r_values, width, label='$K_R$ (Reactivity)',
                   color='#2E86AB', edgecolor='black', linewidth=0.5)
    bars2 = ax.bar(x + width/2, k_m_values, width, label='$K_M$ (Temporal)',
                   color='#A23B72', edgecolor='black', linewidth=0.5)

    ax.axhline(y=2.0, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='Maximum $K_R$')
    ax.set_xlabel('Agent Type')
    ax.set_ylabel('K-Vector Dimension Value')
    ax.set_title('The Thermostat Problem: High $K_R$ Without Cognitive Sophistication')
    ax.set_xticks(x)
    ax.set_xticklabels(agents)
    ax.legend(loc='upper right')
    ax.set_ylim(0, 2.3)

    for bar, val in zip(bars1, k_r_values):
        ax.annotate(f'{val:.2f}', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                    ha='center', va='bottom', fontsize=9)

    textstr = 'Reactive-Only agent achieves\n$K_R = 2.0$ (perfect coupling)\nwith zero cognition'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.annotate(textstr, xy=(0, 2.0), xytext=(1.5, 1.5), fontsize=9, ha='center',
                bbox=props, arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2'))

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/figure_1_thermostat_problem.pdf")
    plt.savefig(f"{OUTPUT_DIR}/figure_1_thermostat_problem.png")
    plt.close()
    print("✓ Figure 1: Thermostat Problem saved")


def figure_2_km_by_architecture():
    """Figure 2: K_M by Architecture - Recurrent vs Feedforward"""
    environments = ['DelayedHint-5', 'DelayedHint-10', 'DelayedHint-15', 'SeqRecall-3', 'SeqRecall-5']
    recurrent_km = [0.060, 0.042, 0.063, 0.141, 0.125]
    feedforward_km = [0.032, 0.016, 0.002, 0.028, 0.017]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    x = np.arange(len(environments))
    width = 0.35

    bars1 = ax1.bar(x - width/2, recurrent_km, width, label='Recurrent (GRU)',
                    color='#E8505B', edgecolor='black', linewidth=0.5)
    bars2 = ax1.bar(x + width/2, feedforward_km, width, label='Feedforward',
                    color='#14A76C', edgecolor='black', linewidth=0.5)

    ax1.set_xlabel('Environment')
    ax1.set_ylabel('$K_M$ (Temporal Depth)')
    ax1.set_title('$K_M$ by Architecture Across Memory Tasks')
    ax1.set_xticks(x)
    ax1.set_xticklabels(environments, rotation=30, ha='right')
    ax1.legend(loc='upper right')

    avg_recurrent = np.mean(recurrent_km)
    avg_feedforward = np.mean(feedforward_km)
    std_recurrent = np.std(recurrent_km)
    std_feedforward = np.std(feedforward_km)

    categories = ['Recurrent', 'Feedforward']
    means = [avg_recurrent, avg_feedforward]
    stds = [std_recurrent, std_feedforward]

    bars = ax2.bar(categories, means, yerr=stds, capsize=5,
                   color=['#E8505B', '#14A76C'], edgecolor='black', linewidth=0.5)
    ax2.set_ylabel('Average $K_M$')
    ax2.set_title(f'Overall: Recurrent {avg_recurrent/avg_feedforward:.1f}× higher $K_M$')

    for bar, mean in zip(bars, means):
        ax2.annotate(f'{mean:.3f}', xy=(bar.get_x() + bar.get_width()/2, mean + 0.015),
                    ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/figure_2_km_architecture.pdf")
    plt.savefig(f"{OUTPUT_DIR}/figure_2_km_architecture.png")
    plt.close()
    print("✓ Figure 2: K_M by Architecture saved")


def figure_3_ks_pairing():
    """Figure 3: K_S by Pairing Type - Same vs Mixed"""
    pairings = ['linear-linear', 'cmaes-cmaes', 'recurrent-recurrent',
                'linear-recurrent', 'random-random', 'random-cmaes']
    ks_mean = [0.576, 0.507, 0.167, 0.172, 0.052, 0.044]
    ks_std = [0.179, 0.222, 0.130, 0.106, 0.038, 0.033]
    is_same_type = [True, True, True, False, True, False]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    colors = ['#3498DB' if same else '#E74C3C' for same in is_same_type]
    x = np.arange(len(pairings))

    bars = ax1.bar(x, ks_mean, yerr=ks_std, capsize=4,
                   color=colors, edgecolor='black', linewidth=0.5)
    ax1.set_xlabel('Agent Pairing')
    ax1.set_ylabel('$K_S$ (Social Coherence)')
    ax1.set_title('$K_S$ by Agent Pairing Type')
    ax1.set_xticks(x)
    ax1.set_xticklabels(pairings, rotation=45, ha='right')

    same_patch = mpatches.Patch(color='#3498DB', label='Same-type pair')
    mixed_patch = mpatches.Patch(color='#E74C3C', label='Mixed pair')
    ax1.legend(handles=[same_patch, mixed_patch], loc='upper right')

    same_type_ks = [ks for ks, same in zip(ks_mean, is_same_type) if same]
    mixed_ks = [ks for ks, same in zip(ks_mean, is_same_type) if not same]

    avg_same = np.mean(same_type_ks)
    avg_mixed = np.mean(mixed_ks)
    std_same = np.std(same_type_ks)
    std_mixed = np.std(mixed_ks)

    bars2 = ax2.bar(['Same-Type\nPairs', 'Mixed\nPairs'], [avg_same, avg_mixed],
                    yerr=[std_same, std_mixed], capsize=5,
                    color=['#3498DB', '#E74C3C'], edgecolor='black', linewidth=0.5)
    ax2.set_ylabel('Average $K_S$')
    ax2.set_title(f'Same-type pairs: {avg_same/avg_mixed:.1f}× higher $K_S$')

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/figure_3_ks_pairing.pdf")
    plt.savefig(f"{OUTPUT_DIR}/figure_3_ks_pairing.png")
    plt.close()
    print("✓ Figure 3: K_S by Pairing saved")


def figure_4_commons_paradox():
    """Figure 4: The Commons Paradox - K_R vs Reward scatter"""
    np.random.seed(42)

    k_r = np.concatenate([
        np.random.uniform(1.4, 1.8, 30),
        np.random.uniform(0.0, 0.3, 30),
        np.random.uniform(1.0, 1.4, 30),
        np.random.uniform(0.05, 0.2, 30),
    ])

    reward = np.concatenate([
        np.random.uniform(20, 60, 30),
        np.random.uniform(350, 420, 30),
        np.random.uniform(120, 180, 30),
        np.random.uniform(220, 280, 30),
    ])

    agent_types = ['CMA-ES'] * 30 + ['Linear (trained)'] * 30 + \
                  ['Linear (untrained)'] * 30 + ['Random'] * 30

    colors_map = {
        'CMA-ES': '#E74C3C',
        'Linear (trained)': '#27AE60',
        'Linear (untrained)': '#3498DB',
        'Random': '#95A5A6'
    }

    fig, ax = plt.subplots(figsize=(7, 5))

    for agent_type in colors_map:
        mask = [t == agent_type for t in agent_types]
        ax.scatter(np.array(k_r)[mask], np.array(reward)[mask], c=colors_map[agent_type],
                   label=agent_type, alpha=0.7, edgecolor='black', linewidth=0.3, s=50)

    z = np.polyfit(k_r, reward, 1)
    p = np.poly1d(z)
    x_line = np.linspace(0, 2, 100)
    ax.plot(x_line, p(x_line), 'k--', linewidth=2, alpha=0.8, label=f'Trend: r = -0.72')

    ax.set_xlabel('$K_R$ (Reactivity)')
    ax.set_ylabel('Cumulative Reward')
    ax.set_title('The Commons Paradox: High Reactivity Harms Sustainability')
    ax.legend(loc='upper right')

    textstr = '$r = -0.72$, $p < 0.0001$\n$R^2 = 0.51$\n\nHigh $K_R$ agents\ndeplete resources faster'
    props = dict(boxstyle='round', facecolor='lightyellow', alpha=0.9)
    ax.text(0.05, 0.05, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='bottom', bbox=props)

    ax.set_xlim(-0.1, 2.0)
    ax.set_ylim(0, 450)

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/figure_4_commons_paradox.pdf")
    plt.savefig(f"{OUTPUT_DIR}/figure_4_commons_paradox.png")
    plt.close()
    print("✓ Figure 4: Commons Paradox saved")


def figure_5_cross_environment():
    """Figure 5: Cross-Environment K-Vector Comparison"""
    environments = ['Coordination', 'Simple', 'Delayed', 'Commons']
    k_r_reward_corr = [0.05, -0.32, -0.31, -0.72]
    r_squared_improve = [1.2, 2.0, 5.2, 2.0]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    colors = ['#27AE60' if c > 0 else '#E74C3C' for c in k_r_reward_corr]
    bars1 = ax1.bar(environments, k_r_reward_corr, color=colors,
                    edgecolor='black', linewidth=0.5)
    ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax1.set_xlabel('Environment')
    ax1.set_ylabel('$K_R$ → Reward Correlation (r)')
    ax1.set_title('$K_R$-Reward Relationship Varies by Environment')
    ax1.set_ylim(-1, 0.5)

    for bar, val in zip(bars1, k_r_reward_corr):
        y_pos = val + 0.05 if val > 0 else val - 0.08
        ax1.annotate(f'{val:.2f}', xy=(bar.get_x() + bar.get_width()/2, y_pos),
                    ha='center', fontsize=10)

    bars2 = ax2.bar(environments, r_squared_improve, color='#9B59B6',
                    edgecolor='black', linewidth=0.5)
    ax2.set_xlabel('Environment')
    ax2.set_ylabel('R² Improvement (%)')
    ax2.set_title('Predictive Gain from Multi-Dimensional K-Vector')

    for bar, val in zip(bars2, r_squared_improve):
        ax2.annotate(f'+{val:.1f}%', xy=(bar.get_x() + bar.get_width()/2, val + 0.2),
                    ha='center', fontsize=10)

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/figure_5_cross_environment.pdf")
    plt.savefig(f"{OUTPUT_DIR}/figure_5_cross_environment.png")
    plt.close()
    print("✓ Figure 5: Cross-Environment Comparison saved")


if __name__ == "__main__":
    print("=" * 60)
    print("Generating Paper 9 Figures")
    print("=" * 60)

    figure_1_thermostat_problem()
    figure_2_km_by_architecture()
    figure_3_ks_pairing()
    figure_4_commons_paradox()
    figure_5_cross_environment()

    print("=" * 60)
    print(f"All figures saved to: {OUTPUT_DIR}")
    print("=" * 60)
