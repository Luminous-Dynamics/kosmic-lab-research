"""
k_topo.py

K_Topo: Topological Consciousness Measure

This module implements K_Topo, an experimental 8th dimension of the Kosmic K-Index
Framework that uses Topological Data Analysis (TDA) to measure operational closure
and self-referential structure in agent behavior.

Theoretical Foundation:
    - Maturana & Varela: Autopoiesis IS a loop (operational closure)
    - Persistent homology can detect stable loops in behavior space
    - High persistence = stable operational closure = consciousness signature

Key Insight:
    A thermostat has no loops in its (O, A)-trajectory.
    A conscious agent exhibits persistent loops (self-referential dynamics).

Usage:
    from core.k_topo import compute_k_topo, compute_k_spectral

    k_topo = compute_k_topo(observations, actions)
    k_spectral = compute_k_spectral(observations, actions)

Author: Kosmic Lab
Date: December 2, 2025
Version: 0.1.0 (Experimental)
"""

from __future__ import annotations

import numpy as np
from typing import Dict, Optional, Tuple, List
import warnings


# =============================================================================
# K_Topo: Topological Consciousness via Persistent Homology
# =============================================================================

def compute_k_topo(
    observations: np.ndarray,
    actions: np.ndarray,
    max_dim: int = 1,
    max_edge_length: float = None,
    subsample: int = 500,
    normalize: bool = True,
) -> float:
    """
    K_Topo: Topological Consciousness Measure

    Measures operational closure via persistent homology of agent trajectories.
    High K_Topo indicates stable loops (self-referential dynamics) in (O, A)-space.

    Mathematical Definition:
        K_Topo = max persistence of 1-dimensional features (loops)
                 normalized by trajectory diameter

    Theoretical Grounding:
        - Autopoiesis (Maturana/Varela): Life is operational closure (loops)
        - A thermostat has β₁ = 0 (no persistent loops)
        - A conscious agent has β₁ > 0 with high persistence

    Args:
        observations: Agent observations [T, obs_dim]
        actions: Agent actions [T, act_dim]
        max_dim: Maximum homology dimension (1 = loops, 2 = voids)
        max_edge_length: Maximum edge length for Rips complex (auto if None)
        subsample: Subsample trajectory if longer (for computational efficiency)
        normalize: Normalize persistence by trajectory diameter

    Returns:
        K_Topo in range [0, 1] (normalized) or [0, ∞) (unnormalized)

    Interpretation:
        K_Topo ≈ 0: No stable loops (reflexive/thermostat behavior)
        K_Topo > 0.3: Moderate operational closure
        K_Topo > 0.6: Strong self-referential dynamics

    Note:
        Requires 'ripser' package for persistent homology.
        Falls back to simplified estimation if not available.
    """
    # Ensure 2D arrays
    observations = np.atleast_2d(observations)
    actions = np.atleast_2d(actions)

    if len(observations) < 10:
        return 0.0

    # Combine O-A space for trajectory analysis
    trajectory = np.hstack([observations, actions])

    # Subsample for computational efficiency
    if len(trajectory) > subsample:
        indices = np.linspace(0, len(trajectory) - 1, subsample, dtype=int)
        trajectory = trajectory[indices]

    # Standardize features
    trajectory = (trajectory - np.mean(trajectory, axis=0)) / (np.std(trajectory, axis=0) + 1e-10)

    # Compute trajectory diameter for normalization
    if normalize:
        from scipy.spatial.distance import pdist
        try:
            diameter = np.max(pdist(trajectory[:min(200, len(trajectory))]))
        except Exception:
            diameter = np.max(np.linalg.norm(trajectory - trajectory.mean(axis=0), axis=1)) * 2
    else:
        diameter = 1.0

    if diameter < 1e-10:
        return 0.0

    # Try ripser for proper TDA
    try:
        from ripser import ripser

        # Compute persistence diagrams
        # Note: For K_Topo, we want to capture ALL persistent features,
        # not filter them with threshold. Use diameter * 2 to be generous.
        if max_edge_length is None:
            max_edge_length = diameter * 2.0  # Generous threshold for all features

        result = ripser(
            trajectory,
            maxdim=max_dim,
            thresh=max_edge_length,
        )
        diagrams = result['dgms']

        # Extract 1D features (loops)
        if len(diagrams) > 1 and len(diagrams[1]) > 0:
            h1 = diagrams[1]
            births, deaths = h1[:, 0], h1[:, 1]

            # Filter out infinite persistence
            finite_mask = np.isfinite(deaths)
            if not np.any(finite_mask):
                return 0.0

            persistences = (deaths - births)[finite_mask]

            if len(persistences) == 0:
                return 0.0

            # Maximum persistence normalized by diameter
            k_topo = np.max(persistences) / diameter

            return float(min(1.0, k_topo)) if normalize else float(k_topo)
        else:
            return 0.0

    except ImportError:
        warnings.warn("ripser not available, using simplified K_Topo estimation")
        return _compute_k_topo_simple(trajectory, diameter, normalize)
    except Exception as e:
        warnings.warn(f"K_Topo computation failed: {e}")
        return _compute_k_topo_simple(trajectory, diameter, normalize)


def _compute_k_topo_simple(
    trajectory: np.ndarray,
    diameter: float,
    normalize: bool = True,
) -> float:
    """
    Simplified K_Topo estimation without ripser.

    Uses autocorrelation structure as proxy for loop detection.
    High autocorrelation at multiple lags indicates periodic/looping behavior.
    """
    if len(trajectory) < 20:
        return 0.0

    # Project to 1D for simplicity
    trajectory_1d = np.linalg.norm(trajectory, axis=1)

    # Compute autocorrelation at multiple lags
    n = len(trajectory_1d)
    mean = np.mean(trajectory_1d)
    var = np.var(trajectory_1d)

    if var < 1e-10:
        return 0.0

    # Check for significant autocorrelation at medium-range lags
    # (short-range is always high, long-range is noise)
    lags = [5, 10, 20, 30, 50]
    lags = [l for l in lags if l < n // 2]

    if len(lags) == 0:
        return 0.0

    autocorrs = []
    for lag in lags:
        ac = np.mean((trajectory_1d[:-lag] - mean) * (trajectory_1d[lag:] - mean)) / var
        autocorrs.append(max(0, ac))  # Only positive correlations indicate loops

    # K_Topo proxy: max autocorrelation at medium lags
    k_topo_proxy = np.max(autocorrs)

    return float(min(1.0, k_topo_proxy))


# =============================================================================
# K_Spectral: Spectral Consciousness via Graph Laplacian
# =============================================================================

def compute_k_spectral(
    observations: np.ndarray,
    actions: np.ndarray,
    k_neighbors: int = 10,
    subsample: int = 500,
) -> float:
    """
    K_Spectral: Spectral Consciousness Measure

    Measures collective coherence via the spectral gap of the trajectory graph.
    Based on spectral graph theory (Chung).

    Mathematical Definition:
        K_Spectral = λ₂(L) / λ_max(L)

    Where L is the graph Laplacian of the k-NN trajectory graph.

    Theoretical Grounding:
        - Spectral gap λ₂ > 0 indicates connected, synchronized behavior
        - λ₂ ≈ 0 indicates fragmented/disconnected dynamics
        - High λ₂/λ_max indicates tight clustering (coherent behavior)

    Args:
        observations: Agent observations [T, obs_dim]
        actions: Agent actions [T, act_dim]
        k_neighbors: Number of neighbors for graph construction
        subsample: Subsample trajectory if too long

    Returns:
        K_Spectral in range [0, 1]

    Interpretation:
        K_Spectral ≈ 0: Fragmented dynamics
        K_Spectral > 0.1: Connected behavior
        K_Spectral > 0.3: Tightly clustered (coherent) trajectory
    """
    # Ensure 2D arrays
    observations = np.atleast_2d(observations)
    actions = np.atleast_2d(actions)

    if len(observations) < k_neighbors + 5:
        return 0.0

    # Combine O-A space
    trajectory = np.hstack([observations, actions])

    # Subsample
    if len(trajectory) > subsample:
        indices = np.linspace(0, len(trajectory) - 1, subsample, dtype=int)
        trajectory = trajectory[indices]

    # Standardize
    trajectory = (trajectory - np.mean(trajectory, axis=0)) / (np.std(trajectory, axis=0) + 1e-10)

    n = len(trajectory)

    try:
        from scipy.spatial.distance import cdist
        from scipy.sparse import csr_matrix
        from scipy.sparse.linalg import eigsh

        # Compute pairwise distances
        distances = cdist(trajectory, trajectory)

        # Build k-NN adjacency matrix
        adjacency = np.zeros((n, n))
        for i in range(n):
            # Find k nearest neighbors (excluding self)
            neighbors = np.argsort(distances[i])[1:k_neighbors + 1]
            adjacency[i, neighbors] = 1

        # Symmetrize
        adjacency = (adjacency + adjacency.T) / 2

        # Compute degree matrix
        degree = np.diag(np.sum(adjacency, axis=1))

        # Compute Laplacian: L = D - A
        laplacian = degree - adjacency

        # Compute eigenvalues (we need the two smallest)
        # For normalized Laplacian: L_norm = D^{-1/2} L D^{-1/2}
        degree_inv_sqrt = np.diag(1.0 / np.sqrt(np.diag(degree) + 1e-10))
        laplacian_norm = degree_inv_sqrt @ laplacian @ degree_inv_sqrt

        eigenvalues = np.linalg.eigvalsh(laplacian_norm)
        eigenvalues = np.sort(eigenvalues)

        # Spectral gap = λ₂ (second smallest eigenvalue)
        # λ₁ ≈ 0 for connected graphs
        lambda_2 = eigenvalues[1] if len(eigenvalues) > 1 else 0.0
        lambda_max = eigenvalues[-1] if len(eigenvalues) > 0 else 1.0

        if lambda_max < 1e-10:
            return 0.0

        k_spectral = lambda_2 / lambda_max

        return float(min(1.0, k_spectral))

    except ImportError:
        warnings.warn("scipy not available for spectral computation")
        return _compute_k_spectral_simple(trajectory)
    except Exception as e:
        warnings.warn(f"K_Spectral computation failed: {e}")
        return _compute_k_spectral_simple(trajectory)


def _compute_k_spectral_simple(trajectory: np.ndarray) -> float:
    """
    Simplified K_Spectral estimation.

    Uses variance ratio as proxy for spectral clustering.
    """
    if len(trajectory) < 10:
        return 0.0

    # Compute cluster coherence via variance structure
    total_var = np.var(trajectory)

    # Split into chunks and compute within-chunk variance
    n_chunks = min(10, len(trajectory) // 5)
    if n_chunks < 2:
        return 0.0

    chunk_size = len(trajectory) // n_chunks
    within_vars = []

    for i in range(n_chunks):
        chunk = trajectory[i * chunk_size:(i + 1) * chunk_size]
        within_vars.append(np.var(chunk))

    mean_within_var = np.mean(within_vars)

    if total_var < 1e-10:
        return 0.0

    # K_Spectral proxy: 1 - (within/total)
    # High if within-chunk variance is low relative to total
    k_spectral_proxy = 1.0 - (mean_within_var / total_var)

    return float(max(0.0, min(1.0, k_spectral_proxy)))


# =============================================================================
# Combined Geometric K-Index
# =============================================================================

def compute_geometric_k(
    observations: np.ndarray,
    actions: np.ndarray,
    include_spectral: bool = True,
) -> Dict:
    """
    Compute the geometric extensions to the K-Index.

    Returns both K_Topo and K_Spectral with metadata.

    Args:
        observations: Agent observations [T, obs_dim]
        actions: Agent actions [T, act_dim]
        include_spectral: Whether to compute K_Spectral

    Returns:
        Dictionary with K_Topo, K_Spectral, and metadata
    """
    k_topo = compute_k_topo(observations, actions)

    k_spectral = None
    if include_spectral:
        k_spectral = compute_k_spectral(observations, actions)

    return {
        "K_Topo (Topological)": k_topo,
        "K_Spectral (Spectral)": k_spectral,
        "metadata": {
            "topo_method": "ripser" if _has_ripser() else "autocorrelation_proxy",
            "spectral_method": "laplacian" if _has_scipy_sparse() else "variance_proxy",
            "n_samples": len(observations),
        }
    }


def _has_ripser() -> bool:
    """Check if ripser is available."""
    try:
        import ripser
        return True
    except ImportError:
        return False


def _has_scipy_sparse() -> bool:
    """Check if scipy sparse is available."""
    try:
        from scipy.sparse.linalg import eigsh
        return True
    except ImportError:
        return False


# =============================================================================
# Integration with main K-Index
# =============================================================================

def extend_kosmic_index_with_geometry(result: Dict,
                                      observations: np.ndarray,
                                      actions: np.ndarray) -> Dict:
    """
    Extend a Kosmic K-Index result with geometric dimensions.

    This adds K_Topo and K_Spectral to an existing 7D result,
    creating a 9D extended K-vector.

    Args:
        result: Output from compute_kosmic_index()
        observations: Agent observations
        actions: Agent actions

    Returns:
        Extended result with 9D K-vector
    """
    geometric = compute_geometric_k(observations, actions)

    # Add to K-vector
    result["K_vector"]["K_Topo (Topological)"] = geometric["K_Topo (Topological)"]
    result["K_vector"]["K_Spectral (Spectral)"] = geometric["K_Spectral (Spectral)"]

    # Update composites
    components = [v for v in result["K_vector"].values() if v is not None and v > 1e-10]

    if len(components) > 0:
        result["K_sigma"] = float(np.prod(components))
        result["K_geo"] = float(np.power(np.prod(components), 1.0 / len(components)))

    # Update metadata
    result["metadata"]["has_geometric"] = True
    result["metadata"]["topo_method"] = geometric["metadata"]["topo_method"]
    result["metadata"]["spectral_method"] = geometric["metadata"]["spectral_method"]

    return result


# =============================================================================
# Self-Test
# =============================================================================

if __name__ == "__main__":
    print("Testing K_Topo and K_Spectral...")

    np.random.seed(42)

    # Test 1: Random trajectory (should have low K_Topo)
    print("\n--- Test 1: Random Trajectory ---")
    obs_random = np.random.randn(200, 8)
    act_random = np.random.randn(200, 2)
    k_topo_random = compute_k_topo(obs_random, act_random)
    k_spectral_random = compute_k_spectral(obs_random, act_random)
    print(f"K_Topo (random): {k_topo_random:.4f}")
    print(f"K_Spectral (random): {k_spectral_random:.4f}")

    # Test 2: Periodic trajectory (should have high K_Topo)
    print("\n--- Test 2: Periodic Trajectory ---")
    t = np.linspace(0, 10 * np.pi, 200)
    obs_periodic = np.column_stack([
        np.sin(t), np.cos(t),
        np.sin(2 * t), np.cos(2 * t),
        np.sin(0.5 * t), np.cos(0.5 * t),
        np.sin(3 * t), np.cos(3 * t),
    ])
    act_periodic = np.column_stack([np.sin(t + 0.5), np.cos(t + 0.5)])
    k_topo_periodic = compute_k_topo(obs_periodic, act_periodic)
    k_spectral_periodic = compute_k_spectral(obs_periodic, act_periodic)
    print(f"K_Topo (periodic): {k_topo_periodic:.4f}")
    print(f"K_Spectral (periodic): {k_spectral_periodic:.4f}")

    # Test 3: Thermostat (reactive but no loops)
    print("\n--- Test 3: Thermostat Behavior ---")
    obs_thermo = np.random.randn(200, 8)
    act_thermo = 0.8 * obs_thermo[:, :2] + 0.1 * np.random.randn(200, 2)
    k_topo_thermo = compute_k_topo(obs_thermo, act_thermo)
    k_spectral_thermo = compute_k_spectral(obs_thermo, act_thermo)
    print(f"K_Topo (thermostat): {k_topo_thermo:.4f}")
    print(f"K_Spectral (thermostat): {k_spectral_thermo:.4f}")

    # Summary
    print("\n--- Summary ---")
    print(f"{'Trajectory':<20} {'K_Topo':>10} {'K_Spectral':>12}")
    print("-" * 45)
    print(f"{'Random':<20} {k_topo_random:>10.4f} {k_spectral_random:>12.4f}")
    print(f"{'Periodic':<20} {k_topo_periodic:>10.4f} {k_spectral_periodic:>12.4f}")
    print(f"{'Thermostat':<20} {k_topo_thermo:>10.4f} {k_spectral_thermo:>12.4f}")

    print("\nExpected: Periodic > Thermostat > Random for K_Topo")
    print("All tests completed!")
