#!/usr/bin/env python3
"""
4D vs 7D Framework Empirical Comparison

The framework reducibility analysis recommended Cluster-4D (K_R, K_I, K_M, K_H)
over Full-7D. This experiment validates this recommendation by testing:

1. Prediction accuracy: Does 4D predict outcomes as well as 7D?
2. Agent discrimination: Does 4D distinguish agent types as well as 7D?
3. Generalization: Does 4D generalize better to new environments?
4. Parsimony: Information content per dimension

Key question: Is the full 7D framework worth its complexity?
"""

import numpy as np
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from scipy.stats import pearsonr, ttest_ind
from collections import defaultdict


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


def extract_framework_features(result: Dict, framework: str) -> np.ndarray:
    """Extract features for a given framework."""
    if framework == "7D":
        return np.array([
            result["K_R"], result["K_A"], result["K_I"],
            result["K_P"], result["K_M"], result["K_S"], result["K_H"]
        ])
    elif framework == "4D":
        return np.array([
            result["K_R"], result["K_I"], result["K_M"], result["K_H"]
        ])
    elif framework == "3D":
        return np.array([
            result["K_R"], result["K_M"], result["K_H"]
        ])
    elif framework == "2D":  # Minimal baseline
        return np.array([result["K_R"], result["K_H"]])
    else:
        raise ValueError(f"Unknown framework: {framework}")


def linear_regression(X: np.ndarray, y: np.ndarray) -> Tuple[float, np.ndarray]:
    """Simple linear regression returning R² and coefficients."""
    X_bias = np.column_stack([np.ones(len(X)), X])
    try:
        coeffs = np.linalg.lstsq(X_bias, y, rcond=None)[0]
        y_pred = X_bias @ coeffs
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        return max(0, r_squared), coeffs
    except:
        return 0.0, np.zeros(X.shape[1] + 1)


def cross_validation_r2(X: np.ndarray, y: np.ndarray, n_folds: int = 5) -> Tuple[float, float]:
    """K-fold cross-validation returning mean and std of R²."""
    n = len(X)
    if n < n_folds * 2:
        return 0.0, 0.0

    indices = np.arange(n)
    np.random.shuffle(indices)
    fold_size = n // n_folds

    r2_scores = []
    for i in range(n_folds):
        test_idx = indices[i * fold_size:(i + 1) * fold_size]
        train_idx = np.concatenate([indices[:i * fold_size], indices[(i + 1) * fold_size:]])

        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        # Train
        X_train_bias = np.column_stack([np.ones(len(X_train)), X_train])
        try:
            coeffs = np.linalg.lstsq(X_train_bias, y_train, rcond=None)[0]

            # Test
            X_test_bias = np.column_stack([np.ones(len(X_test)), X_test])
            y_pred = X_test_bias @ coeffs

            ss_res = np.sum((y_test - y_pred) ** 2)
            ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            r2_scores.append(max(0, r2))
        except:
            r2_scores.append(0.0)

    return float(np.mean(r2_scores)), float(np.std(r2_scores))


def compute_agent_discrimination(results: List[Dict], framework: str) -> Dict:
    """Compute how well a framework discriminates agent types."""
    # Group by agent type
    type_features = defaultdict(list)
    for r in results:
        features = extract_framework_features(r, framework)
        type_features[r["type"]].append(features)

    if len(type_features) < 2:
        return {"mean_f_ratio": 0, "n_types": len(type_features)}

    # Compute F-ratio for each dimension
    all_features = np.array([f for features in type_features.values() for f in features])
    n_dims = all_features.shape[1]

    f_ratios = []
    for dim in range(n_dims):
        dim_values = {t: [f[dim] for f in features] for t, features in type_features.items()}

        # Between-group variance
        overall_mean = np.mean(all_features[:, dim])
        between_var = sum(
            len(vals) * (np.mean(vals) - overall_mean) ** 2
            for vals in dim_values.values()
        ) / len(all_features)

        # Within-group variance
        within_var = sum(
            np.var(vals) * len(vals)
            for vals in dim_values.values()
        ) / len(all_features)

        f_ratio = between_var / (within_var + 1e-10)
        f_ratios.append(f_ratio)

    return {
        "mean_f_ratio": float(np.mean(f_ratios)),
        "max_f_ratio": float(np.max(f_ratios)),
        "min_f_ratio": float(np.min(f_ratios)),
        "n_types": len(type_features),
        "per_dim_f_ratio": [float(f) for f in f_ratios],
    }


def compute_generalization(results: List[Dict], framework: str) -> Dict:
    """Test generalization by training on some environments, testing on others."""
    envs = list(set(r["environment"] for r in results))
    if len(envs) < 2:
        return {"generalization_r2": 0, "within_r2": 0}

    generalization_scores = []
    within_scores = []

    for test_env in envs:
        train_data = [r for r in results if r["environment"] != test_env]
        test_data = [r for r in results if r["environment"] == test_env]

        if len(train_data) < 10 or len(test_data) < 5:
            continue

        X_train = np.array([extract_framework_features(r, framework) for r in train_data])
        y_train = np.array([r["reward"] for r in train_data])
        X_test = np.array([extract_framework_features(r, framework) for r in test_data])
        y_test = np.array([r["reward"] for r in test_data])

        # Train on other environments
        X_train_bias = np.column_stack([np.ones(len(X_train)), X_train])
        try:
            coeffs = np.linalg.lstsq(X_train_bias, y_train, rcond=None)[0]

            # Test on held-out environment
            X_test_bias = np.column_stack([np.ones(len(X_test)), X_test])
            y_pred = X_test_bias @ coeffs

            ss_res = np.sum((y_test - y_pred) ** 2)
            ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
            r2_gen = max(0, 1 - (ss_res / ss_tot)) if ss_tot > 0 else 0
            generalization_scores.append(r2_gen)
        except:
            pass

        # Within-environment R² for comparison
        r2_within, _ = cross_validation_r2(X_test, y_test, n_folds=3)
        within_scores.append(r2_within)

    return {
        "generalization_r2": float(np.mean(generalization_scores)) if generalization_scores else 0,
        "generalization_std": float(np.std(generalization_scores)) if generalization_scores else 0,
        "within_r2": float(np.mean(within_scores)) if within_scores else 0,
    }


def compute_information_efficiency(results: List[Dict], framework: str) -> Dict:
    """Compute information efficiency (R² per dimension)."""
    X = np.array([extract_framework_features(r, framework) for r in results])
    y = np.array([r["reward"] for r in results])

    r2, _ = linear_regression(X, y)
    n_dims = X.shape[1]

    return {
        "r_squared": float(r2),
        "n_dimensions": n_dims,
        "r2_per_dimension": float(r2 / n_dims) if n_dims > 0 else 0,
    }


def run_4d_vs_7d_comparison():
    """Run comprehensive 4D vs 7D comparison."""
    print("=" * 70)
    print("4D vs 7D FRAMEWORK EMPIRICAL COMPARISON")
    print("=" * 70)
    print()

    results = load_all_results()
    print(f"Loaded {len(results)} agent results")
    print()

    frameworks = ["7D", "4D", "3D", "2D"]
    comparisons = {}

    # 1. Reward Prediction
    print("-" * 70)
    print("1. REWARD PREDICTION (Cross-validated R²)")
    print("-" * 70)
    print()

    for framework in frameworks:
        X = np.array([extract_framework_features(r, framework) for r in results])
        y = np.array([r["reward"] for r in results])

        r2_mean, r2_std = cross_validation_r2(X, y)
        r2_full, _ = linear_regression(X, y)

        comparisons[framework] = {
            "cv_r2_mean": r2_mean,
            "cv_r2_std": r2_std,
            "full_r2": r2_full,
        }

        print(f"{framework}: R² = {r2_mean:.3f} ± {r2_std:.3f} (full: {r2_full:.3f})")

    print()

    # 2. Agent Discrimination
    print("-" * 70)
    print("2. AGENT TYPE DISCRIMINATION (Mean F-ratio)")
    print("-" * 70)
    print()

    for framework in frameworks:
        disc = compute_agent_discrimination(results, framework)
        comparisons[framework]["discrimination"] = disc
        print(f"{framework}: Mean F = {disc['mean_f_ratio']:.3f}")

    print()

    # 3. Generalization
    print("-" * 70)
    print("3. CROSS-ENVIRONMENT GENERALIZATION")
    print("-" * 70)
    print()

    for framework in frameworks:
        gen = compute_generalization(results, framework)
        comparisons[framework]["generalization"] = gen
        print(f"{framework}: Generalization R² = {gen['generalization_r2']:.3f}")

    print()

    # 4. Information Efficiency
    print("-" * 70)
    print("4. INFORMATION EFFICIENCY (R² per dimension)")
    print("-" * 70)
    print()

    for framework in frameworks:
        eff = compute_information_efficiency(results, framework)
        comparisons[framework]["efficiency"] = eff
        print(f"{framework}: {eff['r2_per_dimension']:.4f} R²/dim ({eff['n_dimensions']} dims)")

    print()

    # 5. Summary Comparison
    print("-" * 70)
    print("SUMMARY COMPARISON")
    print("-" * 70)
    print()

    print(f"{'Framework':<10} {'CV R²':>10} {'Discrim':>10} {'General':>10} {'R²/dim':>10}")
    print("-" * 55)

    for framework in frameworks:
        c = comparisons[framework]
        print(f"{framework:<10} {c['cv_r2_mean']:>10.3f} "
              f"{c['discrimination']['mean_f_ratio']:>10.3f} "
              f"{c['generalization']['generalization_r2']:>10.3f} "
              f"{c['efficiency']['r2_per_dimension']:>10.4f}")

    # 6. Recommendation
    print()
    print("-" * 70)
    print("RECOMMENDATION")
    print("-" * 70)
    print()

    # Score frameworks
    scores = {}
    for framework in frameworks:
        c = comparisons[framework]
        # Weight: prediction (0.3), discrimination (0.3), generalization (0.2), efficiency (0.2)
        score = (
            c['cv_r2_mean'] * 0.3 +
            min(c['discrimination']['mean_f_ratio'] / 2, 1) * 0.3 +  # Normalize F
            c['generalization']['generalization_r2'] * 0.2 +
            c['efficiency']['r2_per_dimension'] * 10 * 0.2  # Scale efficiency
        )
        scores[framework] = score

    ranked = sorted(scores.items(), key=lambda x: -x[1])

    print("Frameworks ranked by overall quality:")
    for i, (framework, score) in enumerate(ranked, 1):
        print(f"  {i}. {framework}: score = {score:.3f}")

    best = ranked[0][0]
    print()

    if best == "4D":
        print("FINDING: 4D (K_R, K_I, K_M, K_H) is recommended")
        print("  - Removes redundant K_A, K_P (correlated with K_R, K_M)")
        print("  - Removes uninformative K_S (always 0 in single-agent)")
        print("  - Maintains prediction power while improving efficiency")
    elif best == "7D":
        print("FINDING: Full 7D framework remains best")
        print("  - Additional dimensions provide meaningful signal")
        print("  - Theoretical completeness justifies complexity")
    else:
        print(f"FINDING: {best} framework recommended")
        print("  - Consider trade-offs for specific use cases")

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "n_samples": len(results),
        "frameworks": {
            framework: {
                "cv_r2_mean": float(c["cv_r2_mean"]),
                "cv_r2_std": float(c["cv_r2_std"]),
                "mean_f_ratio": float(c["discrimination"]["mean_f_ratio"]),
                "generalization_r2": float(c["generalization"]["generalization_r2"]),
                "r2_per_dimension": float(c["efficiency"]["r2_per_dimension"]),
                "n_dimensions": int(c["efficiency"]["n_dimensions"]),
                "overall_score": float(scores[framework]),
            }
            for framework, c in comparisons.items()
        },
        "ranking": [{"framework": f, "score": float(s)} for f, s in ranked],
        "recommendation": best,
    }

    log_dir = Path("logs/framework_comparison")
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"4d_vs_7d_comparison_{timestamp}.json"

    with open(log_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {log_file}")

    return output


if __name__ == "__main__":
    run_4d_vs_7d_comparison()
