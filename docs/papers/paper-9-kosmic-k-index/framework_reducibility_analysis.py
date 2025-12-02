#!/usr/bin/env python3
"""
Framework Reducibility Analysis

Given that only 3 PCA components explain 95% of variance,
should we reduce from 7D to a smaller framework?

This analysis:
1. Compares 7D vs reduced frameworks (4D, 3D)
2. Tests discriminative power of each framework
3. Evaluates interpretability vs parsimony tradeoff
4. Provides recommendations for paper framing
"""

import numpy as np
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from scipy.stats import pearsonr
try:
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    # Manual PCA implementation for when sklearn is not available
    class StandardScaler:
        def fit_transform(self, X):
            self.mean_ = np.mean(X, axis=0)
            self.std_ = np.std(X, axis=0) + 1e-10
            return (X - self.mean_) / self.std_

    class PCA:
        def __init__(self, n_components=None):
            self.n_components = n_components

        def fit(self, X):
            # SVD-based PCA
            n_samples, n_features = X.shape
            U, S, Vt = np.linalg.svd(X, full_matrices=False)

            # Explained variance
            explained_var = (S ** 2) / (n_samples - 1)
            total_var = np.sum(explained_var)
            self.explained_variance_ratio_ = explained_var / total_var
            self.components_ = Vt
            self.singular_values_ = S
            return self


def load_all_results() -> List[Dict]:
    """Load all Track L results."""
    log_dir = Path("logs/track_l")
    results = []

    for pattern in ["track_l_l6_*.json", "track_l_l4*.json", "track_l_l1_*.json"]:
        for log_file in sorted(log_dir.glob(pattern)):
            try:
                with open(log_file) as f:
                    data = json.load(f)
                if "agent_results" in data:
                    for agent in data["agent_results"]:
                        results.append({
                            "type": agent.get("agent_type", "unknown"),
                            "K_R": agent.get("K_R", 0),
                            "K_A": agent.get("K_A", 0),
                            "K_I": agent.get("K_I", 0),
                            "K_P": agent.get("K_P", 0),
                            "K_M": agent.get("K_M", 0),
                            "K_S": agent.get("K_S", 0),
                            "K_H": agent.get("K_H", 0),
                            "reward": agent.get("total_reward", 0),
                            "environment": data.get("environment", "unknown"),
                        })
            except Exception as e:
                print(f"Warning: Could not load {log_file}: {e}")

    return results


def analyze_pca_structure(results: List[Dict]) -> Dict:
    """Analyze PCA structure of K-vector dimensions."""
    # Exclude K_S (always 0 in single-agent tasks)
    dimensions = ["K_R", "K_A", "K_I", "K_P", "K_M", "K_H"]

    # Build data matrix
    X = []
    for r in results:
        row = [r.get(dim, 0) for dim in dimensions]
        if not any(np.isnan(row)):
            X.append(row)

    X = np.array(X)

    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # PCA
    pca = PCA()
    pca.fit(X_scaled)

    return {
        "n_samples": len(X),
        "n_dimensions": len(dimensions),
        "dimensions": dimensions,
        "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
        "cumulative_variance": np.cumsum(pca.explained_variance_ratio_).tolist(),
        "components": pca.components_.tolist(),
        "singular_values": pca.singular_values_.tolist(),
    }


def propose_reduced_frameworks(pca_results: Dict) -> List[Dict]:
    """Propose reduced frameworks based on PCA."""
    dimensions = pca_results["dimensions"]
    components = np.array(pca_results["components"])
    cumvar = pca_results["cumulative_variance"]

    frameworks = []

    # Framework 1: Principal components directly (statistical)
    n_95 = np.argmax(np.array(cumvar) >= 0.95) + 1

    frameworks.append({
        "name": f"PCA-{n_95}D",
        "type": "statistical",
        "n_dims": n_95,
        "variance_explained": cumvar[n_95-1],
        "interpretability": "Low - components are linear combinations",
        "description": f"First {n_95} principal components",
    })

    # Framework 2: Select representative dimensions (interpretable)
    # Based on correlation analysis: K_M is independent, others cluster
    # Choose one from each cluster + K_M

    frameworks.append({
        "name": "Cluster-4D",
        "type": "interpretable",
        "dimensions": ["K_R", "K_I", "K_M", "K_H"],
        "n_dims": 4,
        "rationale": {
            "K_R": "Representative of behavioral cluster (K_R, K_A)",
            "K_I": "Representative of model quality cluster (K_I, K_P)",
            "K_M": "Uniquely independent (memory)",
            "K_H": "Normative alignment (distinct purpose)",
        },
        "interpretability": "High - each dimension has clear meaning",
    })

    # Framework 3: Minimal interpretable (3D)
    frameworks.append({
        "name": "Minimal-3D",
        "type": "interpretable",
        "dimensions": ["K_R", "K_M", "K_H"],
        "n_dims": 3,
        "rationale": {
            "K_R": "Behavioral responsiveness",
            "K_M": "Temporal memory (independent)",
            "K_H": "Normative alignment",
        },
        "interpretability": "Very High - core distinctions only",
    })

    # Framework 4: Full 7D
    frameworks.append({
        "name": "Full-7D",
        "type": "theoretical",
        "dimensions": ["K_R", "K_A", "K_I", "K_P", "K_M", "K_S", "K_H"],
        "n_dims": 7,
        "rationale": {
            "K_R": "Reactivity (Spinoza)",
            "K_A": "Agency (Autopoiesis)",
            "K_I": "Integration (IIT)",
            "K_P": "Prediction (FEP)",
            "K_M": "Memory (Whitehead)",
            "K_S": "Social (Margulis)",
            "K_H": "Harmonic (West)",
        },
        "interpretability": "High - each maps to theoretical pillar",
    })

    return frameworks


def evaluate_discriminative_power(results: List[Dict], framework: Dict) -> Dict:
    """Evaluate framework's ability to discriminate agent types."""
    if "dimensions" in framework:
        dims = framework["dimensions"]
    else:
        # For PCA framework, use first n components
        return {"note": "PCA framework evaluation requires separate handling"}

    # Extract data
    agent_types = set(r["type"] for r in results)

    # For each dimension, test if it differentiates agent types
    discrimination_scores = {}

    for dim in dims:
        # Get values for each agent type
        type_values = {}
        for agent_type in agent_types:
            values = [r[dim] for r in results if r["type"] == agent_type]
            if values:
                type_values[agent_type] = values

        if len(type_values) < 2:
            continue

        # Calculate discrimination: variance between types / variance within types
        overall_values = [v for vals in type_values.values() for v in vals]
        overall_mean = np.mean(overall_values)

        between_var = sum(
            len(vals) * (np.mean(vals) - overall_mean) ** 2
            for vals in type_values.values()
        ) / len(overall_values)

        within_var = sum(
            np.var(vals) * len(vals)
            for vals in type_values.values()
        ) / len(overall_values)

        f_ratio = between_var / (within_var + 1e-10)
        discrimination_scores[dim] = float(f_ratio)

    # Overall framework discrimination
    mean_discrimination = np.mean(list(discrimination_scores.values())) if discrimination_scores else 0

    return {
        "per_dimension": discrimination_scores,
        "mean_discrimination": mean_discrimination,
        "best_dimension": max(discrimination_scores.keys(), key=lambda x: discrimination_scores[x])
            if discrimination_scores else None,
    }


def evaluate_reward_prediction(results: List[Dict], framework: Dict) -> Dict:
    """Evaluate framework's ability to predict reward."""
    if "dimensions" not in framework:
        return {"note": "Requires explicit dimensions"}

    dims = framework["dimensions"]

    # Extract data
    X = []
    y = []
    for r in results:
        row = [r.get(dim, 0) for dim in dims]
        if not any(np.isnan(row)):
            X.append(row)
            y.append(r["reward"])

    X = np.array(X)
    y = np.array(y)

    if len(X) < 10:
        return {"error": "Insufficient data"}

    # Simple linear regression R²
    from numpy.linalg import lstsq

    # Add intercept
    X_with_intercept = np.column_stack([np.ones(len(X)), X])

    try:
        coeffs, residuals, rank, s = lstsq(X_with_intercept, y, rcond=None)
        y_pred = X_with_intercept @ coeffs

        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)

        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # Per-dimension correlations with reward
        dim_correlations = {}
        for i, dim in enumerate(dims):
            r, p = pearsonr(X[:, i], y)
            dim_correlations[dim] = {"r": float(r), "p": float(p)}

    except Exception as e:
        return {"error": str(e)}

    return {
        "r_squared": float(r_squared),
        "n_samples": len(X),
        "n_dimensions": len(dims),
        "dimension_correlations": dim_correlations,
    }


def run_framework_reducibility_analysis():
    """Run comprehensive framework reducibility analysis."""
    print("=" * 70)
    print("📊 FRAMEWORK REDUCIBILITY ANALYSIS")
    print("=" * 70)
    print()
    print("Evaluating 7D vs reduced frameworks (4D, 3D)")
    print()

    results = load_all_results()
    print(f"Loaded {len(results)} data points")
    print()

    # PCA analysis
    print("-" * 70)
    print("📈 PCA VARIANCE ANALYSIS")
    print("-" * 70)

    pca_results = analyze_pca_structure(results)

    print()
    print("Explained variance by component:")
    for i, (var, cumvar) in enumerate(zip(
        pca_results["explained_variance_ratio"],
        pca_results["cumulative_variance"]
    )):
        print(f"  PC{i+1}: {var*100:.1f}% (cumulative: {cumvar*100:.1f}%)")

    n_95 = np.argmax(np.array(pca_results["cumulative_variance"]) >= 0.95) + 1
    n_99 = np.argmax(np.array(pca_results["cumulative_variance"]) >= 0.99) + 1

    print()
    print(f"Components for 95% variance: {n_95}")
    print(f"Components for 99% variance: {n_99}")

    # Propose frameworks
    frameworks = propose_reduced_frameworks(pca_results)

    print()
    print("-" * 70)
    print("📋 PROPOSED FRAMEWORKS")
    print("-" * 70)

    for fw in frameworks:
        print(f"\n{fw['name']}:")
        print(f"  Type: {fw['type']}")
        print(f"  Dimensions: {fw['n_dims']}")
        if "dimensions" in fw:
            print(f"  Components: {fw['dimensions']}")
        if "interpretability" in fw:
            print(f"  Interpretability: {fw['interpretability']}")

    # Evaluate each framework
    print()
    print("-" * 70)
    print("📊 FRAMEWORK EVALUATION")
    print("-" * 70)

    evaluations = {}

    for fw in frameworks:
        if "dimensions" not in fw:
            continue

        print(f"\n{fw['name']}:")

        # Discriminative power
        disc = evaluate_discriminative_power(results, fw)
        print(f"  Discrimination (F-ratio):")
        if "per_dimension" in disc:
            for dim, score in sorted(disc["per_dimension"].items(), key=lambda x: -x[1]):
                print(f"    {dim}: {score:.3f}")
            print(f"  Mean discrimination: {disc['mean_discrimination']:.3f}")

        # Reward prediction
        pred = evaluate_reward_prediction(results, fw)
        if "r_squared" in pred:
            print(f"  Reward prediction R²: {pred['r_squared']:.3f}")

        evaluations[fw["name"]] = {
            "framework": fw,
            "discrimination": disc,
            "prediction": pred,
        }

    # Comparison summary
    print()
    print("-" * 70)
    print("📋 FRAMEWORK COMPARISON")
    print("-" * 70)
    print()

    print(f"{'Framework':<15} {'Dims':>6} {'Discrim':>10} {'R²':>8} {'Interpret':>12}")
    print("-" * 55)

    for fw in frameworks:
        if fw["name"] not in evaluations:
            continue

        eval_data = evaluations[fw["name"]]
        disc = eval_data["discrimination"].get("mean_discrimination", 0)
        r2 = eval_data["prediction"].get("r_squared", 0)
        interp = fw.get("interpretability", "?")[:12]

        print(f"{fw['name']:<15} {fw['n_dims']:>6} {disc:>10.3f} {r2:>8.3f} {interp:>12}")

    # Recommendations
    print()
    print("-" * 70)
    print("💡 RECOMMENDATIONS")
    print("-" * 70)
    print()

    # Score frameworks
    scores = {}
    for name, eval_data in evaluations.items():
        fw = eval_data["framework"]
        disc = eval_data["discrimination"].get("mean_discrimination", 0)
        r2 = eval_data["prediction"].get("r_squared", 0)

        # Weighted score: discrimination + prediction + interpretability bonus
        interp_bonus = {
            "High - each maps to theoretical pillar": 0.3,
            "High - each dimension has clear meaning": 0.3,
            "Very High - core distinctions only": 0.25,
            "Low - components are linear combinations": 0.0,
        }.get(fw.get("interpretability", ""), 0.1)

        parsimony_bonus = max(0, (7 - fw["n_dims"]) * 0.05)

        score = disc * 0.4 + r2 * 0.3 + interp_bonus + parsimony_bonus
        scores[name] = score

    ranked = sorted(scores.items(), key=lambda x: -x[1])

    print("Frameworks ranked by overall quality:")
    for i, (name, score) in enumerate(ranked, 1):
        print(f"  {i}. {name}: score = {score:.3f}")

    best = ranked[0][0]
    print()
    print(f"Recommendation: {best}")
    print()

    # Specific recommendations
    if best == "Full-7D":
        print("The 7D framework is recommended despite correlation because:")
        print("  1. Each dimension maps to a distinct theoretical pillar")
        print("  2. Correlation ≠ redundancy (conceptually distinct)")
        print("  3. K_M provides unique discriminative power")
        print("  4. Interpretability aids practical application")
    elif "4D" in best:
        print("The 4D framework balances parsimony and interpretability:")
        print("  1. Removes redundant dimensions (K_A, K_P)")
        print("  2. Maintains theoretical grounding")
        print("  3. K_M retained as uniquely independent")
    else:
        print("Consider tradeoffs between statistical parsimony and interpretability")

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "n_samples": len(results),
        "pca_analysis": {
            "explained_variance": [float(x) for x in pca_results["explained_variance_ratio"]],
            "cumulative_variance": [float(x) for x in pca_results["cumulative_variance"]],
            "n_components_95": int(n_95),
            "n_components_99": int(n_99),
        },
        "frameworks": [
            {
                "name": fw["name"],
                "n_dims": int(fw["n_dims"]),
                "dimensions": fw.get("dimensions", []),
                "interpretability": fw.get("interpretability", ""),
            }
            for fw in frameworks
        ],
        "evaluations": {
            name: {
                "mean_discrimination": data["discrimination"].get("mean_discrimination"),
                "r_squared": data["prediction"].get("r_squared"),
            }
            for name, data in evaluations.items()
        },
        "ranking": [{"framework": name, "score": score} for name, score in ranked],
        "recommendation": best,
    }

    log_dir = Path("logs/reducibility")
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"framework_reducibility_{timestamp}.json"

    with open(log_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n💾 Results saved → {log_file}")

    return output


if __name__ == "__main__":
    run_framework_reducibility_analysis()
