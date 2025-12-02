#!/usr/bin/env python3
"""
Visualize Historical K(t) and Seven Harmonies Over Time.

Creates two publication-quality visualizations:
- Option A: Multi-line plot showing all harmonies and K-index together
- Option B: Small multiples showing each harmony in detail

Designed for Track C integration:
- Bootstrap confidence intervals (C-2) ✅
- External validation annotations (C-1) - ready for integration
- Sensitivity analysis overlays (C-3) - ready for integration
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Optional

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Set publication-quality style
sns.set_context("paper", font_scale=1.2)
sns.set_style("whitegrid")
plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["font.family"] = "serif"


def load_k_series(input_file: Path) -> pd.DataFrame:
    """Load K(t) time series with harmonies and bootstrap CI."""
    print(f"📥 Loading K(t) series from {input_file}")
    df = pd.read_csv(input_file)
    print(
        f"   ✅ Loaded {len(df)} records ({df['year'].min():.0f} to {df['year'].max():.0f})"
    )
    return df


def load_external_correlations(corr_file: Optional[Path]) -> Optional[Dict]:
    """Load Track C-1 external validation results if available."""
    if corr_file is None or not corr_file.exists():
        print("   ⚠️  No external correlation file provided (Track C-1 pending)")
        return None

    print(f"📥 Loading external correlations from {corr_file}")
    with open(corr_file) as f:
        correlations = json.load(f)
    print(f"   ✅ Loaded correlations for {len(correlations)} harmonies")
    return correlations


def plot_multi_line(
    df: pd.DataFrame,
    output_file: Path,
    correlations: Optional[Dict] = None,
    show_ci: bool = True,
):
    """
    Option A: Multi-line plot with all harmonies and K-index.

    Args:
        df: DataFrame with year, K, K_lower, K_upper, and seven harmonies
        output_file: Path to save figure
        correlations: Optional dict with external validation results
        show_ci: Whether to show bootstrap confidence intervals
    """
    print("\n📊 Creating Option A: Multi-line plot...")

    # Seven harmonies
    harmonies = [
        "resonant_coherence",
        "interconnection",
        "reciprocity",
        "play_entropy",
        "wisdom_accuracy",
        "flourishing",
        "evolutionary_progression",
    ]

    # Harmony display names
    harmony_names = {
        "resonant_coherence": "Resonant Coherence",
        "interconnection": "Universal Interconnection",
        "reciprocity": "Sacred Reciprocity",
        "play_entropy": "Infinite Play",
        "wisdom_accuracy": "Integral Wisdom",
        "flourishing": "Pan-Sentient Flourishing",
        "evolutionary_progression": "Evolutionary Progression",
    }

    # Create figure
    fig, ax = plt.subplots(figsize=(14, 8))

    # Color palette
    colors = sns.color_palette("husl", len(harmonies))
    k_color = "#2C3E50"  # Dark blue-grey for K-index

    # Plot each harmony
    for i, harmony in enumerate(harmonies):
        ax.plot(
            df["year"],
            df[harmony],
            label=harmony_names[harmony],
            color=colors[i],
            linewidth=1.5,
            alpha=0.7,
        )

    # Plot K-index (thicker, darker line)
    ax.plot(
        df["year"],
        df["K"],
        label="K-Index (composite)",
        color=k_color,
        linewidth=3.0,
        alpha=1.0,
        zorder=10,
    )

    # Add bootstrap confidence interval for K-index if available
    if show_ci and "K_lower" in df.columns and "K_upper" in df.columns:
        ax.fill_between(
            df["year"],
            df["K_lower"],
            df["K_upper"],
            color=k_color,
            alpha=0.15,
            label="K-Index 95% CI (bootstrap)",
            zorder=9,
        )
        print("   ✅ Added bootstrap confidence intervals (Track C-2)")

    # Formatting
    ax.set_xlabel("Year", fontsize=14, fontweight="bold")
    ax.set_ylabel("Normalized Score [0, 1]", fontsize=14, fontweight="bold")
    ax.set_title(
        "Historical K(t) and Seven Harmonies\n3000 BCE - 2020 CE",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )

    # X-axis: Show BCE/CE labels
    xticks = [-3000, -2000, -1000, 0, 1000, 2000]
    xticklabels = ["3000 BCE", "2000 BCE", "1000 BCE", "0", "1000 CE", "2000 CE"]
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)

    # Y-axis
    ax.set_ylim(-0.05, 1.05)
    ax.set_yticks(np.arange(0, 1.1, 0.2))

    # Grid
    ax.grid(True, alpha=0.3, linewidth=0.5)
    ax.set_axisbelow(True)

    # Legend (two columns to fit all)
    ax.legend(loc="upper left", frameon=True, framealpha=0.9, ncol=2, fontsize=10)

    # Add Track C-1 annotation if available
    if correlations:
        print("   ✅ Adding external correlation annotations (Track C-1)")
        # Add text box with key correlations
        corr_text = "External Validation (Track C-1):\n"
        for harmony, metrics in correlations.items():
            if "hdi" in metrics:
                corr_text += f"{harmony_names.get(harmony, harmony)}: r={metrics['hdi']:.2f} (HDI)\n"

        ax.text(
            0.98,
            0.02,
            corr_text.strip(),
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment="bottom",
            horizontalalignment="right",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        )

    # Highlight 2020 peak
    peak_year = df.loc[df["K"].idxmax(), "year"]
    peak_value = df["K"].max()
    ax.scatter([peak_year], [peak_value], color="red", s=100, zorder=15, marker="*")
    ax.annotate(
        f"Peak: {peak_year:.0f}\nK = {peak_value:.3f}",
        xy=(peak_year, peak_value),
        xytext=(peak_year - 500, peak_value - 0.15),
        fontsize=10,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="yellow", alpha=0.7),
        arrowprops=dict(
            arrowstyle="->", connectionstyle="arc3,rad=0", color="red", lw=2
        ),
    )

    plt.tight_layout()

    # Save
    output_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"   ✅ Saved to {output_file}")
    plt.close()


def plot_small_multiples(
    df: pd.DataFrame,
    output_file: Path,
    correlations: Optional[Dict] = None,
    show_ci: bool = True,
):
    """
    Option B: Small multiples showing each harmony in detail.

    Args:
        df: DataFrame with year, K, K_lower, K_upper, and seven harmonies
        output_file: Path to save figure
        correlations: Optional dict with external validation results
        show_ci: Whether to show bootstrap confidence intervals
    """
    print("\n📊 Creating Option B: Small multiples...")

    # Seven harmonies + K-index
    harmonies = [
        "K",  # K-index first
        "resonant_coherence",
        "interconnection",
        "reciprocity",
        "play_entropy",
        "wisdom_accuracy",
        "flourishing",
        "evolutionary_progression",
    ]

    # Display names
    harmony_names = {
        "K": "K-Index (Composite)",
        "resonant_coherence": "Resonant Coherence",
        "interconnection": "Universal Interconnection",
        "reciprocity": "Sacred Reciprocity",
        "play_entropy": "Infinite Play",
        "wisdom_accuracy": "Integral Wisdom",
        "flourishing": "Pan-Sentient Flourishing",
        "evolutionary_progression": "Evolutionary Progression",
    }

    # Create 4x2 grid
    fig, axes = plt.subplots(4, 2, figsize=(14, 16))
    axes = axes.flatten()

    # Color palette
    colors = sns.color_palette("husl", len(harmonies))

    for i, harmony in enumerate(harmonies):
        ax = axes[i]

        # Plot harmony
        ax.plot(df["year"], df[harmony], color=colors[i], linewidth=2.0, alpha=0.8)

        # Add CI for K-index
        if harmony == "K" and show_ci and "K_lower" in df.columns:
            ax.fill_between(
                df["year"],
                df["K_lower"],
                df["K_upper"],
                color=colors[i],
                alpha=0.2,
                label="95% CI",
            )
            ax.legend(loc="upper left", fontsize=8)

        # Formatting
        ax.set_title(harmony_names[harmony], fontsize=12, fontweight="bold")
        ax.set_ylim(-0.05, 1.05)
        ax.set_yticks([0, 0.5, 1.0])
        ax.grid(True, alpha=0.3)

        # X-axis labels only on bottom row
        if i >= 6:
            xticks = [-3000, 0, 2000]
            xticklabels = ["3000 BCE", "0", "2000 CE"]
            ax.set_xticks(xticks)
            ax.set_xticklabels(xticklabels, fontsize=9)
            ax.set_xlabel("Year", fontsize=10)
        else:
            ax.set_xticks([])

        # Y-axis label
        ax.set_ylabel("Score", fontsize=10)

        # Add correlation annotation if available
        if correlations and harmony != "K" and harmony in correlations:
            metrics = correlations[harmony]
            if "hdi" in metrics:
                corr_text = f"r={metrics['hdi']:.2f} (HDI)"
                ax.text(
                    0.98,
                    0.95,
                    corr_text,
                    transform=ax.transAxes,
                    fontsize=8,
                    verticalalignment="top",
                    horizontalalignment="right",
                    bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.5),
                )

        # Highlight peak for K-index
        if harmony == "K":
            peak_year = df.loc[df["K"].idxmax(), "year"]
            peak_value = df["K"].max()
            ax.scatter(
                [peak_year], [peak_value], color="red", s=80, zorder=10, marker="*"
            )
            ax.annotate(
                f"{peak_year:.0f}",
                xy=(peak_year, peak_value),
                xytext=(peak_year - 500, peak_value - 0.15),
                fontsize=9,
                bbox=dict(boxstyle="round", facecolor="yellow", alpha=0.6),
                arrowprops=dict(arrowstyle="->", color="red", lw=1.5),
            )

    # Overall title
    fig.suptitle(
        "Historical K(t) and Seven Harmonies: Detailed View\n3000 BCE - 2020 CE",
        fontsize=16,
        fontweight="bold",
        y=0.995,
    )

    plt.tight_layout(rect=[0, 0, 1, 0.99])

    # Save
    output_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"   ✅ Saved to {output_file}")
    plt.close()


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Visualize Historical K(t) and Seven Harmonies"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default="logs/historical_k_extended/k_t_series_5000y.csv",
        help="Input K(t) time series CSV",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default="figures/harmonies",
        help="Output directory for figures",
    )
    parser.add_argument(
        "--correlations",
        type=Path,
        default=None,
        help="Track C-1 external validation results JSON (optional)",
    )
    parser.add_argument(
        "--no-ci", action="store_true", help="Disable bootstrap confidence intervals"
    )
    parser.add_argument(
        "--option",
        choices=["A", "B", "both"],
        default="both",
        help="Which visualization option to create",
    )

    args = parser.parse_args()

    print("=" * 80)
    print("📊 Historical K(t) and Harmonies Visualization")
    print("=" * 80)
    print()

    # Load data
    df = load_k_series(args.input)

    # Load external correlations if available (Track C-1)
    correlations = load_external_correlations(args.correlations)

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Generate visualizations
    if args.option in ["A", "both"]:
        plot_multi_line(
            df,
            args.output_dir / "k_harmonies_multiline.png",
            correlations,
            show_ci=not args.no_ci,
        )

    if args.option in ["B", "both"]:
        plot_small_multiples(
            df,
            args.output_dir / "k_harmonies_small_multiples.png",
            correlations,
            show_ci=not args.no_ci,
        )

    print("\n" + "=" * 80)
    print("✅ Visualization complete!")
    print(f"📁 Figures saved to: {args.output_dir}")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    exit(main())
