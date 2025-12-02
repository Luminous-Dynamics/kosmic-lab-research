"""
Bayesian Hierarchical Modeling for Historical K(t).

Implements hierarchical Bayesian models for uncertainty quantification
across temporal epochs with proper uncertainty propagation.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

try:
    import arviz as az
    import pymc as pm

    HAS_PYMC = True
except ImportError:
    HAS_PYMC = False
    warnings.warn("PyMC not available. Using simplified Bayesian approximation.")


def fit_hierarchical_k_model(
    k_data: pd.DataFrame, epochs: List[Dict], n_samples: int = 2000, n_tune: int = 1000
) -> Dict:
    """Fit hierarchical Bayesian model to K(t) data.

    Args:
        k_data: DataFrame with year, K, and harmonies
        epochs: List of epoch dicts with 'name', 'start', 'end'
        n_samples: Number of MCMC samples
        n_tune: Number of tuning steps

    Returns:
        Dict with posterior samples and diagnostics
    """
    print(f"🔬 Fitting hierarchical Bayesian model...")
    print(f"   Epochs: {len(epochs)}")
    print(f"   MCMC: {n_samples} samples, {n_tune} tuning steps")

    if not HAS_PYMC:
        print("⚠️  PyMC not available. Using normal approximation.")
        return _fit_normal_approximation(k_data, epochs)

    # Assign each data point to an epoch
    k_data = k_data.copy()
    k_data["epoch_id"] = 0

    for i, epoch in enumerate(epochs):
        mask = (k_data["year"] >= epoch["start"]) & (k_data["year"] <= epoch["end"])
        k_data.loc[mask, "epoch_id"] = i

    # Extract data
    K_obs = k_data["K"].values
    epoch_ids = k_data["epoch_id"].values.astype(int)
    n_epochs = len(epochs)

    print(f"   Building PyMC model...")

    with pm.Model() as model:
        # Hyperpriors (global parameters)
        mu_global = pm.Normal("mu_global", mu=0.5, sigma=0.2)
        sigma_global = pm.HalfNormal("sigma_global", sigma=0.1)

        # Epoch-level parameters (hierarchical)
        mu_epoch = pm.Normal(
            "mu_epoch", mu=mu_global, sigma=sigma_global, shape=n_epochs
        )
        sigma_epoch = pm.HalfNormal("sigma_epoch", sigma=0.05, shape=n_epochs)

        # Likelihood
        K_pred = mu_epoch[epoch_ids]
        sigma_pred = sigma_epoch[epoch_ids]

        K_likelihood = pm.Normal("K_obs", mu=K_pred, sigma=sigma_pred, observed=K_obs)

        # Sample posterior
        print(f"   Sampling posterior...")
        trace = pm.sample(
            n_samples,
            tune=n_tune,
            return_inferencedata=True,
            progressbar=False,
            random_seed=42,
        )

    print(f"   ✅ Sampling complete")

    # Extract results
    results = {
        "trace": trace,
        "model": model,
        "epoch_means": {},
        "epoch_stds": {},
        "global_mean": float(trace.posterior["mu_global"].mean()),
        "global_std": float(trace.posterior["sigma_global"].mean()),
    }

    for i, epoch in enumerate(epochs):
        results["epoch_means"][epoch["name"]] = float(
            trace.posterior["mu_epoch"][:, :, i].mean()
        )
        results["epoch_stds"][epoch["name"]] = float(
            trace.posterior["sigma_epoch"][:, :, i].mean()
        )

    print(f"   ✅ Hierarchical model fit complete")

    return results


def _fit_normal_approximation(k_data: pd.DataFrame, epochs: List[Dict]) -> Dict:
    """Simplified Bayesian approximation using normal distributions."""
    results = {
        "epoch_means": {},
        "epoch_stds": {},
        "global_mean": k_data["K"].mean(),
        "global_std": k_data["K"].std(),
    }

    for epoch in epochs:
        mask = (k_data["year"] >= epoch["start"]) & (k_data["year"] <= epoch["end"])
        epoch_data = k_data.loc[mask, "K"]

        if len(epoch_data) > 0:
            results["epoch_means"][epoch["name"]] = epoch_data.mean()
            results["epoch_stds"][epoch["name"]] = epoch_data.std()
        else:
            results["epoch_means"][epoch["name"]] = results["global_mean"]
            results["epoch_stds"][epoch["name"]] = results["global_std"]

    return results


def compute_posterior_predictions(
    model_results: Dict, years: np.ndarray, epochs: List[Dict], n_samples: int = 1000
) -> pd.DataFrame:
    """Generate posterior predictive samples.

    Args:
        model_results: Results from fit_hierarchical_k_model
        years: Years to predict
        epochs: Epoch definitions
        n_samples: Number of posterior samples

    Returns:
        DataFrame with predictive samples
    """
    print(f"📊 Computing posterior predictions for {len(years)} years...")

    predictions = pd.DataFrame({"year": years})

    if "trace" in model_results and HAS_PYMC:
        # Use PyMC trace
        trace = model_results["trace"]
        epoch_means = trace.posterior["mu_epoch"].values
        epoch_stds = trace.posterior["sigma_epoch"].values

        # Flatten chains
        epoch_means_flat = epoch_means.reshape(-1, epoch_means.shape[-1])
        epoch_stds_flat = epoch_stds.reshape(-1, epoch_stds.shape[-1])

        # Random sample indices
        sample_indices = np.random.choice(len(epoch_means_flat), size=n_samples)

        pred_samples = np.zeros((len(years), n_samples))

        for i, year in enumerate(years):
            # Find epoch for this year
            epoch_id = 0
            for j, epoch in enumerate(epochs):
                if epoch["start"] <= year <= epoch["end"]:
                    epoch_id = j
                    break

            # Sample from posterior
            for s, idx in enumerate(sample_indices):
                mu = epoch_means_flat[idx, epoch_id]
                sigma = epoch_stds_flat[idx, epoch_id]
                pred_samples[i, s] = np.random.normal(mu, sigma)

    else:
        # Use normal approximation
        pred_samples = np.zeros((len(years), n_samples))

        for i, year in enumerate(years):
            # Find epoch
            epoch_name = "modern"  # Default
            for epoch in epochs:
                if epoch["start"] <= year <= epoch["end"]:
                    epoch_name = epoch["name"]
                    break

            mu = model_results["epoch_means"][epoch_name]
            sigma = model_results["epoch_stds"][epoch_name]

            pred_samples[i, :] = np.random.normal(mu, sigma, size=n_samples)

    # Compute summary statistics
    predictions["mean"] = pred_samples.mean(axis=1)
    predictions["std"] = pred_samples.std(axis=1)
    predictions["lower_95"] = np.percentile(pred_samples, 2.5, axis=1)
    predictions["upper_95"] = np.percentile(pred_samples, 97.5, axis=1)
    predictions["lower_50"] = np.percentile(pred_samples, 25, axis=1)
    predictions["upper_50"] = np.percentile(pred_samples, 75, axis=1)

    print(f"   ✅ Posterior predictions computed")

    return predictions


def plot_hierarchical_results(
    k_data: pd.DataFrame,
    predictions: pd.DataFrame,
    epochs: List[Dict],
    output_path: str | Path,
) -> None:
    """Visualize hierarchical Bayesian model results."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(16, 8))

    # Plot observed data
    ax.plot(
        k_data["year"],
        k_data["K"],
        "o",
        color="black",
        alpha=0.5,
        markersize=3,
        label="Observed K(t)",
    )

    # Plot predictions
    ax.plot(
        predictions["year"],
        predictions["mean"],
        "-",
        color="#3498db",
        linewidth=2,
        label="Posterior Mean",
    )

    # 95% credible interval
    ax.fill_between(
        predictions["year"],
        predictions["lower_95"],
        predictions["upper_95"],
        color="#3498db",
        alpha=0.2,
        label="95% Credible Interval",
    )

    # 50% credible interval
    ax.fill_between(
        predictions["year"],
        predictions["lower_50"],
        predictions["upper_50"],
        color="#3498db",
        alpha=0.3,
        label="50% Credible Interval",
    )

    # Mark epochs
    epoch_colors = ["#f39c12", "#2ecc71", "#9b59b6", "#e74c3c"]
    for i, epoch in enumerate(epochs):
        color = epoch_colors[i % len(epoch_colors)]
        ax.axvspan(epoch["start"], epoch["end"], alpha=0.1, color=color)
        mid_year = (epoch["start"] + epoch["end"]) / 2
        ax.text(
            mid_year,
            ax.get_ylim()[1] * 0.95,
            epoch["name"],
            horizontalalignment="center",
            fontsize=10,
            fontweight="bold",
            bbox=dict(boxstyle="round", facecolor=color, alpha=0.5),
        )

    ax.set_xlabel("Year", fontsize=14, fontweight="bold")
    ax.set_ylabel("K-index", fontsize=14, fontweight="bold")
    ax.set_title(
        "Hierarchical Bayesian Model: K(t) with Epoch-Level Structure",
        fontsize=16,
        fontweight="bold",
    )
    ax.legend(loc="best", fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✅ Hierarchical results plot saved to {output_path}")


def generate_bayesian_report(
    model_results: Dict, epochs: List[Dict], output_path: str | Path
) -> None:
    """Generate markdown report of Bayesian analysis."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    report = "# Hierarchical Bayesian Model Analysis\n\n"
    report += "## Model Structure\n\n"
    report += "Three-level hierarchical model:\n\n"
    report += "1. **Global Level**: Overall mean and variance across all time\n"
    report += "2. **Epoch Level**: Era-specific parameters (ancient, medieval, modern, etc.)\n"
    report += "3. **Observation Level**: Individual year measurements\n\n"

    report += "## Global Parameters\n\n"
    report += f"- **Global Mean (μ_global)**: {model_results['global_mean']:.4f}\n"
    report += f"- **Global Std (σ_global)**: {model_results['global_std']:.4f}\n\n"

    report += "## Epoch-Level Parameters\n\n"
    report += "| Epoch | Posterior Mean (μ) | Posterior Std (σ) |\n"
    report += "|-------|-------------------|-------------------|\n"

    for epoch in epochs:
        name = epoch["name"]
        if name in model_results["epoch_means"]:
            mu = model_results["epoch_means"][name]
            sigma = model_results["epoch_stds"][name]
            report += f"| {name} | {mu:.4f} | {sigma:.4f} |\n"

    report += "\n## Interpretation\n\n"
    report += "**Posterior Mean**: Best estimate of K-index for each epoch\n\n"
    report += "**Posterior Std**: Uncertainty in K-index estimate\n\n"
    report += (
        "**Hierarchical Shrinkage**: Epoch estimates are pulled toward global mean, "
    )
    report += "providing regularization and reducing overfitting.\n\n"

    report += "## Model Benefits\n\n"
    report += "1. **Proper Uncertainty Quantification**: Credible intervals account for epoch-level variation\n"
    report += "2. **Borrowing Strength**: Data-sparse epochs benefit from global information\n"
    report += "3. **Interpretable Parameters**: Each epoch has meaningful mean/std\n"
    report += "4. **Flexible**: Can accommodate additional levels (e.g., region, civilization)\n\n"

    output_path.write_text(report)
    print(f"✅ Bayesian report saved to {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Hierarchical Bayesian modeling for K(t)"
    )
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, default="logs/bayesian")
    parser.add_argument("--samples", type=int, default=2000)
    parser.add_argument("--tune", type=int, default=1000)

    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    # Load data
    df = pd.read_csv(args.data)
    print(f"📊 Loaded data: {df.shape}")

    # Define epochs
    epochs = [
        {"name": "ancient", "start": -3000, "end": 500},
        {"name": "medieval", "start": 500, "end": 1500},
        {"name": "early_modern", "start": 1500, "end": 1800},
        {"name": "modern", "start": 1800, "end": 2020},
    ]

    # Fit model
    model_results = fit_hierarchical_k_model(df, epochs, args.samples, args.tune)

    # Generate predictions
    years = df["year"].values
    predictions = compute_posterior_predictions(model_results, years, epochs)

    # Save predictions
    predictions.to_csv(args.output / "posterior_predictions.csv", index=False)
    print(f"✅ Predictions saved to {args.output / 'posterior_predictions.csv'}")

    # Plot results
    plot_hierarchical_results(
        df, predictions, epochs, args.output / "hierarchical_model.png"
    )

    # Generate report
    generate_bayesian_report(model_results, epochs, args.output / "bayesian_report.md")

    print(f"\n✅ Hierarchical Bayesian analysis complete!")
    print(f"📁 Results saved to: {args.output}")
