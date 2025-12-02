#!/usr/bin/env python3
"""
Test Suite for Geometric Mean Conversion

Validates that:
1. Geometric mean ≤ Arithmetic mean (mathematical requirement)
2. Numerical stability (handles zeros, near-zeros)
3. Weighted geometric mean works correctly
4. Bootstrap confidence intervals remain valid
5. Results match expected benchmarks

Run: pytest historical_k/test_geometric_conversion.py -v
"""

import numpy as np
import pandas as pd
import pytest


def geometric_mean(values, weights=None):
    """
    Compute geometric mean with numerical stability.

    Formula: GM = exp(mean(log(values)))
    Handles zeros by adding small epsilon.

    Args:
        values: Array-like of positive values
        weights: Optional weights (must sum to 1)

    Returns:
        Geometric mean (float)
    """
    values = np.asarray(values)

    # Add small epsilon to handle zeros
    epsilon = 1e-10
    values_safe = values + epsilon

    # Compute in log-space for numerical stability
    log_values = np.log(values_safe)

    if weights is None:
        # Unweighted geometric mean
        log_mean = np.mean(log_values)
    else:
        # Weighted geometric mean
        weights = np.asarray(weights)
        if not np.isclose(weights.sum(), 1.0):
            raise ValueError(f"Weights must sum to 1.0, got {weights.sum()}")
        log_mean = np.sum(log_values * weights)

    return np.exp(log_mean)


class TestGeometricMeanProperties:
    """Test mathematical properties of geometric mean."""

    def test_geometric_le_arithmetic(self):
        """GM ≤ AM (equality only when all values equal)."""
        # Random positive values
        values = np.random.uniform(0.1, 1.0, size=100)
        gm = geometric_mean(values)
        am = np.mean(values)

        assert gm <= am, f"Geometric mean ({gm:.6f}) > Arithmetic mean ({am:.6f})"
        assert gm <= am + 1e-10  # Numerical tolerance

    def test_equality_when_uniform(self):
        """GM = AM when all values are equal."""
        values = np.ones(10) * 0.5
        gm = geometric_mean(values)
        am = np.mean(values)

        assert np.isclose(gm, am, atol=1e-9), f"GM ({gm}) ≠ AM ({am}) for uniform values"

    def test_weighted_geometric_mean(self):
        """Weighted geometric mean works correctly."""
        values = np.array([0.2, 0.4, 0.6, 0.8])
        weights = np.array([0.25, 0.25, 0.25, 0.25])  # Equal weights

        gm_weighted = geometric_mean(values, weights)
        gm_unweighted = geometric_mean(values)

        assert np.isclose(gm_weighted, gm_unweighted, atol=1e-9)

    def test_zero_handling(self):
        """Geometric mean handles zeros gracefully."""
        values = np.array([0.0, 0.5, 1.0])
        gm = geometric_mean(values)

        # Should be close to zero but not exactly zero (due to epsilon)
        assert gm < 0.1, f"GM of {values} should be near zero, got {gm}"
        assert gm > 0.0, "GM should never be exactly zero"

    def test_sensitivity_to_zeros(self):
        """Geometric mean is sensitive to low values (weakest link)."""
        # Case 1: All moderate values
        moderate = np.array([0.5, 0.6, 0.7, 0.8])
        gm_moderate = geometric_mean(moderate)
        am_moderate = np.mean(moderate)

        # Case 2: One very low value
        with_weak_link = np.array([0.1, 0.6, 0.7, 0.8])
        gm_weak = geometric_mean(with_weak_link)
        am_weak = np.mean(with_weak_link)

        # Geometric mean should drop more dramatically
        gm_ratio = gm_weak / gm_moderate
        am_ratio = am_weak / am_moderate

        assert gm_ratio < am_ratio, "GM should be more sensitive to weak links than AM"


class TestKIndexConversion:
    """Test K(t) index conversion from arithmetic to geometric."""

    def test_k_2020_drops_as_expected(self):
        """K₂₀₂₀ should drop by ~25% with geometric mean."""
        # Simulate 7 harmonies at 2020 (realistic values)
        harmonies_2020 = np.array([
            0.85,  # H1: Governance
            0.95,  # H2: Interconnection
            0.65,  # H3: Reciprocity (weakest link!)
            0.90,  # H4: Complexity
            0.90,  # H5: Knowledge
            0.80,  # H6: Wellbeing
            0.98,  # H7: Technology
        ])

        k_arithmetic = np.mean(harmonies_2020)
        k_geometric = geometric_mean(harmonies_2020)

        drop_pct = (k_arithmetic - k_geometric) / k_arithmetic * 100

        print(f"\nK₂₀₂₀ Arithmetic: {k_arithmetic:.4f}")
        print(f"K₂₀₂₀ Geometric:  {k_geometric:.4f}")
        print(f"Drop: {drop_pct:.1f}%")

        # Expected: 20-30% drop
        assert 15 <= drop_pct <= 35, f"Drop should be 15-35%, got {drop_pct:.1f}%"
        assert k_geometric < k_arithmetic

    def test_k_1810_drops_more(self):
        """K₁₈₁₀ should drop more (lower absolute values)."""
        # Simulate 7 harmonies at 1810 (all low)
        harmonies_1810 = np.array([0.12, 0.15, 0.10, 0.08, 0.14, 0.11, 0.18])

        k_arithmetic = np.mean(harmonies_1810)
        k_geometric = geometric_mean(harmonies_1810)

        drop_pct = (k_arithmetic - k_geometric) / k_arithmetic * 100

        # Lower values → more dramatic GM drop
        assert drop_pct > 20, f"K₁₈₁₀ drop should be >20%, got {drop_pct:.1f}%"

    def test_time_series_consistency(self):
        """Geometric K(t) should maintain same general trends as arithmetic."""
        # Simulate time series
        np.random.seed(42)
        years = np.arange(1810, 2021, 10)

        # Create realistic harmony trajectories (growing over time)
        def harmony_trajectory(start, end, noise=0.05):
            trend = np.linspace(start, end, len(years))
            noise_vals = np.random.normal(0, noise, len(years))
            return np.clip(trend + noise_vals, 0.01, 1.0)

        harmonies = np.array([
            harmony_trajectory(0.12, 0.85),  # H1
            harmony_trajectory(0.15, 0.95),  # H2
            harmony_trajectory(0.10, 0.65),  # H3
            harmony_trajectory(0.08, 0.90),  # H4
            harmony_trajectory(0.14, 0.90),  # H5
            harmony_trajectory(0.11, 0.80),  # H6
            harmony_trajectory(0.18, 0.98),  # H7
        ])

        k_arithmetic = np.mean(harmonies, axis=0)
        k_geometric = np.array([geometric_mean(harmonies[:, i]) for i in range(len(years))])

        # Correlation should be very high (>0.95)
        correlation = np.corrcoef(k_arithmetic, k_geometric)[0, 1]
        assert correlation > 0.95, f"Correlation should be >0.95, got {correlation:.3f}"

        # Both should be monotonically increasing (with minor fluctuations)
        assert k_geometric[-1] > k_geometric[0], "K(t) should increase 1810→2020"
        assert k_arithmetic[-1] > k_arithmetic[0], "K(t) should increase 1810→2020"


class TestNumericalStability:
    """Test numerical stability edge cases."""

    def test_very_small_values(self):
        """Handle values near zero without underflow."""
        values = np.array([1e-8, 1e-7, 1e-6, 1e-5])
        gm = geometric_mean(values)

        assert np.isfinite(gm), "GM should be finite for very small values"
        assert gm > 0, "GM should be positive"

    def test_very_large_values(self):
        """Handle large values without overflow."""
        values = np.array([1e6, 1e7, 1e8])
        gm = geometric_mean(values)

        assert np.isfinite(gm), "GM should be finite for large values"

    def test_mixed_scales(self):
        """Handle values across many orders of magnitude."""
        values = np.array([1e-5, 0.01, 0.5, 0.9, 0.99])
        gm = geometric_mean(values)

        assert np.isfinite(gm), "GM should handle mixed scales"
        # GM should be dominated by smallest value
        assert gm < 0.1, f"GM should be pulled down by 1e-5, got {gm}"


class TestBootstrapCompatibility:
    """Test that bootstrap confidence intervals work with geometric mean."""

    def test_bootstrap_geometric_mean(self):
        """Bootstrap CI on geometric mean converges properly."""
        np.random.seed(42)

        # Simulate a harmony time series
        true_values = np.random.beta(5, 2, size=100)  # Skewed towards higher values

        # Bootstrap resampling
        n_samples = 1000
        bootstrap_gms = []

        for _ in range(n_samples):
            resampled = np.random.choice(true_values, size=len(true_values), replace=True)
            bootstrap_gms.append(geometric_mean(resampled))

        # Compute 95% CI
        ci_low = np.percentile(bootstrap_gms, 2.5)
        ci_high = np.percentile(bootstrap_gms, 97.5)
        true_gm = geometric_mean(true_values)

        # True value should be within CI (with high probability)
        assert ci_low <= true_gm <= ci_high, \
            f"True GM ({true_gm:.4f}) outside CI [{ci_low:.4f}, {ci_high:.4f}]"

        # CI should be reasonable (not degenerate)
        ci_width = ci_high - ci_low
        assert ci_width > 0.01, f"CI too narrow: {ci_width:.4f}"
        assert ci_width < 0.5, f"CI too wide: {ci_width:.4f}"


class TestValidationBenchmarks:
    """Test against known mathematical benchmarks."""

    def test_known_values(self):
        """Validate against hand-calculated geometric means."""
        # Test case 1: Powers of 2
        values1 = np.array([1, 2, 4, 8])
        gm1 = geometric_mean(values1)
        expected1 = (1 * 2 * 4 * 8) ** 0.25  # = 64^0.25 = 2.828...
        assert np.isclose(gm1, expected1, atol=1e-6)

        # Test case 2: Simple case
        values2 = np.array([0.1, 0.2, 0.3, 0.4])
        gm2 = geometric_mean(values2)
        expected2 = (0.1 * 0.2 * 0.3 * 0.4) ** 0.25  # = 0.0024^0.25 = 0.2213...
        assert np.isclose(gm2, expected2, atol=1e-4)

    def test_scipy_compatibility(self):
        """Compare with scipy.stats.gmean if available."""
        try:
            from scipy.stats import gmean as scipy_gmean
        except ImportError:
            pytest.skip("scipy not available")

        values = np.random.uniform(0.1, 1.0, size=50)

        our_gm = geometric_mean(values)
        scipy_gm = scipy_gmean(values)

        assert np.isclose(our_gm, scipy_gm, atol=1e-9), \
            f"Our GM ({our_gm:.9f}) ≠ SciPy GM ({scipy_gm:.9f})"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_single_value(self):
        """Geometric mean of single value is itself."""
        value = 0.7
        gm = geometric_mean([value])
        assert np.isclose(gm, value)

    def test_two_values(self):
        """Geometric mean of two values: sqrt(a*b)."""
        values = np.array([0.25, 0.64])
        gm = geometric_mean(values)
        expected = np.sqrt(0.25 * 0.64)  # = sqrt(0.16) = 0.4
        assert np.isclose(gm, expected, atol=1e-9)

    def test_invalid_weights(self):
        """Weights that don't sum to 1.0 should raise error."""
        values = np.array([0.1, 0.2, 0.3])
        weights = np.array([0.5, 0.3, 0.1])  # Sum = 0.9, not 1.0

        with pytest.raises(ValueError, match="Weights must sum to 1.0"):
            geometric_mean(values, weights)


if __name__ == "__main__":
    # Run all tests with verbose output
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"],
        cwd="/srv/luminous-dynamics/kosmic-lab"
    )
    sys.exit(result.returncode)
