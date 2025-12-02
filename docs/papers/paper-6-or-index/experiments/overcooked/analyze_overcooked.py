"""
Analyze Overcooked trajectories: compute O/R Index and generate publication figures
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
    n_actions = int(actions.max()) + 1  # Assume actions are 0-indexed
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


def compute_coordination_success(episode_return, scenario_id):
    """
    Normalize episode return to [0, 1] coordination score.

    These baselines are approximate - adjust based on your observed ranges.
    Different scenarios have different difficulty levels.
    """
    # Approximate baselines per scenario (adjust after seeing data)
    baselines = {
        # Option A: Baseline scenarios
        "cramped_room_h400_baseline": {"random": 0, "expert": 200},
        "asymmetric_advantages_h400_baseline": {"random": 0, "expert": 250},

        # Option B: Stress tests (harder = lower expert performance)
        "coordination_ring_h400_stress_spatial": {"random": 0, "expert": 150},
        "forced_coordination_h400_stress_sequential": {"random": 0, "expert": 180},
        "cramped_room_h800_stress_temporal": {"random": 0, "expert": 350},  # 2x horizon

        # Option C: Many-agent simulation
        "cramped_room_h400_multiagent_sim": {"random": 0, "expert": 180},
    }

    # Fallback if scenario not found
    default = {"random": 0, "expert": 200}
    return_random = baselines.get(scenario_id, default).get("random", 0)
    return_expert = baselines.get(scenario_id, default).get("expert", 200)

    score = (episode_return - return_random) / (return_expert - return_random)
    return np.clip(score, 0, 1)


def analyze_all_trajectories():
    """Walk all trajectories, compute O/R, and create summary CSV - A+B+C Validation"""

    print("="*60)
    print("Analyzing Overcooked Trajectories - A+B+C Validation")
    print("="*60)

    results = []

    # Match collection configuration
    scenarios = [
        # OPTION A: Standard validation
        ("cramped_room", 400, "baseline"),
        ("asymmetric_advantages", 400, "baseline"),

        # OPTION B: Stress tests
        ("coordination_ring", 400, "stress_spatial"),
        ("forced_coordination", 400, "stress_sequential"),
        ("cramped_room", 800, "stress_temporal"),

        # OPTION C: Many-agent simulation
        ("cramped_room", 400, "multiagent_sim"),
    ]

    policy_types = ["random", "ppo_5k", "ppo_50k", "ppo_200k"]
    trajectories_path = Path("./trajectories")

    for layout_name, horizon, scenario_type in scenarios:
        scenario_id = f"{layout_name}_h{horizon}_{scenario_type}"

        print(f"\n{'#'*60}")
        print(f"# Scenario: {scenario_id}")
        print(f"{'#'*60}")

        scenario_path = trajectories_path / scenario_id
        if not scenario_path.exists():
            print(f"  ⚠ Directory not found: {scenario_path}")
            print(f"  ⚠ Run collect_overcooked.py first!")
            continue

        for policy_type in policy_types:
            policy_path = scenario_path / policy_type

            if not policy_path.exists():
                print(f"  ⚠ Policy directory not found: {policy_path}")
                continue

            print(f"\n  Analyzing {policy_type}...")

            # Find all seed directories
            seed_dirs = sorted(policy_path.glob("seed_*"))

            for seed_dir in tqdm(seed_dirs, desc=f"    {policy_type}"):
                try:
                    # Load trajectory
                    data = np.load(seed_dir / "trajectories.npz")
                    obs = data["obs"]
                    actions = data["actions"]
                    ep_return = float(data["ep_return"])

                    # Load metadata
                    with open(seed_dir / "meta.json") as f:
                        meta = json.load(f)

                    # Compute O/R Index
                    or_value = compute_or_index(obs, actions, n_bins=10)

                    # Compute coordination success (using scenario_id for proper baselines)
                    coord_success = compute_coordination_success(ep_return, scenario_id)

                    # Store result with all scenario metadata
                    results.append({
                        "scenario_id": scenario_id,
                        "layout": layout_name,
                        "horizon": horizon,
                        "scenario_type": scenario_type,
                        "policy_type": policy_type,
                        "seed": meta["seed"],
                        "episode_return": ep_return,
                        "episode_length": meta["episode_length"],
                        "or_index": or_value,
                        "coordination_success": coord_success,
                    })

                except Exception as e:
                    print(f"    ⚠ Error processing {seed_dir}: {e}")
                    continue

    # Create DataFrame
    df = pd.DataFrame(results)

    if df.empty:
        print("\n⚠ No results found! Check that trajectories were collected.")
        return None

    # Save summary CSV
    output_path = Path("./overcooked_summary.csv")
    df.to_csv(output_path, index=False)

    print(f"\n{'='*60}")
    print(f"✓ Analysis complete!")
    print(f"{'='*60}")
    print(f"\nSaved summary to: {output_path}")
    print(f"Total trajectories analyzed: {len(df)}")

    # Print overall correlation
    overall_r, overall_p = pearsonr(df["or_index"], df["coordination_success"])
    print(f"\nOverall correlation: r = {overall_r:.3f} (p = {overall_p:.2e})")

    # Print per-scenario correlations
    print("\nPer-scenario correlations:")
    for scenario_id in df["scenario_id"].unique():
        scenario_df = df[df["scenario_id"] == scenario_id]
        if len(scenario_df) < 2:
            print(f"  {scenario_id}: insufficient data (n = {len(scenario_df)})")
            continue
        r, p = pearsonr(scenario_df["or_index"], scenario_df["coordination_success"])
        print(f"  {scenario_id}: r = {r:.3f} (p = {p:.2e}), n = {len(scenario_df)}")

    # Group by scenario type (baseline vs stress vs multiagent)
    print("\nPer-scenario-type correlations:")
    for scenario_type in df["scenario_type"].unique():
        type_df = df[df["scenario_type"] == scenario_type]
        if len(type_df) < 2:
            continue
        r, p = pearsonr(type_df["or_index"], type_df["coordination_success"])
        print(f"  {scenario_type}: r = {r:.3f} (p = {p:.2e}), n = {len(type_df)}")

    return df


def plot_scatter_by_scenario(df):
    """Generate 3x2 scatter plot grid (one per scenario) - A+B+C Validation"""

    fig, axes = plt.subplots(3, 2, figsize=(14, 18))
    axes = axes.flatten()

    scenarios = [
        ("cramped_room_h400_baseline", "Cramped Room (baseline)"),
        ("asymmetric_advantages_h400_baseline", "Asymmetric Advantages (baseline)"),
        ("coordination_ring_h400_stress_spatial", "Coordination Ring (spatial stress)"),
        ("forced_coordination_h400_stress_sequential", "Forced Coordination (sequential stress)"),
        ("cramped_room_h800_stress_temporal", "Cramped Room 2× Horizon (temporal stress)"),
        ("cramped_room_h400_multiagent_sim", "Cramped Room (many-agent sim)"),
    ]

    # Color by policy type
    policy_colors = {
        "random": "gray",
        "ppo_5k": "lightblue",
        "ppo_50k": "blue",
        "ppo_200k": "darkblue",
    }

    for idx, (scenario_id, title) in enumerate(scenarios):
        ax = axes[idx]
        scenario_df = df[df["scenario_id"] == scenario_id]

        if len(scenario_df) == 0:
            ax.text(0.5, 0.5, "No data", ha='center', va='center', transform=ax.transAxes)
            ax.set_title(title, fontsize=12, fontweight='bold')
            continue

        for policy_type, color in policy_colors.items():
            policy_data = scenario_df[scenario_df["policy_type"] == policy_type]
            if len(policy_data) > 0:
                ax.scatter(
                    policy_data["or_index"],
                    policy_data["coordination_success"],
                    label=policy_type,
                    color=color,
                    alpha=0.6,
                    s=40,
                    edgecolors='white',
                    linewidth=0.5
                )

        # Compute correlation
        if len(scenario_df) >= 2:
            r, p = pearsonr(scenario_df["or_index"], scenario_df["coordination_success"])

            # Add best-fit line
            z = np.polyfit(scenario_df["or_index"], scenario_df["coordination_success"], 1)
            p_func = np.poly1d(z)
            x_line = np.linspace(scenario_df["or_index"].min(), scenario_df["or_index"].max(), 100)
            ax.plot(x_line, p_func(x_line), "r--", alpha=0.5, linewidth=2)

            # Formatting with correlation
            ax.set_title(
                f"{title}\n$r = {r:.2f}${'***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''}, $n = {len(scenario_df)}$",
                fontsize=11,
                fontweight='bold'
            )
        else:
            ax.set_title(title, fontsize=11, fontweight='bold')

        ax.set_xlabel("O/R Index", fontsize=10)
        ax.set_ylabel("Coordination Success", fontsize=10)
        ax.legend(loc='best', fontsize=8)
        ax.grid(alpha=0.3, linestyle='--')

    plt.tight_layout()

    # Save figure
    output_path = Path("../../figures/overcooked/figure_overcooked_scatter_comprehensive.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved comprehensive scatter plot: {output_path}")

    return fig


def plot_training_evolution(df):
    """Generate training evolution plot (O/R vs timesteps) - Grouped by scenario type"""

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    policy_order = ["random", "ppo_5k", "ppo_50k", "ppo_200k"]
    timesteps = [0, 5000, 50000, 200000]

    # Group scenarios by type
    scenario_groups = {
        "Baseline": ["cramped_room_h400_baseline", "asymmetric_advantages_h400_baseline"],
        "Stress Tests": ["coordination_ring_h400_stress_spatial", "forced_coordination_h400_stress_sequential", "cramped_room_h800_stress_temporal"],
        "Many-Agent Sim": ["cramped_room_h400_multiagent_sim"],
    }

    colors = plt.cm.tab10.colors

    for ax_idx, (group_name, scenario_ids) in enumerate(scenario_groups.items()):
        ax = axes[ax_idx]

        for color_idx, scenario_id in enumerate(scenario_ids):
            or_means = []
            or_stds = []

            for policy_type in policy_order:
                policy_data = df[(df["scenario_id"] == scenario_id) & (df["policy_type"] == policy_type)]

                if len(policy_data) > 0:
                    or_means.append(policy_data["or_index"].mean())
                    or_stds.append(policy_data["or_index"].std())
                else:
                    or_means.append(np.nan)
                    or_stds.append(np.nan)

            # Shortened label for readability
            label = scenario_id.replace("_h400_", " ").replace("_h800_", " 2×h ").replace("_", " ")

            # Plot O/R evolution
            ax.errorbar(
                timesteps, or_means, yerr=or_stds,
                label=label,
                marker='o',
                linestyle='-',
                linewidth=2,
                capsize=4,
                alpha=0.8,
                color=colors[color_idx % len(colors)]
            )

        # Formatting
        ax.set_xlabel("Training Timesteps", fontsize=11)
        ax.set_ylabel("O/R Index", fontsize=11)
        ax.set_title(f"{group_name}", fontsize=12, fontweight='bold')
        ax.legend(loc='best', fontsize=8)
        ax.grid(alpha=0.3, linestyle='--')
        ax.set_xscale('symlog')  # Use symlog for better visualization of 0

    plt.tight_layout()

    # Save figure
    output_path = Path("../../figures/overcooked/figure_overcooked_evolution_comprehensive.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved comprehensive evolution plot: {output_path}")

    return fig


def generate_latex_table(df):
    """Generate LaTeX table for paper - A+B+C Comprehensive Validation"""

    print("\n" + "="*60)
    print("LaTeX Table for Paper - Comprehensive Validation")
    print("="*60)

    print("\n\\begin{center}")
    print("\\begin{tabular}{lcccp{6cm}}")
    print("\\toprule")
    print("\\textbf{Scenario} & \\textbf{Type} & \\textbf{r} & \\textbf{p} & \\textbf{n} \\\\")
    print("\\midrule")

    # Group by scenario type for better presentation
    scenario_types = df["scenario_type"].unique()

    for scenario_type in sorted(scenario_types):
        # Section header
        type_name = scenario_type.replace("_", " ").title()
        print(f"\\multicolumn{{5}}{{l}}{{\\textit{{{type_name}}}}} \\\\")

        # Get scenarios of this type
        type_scenarios = df[df["scenario_type"] == scenario_type]["scenario_id"].unique()

        for scenario_id in sorted(type_scenarios):
            scenario_df = df[df["scenario_id"] == scenario_id]

            if len(scenario_df) < 2:
                continue

            r, p = pearsonr(scenario_df["or_index"], scenario_df["coordination_success"])

            # Format scenario name (shortened)
            scenario_name = scenario_id.replace("_h400", "").replace("_h800", " (2×h)").replace("_", " ").replace(" baseline", "").replace(" stress ", " ")
            if len(scenario_name) > 30:
                scenario_name = scenario_name[:27] + "..."

            # Format p-value
            if p < 0.001:
                p_str = "$<0.001$***"
            elif p < 0.01:
                p_str = f"${p:.3f}$**"
            elif p < 0.05:
                p_str = f"${p:.3f}$*"
            else:
                p_str = f"${p:.3f}$"

            print(f"  {scenario_name} & & ${r:.2f}$ & {p_str} & {len(scenario_df)} \\\\")

        print("\\midrule")

    # Overall
    overall_r, overall_p = pearsonr(df["or_index"], df["coordination_success"])
    if overall_p < 0.001:
        overall_p_str = "$<0.001$***"
    elif overall_p < 0.01:
        overall_p_str = f"${overall_p:.3f}$**"
    elif overall_p < 0.05:
        overall_p_str = f"${overall_p:.3f}$*"
    else:
        overall_p_str = f"${overall_p:.3f}$"

    print(f"\\textbf{{Combined (all scenarios)}} & & $\\mathbf{{{overall_r:.2f}}}$ & {overall_p_str} & {len(df)} \\\\")
    print("\\bottomrule")
    print("\\end{tabular}")
    print("\\end{center}")
    print("\n\\textit{Note: *** p < 0.001, ** p < 0.01, * p < 0.05}")


def main():
    """Run complete analysis pipeline - A+B+C Comprehensive Validation"""

    # Analyze all trajectories
    df = analyze_all_trajectories()

    if df is None:
        return

    # Generate plots
    print("\n" + "="*60)
    print("Generating Publication Figures - Comprehensive Validation")
    print("="*60)

    plot_scatter_by_scenario(df)
    plot_training_evolution(df)

    # Generate LaTeX table
    generate_latex_table(df)

    print("\n" + "="*60)
    print("✓ All analysis complete!")
    print("="*60)
    print("\nGenerated files:")
    print("  - overcooked_summary.csv")
    print("  - figures/overcooked/figure_overcooked_scatter_comprehensive.png (3×2 grid)")
    print("  - figures/overcooked/figure_overcooked_evolution_comprehensive.png (3-panel)")
    print("\nValidation coverage:")
    print("  - Option A (baseline): 2 scenarios")
    print("  - Option B (stress tests): 3 scenarios")
    print("  - Option C (many-agent sim): 1 scenario")
    print("  - Total: 6 scenarios × 4 checkpoints × 30 seeds = 720 trajectories")
    print("\nNext step: Integrate results into paper Section 5.X")


if __name__ == "__main__":
    # Set plotting style
    sns.set_style("whitegrid")
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.size'] = 11

    main()
