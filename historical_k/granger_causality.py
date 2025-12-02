"""
Granger Causality Network Analysis for Historical K(t).

Analyzes directed causal relationships between harmonies using
Granger causality tests and constructs causal networks.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from scipy import stats

try:
    from statsmodels.tsa.stattools import grangercausalitytests

    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False
    warnings.warn(
        "statsmodels not available. Install for full Granger causality tests."
    )


HARMONY_NAMES = [
    "resonant_coherence",
    "interconnection",
    "reciprocity",
    "play_entropy",
    "wisdom_accuracy",
    "flourishing",
    "evolutionary_progression",
]


def compute_granger_causality_network(
    k_data: pd.DataFrame, max_lag: int = 5, significance: float = 0.05
) -> Tuple[pd.DataFrame, nx.DiGraph]:
    """Compute Granger causality network between harmonies.

    Args:
        k_data: DataFrame with year and harmony columns
        max_lag: Maximum lag to test (years)
        significance: P-value threshold for significance

    Returns:
        Tuple of (causality matrix DataFrame, NetworkX DiGraph)
    """
    print(f"🔗 Computing Granger causality network (max_lag={max_lag})...")

    if not HAS_STATSMODELS:
        print("⚠️  statsmodels not available. Using correlation-based approximation.")
        return _compute_correlation_network(k_data, max_lag, significance)

    # Extract harmony columns
    harmonies = [col for col in HARMONY_NAMES if col in k_data.columns]
    n_harmonies = len(harmonies)

    print(f"   Testing {n_harmonies} harmonies: {', '.join(harmonies)}")

    # Initialize causality matrix
    causality_matrix = pd.DataFrame(
        np.zeros((n_harmonies, n_harmonies)), index=harmonies, columns=harmonies
    )

    # Test all pairs
    total_tests = n_harmonies * (n_harmonies - 1)
    current_test = 0

    for i, cause in enumerate(harmonies):
        for j, effect in enumerate(harmonies):
            if i == j:
                continue  # Skip self-causation

            current_test += 1
            if current_test % 10 == 0:
                print(f"      Progress: {current_test}/{total_tests}")

            try:
                # Prepare data: [effect, cause]
                test_data = k_data[[effect, cause]].dropna()

                if len(test_data) < max_lag + 10:
                    # Not enough data
                    continue

                # Run Granger causality test
                gc_result = grangercausalitytests(
                    test_data, maxlag=max_lag, verbose=False
                )

                # Extract minimum p-value across all lags
                p_values = [
                    gc_result[lag][0]["ssr_ftest"][1]  # F-test p-value
                    for lag in range(1, max_lag + 1)
                ]
                min_p = min(p_values)
                best_lag = p_values.index(min_p) + 1

                # Store if significant
                if min_p < significance:
                    # Store -log10(p) for strength (higher = stronger causality)
                    causality_matrix.loc[cause, effect] = -np.log10(min_p)

            except Exception as e:
                # Skip pairs that fail (e.g., non-stationary)
                pass

    print(f"   ✅ Granger causality matrix computed")

    # Construct directed graph
    G = nx.DiGraph()

    # Add nodes
    for harmony in harmonies:
        G.add_node(harmony)

    # Add edges for significant causal relationships
    for cause in harmonies:
        for effect in harmonies:
            strength = causality_matrix.loc[cause, effect]
            if strength > 0:
                # Edge weight is causality strength
                G.add_edge(cause, effect, weight=strength)

    print(
        f"   ✅ Causal network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges"
    )

    return causality_matrix, G


def _compute_correlation_network(
    k_data: pd.DataFrame, max_lag: int, significance: float
) -> Tuple[pd.DataFrame, nx.DiGraph]:
    """Fallback: Compute lagged correlation network if statsmodels unavailable."""
    harmonies = [col for col in HARMONY_NAMES if col in k_data.columns]
    n_harmonies = len(harmonies)

    causality_matrix = pd.DataFrame(
        np.zeros((n_harmonies, n_harmonies)), index=harmonies, columns=harmonies
    )

    # Compute lagged correlations as proxy for causality
    for cause in harmonies:
        for effect in harmonies:
            if cause == effect:
                continue

            # Compute correlation at various lags
            max_corr = 0
            for lag in range(1, max_lag + 1):
                if len(k_data) <= lag:
                    break

                # Lagged correlation
                cause_series = k_data[cause].iloc[:-lag].values
                effect_series = k_data[effect].iloc[lag:].values

                if len(cause_series) > 0 and len(effect_series) > 0:
                    corr = np.corrcoef(cause_series, effect_series)[0, 1]
                    max_corr = max(max_corr, abs(corr))

            # Simple threshold for "causality"
            if max_corr > 0.3:  # Moderate correlation
                causality_matrix.loc[cause, effect] = (
                    max_corr * 3
                )  # Scale for visibility

    # Build graph
    G = nx.DiGraph()
    for harmony in harmonies:
        G.add_node(harmony)

    for cause in harmonies:
        for effect in harmonies:
            strength = causality_matrix.loc[cause, effect]
            if strength > 0:
                G.add_edge(cause, effect, weight=strength)

    return causality_matrix, G


def plot_causality_network(
    G: nx.DiGraph, output_path: str | Path, layout: str = "circular"
) -> None:
    """Visualize Granger causality network.

    Args:
        G: NetworkX DiGraph with causal relationships
        output_path: Where to save plot
        layout: 'circular', 'spring', or 'hierarchical'
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(14, 14))

    # Choose layout
    if layout == "circular":
        pos = nx.circular_layout(G)
    elif layout == "spring":
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    elif layout == "hierarchical":
        # Try to arrange by influence (in-degree)
        in_degrees = dict(G.in_degree())
        layers = {}
        for node, deg in in_degrees.items():
            layer = min(deg, 3)  # Max 3 layers
            if layer not in layers:
                layers[layer] = []
            layers[layer].append(node)

        pos = {}
        for layer, nodes in sorted(layers.items()):
            y = -layer
            for i, node in enumerate(nodes):
                x = (i - len(nodes) / 2) * 2
                pos[node] = (x, y)
    else:
        pos = nx.spring_layout(G)

    # Draw nodes
    node_colors = [
        "#3498db",
        "#e74c3c",
        "#2ecc71",
        "#f39c12",
        "#9b59b6",
        "#1abc9c",
        "#e67e22",
    ]
    nx.draw_networkx_nodes(
        G,
        pos,
        node_color=node_colors[: len(G.nodes())],
        node_size=3000,
        alpha=0.9,
        ax=ax,
    )

    # Draw edges with varying width based on causality strength
    edges = G.edges()
    weights = [G[u][v]["weight"] for u, v in edges]
    max_weight = max(weights) if weights else 1

    for (u, v), weight in zip(edges, weights):
        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=[(u, v)],
            width=1 + 5 * (weight / max_weight),
            alpha=0.6,
            edge_color="gray",
            arrows=True,
            arrowsize=20,
            arrowstyle="->",
            connectionstyle="arc3,rad=0.1",
            ax=ax,
        )

    # Draw labels
    labels = {node: node.replace("_", "\n") for node in G.nodes()}
    nx.draw_networkx_labels(
        G, pos, labels, font_size=10, font_weight="bold", font_color="white", ax=ax
    )

    # Add title and legend
    ax.set_title(
        "Granger Causality Network: Seven Harmonies",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )
    ax.text(
        0.02,
        0.98,
        f"{G.number_of_nodes()} Harmonies\n{G.number_of_edges()} Causal Links",
        transform=ax.transAxes,
        fontsize=12,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
    )

    ax.axis("off")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✅ Causality network plot saved to {output_path}")


def analyze_causal_pathways(
    G: nx.DiGraph, source: str = None, target: str = None
) -> Dict:
    """Analyze causal pathways in the network.

    Args:
        G: Causal network
        source: Source harmony (if None, analyze all)
        target: Target harmony (if None, analyze all)

    Returns:
        Dictionary with pathway analysis
    """
    print("🔍 Analyzing causal pathways...")

    results = {
        "direct_effects": {},
        "indirect_pathways": {},
        "most_influential": [],
        "most_influenced": [],
    }

    # Direct effects
    if source and target:
        if G.has_edge(source, target):
            results["direct_effects"][(source, target)] = G[source][target]["weight"]
    else:
        for u, v in G.edges():
            results["direct_effects"][(u, v)] = G[u][v]["weight"]

    # Find all simple paths (up to length 3)
    if source and target:
        node_pairs = [(source, target)]
    else:
        node_pairs = [(u, v) for u in G.nodes() for v in G.nodes() if u != v]

    for src, tgt in node_pairs:
        try:
            paths = list(nx.all_simple_paths(G, src, tgt, cutoff=3))
            if paths:
                results["indirect_pathways"][(src, tgt)] = len(paths)
        except nx.NetworkXNoPath:
            pass

    # Most influential (highest out-degree weighted by edge strength)
    influence_scores = {}
    for node in G.nodes():
        out_edges = G.out_edges(node, data="weight")
        influence = sum(weight for _, _, weight in out_edges)
        influence_scores[node] = influence

    results["most_influential"] = sorted(
        influence_scores.items(), key=lambda x: x[1], reverse=True
    )

    # Most influenced (highest in-degree weighted by edge strength)
    influenced_scores = {}
    for node in G.nodes():
        in_edges = G.in_edges(node, data="weight")
        influenced = sum(weight for _, _, weight in in_edges)
        influenced_scores[node] = influenced

    results["most_influenced"] = sorted(
        influenced_scores.items(), key=lambda x: x[1], reverse=True
    )

    print(f"   ✅ Found {len(results['direct_effects'])} direct causal links")
    print(
        f"   ✅ Found indirect pathways between {len(results['indirect_pathways'])} harmony pairs"
    )

    return results


def generate_causality_report(
    causality_matrix: pd.DataFrame,
    G: nx.DiGraph,
    pathway_analysis: Dict,
    output_path: str | Path,
) -> None:
    """Generate markdown report of Granger causality analysis."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    report = "# Granger Causality Network Analysis\n\n"
    report += "## Overview\n\n"
    report += f"- **Harmonies Analyzed**: {G.number_of_nodes()}\n"
    report += f"- **Significant Causal Links**: {G.number_of_edges()}\n"
    report += f"- **Network Density**: {nx.density(G):.3f}\n\n"

    # Most influential harmonies
    report += "## Most Influential Harmonies\n\n"
    report += "Harmonies that causally influence others (ranked by total causal strength):\n\n"
    report += "| Rank | Harmony | Causal Influence |\n"
    report += "|------|---------|------------------|\n"

    for i, (harmony, influence) in enumerate(
        pathway_analysis["most_influential"][:5], 1
    ):
        report += f"| {i} | {harmony} | {influence:.2f} |\n"

    report += "\n## Most Influenced Harmonies\n\n"
    report += "Harmonies that are causally influenced by others:\n\n"
    report += "| Rank | Harmony | Total Influence Received |\n"
    report += "|------|---------|-------------------------|\n"

    for i, (harmony, influenced) in enumerate(
        pathway_analysis["most_influenced"][:5], 1
    ):
        report += f"| {i} | {harmony} | {influenced:.2f} |\n"

    # Direct causal links
    report += "\n## Direct Causal Relationships\n\n"
    report += "| Cause | → | Effect | Strength |\n"
    report += "|-------|---|--------|----------|\n"

    sorted_links = sorted(
        pathway_analysis["direct_effects"].items(), key=lambda x: x[1], reverse=True
    )

    for (cause, effect), strength in sorted_links[:20]:
        report += f"| {cause} | → | {effect} | {strength:.2f} |\n"

    # Interpretation
    report += "\n## Interpretation\n\n"
    report += (
        "**Causality Strength**: Measured as -log10(p-value) from Granger F-test. "
    )
    report += "Higher values indicate stronger evidence of causal influence.\n\n"
    report += (
        "**Network Density**: Proportion of possible directed links that are present. "
    )
    report += "Higher density suggests more interconnected harmonies.\n\n"

    output_path.write_text(report)
    print(f"✅ Causality report saved to {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Granger causality analysis for Historical K(t)"
    )
    parser.add_argument(
        "--data", type=Path, required=True, help="K(t) data with harmonies"
    )
    parser.add_argument("--output", type=Path, default="logs/granger")
    parser.add_argument("--max-lag", type=int, default=5)
    parser.add_argument("--significance", type=float, default=0.05)
    parser.add_argument(
        "--layout", choices=["circular", "spring", "hierarchical"], default="circular"
    )

    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    # Load data
    df = pd.read_csv(args.data)
    print(f"📊 Loaded data: {df.shape}")

    # Compute Granger causality network
    causality_matrix, G = compute_granger_causality_network(
        df, max_lag=args.max_lag, significance=args.significance
    )

    # Save causality matrix
    causality_matrix.to_csv(args.output / "causality_matrix.csv")
    print(f"✅ Causality matrix saved to {args.output / 'causality_matrix.csv'}")

    # Plot network
    plot_causality_network(G, args.output / "causality_network.png", layout=args.layout)

    # Analyze pathways
    pathway_analysis = analyze_causal_pathways(G)

    # Generate report
    generate_causality_report(
        causality_matrix, G, pathway_analysis, args.output / "causality_report.md"
    )

    print(f"\n✅ Granger causality analysis complete!")
    print(f"📁 Results saved to: {args.output}")
