"""
Extended Statistical Analysis for O/R Index Validation

Performs:
  - ANOVA and pairwise t-tests for significance
  - Effect size calculations (Cohen's d, eta-squared)
  - Correlation analysis
  - Per-scenario progression curves
  - Publication-ready LaTeX tables
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats
from typing import Dict, List, Tuple
import json


def load_results() -> pd.DataFrame:
    """Load O/R Index results from CSV."""
    return pd.read_csv("outputs/full_abc_or_index_results.csv")


def compute_effect_size(group1: np.ndarray, group2: np.ndarray) -> float:
    """
    Compute Cohen's d effect size.

    d = (mean1 - mean2) / pooled_std

    Interpretation:
      Small: 0.2
      Medium: 0.5
      Large: 0.8
    """
    mean1, mean2 = np.mean(group1), np.mean(group2)
    std1, std2 = np.std(group1, ddof=1), np.std(group2, ddof=1)
    n1, n2 = len(group1), len(group2)

    pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))

    if pooled_std == 0:
        return 0.0

    return (mean1 - mean2) / pooled_std


def anova_checkpoint_effect(df: pd.DataFrame) -> Dict:
    """One-way ANOVA: effect of training checkpoint on O/R Index."""
    groups = [df[df['checkpoint'] == ckpt]['or_index'].values
              for ckpt in sorted(df['checkpoint'].unique())]

    f_stat, p_value = stats.f_oneway(*groups)

    # Eta-squared (effect size for ANOVA)
    grand_mean = df['or_index'].mean()
    ss_between = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in groups)
    ss_total = sum((df['or_index'] - grand_mean)**2)
    eta_squared = ss_between / ss_total if ss_total > 0 else 0

    return {
        'f_statistic': f_stat,
        'p_value': p_value,
        'eta_squared': eta_squared,
        'significant': p_value < 0.05,
        'interpretation': interpret_eta_squared(eta_squared)
    }


def interpret_eta_squared(eta_sq: float) -> str:
    """Interpret eta-squared effect size."""
    if eta_sq < 0.01:
        return "negligible"
    elif eta_sq < 0.06:
        return "small"
    elif eta_sq < 0.14:
        return "medium"
    else:
        return "large"


def pairwise_checkpoint_tests(df: pd.DataFrame) -> pd.DataFrame:
    """Pairwise t-tests between consecutive checkpoints."""
    checkpoints = sorted(df['checkpoint'].unique())
    results = []

    for i in range(len(checkpoints) - 1):
        ckpt1, ckpt2 = checkpoints[i], checkpoints[i + 1]
        group1 = df[df['checkpoint'] == ckpt1]['or_index'].values
        group2 = df[df['checkpoint'] == ckpt2]['or_index'].values

        t_stat, p_value = stats.ttest_ind(group1, group2)
        effect_size = compute_effect_size(group1, group2)

        results.append({
            'comparison': f'{ckpt1} vs {ckpt2}',
            't_statistic': t_stat,
            'p_value': p_value,
            'cohen_d': effect_size,
            'mean_diff': np.mean(group1) - np.mean(group2),
            'significant': p_value < 0.05,
            'effect_interpretation': interpret_cohen_d(abs(effect_size))
        })

    return pd.DataFrame(results)


def interpret_cohen_d(d: float) -> str:
    """Interpret Cohen's d effect size."""
    d = abs(d)
    if d < 0.2:
        return "negligible"
    elif d < 0.5:
        return "small"
    elif d < 0.8:
        return "medium"
    else:
        return "large"


def anova_scenario_effect(df: pd.DataFrame) -> Dict:
    """One-way ANOVA: effect of scenario on O/R Index."""
    groups = [df[df['scenario'] == scenario]['or_index'].values
              for scenario in df['scenario'].unique()]

    f_stat, p_value = stats.f_oneway(*groups)

    grand_mean = df['or_index'].mean()
    ss_between = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in groups)
    ss_total = sum((df['or_index'] - grand_mean)**2)
    eta_squared = ss_between / ss_total if ss_total > 0 else 0

    return {
        'f_statistic': f_stat,
        'p_value': p_value,
        'eta_squared': eta_squared,
        'significant': p_value < 0.05,
        'interpretation': interpret_eta_squared(eta_squared)
    }


def scenario_ranking_table(df: pd.DataFrame) -> pd.DataFrame:
    """Create scenario ranking table with statistics."""
    scenario_stats = df.groupby('scenario')['or_index'].agg([
        'mean', 'std', 'min', 'max', 'count'
    ]).reset_index()

    scenario_stats = scenario_stats.sort_values('mean', ascending=False)
    scenario_stats['rank'] = range(1, len(scenario_stats) + 1)

    # Reorder columns
    scenario_stats = scenario_stats[['rank', 'scenario', 'mean', 'std', 'min', 'max', 'count']]

    return scenario_stats


def per_scenario_progression(df: pd.DataFrame, output_dir: Path):
    """Create individual progression plots for each scenario."""
    scenarios = df['scenario'].unique()

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()

    checkpoints = sorted(df['checkpoint'].unique())
    checkpoint_labels = ['Random', '5K', '50K', '200K']

    for idx, scenario in enumerate(scenarios):
        ax = axes[idx]
        scenario_df = df[df['scenario'] == scenario].sort_values('checkpoint')

        means = [scenario_df[scenario_df['checkpoint'] == ckpt]['or_index'].mean()
                 for ckpt in checkpoints]
        stds = [scenario_df[scenario_df['checkpoint'] == ckpt]['or_index'].std()
                for ckpt in checkpoints]

        ax.errorbar(range(len(checkpoints)), means, yerr=stds,
                    marker='o', linewidth=2, markersize=8, capsize=5)
        ax.set_xticks(range(len(checkpoints)))
        ax.set_xticklabels(checkpoint_labels)
        ax.set_title(scenario.replace('_', ' ').title(), fontsize=12, fontweight='bold')
        ax.set_ylabel('O/R Index', fontsize=10)
        ax.set_xlabel('Training Checkpoint', fontsize=10)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'per_scenario_progression.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_dir / 'per_scenario_progression.png'}")
    plt.close()


def generate_latex_tables(df: pd.DataFrame, stats_results: Dict, output_dir: Path):
    """Generate LaTeX-formatted tables for manuscript."""

    # Table 1: Summary statistics by checkpoint
    checkpoint_stats = df.groupby('checkpoint')['or_index'].agg(['mean', 'std', 'count']).reset_index()
    checkpoint_stats['checkpoint'] = checkpoint_stats['checkpoint'].map({
        0: 'Random',
        5000: 'PPO 5K',
        50000: 'PPO 50K',
        200000: 'PPO 200K'
    })

    latex_table1 = checkpoint_stats.to_latex(
        index=False,
        columns=['checkpoint', 'mean', 'std', 'count'],
        header=['Checkpoint', 'Mean O/R Index', 'Std Dev', 'N'],
        float_format='%.2f',
        caption='O/R Index statistics by training checkpoint.',
        label='tab:or_index_checkpoint'
    )

    # Table 2: Scenario ranking
    scenario_ranking = scenario_ranking_table(df)
    scenario_ranking['scenario'] = scenario_ranking['scenario'].str.replace('_', '\\_')

    latex_table2 = scenario_ranking.to_latex(
        index=False,
        columns=['rank', 'scenario', 'mean', 'std'],
        header=['Rank', 'Scenario', 'Mean O/R Index', 'Std Dev'],
        float_format='%.2f',
        caption='O/R Index ranking by scenario.',
        label='tab:or_index_scenario'
    )

    # Table 3: Pairwise checkpoint comparisons
    pairwise_df = stats_results['pairwise_checkpoints']
    pairwise_df['p_value_str'] = pairwise_df['p_value'].apply(lambda p: f"{p:.4f}{'*' if p < 0.05 else ''}")

    latex_table3 = pairwise_df.to_latex(
        index=False,
        columns=['comparison', 'mean_diff', 'cohen_d', 'p_value_str', 'effect_interpretation'],
        header=['Comparison', 'Mean Diff', "Cohen's d", 'p-value', 'Effect Size'],
        float_format='%.3f',
        caption='Pairwise comparisons between consecutive training checkpoints. * indicates p < 0.05.',
        label='tab:pairwise_checkpoints'
    )

    # Save all tables
    with open(output_dir / 'latex_tables.tex', 'w') as f:
        f.write("% Table 1: Checkpoint Statistics\n")
        f.write(latex_table1)
        f.write("\n\n% Table 2: Scenario Ranking\n")
        f.write(latex_table2)
        f.write("\n\n% Table 3: Pairwise Checkpoint Comparisons\n")
        f.write(latex_table3)

    print(f"✓ Saved LaTeX tables: {output_dir / 'latex_tables.tex'}")


def create_publication_figure(df: pd.DataFrame, output_dir: Path):
    """Create high-resolution publication-quality figure."""

    # Set publication style
    plt.rcParams.update({
        'font.size': 11,
        'axes.labelsize': 12,
        'axes.titlesize': 13,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.titlesize': 14,
        'font.family': 'serif',
        'font.serif': ['Times New Roman'],
    })

    fig = plt.figure(figsize=(12, 8))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

    # Panel A: Training progression (boxplot)
    ax1 = fig.add_subplot(gs[0, 0])
    policy_order = ['random', 'ppo_5k', 'ppo_50k', 'ppo_200k']
    policy_labels = ['Random', 'PPO 5K', 'PPO 50K', 'PPO 200K']
    sns.boxplot(data=df, x='policy', y='or_index', order=policy_order, ax=ax1, palette='Set2')
    ax1.set_xticklabels(policy_labels, rotation=15, ha='right')
    ax1.set_xlabel('Training Checkpoint', fontweight='bold')
    ax1.set_ylabel('O/R Index', fontweight='bold')
    ax1.set_title('(A) Training Progression', fontweight='bold', loc='left')
    ax1.grid(True, alpha=0.3, linestyle='--')

    # Panel B: Scenario comparison
    ax2 = fig.add_subplot(gs[0, 1])
    scenario_order = df.groupby('scenario')['or_index'].mean().sort_values(ascending=False).index
    scenario_labels = [s.replace('_', ' ').replace('h400', '(H400)').replace('h800', '(H800)')
                       for s in scenario_order]
    sns.boxplot(data=df, x='scenario', y='or_index', order=scenario_order, ax=ax2, palette='Set3')
    ax2.set_xticklabels(scenario_labels, rotation=45, ha='right', fontsize=8)
    ax2.set_xlabel('Scenario', fontweight='bold')
    ax2.set_ylabel('O/R Index', fontweight='bold')
    ax2.set_title('(B) Scenario Comparison', fontweight='bold', loc='left')
    ax2.grid(True, alpha=0.3, linestyle='--')

    # Panel C: Heatmap
    ax3 = fig.add_subplot(gs[1, 0])
    pivot_table = df.pivot_table(values='or_index', index='scenario', columns='policy', aggfunc='mean')
    pivot_table = pivot_table[policy_order]
    pivot_table.columns = policy_labels
    pivot_table.index = [s.replace('_', ' ')[:30] for s in pivot_table.index]
    sns.heatmap(pivot_table, annot=True, fmt='.0f', cmap='YlOrRd', ax=ax3,
                cbar_kws={'label': 'O/R Index'}, linewidths=0.5)
    ax3.set_xlabel('Training Checkpoint', fontweight='bold')
    ax3.set_ylabel('Scenario', fontweight='bold')
    ax3.set_title('(C) Scenario × Checkpoint Heatmap', fontweight='bold', loc='left')

    # Panel D: Progression curves
    ax4 = fig.add_subplot(gs[1, 1])
    checkpoints = sorted(df['checkpoint'].unique())
    for scenario in df['scenario'].unique():
        scenario_df = df[df['scenario'] == scenario].sort_values('checkpoint')
        means = [scenario_df[scenario_df['checkpoint'] == ckpt]['or_index'].mean()
                 for ckpt in checkpoints]
        label = scenario.replace('_', ' ')[:25]
        ax4.plot(checkpoints, means, marker='o', label=label, alpha=0.7, linewidth=2)

    ax4.set_xlabel('Training Episodes', fontweight='bold')
    ax4.set_ylabel('O/R Index', fontweight='bold')
    ax4.set_title('(D) Learning Curves', fontweight='bold', loc='left')
    ax4.legend(fontsize=7, loc='best')
    ax4.grid(True, alpha=0.3, linestyle='--')
    ax4.set_xscale('symlog')
    ax4.set_xticks(checkpoints)
    ax4.set_xticklabels(['0', '5K', '50K', '200K'])

    plt.savefig(output_dir / 'publication_figure.png', dpi=600, bbox_inches='tight')
    plt.savefig(output_dir / 'publication_figure.pdf', bbox_inches='tight')
    print(f"✓ Saved publication figure (PNG + PDF)")
    plt.close()


def main():
    output_dir = Path("outputs")

    print("="*80)
    print("Extended Statistical Analysis")
    print("="*80)

    # Load data
    print("\n1. Loading results...")
    df = load_results()
    print(f"   Loaded {len(df)} results")

    # Statistical tests
    print("\n2. Running statistical tests...")
    stats_results = {}

    # ANOVA: Checkpoint effect
    print("   - ANOVA: Checkpoint effect...")
    stats_results['anova_checkpoint'] = anova_checkpoint_effect(df)

    # ANOVA: Scenario effect
    print("   - ANOVA: Scenario effect...")
    stats_results['anova_scenario'] = anova_scenario_effect(df)

    # Pairwise checkpoint tests
    print("   - Pairwise checkpoint tests...")
    stats_results['pairwise_checkpoints'] = pairwise_checkpoint_tests(df)

    # Scenario ranking
    print("   - Scenario ranking...")
    stats_results['scenario_ranking'] = scenario_ranking_table(df)

    # Visualizations
    print("\n3. Creating visualizations...")
    print("   - Per-scenario progression curves...")
    per_scenario_progression(df, output_dir)

    print("   - Publication-quality figure...")
    create_publication_figure(df, output_dir)

    # LaTeX tables
    print("\n4. Generating LaTeX tables...")
    generate_latex_tables(df, stats_results, output_dir)

    # Save statistical results
    print("\n5. Saving statistical results...")

    # Helper to convert numpy types to Python native types
    def convert_numpy_types(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif isinstance(obj, dict):
            return {key: convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy_types(item) for item in obj]
        return obj

    # Convert DataFrames to dict for JSON serialization
    stats_json = {
        'anova_checkpoint': convert_numpy_types(stats_results['anova_checkpoint']),
        'anova_scenario': convert_numpy_types(stats_results['anova_scenario']),
        'pairwise_checkpoints': convert_numpy_types(stats_results['pairwise_checkpoints'].to_dict('records')),
        'scenario_ranking': convert_numpy_types(stats_results['scenario_ranking'].to_dict('records'))
    }

    with open(output_dir / 'statistical_analysis.json', 'w') as f:
        json.dump(stats_json, f, indent=2)

    print(f"   ✓ Saved: {output_dir / 'statistical_analysis.json'}")

    # Print summary
    print("\n" + "="*80)
    print("STATISTICAL SUMMARY")
    print("="*80)

    print("\n📊 ANOVA Results:")
    print(f"\nCheckpoint Effect:")
    print(f"  F({len(df['checkpoint'].unique())-1}, {len(df)-len(df['checkpoint'].unique())}) = "
          f"{stats_results['anova_checkpoint']['f_statistic']:.3f}, "
          f"p = {stats_results['anova_checkpoint']['p_value']:.4f}")
    print(f"  η² = {stats_results['anova_checkpoint']['eta_squared']:.4f} "
          f"({stats_results['anova_checkpoint']['interpretation']})")
    print(f"  Significant: {stats_results['anova_checkpoint']['significant']}")

    print(f"\nScenario Effect:")
    print(f"  F({len(df['scenario'].unique())-1}, {len(df)-len(df['scenario'].unique())}) = "
          f"{stats_results['anova_scenario']['f_statistic']:.3f}, "
          f"p = {stats_results['anova_scenario']['p_value']:.4f}")
    print(f"  η² = {stats_results['anova_scenario']['eta_squared']:.4f} "
          f"({stats_results['anova_scenario']['interpretation']})")
    print(f"  Significant: {stats_results['anova_scenario']['significant']}")

    print("\n📈 Pairwise Checkpoint Comparisons:")
    for _, row in stats_results['pairwise_checkpoints'].iterrows():
        sig_marker = " ***" if row['p_value'] < 0.001 else " **" if row['p_value'] < 0.01 else " *" if row['significant'] else ""
        print(f"  {row['comparison']:20s}: d={row['cohen_d']:6.3f} ({row['effect_interpretation']:10s}), "
              f"p={row['p_value']:.4f}{sig_marker}")

    print("\n🏆 Top 3 Scenarios (by mean O/R Index):")
    for _, row in stats_results['scenario_ranking'].head(3).iterrows():
        print(f"  {row['rank']}. {row['scenario']:50s}: {row['mean']:8.2f} ± {row['std']:7.2f}")

    print("\n" + "="*80)
    print("✅ EXTENDED ANALYSIS COMPLETE!")
    print("="*80)
    print(f"\nOutputs:")
    print(f"  - Statistical results:    {output_dir / 'statistical_analysis.json'}")
    print(f"  - LaTeX tables:          {output_dir / 'latex_tables.tex'}")
    print(f"  - Progression curves:    {output_dir / 'per_scenario_progression.png'}")
    print(f"  - Publication figure:    {output_dir / 'publication_figure.png|.pdf'}")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
