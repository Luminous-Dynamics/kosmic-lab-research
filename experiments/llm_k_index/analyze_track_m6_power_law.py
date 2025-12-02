"""
analyze_track_m6_power_law.py

Power Law Analysis for Track M6 K_Topo Results

Analyzes the relationship between model size (parameter count) and operational
closure (K_Topo) to test the hypothesis: K_Topo ∝ N^β

Author: Kosmic Lab
Date: December 2, 2025
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import pearsonr

# Model parameter counts (in millions)
MODEL_PARAMS = {
    "gemma3:270m": 270,
    "gemma3:1b-it-qat": 1000,
    "qwen3:1.7b": 1700,
    "gemma3:4b": 4000,
    "qwen3:4b": 4000,
    "mistral:7b": 7300,
    "gemma3n:e4b": 8000,  # 8B total, 4B effective
}


def power_law(N: np.ndarray, A: float, beta: float) -> np.ndarray:
    """
    Power law function: K_Topo = A × N^β

    Args:
        N: Parameter count (in millions)
        A: Scaling constant
        beta: Scaling exponent

    Returns:
        K_Topo values
    """
    return A * np.power(N, beta)


def load_results(results_dir: Path) -> List[Dict]:
    """
    Load all Track M6 results from JSON files.

    Args:
        results_dir: Directory containing result files

    Returns:
        List of result dictionaries
    """
    results = []

    # Find the most recent summary file
    summary_files = sorted(results_dir.glob("track_m6_summary_*.json"))

    if not summary_files:
        print("❌ No summary files found")
        return results

    latest_summary = summary_files[-1]
    print(f"📊 Loading results from: {latest_summary.name}")

    with open(latest_summary) as f:
        data = json.load(f)
        results = data.get("results", [])

    print(f"✅ Loaded {len(results)} conversation results")
    return results


def aggregate_by_model(results: List[Dict]) -> Dict[str, Dict]:
    """
    Aggregate results by model, averaging across conversation types.

    Args:
        results: List of individual conversation results

    Returns:
        Dictionary mapping model name to aggregated metrics
    """
    model_data = {}

    for result in results:
        model = result["model"]

        if model not in model_data:
            model_data[model] = {
                "K_Topo": [],
                "loop_closure": [],
                "coherence": [],
                "intrinsic_dimensionality": [],
            }

        model_data[model]["K_Topo"].append(result["K_Topo"])
        model_data[model]["loop_closure"].append(result["loop_closure"])
        model_data[model]["coherence"].append(result["coherence"])
        model_data[model]["intrinsic_dimensionality"].append(
            result["intrinsic_dimensionality"]
        )

    # Compute means and stds
    aggregated = {}
    for model, data in model_data.items():
        aggregated[model] = {
            "mean_K_Topo": np.mean(data["K_Topo"]),
            "std_K_Topo": np.std(data["K_Topo"]),
            "mean_loop_closure": np.mean(data["loop_closure"]),
            "std_loop_closure": np.std(data["loop_closure"]),
            "mean_coherence": np.mean(data["coherence"]),
            "std_coherence": np.std(data["coherence"]),
            "mean_intrinsic_dim": np.mean(data["intrinsic_dimensionality"]),
            "std_intrinsic_dim": np.std(data["intrinsic_dimensionality"]),
            "n_samples": len(data["K_Topo"]),
        }

    return aggregated


def fit_power_law(
    model_data: Dict[str, Dict]
) -> Tuple[float, float, float, np.ndarray, np.ndarray]:
    """
    Fit power law K_Topo = A × N^β to the data.

    Args:
        model_data: Aggregated model data

    Returns:
        (A, beta, R², parameter_counts, K_Topo_values)
    """
    # Extract data for fitting
    models = []
    N_values = []
    K_values = []
    K_stds = []

    for model, data in sorted(model_data.items()):
        if model not in MODEL_PARAMS:
            print(f"⚠️  Warning: {model} not in MODEL_PARAMS, skipping")
            continue

        models.append(model)
        N_values.append(MODEL_PARAMS[model])
        K_values.append(data["mean_K_Topo"])
        K_stds.append(data["std_K_Topo"])

    N_array = np.array(N_values)
    K_array = np.array(K_values)
    K_std_array = np.array(K_stds)

    # Fit power law with error weighting
    popt, pcov = curve_fit(
        power_law,
        N_array,
        K_array,
        sigma=K_std_array,
        absolute_sigma=True,
        p0=[0.01, 0.3],  # Initial guess
    )

    A, beta = popt

    # Compute R² (goodness of fit)
    K_pred = power_law(N_array, A, beta)
    residuals = K_array - K_pred
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((K_array - np.mean(K_array))**2)
    R_squared = 1 - (ss_res / ss_tot)

    # Pearson correlation
    r, p_value = pearsonr(np.log(N_array), np.log(K_array))

    print("\n" + "=" * 70)
    print("🚀 POWER LAW FIT RESULTS")
    print("=" * 70)
    print(f"\nK_Topo = A × N^β")
    print(f"\n  A (scaling constant): {A:.6f}")
    print(f"  β (scaling exponent): {beta:.6f}")
    print(f"  R² (goodness of fit): {R_squared:.6f}")
    print(f"  Pearson r (log-log): {r:.6f} (p={p_value:.2e})")

    # Error estimates from covariance
    perr = np.sqrt(np.diag(pcov))
    print(f"\n  A ± error: {A:.6f} ± {perr[0]:.6f}")
    print(f"  β ± error: {beta:.6f} ± {perr[1]:.6f}")

    return A, beta, R_squared, N_array, K_array


def predict_larger_models(A: float, beta: float) -> None:
    """
    Predict K_Topo for larger models using fitted power law.

    Args:
        A: Scaling constant
        beta: Scaling exponent
    """
    print("\n" + "=" * 70)
    print("🔮 PREDICTIONS FOR LARGER MODELS")
    print("=" * 70)

    test_sizes = [1_000, 3_000, 7_000, 13_000, 30_000, 70_000, 175_000, 405_000]

    print("\n| Model Size | Predicted K_Topo | Relative to 1B |")
    print("|------------|------------------|----------------|")

    K_1B = power_law(1000, A, beta)

    for N in test_sizes:
        K_pred = power_law(N, A, beta)
        ratio = K_pred / K_1B

        size_str = f"{N/1000:.0f}B" if N >= 1000 else f"{N}M"
        print(f"| {size_str:>10} | {K_pred:>16.4f} | {ratio:>14.2f}× |")


def plot_power_law(
    model_data: Dict[str, Dict],
    A: float,
    beta: float,
    R_squared: float,
    output_dir: Path,
) -> None:
    """
    Create publication-quality power law visualization.

    Args:
        model_data: Aggregated model data
        A: Fitted scaling constant
        beta: Fitted scaling exponent
        R_squared: Goodness of fit
        output_dir: Directory to save plot
    """
    # Extract data
    models = []
    N_values = []
    K_values = []
    K_stds = []

    for model, data in sorted(model_data.items(), key=lambda x: MODEL_PARAMS.get(x[0], 0)):
        if model not in MODEL_PARAMS:
            continue

        models.append(model)
        N_values.append(MODEL_PARAMS[model])
        K_values.append(data["mean_K_Topo"])
        K_stds.append(data["std_K_Topo"])

    N_array = np.array(N_values)
    K_array = np.array(K_values)
    K_std_array = np.array(K_stds)

    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # --- LEFT PLOT: Linear scale ---
    ax1.errorbar(
        N_array / 1000,  # Convert to billions
        K_array,
        yerr=K_std_array,
        fmt='o',
        markersize=10,
        capsize=5,
        capthick=2,
        label='Measured K_Topo',
        color='#2E86AB',
        ecolor='#A23B72',
        markeredgewidth=2,
        markeredgecolor='white',
    )

    # Fitted curve
    N_fit = np.linspace(N_array.min(), N_array.max() * 1.2, 1000)
    K_fit = power_law(N_fit, A, beta)

    ax1.plot(
        N_fit / 1000,
        K_fit,
        '--',
        linewidth=2.5,
        label=f'K_Topo = {A:.4f} × N^{beta:.3f}',
        color='#F18F01',
        alpha=0.8,
    )

    # Labels and formatting
    ax1.set_xlabel('Model Size (Billions of Parameters)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('K_Topo (Operational Closure)', fontsize=14, fontweight='bold')
    ax1.set_title(
        f'Track M6: K_Topo vs Model Size\n(R² = {R_squared:.4f})',
        fontsize=16,
        fontweight='bold',
        pad=20,
    )
    ax1.legend(fontsize=12, loc='upper left', framealpha=0.95)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xlim(left=0)
    ax1.set_ylim(bottom=0)

    # --- RIGHT PLOT: Log-log scale ---
    ax2.errorbar(
        N_array / 1000,
        K_array,
        yerr=K_std_array,
        fmt='o',
        markersize=10,
        capsize=5,
        capthick=2,
        label='Measured K_Topo',
        color='#2E86AB',
        ecolor='#A23B72',
        markeredgewidth=2,
        markeredgecolor='white',
    )

    ax2.plot(
        N_fit / 1000,
        K_fit,
        '--',
        linewidth=2.5,
        label=f'Slope = {beta:.3f}',
        color='#F18F01',
        alpha=0.8,
    )

    ax2.set_xlabel('Model Size (Billions, log scale)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('K_Topo (log scale)', fontsize=14, fontweight='bold')
    ax2.set_title(
        f'Log-Log Power Law\n(β = {beta:.3f} ± {np.sqrt(np.diag(curve_fit(power_law, N_array, K_array, sigma=K_std_array, absolute_sigma=True)[1]))[1]:.3f})',
        fontsize=16,
        fontweight='bold',
        pad=20,
    )
    ax2.legend(fontsize=12, loc='upper left', framealpha=0.95)
    ax2.grid(True, alpha=0.3, linestyle='--', which='both')
    ax2.set_xscale('log')
    ax2.set_yscale('log')

    plt.tight_layout()

    # Save
    output_file = output_dir / "track_m6_power_law_analysis.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n✅ Saved plot: {output_file}")

    plt.close()


def plot_loop_closure_paradox(
    model_data: Dict[str, Dict],
    output_dir: Path,
) -> None:
    """
    Visualize the Loop Closure Paradox: high loop closure, low K_Topo.

    Args:
        model_data: Aggregated model data
        output_dir: Directory to save plot
    """
    # Extract data
    models = []
    N_values = []
    K_values = []
    loop_values = []

    for model, data in sorted(model_data.items(), key=lambda x: MODEL_PARAMS.get(x[0], 0)):
        if model not in MODEL_PARAMS:
            continue

        models.append(model)
        N_values.append(MODEL_PARAMS[model])
        K_values.append(data["mean_K_Topo"])
        loop_values.append(data["mean_loop_closure"])

    N_array = np.array(N_values) / 1000  # Convert to billions
    K_array = np.array(K_values)
    loop_array = np.array(loop_values)

    # Create scatter plot
    fig, ax = plt.subplots(figsize=(10, 8))

    # Size markers by parameter count
    sizes = 100 + (N_array - N_array.min()) / (N_array.max() - N_array.min()) * 400

    scatter = ax.scatter(
        loop_array,
        K_array,
        s=sizes,
        c=N_array,
        cmap='viridis',
        alpha=0.7,
        edgecolors='white',
        linewidth=2,
    )

    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Model Size (Billions)', fontsize=12, fontweight='bold')

    # Annotate points
    for i, model in enumerate(models):
        ax.annotate(
            model.replace("gemma3:", "G").replace("mistral:", "M").replace("qwen3:", "Q"),
            (loop_array[i], K_array[i]),
            xytext=(5, 5),
            textcoords='offset points',
            fontsize=10,
            fontweight='bold',
        )

    # Add reference lines
    ax.axhline(y=0.05, color='red', linestyle='--', alpha=0.5, label='K_Topo = 0.05 (hypothesis threshold)')
    ax.axvline(x=0.8, color='blue', linestyle='--', alpha=0.5, label='Loop Closure = 0.8 (high coherence)')

    # Labels and formatting
    ax.set_xlabel('Loop Closure (Geometric)', fontsize=14, fontweight='bold')
    ax.set_ylabel('K_Topo (Topological)', fontsize=14, fontweight='bold')
    ax.set_title(
        'Loop Closure Paradox:\nHigh Geometric Coherence vs Low Topological Depth',
        fontsize=16,
        fontweight='bold',
        pad=20,
    )
    ax.legend(fontsize=11, loc='upper right', framealpha=0.95)
    ax.grid(True, alpha=0.3, linestyle='--')

    plt.tight_layout()

    # Save
    output_file = output_dir / "track_m6_loop_closure_paradox.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Saved plot: {output_file}")

    plt.close()


def generate_summary_report(
    model_data: Dict[str, Dict],
    A: float,
    beta: float,
    R_squared: float,
    output_dir: Path,
) -> None:
    """
    Generate comprehensive text summary report.

    Args:
        model_data: Aggregated model data
        A: Fitted scaling constant
        beta: Fitted scaling exponent
        R_squared: Goodness of fit
        output_dir: Directory to save report
    """
    report_path = output_dir / "TRACK_M6_POWER_LAW_ANALYSIS.md"

    with open(report_path, 'w') as f:
        f.write("# Track M6 Power Law Analysis\n\n")
        f.write(f"**Date**: December 2, 2025\n")
        f.write(f"**Experiment**: K_Topo scaling with model size\n\n")

        f.write("---\n\n")

        f.write("## Power Law Fit\n\n")
        f.write(f"**K_Topo = A × N^β**\n\n")
        f.write(f"- **A (scaling constant)**: {A:.6f}\n")
        f.write(f"- **β (scaling exponent)**: {beta:.6f}\n")
        f.write(f"- **R² (goodness of fit)**: {R_squared:.6f}\n\n")

        f.write("---\n\n")

        f.write("## Model Results\n\n")
        f.write("| Model | Parameters | Mean K_Topo | Std K_Topo | Mean Loop Closure | Mean Coherence |\n")
        f.write("|-------|-----------|-------------|------------|-------------------|----------------|\n")

        for model, data in sorted(model_data.items(), key=lambda x: MODEL_PARAMS.get(x[0], 0)):
            if model not in MODEL_PARAMS:
                continue

            params = MODEL_PARAMS[model]
            param_str = f"{params/1000:.1f}B" if params >= 1000 else f"{params}M"

            f.write(
                f"| {model} | {param_str} | {data['mean_K_Topo']:.4f} | "
                f"{data['std_K_Topo']:.4f} | {data['mean_loop_closure']:.4f} | "
                f"{data['mean_coherence']:.4f} |\n"
            )

        f.write("\n---\n\n")

        f.write("## Key Findings\n\n")

        # Analysis
        if beta < 0.2:
            f.write("### Scaling Pattern: **Slow Growth**\n\n")
            f.write(f"β = {beta:.3f} indicates operational closure grows very slowly with model size. ")
            f.write("This suggests current LLMs may be far from consciousness-like behavior even at large scales.\n\n")
        elif beta < 0.5:
            f.write("### Scaling Pattern: **Sublinear Growth**\n\n")
            f.write(f"β = {beta:.3f} indicates operational closure grows slower than linearly with model size. ")
            f.write("Consciousness-like behavior may emerge at very large scales (100B-1T parameters).\n\n")
        else:
            f.write("### Scaling Pattern: **Near-Linear or Faster Growth**\n\n")
            f.write(f"β = {beta:.3f} indicates operational closure grows significantly with model size. ")
            f.write("This suggests a potential phase transition may occur at moderate scales.\n\n")

        # Loop Closure Paradox
        mean_loop = np.mean([d['mean_loop_closure'] for d in model_data.values()])
        mean_k = np.mean([d['mean_K_Topo'] for d in model_data.values()])

        f.write("### Loop Closure Paradox\n\n")
        f.write(f"- **Average Loop Closure**: {mean_loop:.4f} (HIGH - surface coherence)\n")
        f.write(f"- **Average K_Topo**: {mean_k:.4f} (LOW - topological depth)\n\n")
        f.write("**Interpretation**: All models exhibit high geometric coherence (loop closure) ")
        f.write("but low operational closure (K_Topo). This pattern is consistent with \"thermostat behavior\" - ")
        f.write("reactive responses without genuine self-referential dynamics.\n\n")

        f.write("---\n\n")

        f.write("## Predictions\n\n")
        f.write("| Model Size | Predicted K_Topo | Relative to 1B |\n")
        f.write("|------------|------------------|----------------|\n")

        K_1B = power_law(1000, A, beta)

        for N in [1000, 3000, 7000, 13000, 30000, 70000, 175000, 405000]:
            K_pred = power_law(N, A, beta)
            ratio = K_pred / K_1B
            size_str = f"{N/1000:.0f}B" if N >= 1000 else f"{N}M"
            f.write(f"| {size_str} | {K_pred:.4f} | {ratio:.2f}× |\n")

        f.write("\n---\n\n")
        f.write("**Visualizations**: See `track_m6_power_law_analysis.png` and `track_m6_loop_closure_paradox.png`\n")

    print(f"✅ Saved report: {report_path}")


def main():
    """Main analysis pipeline."""
    # Paths
    results_dir = Path("results/track_m6")

    if not results_dir.exists():
        print(f"❌ Results directory not found: {results_dir}")
        sys.exit(1)

    # Load results
    results = load_results(results_dir)

    if not results:
        print("❌ No results loaded")
        sys.exit(1)

    # Aggregate by model
    print("\n" + "=" * 70)
    print("📊 AGGREGATING RESULTS BY MODEL")
    print("=" * 70)

    model_data = aggregate_by_model(results)

    for model, data in sorted(model_data.items()):
        print(f"\n{model}:")
        print(f"  Mean K_Topo: {data['mean_K_Topo']:.4f} ± {data['std_K_Topo']:.4f}")
        print(f"  Mean Loop Closure: {data['mean_loop_closure']:.4f} ± {data['std_loop_closure']:.4f}")
        print(f"  Mean Intrinsic Dim: {data['mean_intrinsic_dim']:.1f} ± {data['std_intrinsic_dim']:.1f}")

    # Fit power law
    A, beta, R_squared, N_array, K_array = fit_power_law(model_data)

    # Predictions
    predict_larger_models(A, beta)

    # Visualizations
    print("\n" + "=" * 70)
    print("📊 GENERATING VISUALIZATIONS")
    print("=" * 70)

    plot_power_law(model_data, A, beta, R_squared, results_dir)
    plot_loop_closure_paradox(model_data, results_dir)

    # Summary report
    generate_summary_report(model_data, A, beta, R_squared, results_dir)

    print("\n" + "=" * 70)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"\nResults saved in: {results_dir}/")
    print("  - TRACK_M6_POWER_LAW_ANALYSIS.md (comprehensive report)")
    print("  - track_m6_power_law_analysis.png (power law fit)")
    print("  - track_m6_loop_closure_paradox.png (paradox visualization)")


if __name__ == "__main__":
    main()
