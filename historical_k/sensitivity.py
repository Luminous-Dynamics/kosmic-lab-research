"""
Sensitivity Analysis for Historical K(t).

Performs proxy ablation study to identify which variables most strongly
influence the K-index computation.
"""

from __future__ import annotations

import subprocess
from copy import deepcopy
from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml


def proxy_ablation_study(
    config_path: str | Path, output_dir: str | Path = "logs/sensitivity"
) -> pd.DataFrame:
    """Remove each proxy one at a time and measure impact on K(t).

    Args:
        config_path: Path to Historical K configuration YAML
        output_dir: Directory for output files

    Returns:
        DataFrame ranking proxies by importance (RMSE impact)
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load config
    config_path = Path(config_path)
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Compute baseline K (run compute_k if needed)
    baseline_path = Path("logs/historical_k/k_t_series.csv")
    if not baseline_path.exists():
        print("Computing baseline K(t)...")
        subprocess.run(
            ["python", "-m", "historical_k.compute_k", "--config", str(config_path)],
            check=True,
        )

    baseline_k = _load_k_series(baseline_path)

    results = {}
    total_proxies = sum(len(proxies) for proxies in config["proxies"].values())
    current = 0

    for harmony, proxies in config["proxies"].items():
        for proxy in proxies:
            current += 1
            print(
                f"[{current}/{total_proxies}] Testing ablation: {proxy} from {harmony}"
            )

            # Create modified config
            modified_config = deepcopy(config)
            modified_config["proxies"][harmony] = [p for p in proxies if p != proxy]

            if not modified_config["proxies"][harmony]:
                # Don't test if harmony would be empty
                results[proxy] = {
                    "harmony": harmony,
                    "rmse_impact": np.nan,
                    "max_deviation": np.nan,
                    "correlation_drop": np.nan,
                    "mean_change": np.nan,
                    "status": "skipped_empty_harmony",
                }
                continue

            # Save modified config
            temp_config_path = output_dir / f"config_ablate_{proxy}.yaml"
            with open(temp_config_path, "w") as f:
                yaml.dump(modified_config, f)

            # Recompute K with ablated proxy
            try:
                subprocess.run(
                    [
                        "python",
                        "-m",
                        "historical_k.compute_k",
                        "--config",
                        str(temp_config_path),
                    ],
                    check=True,
                    capture_output=True,
                )

                ablated_k = _load_k_series(baseline_path)

                # Measure impact
                diff = baseline_k - ablated_k
                rmse = np.sqrt((diff**2).mean())
                max_dev = abs(diff).max()
                corr = baseline_k.corr(ablated_k)
                mean_change = diff.mean()

                results[proxy] = {
                    "harmony": harmony,
                    "rmse_impact": rmse,
                    "max_deviation": max_dev,
                    "correlation_drop": 1 - corr,
                    "mean_change": mean_change,
                    "status": "success",
                }

                # Clean up temp config
                temp_config_path.unlink()

            except Exception as e:
                results[proxy] = {
                    "harmony": harmony,
                    "rmse_impact": np.nan,
                    "max_deviation": np.nan,
                    "correlation_drop": np.nan,
                    "mean_change": np.nan,
                    "status": f"error: {str(e)}",
                }

    # Convert to DataFrame
    results_df = pd.DataFrame(results).T
    results_df.index.name = "proxy"
    results_df = results_df.sort_values("rmse_impact", ascending=False)

    # Save results
    results_df.to_csv(output_dir / "ablation_results.csv")
    print(
        f"\n✅ Ablation study complete. Results saved to {output_dir / 'ablation_results.csv'}"
    )

    return results_df


def plot_ablation_results(results_df: pd.DataFrame, output_path: str | Path) -> None:
    """Visualize proxy importance from ablation study."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(20, 8))

    # Filter valid results
    valid = results_df[results_df["status"] == "success"].copy()

    if valid.empty:
        print("No valid results to plot")
        return

    # Color by harmony
    harmonies_unique = valid["harmony"].unique()
    color_map = {h: plt.cm.Set3(i % 12) for i, h in enumerate(harmonies_unique)}

    # Plot 1: RMSE impact
    ax = axes[0]
    valid_sorted = valid.sort_values("rmse_impact", ascending=True)
    colors_sorted = [color_map[h] for h in valid_sorted["harmony"]]

    y_pos = range(len(valid_sorted))
    ax.barh(
        y_pos,
        valid_sorted["rmse_impact"],
        color=colors_sorted,
        alpha=0.8,
        edgecolor="black",
    )
    ax.set_yticks(y_pos)
    ax.set_yticklabels(valid_sorted.index, fontsize=9)
    ax.set_xlabel("RMSE Impact", fontsize=12)
    ax.set_title("Proxy Importance (Ablation Study)", fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="x")

    # Plot 2: Max deviation
    ax = axes[1]
    valid_sorted = valid.sort_values("max_deviation", ascending=True)
    colors_sorted = [color_map[h] for h in valid_sorted["harmony"]]

    ax.barh(
        y_pos,
        valid_sorted["max_deviation"],
        color=colors_sorted,
        alpha=0.8,
        edgecolor="black",
    )
    ax.set_yticks(y_pos)
    ax.set_yticklabels(valid_sorted.index, fontsize=9)
    ax.set_xlabel("Max Deviation", fontsize=12)
    ax.set_title("Maximum K Impact", fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="x")

    # Plot 3: Correlation drop
    ax = axes[2]
    valid_sorted = valid.sort_values("correlation_drop", ascending=True)
    colors_sorted = [color_map[h] for h in valid_sorted["harmony"]]

    ax.barh(
        y_pos,
        valid_sorted["correlation_drop"],
        color=colors_sorted,
        alpha=0.8,
        edgecolor="black",
    )
    ax.set_yticks(y_pos)
    ax.set_yticklabels(valid_sorted.index, fontsize=9)
    ax.set_xlabel("Correlation Drop (1 - r)", fontsize=12)
    ax.set_title("Shape Change Impact", fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="x")

    # Add legend
    legend_elements = [
        plt.Rectangle((0, 0), 1, 1, fc=color_map[h], alpha=0.8, edgecolor="black")
        for h in harmonies_unique
    ]
    fig.legend(
        legend_elements,
        harmonies_unique,
        loc="upper center",
        ncol=len(harmonies_unique),
        fontsize=10,
        frameon=True,
    )

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✅ Ablation plot saved to {output_path}")


def summarize_top_proxies(results_df: pd.DataFrame, n: int = 10) -> str:
    """Generate markdown summary of top N most important proxies.

    Args:
        results_df: Results from proxy_ablation_study
        n: Number of top proxies to include

    Returns:
        Markdown-formatted summary string
    """
    valid = results_df[results_df["status"] == "success"].copy()

    if valid.empty:
        return "# Proxy Sensitivity Analysis\n\nNo valid results available.\n"

    top_n = valid.sort_values("rmse_impact", ascending=False).head(n)

    summary = f"# Top {n} Most Influential Proxies\n\n"
    summary += "Ranked by RMSE impact on K(t) when removed.\n\n"
    summary += (
        "| Rank | Proxy | Harmony | RMSE Impact | Max Deviation | Correlation Drop |\n"
    )
    summary += (
        "|------|-------|---------|-------------|---------------|------------------|\n"
    )

    for i, (proxy, row) in enumerate(top_n.iterrows(), 1):
        summary += f"| {i} | {proxy} | {row['harmony']} | "
        summary += f"{row['rmse_impact']:.4f} | {row['max_deviation']:.4f} | "
        summary += f"{row['correlation_drop']:.4f} |\n"

    summary += "\n## Interpretation\n\n"
    summary += f"- **RMSE Impact**: Average deviation in K(t) when proxy removed\n"
    summary += f"- **Max Deviation**: Largest single-year change in K(t)\n"
    summary += f"- **Correlation Drop**: How much K(t) shape changes (0=no change, 1=complete change)\n\n"

    # Harmony-level summary
    summary += "## Impact by Harmony\n\n"
    harmony_impacts = valid.groupby("harmony")["rmse_impact"].agg(
        ["mean", "max", "count"]
    )
    harmony_impacts = harmony_impacts.sort_values("mean", ascending=False)

    for harmony, row_data in harmony_impacts.iterrows():
        summary += f"- **{harmony}**: "
        summary += f"{row_data['count']} proxies, "
        summary += f"mean impact {row_data['mean']:.4f}, "
        summary += f"max impact {row_data['max']:.4f}\n"

    return summary


def _load_k_series(path: str | Path) -> pd.Series:
    """Helper to load K series from CSV."""
    df = pd.read_csv(path)
    return pd.Series(df["K"].values, index=df["year"].values, name="K")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Historical K(t) sensitivity analysis")
    parser.add_argument("--config", type=Path, default="historical_k/k_config.yaml")
    parser.add_argument("--output", type=Path, default="logs/sensitivity")
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()

    results = proxy_ablation_study(args.config, args.output)
    if args.plot:
        plot_ablation_results(results, args.output / "ablation_analysis.png")
    print("\n🎉 Sensitivity analysis complete!")
