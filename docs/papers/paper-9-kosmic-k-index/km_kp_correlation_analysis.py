#!/usr/bin/env python3
"""
K_M - K_P Correlation Analysis

The K_M architecture validation showed r=0.84 correlation between K_M and K_P.
This is concerning because they should measure different constructs:
- K_M: Temporal memory utilization
- K_P: World model prediction accuracy

This analysis investigates WHY they are correlated:
1. Do they have overlapping mathematical definitions?
2. Are they capturing the same underlying capability?
3. Can we modify K_M to be more independent?

Hypotheses:
H1: Both measure "model quality" - agents with good predictive models also use history
H2: K_M computation inadvertently includes prediction-like components
H3: The environments don't sufficiently separate temporal vs predictive demands
"""

import numpy as np
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
from scipy.stats import pearsonr, spearmanr


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


def analyze_km_kp_definitions():
    """Analyze the mathematical definitions of K_M and K_P."""
    print("-" * 70)
    print("1. MATHEMATICAL DEFINITION ANALYSIS")
    print("-" * 70)
    print()
    print("K_P Definition:")
    print("  K_P = 1 - NPE")
    print("  NPE = E[||O_{t+1} - Ô||²] / E[||O_{t+1} - Ō||²]")
    print("  → Measures prediction accuracy relative to baseline")
    print()
    print("K_M Definition:")
    print("  K_M = (L_markov - L_history) / (L_markov + ε)")
    print("  L_markov = MSE predicting a_t from o_t only")
    print("  L_history = MSE predicting a_t from o_{t-k:t}")
    print("  → Measures how much history improves action prediction")
    print()
    print("POTENTIAL OVERLAP:")
    print("  Both involve prediction tasks - K_P predicts observations,")
    print("  K_M's history model implicitly predicts better actions.")
    print("  If good action prediction requires good observation prediction,")
    print("  then K_M and K_P will correlate.")
    print()


def analyze_empirical_correlation(results: List[Dict]) -> Dict:
    """Analyze empirical K_M-K_P correlation patterns."""
    print("-" * 70)
    print("2. EMPIRICAL CORRELATION ANALYSIS")
    print("-" * 70)
    print()

    km_values = [r["K_M"] for r in results if r["K_M"] > 0 and r["K_P"] > 0]
    kp_values = [r["K_P"] for r in results if r["K_M"] > 0 and r["K_P"] > 0]

    if len(km_values) < 10:
        print("Insufficient data with non-zero K_M and K_P")
        return {}

    # Overall correlation
    r_pearson, p_pearson = pearsonr(km_values, kp_values)
    r_spearman, p_spearman = spearmanr(km_values, kp_values)

    print(f"Overall K_M-K_P correlation:")
    print(f"  Pearson r = {r_pearson:.3f} (p = {p_pearson:.6f})")
    print(f"  Spearman ρ = {r_spearman:.3f} (p = {p_spearman:.6f})")
    print()

    # By environment
    print("By Environment:")
    env_correlations = {}
    for env in set(r["environment"] for r in results):
        env_data = [r for r in results if r["environment"] == env
                   and r["K_M"] > 0 and r["K_P"] > 0]
        if len(env_data) >= 10:
            km_env = [r["K_M"] for r in env_data]
            kp_env = [r["K_P"] for r in env_data]
            r_env, p_env = pearsonr(km_env, kp_env)
            env_correlations[env] = {"r": r_env, "p": p_env, "n": len(env_data)}
            print(f"  {env}: r = {r_env:.3f} (n={len(env_data)})")

    print()

    # By agent type
    print("By Agent Type:")
    type_correlations = {}
    for agent_type in set(r["type"] for r in results):
        type_data = [r for r in results if r["type"] == agent_type
                    and r["K_M"] > 0 and r["K_P"] > 0]
        if len(type_data) >= 10:
            km_type = [r["K_M"] for r in type_data]
            kp_type = [r["K_P"] for r in type_data]
            r_type, p_type = pearsonr(km_type, kp_type)
            type_correlations[agent_type] = {"r": r_type, "p": p_type, "n": len(type_data)}
            print(f"  {agent_type}: r = {r_type:.3f} (n={len(type_data)})")

    return {
        "overall": {"pearson_r": r_pearson, "spearman_rho": r_spearman},
        "by_environment": env_correlations,
        "by_agent_type": type_correlations,
    }


def analyze_partial_correlations(results: List[Dict]) -> Dict:
    """Analyze partial correlations controlling for other dimensions."""
    print()
    print("-" * 70)
    print("3. PARTIAL CORRELATION ANALYSIS")
    print("-" * 70)
    print()
    print("Controlling for other dimensions to isolate K_M-K_P relationship:")
    print()

    # Get clean data
    clean_results = [r for r in results if r["K_M"] > 0 and r["K_P"] > 0]
    if len(clean_results) < 20:
        print("Insufficient data")
        return {}

    km = np.array([r["K_M"] for r in clean_results])
    kp = np.array([r["K_P"] for r in clean_results])
    kr = np.array([r["K_R"] for r in clean_results])
    ka = np.array([r["K_A"] for r in clean_results])
    ki = np.array([r["K_I"] for r in clean_results])
    kh = np.array([r["K_H"] for r in clean_results])

    # Simple partial correlation (controlling for one variable at a time)
    def partial_correlation(x, y, z):
        """Compute partial correlation between x and y controlling for z."""
        # Residualize x and y on z
        z_with_intercept = np.column_stack([np.ones_like(z), z])
        try:
            coef_x = np.linalg.lstsq(z_with_intercept, x, rcond=None)[0]
            coef_y = np.linalg.lstsq(z_with_intercept, y, rcond=None)[0]
            resid_x = x - z_with_intercept @ coef_x
            resid_y = y - z_with_intercept @ coef_y
            r, p = pearsonr(resid_x, resid_y)
            return r, p
        except:
            return np.nan, 1.0

    # Raw correlation
    r_raw, p_raw = pearsonr(km, kp)
    print(f"Raw K_M-K_P: r = {r_raw:.3f}")

    partial_results = {}

    # Control for each dimension
    controls = [("K_R", kr), ("K_A", ka), ("K_I", ki), ("K_H", kh)]
    for name, control in controls:
        r_partial, p_partial = partial_correlation(km, kp, control)
        partial_results[f"controlling_{name}"] = {"r": r_partial, "p": p_partial}
        print(f"Controlling for {name}: r = {r_partial:.3f}")

    # Control for all other dimensions
    all_controls = np.column_stack([kr, ka, ki, kh])
    r_all, p_all = partial_correlation(km, kp, all_controls)
    partial_results["controlling_all"] = {"r": r_all, "p": p_all}
    print(f"Controlling for all: r = {r_all:.3f}")
    print()

    # Interpretation
    if abs(r_all) < abs(r_raw) * 0.5:
        print("FINDING: Correlation substantially reduces when controlling for")
        print("         other dimensions → K_M-K_P relationship may be spurious,")
        print("         mediated by shared variance with other dimensions.")
    else:
        print("FINDING: Correlation persists when controlling for other dimensions")
        print("         → K_M and K_P share direct, not spurious, variance.")

    return partial_results


def propose_alternative_km() -> None:
    """Propose alternative K_M definitions that might be more independent."""
    print()
    print("-" * 70)
    print("4. ALTERNATIVE K_M DEFINITIONS")
    print("-" * 70)
    print()
    print("Current K_M measures: 'How much does history help predict actions?'")
    print()
    print("PROBLEM: Good predictive models (high K_P) might naturally use history")
    print("         to make better predictions, creating correlation.")
    print()
    print("Alternative definitions to consider:")
    print()
    print("Option A: Pure Memory Capacity")
    print("  K_M_capacity = accuracy on N-back task")
    print("  → Directly measures memory length, not prediction quality")
    print()
    print("Option B: History-Action Independence")
    print("  K_M_independent = I(A_t; O_{t-k:t-1} | O_t)")
    print("  → Mutual information between actions and past observations,")
    print("    conditioning on current observation")
    print("  → Measures how much past influences actions beyond current state")
    print()
    print("Option C: Temporal Autocorrelation")
    print("  K_M_autocorr = mean(|corr(A_t, A_{t-k})|) for k=1..K")
    print("  → Measures temporal smoothness of action sequences")
    print("  → Memory agents tend to have correlated actions over time")
    print()
    print("Option D: State Reconstruction")
    print("  K_M_reconstruct = accuracy of reconstructing O_{t-k} from h_t")
    print("  → If agent stores information, it should be reconstructable")
    print("  → More directly measures what's IN memory, not what's used")
    print()


def run_km_kp_analysis():
    """Run comprehensive K_M-K_P correlation analysis."""
    print("=" * 70)
    print("K_M - K_P CORRELATION ANALYSIS")
    print("=" * 70)
    print()
    print("Investigating why K_M and K_P are highly correlated (r=0.84)")
    print()

    # 1. Definition analysis
    analyze_km_kp_definitions()

    # 2. Load data
    results = load_all_results()
    print(f"Loaded {len(results)} agent results")
    print()

    # 3. Empirical analysis
    empirical = analyze_empirical_correlation(results)

    # 4. Partial correlations
    partial = analyze_partial_correlations(results)

    # 5. Alternative definitions
    propose_alternative_km()

    # Summary
    print()
    print("-" * 70)
    print("SUMMARY & RECOMMENDATIONS")
    print("-" * 70)
    print()
    print("1. K_M and K_P both involve prediction-like computations")
    print("2. Correlation may be inherent to agent capabilities (not a flaw)")
    print("3. Consider K_M as 'temporal model quality' rather than pure memory")
    print("4. Alternative K_M definitions could provide more independence")
    print()
    print("PAPER RECOMMENDATION:")
    print("  Acknowledge K_M-K_P correlation and interpret K_M as measuring")
    print("  'temporal model sophistication' which naturally correlates with")
    print("  predictive capability. The correlation reflects that agents with")
    print("  good world models tend to also have good temporal models.")
    print()

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "n_samples": len(results),
        "empirical_correlations": empirical,
        "partial_correlations": {
            k: {"r": float(v["r"]) if not np.isnan(v["r"]) else None,
                "p": float(v["p"])}
            for k, v in partial.items()
        } if partial else {},
        "recommendations": [
            "Acknowledge K_M-K_P correlation in paper",
            "Interpret K_M as 'temporal model sophistication'",
            "Consider alternative K_M definitions for future work",
        ],
    }

    log_dir = Path("logs/km_kp_analysis")
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"km_kp_correlation_{timestamp}.json"

    with open(log_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Results saved: {log_file}")

    return output


if __name__ == "__main__":
    run_km_kp_analysis()
