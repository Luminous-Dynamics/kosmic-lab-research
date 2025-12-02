#!/usr/bin/env python3
"""
O/R Index: Observation-Response Index for Multi-Agent Coordination

This module implements the O/R Index metric for measuring behavioral flexibility
in multi-agent systems. The O/R Index quantifies how observation variation
translates to action variation, providing a measure of adaptive responsiveness.

Formula:
    O/R Index = Var(P(a|o)) / Var(P(a)) - 1

Where:
    - Lower (more negative) values indicate more flexible, adaptive behavior
    - Values near 0 indicate rigid, non-adaptive behavior
    - The index correlates with coordination success in MARL tasks
"""

from typing import List, Tuple, Union

import numpy as np


def compute_or_index(
    observations: np.ndarray,
    actions: np.ndarray,
    n_bins: int = 10,
    epsilon: float = 1e-8,
) -> float:
    """
    Compute the O/R Index for a trajectory of observations and actions.

    Parameters
    ----------
    observations : np.ndarray
        Observation sequence. Shape: (timesteps, n_agents, obs_dim) or (timesteps, obs_dim)
    actions : np.ndarray
        Action sequence. Shape: (timesteps, n_agents) or (timesteps,)
    n_bins : int
        Number of bins for discretizing observations
    epsilon : float
        Small value to prevent division by zero

    Returns
    -------
    float
        O/R Index value. More negative = more flexible/adaptive behavior.
    """
    # Basic validations
    try:
        observations = np.asarray(observations)
        actions = np.asarray(actions)
    except Exception:
        return 0.0

    # Align lengths
    if len(observations) != len(actions):
        m = min(len(observations), len(actions))
        if m < 2:
            return 0.0
        observations = observations[:m]
        actions = actions[:m]

    # Normalize n_bins
    n_bins = max(2, int(n_bins))

    # Filter NaNs across aligned pairs
    if observations.ndim > 1:
        mask_obs = ~np.isnan(observations).any(axis=1)
    else:
        mask_obs = ~np.isnan(observations)
    mask_act = ~np.isnan(actions).any(axis=1) if actions.ndim > 1 else ~np.isnan(actions)
    mask = mask_obs & mask_act
    if mask.sum() < 2:
        return 0.0
    observations = observations[mask]
    actions = actions[mask]

    # Flatten multi-agent trajectories if needed
    if observations.ndim == 3:
        # (timesteps, n_agents, obs_dim) -> (timesteps * n_agents, obs_dim)
        n_timesteps, n_agents, obs_dim = observations.shape
        obs_flat = observations.reshape(-1, obs_dim)
        act_flat = actions.reshape(-1)
    elif observations.ndim == 2:
        obs_flat = observations
        act_flat = actions.flatten()
    else:
        obs_flat = observations.reshape(-1, 1)
        act_flat = actions.flatten()

    if len(obs_flat) < 2:
        return 0.0

    # Handle continuous observations by using PCA projection
    if obs_flat.shape[1] > 1:
        # Project observations to 1D using variance-maximizing direction
        obs_centered = obs_flat - obs_flat.mean(axis=0)
        cov = np.cov(obs_centered.T)
        if cov.ndim == 0:
            obs_1d = obs_flat[:, 0]
        else:
            # Use first principal component
            try:
                eigvals, eigvecs = np.linalg.eigh(cov)
                pc1 = eigvecs[:, -1]  # Largest eigenvalue
                obs_1d = obs_centered @ pc1
            except Exception:
                obs_1d = obs_flat[:, 0]
    else:
        obs_1d = obs_flat.flatten()

    # Discretize observations into bins
    obs_min, obs_max = obs_1d.min(), obs_1d.max()
    if obs_max - obs_min < epsilon:
        return 0.0

    # Build bin edges (exclude endpoints for np.digitize threshold vector)
    edges = np.linspace(obs_min, obs_max, n_bins + 1)[1:-1]
    obs_bins = np.digitize(obs_1d, edges)

    # Handle continuous actions
    if np.issubdtype(act_flat.dtype, np.floating):
        if np.std(act_flat) < epsilon:
            return 0.0
        # Discretize continuous actions
        act_min, act_max = act_flat.min(), act_flat.max()
        if act_max - act_min < epsilon:
            act_discrete = np.zeros_like(act_flat, dtype=int)
        else:
            aedges = np.linspace(act_min, act_max, n_bins + 1)[1:-1]
            act_discrete = np.digitize(act_flat, aedges)
    else:
        act_discrete = act_flat.astype(int)

    # Compute P(a) - marginal action distribution
    unique_actions = np.unique(act_discrete)
    n_actions = len(unique_actions)

    if n_actions < 2:
        return 0.0

    p_a = np.zeros(n_actions)
    for i, a in enumerate(unique_actions):
        p_a[i] = np.mean(act_discrete == a)

    var_p_a = np.var(p_a)

    if var_p_a < epsilon:
        return 0.0

    # Compute P(a|o) - conditional action distribution given observation
    unique_obs = np.unique(obs_bins)
    conditional_probs = []

    for o in unique_obs:
        mask = obs_bins == o
        if mask.sum() < 2:
            continue

        p_a_given_o = np.zeros(n_actions)
        for i, a in enumerate(unique_actions):
            p_a_given_o[i] = np.mean(act_discrete[mask] == a)

        conditional_probs.append(p_a_given_o)

    if len(conditional_probs) < 2:
        return 0.0

    # Compute variance of conditional distributions
    conditional_probs = np.array(conditional_probs)
    var_p_a_given_o = np.mean([np.var(cp) for cp in conditional_probs])

    # O/R Index: normalized variance ratio
    # More negative = more variation in P(a|o) relative to P(a)
    or_index = (var_p_a_given_o / var_p_a) - 1

    return float(or_index)


def compute_or_index_batch(
    trajectories: List[Tuple[np.ndarray, np.ndarray]], **kwargs
) -> List[float]:
    """
    Compute O/R Index for a batch of trajectories.

    Parameters
    ----------
    trajectories : list of (observations, actions) tuples
        Each trajectory is a tuple of observation and action arrays
    **kwargs : dict
        Additional arguments passed to compute_or_index

    Returns
    -------
    list of float
        O/R Index for each trajectory
    """
    return [compute_or_index(obs, act, **kwargs) for obs, act in trajectories]


def compute_team_or_index(
    team_observations: List[np.ndarray],
    team_actions: List[np.ndarray],
    aggregation: str = "mean",
    **kwargs,
) -> float:
    """
    Compute aggregated O/R Index for a team across episodes.

    Parameters
    ----------
    team_observations : list of np.ndarray
        Observations for each episode
    team_actions : list of np.ndarray
        Actions for each episode
    aggregation : str
        How to aggregate: 'mean', 'median', 'min', 'max'
    **kwargs : dict
        Additional arguments passed to compute_or_index

    Returns
    -------
    float
        Aggregated O/R Index for the team
    """
    or_indices = []
    for obs, act in zip(team_observations, team_actions):
        or_idx = compute_or_index(obs, act, **kwargs)
        or_indices.append(or_idx)

    if not or_indices:
        return 0.0

    if aggregation == "mean":
        return float(np.mean(or_indices))
    elif aggregation == "median":
        return float(np.median(or_indices))
    elif aggregation == "min":
        return float(np.min(or_indices))
    elif aggregation == "max":
        return float(np.max(or_indices))
    else:
        raise ValueError(f"Unknown aggregation method: {aggregation}")


if __name__ == "__main__":
    # Quick test
    np.random.seed(42)

    # Test 1: Random behavior (low flexibility)
    obs_random = np.random.randn(100, 10)
    act_random = np.random.randint(0, 5, 100)
    or_random = compute_or_index(obs_random, act_random)
    print(f"Random policy O/R Index: {or_random:.4f}")

    # Test 2: Responsive behavior (high flexibility)
    obs_responsive = np.random.randn(100, 10)
    act_responsive = (obs_responsive[:, 0] > 0).astype(int)  # Respond to obs
    or_responsive = compute_or_index(obs_responsive, act_responsive)
    print(f"Responsive policy O/R Index: {or_responsive:.4f}")

    # Test 3: Highly adaptive (multi-bin response)
    obs_adaptive = np.random.randn(100, 10)
    act_adaptive = np.digitize(obs_adaptive[:, 0], [-1, 0, 1])
    or_adaptive = compute_or_index(obs_adaptive, act_adaptive)
    print(f"Adaptive policy O/R Index: {or_adaptive:.4f}")
