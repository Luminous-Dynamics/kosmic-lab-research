#!/usr/bin/env python3
"""
Supplementary: Statistical Power Analysis

Determine required sample size for detecting K-Index effect.

Run with:
    nix-shell -p python3 python3Packages.numpy python3Packages.scipy --run "python3 -u supplementary_power.py"
"""

import numpy as np
from scipy import stats
from datetime import datetime


def power_analysis_correlation(r, alpha=0.05, power=0.80):
    """
    Compute required sample size for correlation.

    Uses Fisher's z-transformation.
    """
    # Z-scores for alpha and power
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)

    # Fisher z-transformation
    z_r = np.arctanh(r)

    # Required sample size
    n = ((z_alpha + z_beta) / z_r) ** 2 + 3

    return int(np.ceil(n))


def simulate_power(true_r, n, n_simulations=1000, alpha=0.05):
    """
    Simulate power for given effect size and sample size.
    """
    significant_count = 0

    for _ in range(n_simulations):
        # Generate correlated data
        x = np.random.randn(n)
        y = true_r * x + np.sqrt(1 - true_r**2) * np.random.randn(n)

        # Test correlation
        r, p = stats.pearsonr(x, y)

        if p < alpha:
            significant_count += 1

    return significant_count / n_simulations


def main():
    print("\n" + "=" * 70)
    print("SUPPLEMENTARY: STATISTICAL POWER ANALYSIS")
    print("=" * 70)

    np.random.seed(42)

    # Our observed effect size
    observed_r = 0.70

    print("\n" + "-" * 70)
    print("REQUIRED SAMPLE SIZE BY EFFECT SIZE")
    print("-" * 70)

    effect_sizes = [0.30, 0.50, 0.70, 0.80, 0.90]

    print(f"\n{'Effect (r)':>12} {'n for 80%':>12} {'n for 90%':>12} {'n for 95%':>12}")
    print("-" * 50)

    for r in effect_sizes:
        n_80 = power_analysis_correlation(r, power=0.80)
        n_90 = power_analysis_correlation(r, power=0.90)
        n_95 = power_analysis_correlation(r, power=0.95)

        marker = " ← Our effect" if r == 0.70 else ""
        print(f"{r:>12.2f} {n_80:>12} {n_90:>12} {n_95:>12}{marker}")

    print("\n" + "-" * 70)
    print("POWER FOR OUR SAMPLE SIZES")
    print("-" * 70)

    sample_sizes = [10, 20, 30, 50, 100]

    print(f"\nFor r = {observed_r}:")
    print(f"\n{'Sample size':>12} {'Power':>10} {'Assessment':>20}")
    print("-" * 45)

    for n in sample_sizes:
        power = simulate_power(observed_r, n, n_simulations=1000)

        if power >= 0.95:
            assessment = "Excellent"
        elif power >= 0.80:
            assessment = "Adequate"
        elif power >= 0.50:
            assessment = "Underpowered"
        else:
            assessment = "Severely underpowered"

        marker = " ← Our n" if n == 30 else ""
        print(f"{n:>12} {power:>10.2%} {assessment:>20}{marker}")

    print("\n" + "-" * 70)
    print("MINIMUM DETECTABLE EFFECT BY SAMPLE SIZE")
    print("-" * 70)

    print(f"\nFor 80% power at α = 0.05:")
    print(f"\n{'Sample size':>12} {'Min effect (r)':>15}")
    print("-" * 30)

    for n in sample_sizes:
        # Binary search for minimum effect
        low, high = 0.01, 0.99
        while high - low > 0.01:
            mid = (low + high) / 2
            required_n = power_analysis_correlation(mid, power=0.80)
            if required_n <= n:
                high = mid
            else:
                low = mid

        marker = " ← Our n" if n == 30 else ""
        print(f"{n:>12} {high:>15.2f}{marker}")

    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    # Our specific situation
    our_n = 30
    our_r = 0.70
    our_power = simulate_power(our_r, our_n)
    required_n = power_analysis_correlation(our_r, power=0.80)

    print(f"\nOur study: n = {our_n}, r = {our_r}")
    print(f"Estimated power: {our_power:.1%}")
    print(f"Required n for 80% power: {required_n}")

    if our_power >= 0.80:
        print(f"\n✓ STUDY IS ADEQUATELY POWERED")
        print(f"  Power = {our_power:.1%} exceeds 80% threshold")
    else:
        print(f"\n⚠ Study may be underpowered")
        print(f"  Power = {our_power:.1%} below 80% threshold")

    # Additional recommendations
    print("\n" + "-" * 70)
    print("RECOMMENDATIONS")
    print("-" * 70)

    if our_power >= 0.95:
        print("\n• Current sample size provides excellent power")
        print("• Results are highly reliable")
    elif our_power >= 0.80:
        print("\n• Current sample size provides adequate power")
        print("• Consider n=50 for supplementary experiments")
        print("• This would achieve power > 99%")
    else:
        print("\n• Recommend increasing sample size")
        print(f"• Need n ≥ {required_n} for 80% power")

    # Type I error considerations
    print("\n• With 25 experiments, expect ~1 false positive")
    print("• Use Bonferroni correction for multiple testing")
    print(f"• Adjusted α = 0.05/25 = {0.05/25:.4f}")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"supplementary_power_{timestamp}.npz"
    np.savez(filename,
             observed_r=observed_r,
             our_n=our_n,
             our_power=our_power,
             required_n=required_n)
    print(f"\nSaved: {filename}")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
