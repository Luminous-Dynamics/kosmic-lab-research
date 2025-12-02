"""
Regime Detection for Historical K(t).

Identifies coherence transitions using change-point detection algorithms.
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

try:
    import ruptures as rpt

    HAS_RUPTURES = True
except ImportError:
    HAS_RUPTURES = False
    print("Warning: ruptures not installed. Install with: pip install ruptures")


def detect_regime_changes(
    k_series: pd.Series, penalty: float = 3.0, model: str = "rbf", min_size: int = 3
) -> Tuple[pd.DataFrame, list]:
    """Detect breakpoints in K(t) using change-point detection.

    Args:
        k_series: Pandas Series of K values
        penalty: Penalty for adding breakpoints (higher = fewer breaks)
        model: 'rbf' (Gaussian kernel), 'l1' (absolute), 'l2' (squared)
        min_size: Minimum regime size in periods

    Returns:
        Tuple of (regimes_df, breakpoints)
    """
    if not HAS_RUPTURES:
        raise ImportError(
            "ruptures package required. Install with: pip install ruptures"
        )

    # Prepare data
    signal = k_series.values.reshape(-1, 1)
    years = k_series.index.values

    # Detect change points
    algo = rpt.Pelt(model=model, min_size=min_size, jump=1).fit(signal)
    breakpoints = algo.predict(pen=penalty)

    # Analyze regimes between breakpoints
    regimes = []
    start_idx = 0

    for i, end_idx in enumerate(breakpoints):
        if end_idx >= len(signal):
            end_idx = len(signal)

        regime_k = k_series.iloc[start_idx:end_idx]
        regime_years = years[start_idx:end_idx]

        if len(regime_k) == 0:
            continue

        # Compute regime statistics
        mean_k = float(regime_k.mean())
        std_k = float(regime_k.std())

        # Linear trend
        if len(regime_k) > 1:
            trend_coef = float(np.polyfit(range(len(regime_k)), regime_k.values, 1)[0])
            trend_direction = (
                "increasing"
                if trend_coef > 0.01
                else ("decreasing" if trend_coef < -0.01 else "stable")
            )
        else:
            trend_coef = 0.0
            trend_direction = "stable"

        # Volatility (normalized by mean)
        volatility = float(std_k / mean_k if mean_k != 0 else 0)

        regimes.append(
            {
                "regime_id": i + 1,
                "start_year": int(regime_years[0]),
                "end_year": int(regime_years[-1]),
                "duration": len(regime_years),
                "mean_K": mean_k,
                "std_K": std_k,
                "trend_slope": trend_coef,
                "trend_direction": trend_direction,
                "volatility": volatility,
                "min_K": float(regime_k.min()),
                "max_K": float(regime_k.max()),
                "range_K": float(regime_k.max() - regime_k.min()),
            }
        )

        start_idx = end_idx

    regimes_df = pd.DataFrame(regimes)

    return regimes_df, breakpoints


def plot_regime_analysis(
    k_series: pd.Series,
    regimes_df: pd.DataFrame,
    breakpoints: list,
    output_path: str | Path,
) -> None:
    """Visualize regime detection results.

    Args:
        k_series: Original K(t) series
        regimes_df: DataFrame from detect_regime_changes()
        breakpoints: List of breakpoint indices
        output_path: Path for output PNG
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    years = k_series.index.values

    # Plot 1: K(t) with regime boundaries
    ax = axes[0]
    ax.plot(years, k_series.values, "b-", linewidth=2, label="K(t)")

    # Mark breakpoints
    for bp_idx in breakpoints[:-1]:  # Last one is end of series
        if bp_idx < len(years):
            ax.axvline(
                years[bp_idx], color="red", linestyle="--", alpha=0.7, linewidth=1.5
            )

    # Shade regimes with alternating colors
    colors = [
        "lightblue",
        "lightcoral",
        "lightgreen",
        "lightyellow",
        "lightgray",
        "lightpink",
    ]
    for i, regime in regimes_df.iterrows():
        start = regime["start_year"]
        end = regime["end_year"]
        ax.axvspan(
            start,
            end,
            alpha=0.2,
            color=colors[int(i) % len(colors)],
            label=f'Regime {regime["regime_id"]}',
        )

    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("K-index", fontsize=12)
    ax.set_title(
        "Historical K(t) with Detected Regimes", fontsize=14, fontweight="bold"
    )
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best", fontsize=8, ncol=min(len(regimes_df), 4))

    # Plot 2: Regime characteristics
    ax = axes[1]
    x_pos = range(len(regimes_df))
    width = 0.25

    # Mean K
    ax.bar(
        [x - width for x in x_pos],
        regimes_df["mean_K"],
        width,
        label="Mean K",
        alpha=0.8,
        color="steelblue",
        edgecolor="black",
    )
    # Volatility (scaled for visibility)
    ax.bar(
        x_pos,
        regimes_df["volatility"] * 10,
        width,
        label="Volatility (×10)",
        alpha=0.8,
        color="coral",
        edgecolor="black",
    )
    # Trend slope (scaled)
    ax.bar(
        [x + width for x in x_pos],
        regimes_df["trend_slope"] * 100,
        width,
        label="Trend (×100)",
        alpha=0.8,
        color="lightgreen",
        edgecolor="black",
    )

    ax.set_xlabel("Regime", fontsize=12)
    ax.set_ylabel("Value", fontsize=12)
    ax.set_title("Regime Characteristics", fontsize=14, fontweight="bold")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(
        [
            f"R{int(r['regime_id'])}\n{int(r['start_year'])}-{int(r['end_year'])}"
            for _, r in regimes_df.iterrows()
        ],
        fontsize=9,
    )
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")
    ax.axhline(0, color="black", linewidth=0.5)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✅ Regime analysis plot saved to {output_path}")


def interpret_regimes(regimes_df: pd.DataFrame) -> str:
    """Generate narrative interpretation of regimes.

    Args:
        regimes_df: DataFrame from detect_regime_changes()

    Returns:
        Markdown-formatted interpretation
    """
    interpretations = []

    for _, regime in regimes_df.iterrows():
        # Classify regime
        if regime["mean_K"] > 1.2:
            coherence_level = "high"
        elif regime["mean_K"] > 0.8:
            coherence_level = "moderate"
        else:
            coherence_level = "low"

        if regime["volatility"] > 0.2:
            stability = "volatile"
        elif regime["volatility"] > 0.1:
            stability = "moderately stable"
        else:
            stability = "stable"

        interpretation = (
            f"**Regime {int(regime['regime_id'])}** ({int(regime['start_year'])}-{int(regime['end_year'])}, "
            f"{int(regime['duration'])} periods): "
            f"{coherence_level.capitalize()} coherence (K̄ = {regime['mean_K']:.2f}), "
            f"{stability}. "
            f"Trend: {regime['trend_direction']} "
            f"({regime['trend_slope']:.4f} per period). "
            f"Range: {regime['min_K']:.2f} to {regime['max_K']:.2f}."
        )

        interpretations.append(interpretation)

    return "\n\n".join(interpretations)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Regime detection for Historical K(t)")
    parser.add_argument(
        "--data",
        type=Path,
        default="logs/historical_k/k_t_series.csv",
        help="Path to K(t) series CSV",
    )
    parser.add_argument(
        "--output", type=Path, default="logs/regimes", help="Output directory"
    )
    parser.add_argument(
        "--penalty",
        type=float,
        default=3.0,
        help="Penalty parameter (higher = fewer regimes)",
    )
    parser.add_argument(
        "--model",
        choices=["rbf", "l1", "l2"],
        default="rbf",
        help="Change-point detection model",
    )

    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    # Load data
    df = pd.read_csv(args.data)
    k_series = pd.Series(df["K"].values, index=df["year"].values, name="K")

    # Detect regimes
    print(f"🔬 Detecting regimes with penalty={args.penalty}, model={args.model}...")
    regimes_df, breakpoints = detect_regime_changes(
        k_series, penalty=args.penalty, model=args.model
    )

    # Save results
    regimes_df.to_csv(args.output / "regimes.csv", index=False)
    print(f"✅ Found {len(regimes_df)} regimes")

    # Generate interpretation
    interpretation = interpret_regimes(regimes_df)
    (args.output / "regime_interpretation.md").write_text(interpretation)

    # Plot
    plot_regime_analysis(
        k_series, regimes_df, breakpoints, args.output / "regime_analysis.png"
    )

    print("\n🎉 Regime analysis complete!")
    print(f"📊 Results saved to {args.output}")
