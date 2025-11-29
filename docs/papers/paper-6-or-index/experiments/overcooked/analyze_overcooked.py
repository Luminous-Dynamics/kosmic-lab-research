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


def compute_coordination_success(episode_return, layout):
    """
    Normalize episode return to [0, 1] coordination score.

    These baselines are approximate - adjust based on your observed ranges.
    """
    # Approximate baselines per layout (adjust after seeing data)
    baselines = {
        "cramped_room": {"random": 0, "expert": 200},
        "asymmetric_advantages": {"random": 0, "expert": 250},
    }

    return_random = baselines.get(layout, {}).get("random", 0)
    return_expert = baselines.get(layout, {}).get("expert", 200)

    score = (episode_return - return_random) / (return_expert - return_random)
    return np.clip(score, 0, 1)


def analyze_all_trajectories():
    """Walk all trajectories, compute O/R, and create summary CSV"""

    print("="*60)
    print("Analyzing Overcooked Trajectories")
    print("="*60)

    results = []

    layouts = ["cramped_room", "asymmetric_advantages"]
    policy_types = ["random", "ppo_5k", "ppo_50k", "ppo_200k"]

    for layout in layouts:
        print(f"\n{'#'*60}")
        print(f"# Layout: {layout}")
        print(f"{'#'*60}")

        layout_path = Path(f"./{layout}")
        if not layout_path.exists():
            print(f"  ⚠ Directory not found: {layout_path}")
            print(f"  ⚠ Run collect_overcooked.py first!")
            continue

        for policy_type in policy_types:
            policy_path = layout_path / policy_type

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

                    # Compute coordination success
                    coord_success = compute_coordination_success(ep_return, layout)

                    # Store result
                    results.append({
                        "layout": layout,
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

    # Print per-layout correlations
    print("\nPer-layout correlations:")
    for layout in df["layout"].unique():
        layout_df = df[df["layout"] == layout]
        r, p = pearsonr(layout_df["or_index"], layout_df["coordination_success"])
        print(f"  {layout}: r = {r:.3f} (p = {p:.2e}), n = {len(layout_df)}")

    return df


def plot_scatter_by_layout(df):
    """Generate 2-panel scatter plot (one per layout)"""

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    layouts = ["cramped_room", "asymmetric_advantages"]
    layout_titles = ["Cramped Room", "Asymmetric Advantages"]

    for idx, (layout, title) in enumerate(zip(layouts, layout_titles)):
        ax = axes[idx]
        layout_df = df[df["layout"] == layout]

        # Color by policy type
        policy_colors = {
            "random": "gray",
            "ppo_5k": "lightblue",
            "ppo_50k": "blue",
            "ppo_200k": "darkblue",
        }

        for policy_type, color in policy_colors.items():
            policy_data = layout_df[layout_df["policy_type"] == policy_type]
            if len(policy_data) > 0:
                ax.scatter(
                    policy_data["or_index"],
                    policy_data["coordination_success"],
                    label=policy_type,
                    color=color,
                    alpha=0.6,
                    s=50,
                    edgecolors='white',
                    linewidth=0.5
                )

        # Compute correlation
        r, p = pearsonr(layout_df["or_index"], layout_df["coordination_success"])

        # Add best-fit line
        z = np.polyfit(layout_df["or_index"], layout_df["coordination_success"], 1)
        p_func = np.poly1d(z)
        x_line = np.linspace(layout_df["or_index"].min(), layout_df["or_index"].max(), 100)
        ax.plot(x_line, p_func(x_line), "r--", alpha=0.5, linewidth=2)

        # Formatting
        ax.set_xlabel("O/R Index", fontsize=13)
        ax.set_ylabel("Coordination Success", fontsize=13)
        ax.set_title(
            f"{title}\n$r = {r:.3f}${'***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''}, $n = {len(layout_df)}$",
            fontsize=14,
            fontweight='bold'
        )
        ax.legend(loc='best', fontsize=10)
        ax.grid(alpha=0.3, linestyle='--')

    plt.tight_layout()

    # Save figure
    output_path = Path("../../figures/overcooked/figure_overcooked_scatter.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved scatter plot: {output_path}")

    return fig


def plot_training_evolution(df):
    """Generate training evolution plot (O/R vs timesteps)"""

    fig, ax = plt.subplots(figsize=(10, 6))

    policy_order = ["random", "ppo_5k", "ppo_50k", "ppo_200k"]
    timesteps = [0, 5000, 50000, 200000]

    layouts = ["cramped_room", "asymmetric_advantages"]
    layout_styles = {
        "cramped_room": {"marker": 'o', "linestyle": '-'},
        "asymmetric_advantages": {"marker": 's', "linestyle": '--'},
    }

    for layout in layouts:
        or_means = []
        or_stds = []
        success_means = []

        for policy_type in policy_order:
            policy_data = df[(df["layout"] == layout) & (df["policy_type"] == policy_type)]

            if len(policy_data) > 0:
                or_means.append(policy_data["or_index"].mean())
                or_stds.append(policy_data["or_index"].std())
                success_means.append(policy_data["coordination_success"].mean())
            else:
                or_means.append(np.nan)
                or_stds.append(np.nan)
                success_means.append(np.nan)

        # Plot O/R evolution
        ax.errorbar(
            timesteps, or_means, yerr=or_stds,
            label=f"{layout} (O/R)",
            marker=layout_styles[layout]["marker"],
            linestyle=layout_styles[layout]["linestyle"],
            linewidth=2,
            capsize=5,
            alpha=0.8
        )

    # Formatting
    ax.set_xlabel("Training Timesteps", fontsize=13)
    ax.set_ylabel("O/R Index", fontsize=13)
    ax.set_title("O/R Index Evolution During Training", fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=11)
    ax.grid(alpha=0.3, linestyle='--')
    ax.set_xscale('symlog')  # Use symlog for better visualization of 0

    plt.tight_layout()

    # Save figure
    output_path = Path("../../figures/overcooked/figure_overcooked_evolution.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved evolution plot: {output_path}")

    return fig


def generate_latex_table(df):
    """Generate LaTeX table for paper"""

    print("\n" + "="*60)
    print("LaTeX Table for Paper")
    print("="*60)

    print("\n\\begin{center}")
    print("\\begin{tabular}{lccc}")
    print("\\toprule")
    print("\\textbf{Layout} & \\textbf{r} & \\textbf{p-value} & \\textbf{n} \\\\")
    print("\\midrule")

    for layout in df["layout"].unique():
        layout_df = df[df["layout"] == layout]
        r, p = pearsonr(layout_df["or_index"], layout_df["coordination_success"])

        # Format layout name
        layout_name = layout.replace("_", " ").title()

        # Format p-value
        if p < 0.001:
            p_str = "$<0.001$"
        else:
            p_str = f"${p:.3f}$"

        print(f"{layout_name} & ${r:.2f}$ & {p_str} & {len(layout_df)} \\\\")

    # Overall
    overall_r, overall_p = pearsonr(df["or_index"], df["coordination_success"])
    if overall_p < 0.001:
        overall_p_str = "$<0.001$"
    else:
        overall_p_str = f"${overall_p:.3f}$"

    print("\\midrule")
    print(f"\\textbf{{Combined}} & $\\mathbf{{{overall_r:.2f}}}$ & {overall_p_str} & {len(df)} \\\\")
    print("\\bottomrule")
    print("\\end{tabular}")
    print("\\end{center}")


def main():
    """Run complete analysis pipeline"""

    # Analyze all trajectories
    df = analyze_all_trajectories()

    if df is None:
        return

    # Generate plots
    print("\n" + "="*60)
    print("Generating Publication Figures")
    print("="*60)

    plot_scatter_by_layout(df)
    plot_training_evolution(df)

    # Generate LaTeX table
    generate_latex_table(df)

    print("\n" + "="*60)
    print("✓ All analysis complete!")
    print("="*60)
    print("\nGenerated files:")
    print("  - overcooked_summary.csv")
    print("  - figures/overcooked/figure_overcooked_scatter.png")
    print("  - figures/overcooked/figure_overcooked_evolution.png")
    print("\nNext step: Integrate results into paper Section 5.X")


if __name__ == "__main__":
    # Set plotting style
    sns.set_style("whitegrid")
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.size'] = 11

    main()
