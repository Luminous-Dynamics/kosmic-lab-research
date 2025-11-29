#!/usr/bin/env python3
"""
🔗 Track L: K-Index ↔ O/R Index Bridge Study Runner

Goal: Establish relationship between magnitude coupling (K) and behavioral consistency (O/R)
Paper 8: Unified Indices of Machine Consciousness
Paper 9: The Kosmic K-Index Framework (7D extension)

Sub-tracks:
- L1: Correlation study (K vs O/R across agent population)
- L2: Unified index validation (compare predictive power)
- L3: Causal analysis (intervention experiments)
- L4: Unified optimization (CMA-ES with coherence fitness)
- L5: Cross-environment validation
- L6: Kosmic K-Vector validation (7D framework from Paper 9)

Usage:
    python track_l_runner.py --phase l1 --config track_l_unified_indices.yaml
    python track_l_runner.py --phase l2 --episodes 300
    python track_l_runner.py --phase l4 --generations 100
    python track_l_runner.py --phase l6 --kosmic  # 7D Kosmic K-Vector

NOTE: Copy this file to fre/ directory when ready for production use.
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy.stats import pearsonr, spearmanr, kendalltau

# Import Kosmic K-Index module from Paper 9
sys.path.insert(0, str(Path(__file__).parent.parent / "paper-9-kosmic-k-index"))
try:
    from kosmic_k_index import compute_kosmic_index
    HAS_KOSMIC = True
except ImportError:
    HAS_KOSMIC = False
    print("⚠️  kosmic_k_index.py not available. L6 phase disabled.")

# Try to import optional dependencies
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    print("⚠️  PyYAML not available. Using default config.")


# =============================================================================
# METRICS: K-Index and O/R Index
# =============================================================================

def compute_k_index(obs_norms: np.ndarray, act_norms: np.ndarray) -> float:
    """
    Compute K-Index: magnitude coupling between observations and actions.

    K = 2 × |ρ(||O||, ||A||)| ∈ [0, 2]

    Args:
        obs_norms: Observation norms [T]
        act_norms: Action norms [T]

    Returns:
        K-Index value
    """
    if len(obs_norms) < 2:
        return np.nan

    r, _ = pearsonr(obs_norms, act_norms)
    k = 2.0 * abs(r)

    return float(np.clip(k, 0, 2))


def compute_or_index(
    actions: np.ndarray,
    observations: np.ndarray,
    n_obs_bins: int = 10,
    n_action_bins: int = 5,
) -> float:
    """
    Compute O/R Index: behavioral consistency (Paper 6 methodology).

    O/R = Var(P(a|o)) / Var(P(a)) - 1

    Lower O/R = more consistent behavior.

    This implementation matches Paper 6's approach:
    - Discretize observations into bins
    - Build action histograms per observation bin
    - Compute variance of histogram shapes

    For continuous actions, we use action norm quantiles to create
    a manageable number of action categories (matching Paper 6's 5 actions).

    Args:
        actions: Action vectors [T, A] (continuous) or [T] (discrete)
        observations: Observation vectors [T, O]
        n_obs_bins: Number of bins for observation discretization
        n_action_bins: Number of bins for action discretization

    Returns:
        O/R Index value in [-1, inf)
        -1 = perfectly consistent (deterministic or observation-independent)
        0 = marginal and conditional variance equal
        >0 = context-sensitive (high variance given observation)
    """
    T = len(actions)
    if T < 2:
        return np.nan

    # Handle both 1D and 2D action arrays
    if actions.ndim == 1:
        # Discrete actions: use as-is
        action_indices = actions.astype(int)
        n_actions = int(action_indices.max()) + 1
    else:
        # Continuous actions: discretize by action NORM using FIXED bins
        # Fixed bins preserve the distribution shape (unlike quantile binning)
        action_norms = np.linalg.norm(actions, axis=1)
        # Use fixed bins from min to max
        bin_edges = np.linspace(action_norms.min() - 1e-8, action_norms.max() + 1e-8, n_action_bins + 1)
        action_indices = np.digitize(action_norms, bin_edges) - 1
        action_indices = np.clip(action_indices, 0, n_action_bins - 1)
        n_actions = n_action_bins

    # Discretize observations into bins using norm with FIXED bins
    obs_norms = np.linalg.norm(observations, axis=1) if observations.ndim > 1 else observations
    obs_bin_edges = np.linspace(obs_norms.min() - 1e-8, obs_norms.max() + 1e-8, n_obs_bins + 1)
    obs_bins = np.digitize(obs_norms, obs_bin_edges) - 1
    obs_bins = np.clip(obs_bins, 0, n_obs_bins - 1)

    # Compute P(a) - marginal action distribution (histogram)
    action_counts = np.bincount(action_indices, minlength=n_actions)
    p_a = action_counts / T
    var_p_a = np.var(p_a)

    if var_p_a < 1e-10:
        # All actions the same -> perfectly consistent
        return -1.0

    # Compute P(a|o) for each observation bin and get variance
    conditional_variances = []
    for b in range(n_obs_bins):
        mask = obs_bins == b
        n_in_bin = mask.sum()
        if n_in_bin > 1:
            actions_in_bin = action_indices[mask]
            cond_counts = np.bincount(actions_in_bin, minlength=n_actions)
            p_a_given_o = cond_counts / n_in_bin
            var_p_a_given_o = np.var(p_a_given_o)
            conditional_variances.append(var_p_a_given_o)

    if len(conditional_variances) == 0:
        return np.nan

    # Average variance of P(a|o) across observations
    mean_var_p_a_given_o = np.mean(conditional_variances)

    # O/R Index (Paper 6 formula)
    or_index = mean_var_p_a_given_o / var_p_a - 1

    return float(or_index)


def compute_unified_coherence(
    k: float,
    or_index: float,
    formula: str = "original"
) -> float:
    """
    Compute unified coherence score.

    Formulas:
    - "original": K × (1 - tanh(O/R)) - penalizes high O/R
    - "multiplicative": K × (1 + max(0, O/R)) - rewards both high K and high O/R
    - "additive": K + 0.5 × (O/R + 1) - balanced additive
    - "geometric": sqrt(K × (O/R + 2)) - geometric mean with shift
    - "log_scaled": K × log(O/R + 2) - log-scaled O/R contribution

    Args:
        k: K-Index value
        or_index: O/R Index value
        formula: Which formula to use

    Returns:
        Unified coherence score
    """
    if np.isnan(k) or np.isnan(or_index):
        return np.nan

    if formula == "original":
        # Original: penalizes high O/R
        return k * (1 - np.tanh(or_index))
    elif formula == "multiplicative":
        # Multiplicative: rewards both high K and high O/R
        return k * (1 + max(0, or_index))
    elif formula == "additive":
        # Additive: balanced contributions
        return k + 0.5 * (or_index + 1)
    elif formula == "geometric":
        # Geometric mean with shift
        return np.sqrt(k * (or_index + 2))
    elif formula == "log_scaled":
        # Log-scaled O/R contribution
        return k * np.log(or_index + 2)
    elif formula == "k_only":
        # K-only baseline (for comparison)
        return k
    elif formula == "or_only":
        # O/R-only (control condition - reviewer requested)
        # Shift O/R to be positive for optimization (O/R >= -1, so O/R + 1 >= 0)
        return or_index + 1
    else:
        raise ValueError(f"Unknown formula: {formula}")


# =============================================================================
# ENVIRONMENTS
# =============================================================================

@dataclass
class CoordinationEnvironment:
    """Environment for testing K-O/R relationship."""

    obs_dim: int = 20
    action_dim: int = 10
    episode_length: int = 200
    difficulty: float = 1.0
    noise_level: float = 0.1

    def __post_init__(self):
        self.state = None
        self.step_count = 0
        self.target = None

    def reset(self) -> np.ndarray:
        """Reset environment."""
        self.state = np.random.randn(self.obs_dim) * self.difficulty
        self.target = np.random.randn(self.action_dim)
        self.target = self.target / (np.linalg.norm(self.target) + 1e-8)
        self.step_count = 0
        return self.state.copy()

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, Dict]:
        """Execute action."""
        # Compute coordination reward (how well action matches target)
        action_normalized = action / (np.linalg.norm(action) + 1e-8)
        reward = np.dot(action_normalized, self.target)

        # Update state with some dynamics
        self.state = 0.9 * self.state + 0.1 * np.random.randn(self.obs_dim)
        self.state += self.noise_level * np.random.randn(self.obs_dim)
        self.step_count += 1

        # Occasionally change target (coordination challenge)
        if self.step_count % 50 == 0:
            self.target = np.random.randn(self.action_dim)
            self.target = self.target / (np.linalg.norm(self.target) + 1e-8)

        done = self.step_count >= self.episode_length

        info = {
            "step": self.step_count,
            "target_match": reward,
        }

        return self.state.copy(), float(reward), done, info


@dataclass
class SimpleEnvironment:
    """
    Minimal environment from CMA-ES stability investigation.
    Achieves K > 1.9 (higher than CoordinationEnvironment).
    """

    obs_dim: int = 20
    action_dim: int = 10
    episode_length: int = 200

    def __post_init__(self):
        self.state = None
        self.step_count = 0

    def reset(self) -> np.ndarray:
        """Reset environment."""
        self.state = np.random.randn(self.obs_dim)
        self.step_count = 0
        return self.state.copy()

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, Dict]:
        """Execute action with simple dynamics."""
        # Simple dynamics - smooth state evolution
        self.state = 0.9 * self.state + 0.1 * np.random.randn(self.obs_dim)

        # Reward: alignment between action and state
        min_dim = min(len(action), self.obs_dim)
        reward = np.dot(action[:min_dim], self.state[:min_dim])

        self.step_count += 1
        done = self.step_count >= self.episode_length

        return self.state.copy(), float(reward), done, {}


@dataclass
class DelayedForagingEnvironment:
    """
    Environment for testing K_M (temporal/meta dimension).

    Food locations are shown at t=0 but only collectible after delay T.
    Feedforward agents (no memory) should have K_M ≈ 0.
    Recurrent agents (with memory) should have higher K_M.

    Paper 9 Phase 2 validation environment.
    """

    grid_size: int = 10
    n_food: int = 5
    delay: int = 10  # Food becomes collectible after this many steps
    episode_length: int = 100
    obs_dim: int = 8  # Agent position (2) + food locations (2*n_food visible at start)

    def __post_init__(self):
        self.agent_pos = None
        self.food_locations = None
        self.food_available = None  # Track when each food becomes available
        self.food_collected = None
        self.step_count = 0
        self.initial_obs = None  # Store initial observation for K_M testing

    def reset(self) -> np.ndarray:
        """Reset environment with new food locations."""
        self.agent_pos = np.array([self.grid_size // 2, self.grid_size // 2], dtype=float)

        # Place food randomly
        self.food_locations = []
        for _ in range(self.n_food):
            pos = np.random.randint(0, self.grid_size, size=2).astype(float)
            self.food_locations.append(pos)
        self.food_locations = np.array(self.food_locations)

        # Food becomes available after delay
        self.food_available = np.zeros(self.n_food, dtype=bool)
        self.food_collected = np.zeros(self.n_food, dtype=bool)
        self.step_count = 0

        # Initial observation includes food locations (visible at start)
        self.initial_obs = self._get_observation(show_food=True)
        return self.initial_obs.copy()

    def _get_observation(self, show_food: bool = False) -> np.ndarray:
        """Get current observation."""
        obs = [self.agent_pos[0] / self.grid_size, self.agent_pos[1] / self.grid_size]

        # Only show food locations in initial observation
        # After that, agent must remember where food was
        if show_food:
            for food_pos in self.food_locations:
                obs.extend([food_pos[0] / self.grid_size, food_pos[1] / self.grid_size])
        else:
            # After initial observation, food locations hidden
            # Agent must use memory (K_M) to find food
            obs.extend([0.0] * (2 * self.n_food))

        # Pad or truncate to obs_dim
        obs = np.array(obs[:self.obs_dim])
        if len(obs) < self.obs_dim:
            obs = np.concatenate([obs, np.zeros(self.obs_dim - len(obs))])

        return obs

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, Dict]:
        """Execute action (movement)."""
        self.step_count += 1

        # Action is 2D movement direction
        if len(action) >= 2:
            direction = action[:2]
        else:
            direction = np.concatenate([action, np.zeros(2 - len(action))])

        # Normalize and move
        direction = direction / (np.linalg.norm(direction) + 1e-8)
        self.agent_pos = self.agent_pos + direction * 0.5
        self.agent_pos = np.clip(self.agent_pos, 0, self.grid_size - 1)

        # Activate food after delay
        if self.step_count >= self.delay:
            self.food_available[:] = True

        # Check for food collection
        reward = 0.0
        for i, food_pos in enumerate(self.food_locations):
            if self.food_available[i] and not self.food_collected[i]:
                dist = np.linalg.norm(self.agent_pos - food_pos)
                if dist < 1.0:  # Collection radius
                    self.food_collected[i] = True
                    reward = 1.0

        # Observation after t=0 doesn't show food locations
        obs = self._get_observation(show_food=False)

        done = self.step_count >= self.episode_length or self.food_collected.all()

        info = {
            "step": self.step_count,
            "food_collected": int(self.food_collected.sum()),
            "food_available": self.food_available.all(),
        }

        return obs, float(reward), done, info


@dataclass
class CommonsEnvironment:
    """
    Environment for testing K_H (harmonic/normative dimension).

    A shared resource that regenerates slowly but can be depleted.
    High K_H agents should harvest sustainably.
    Low K_H agents over-harvest and cause collapse.

    Paper 9 Phase 4 validation environment.
    """

    grid_size: int = 20
    initial_resource: float = 100.0
    regeneration_rate: float = 0.1  # Resources regenerate at this rate
    collapse_threshold: float = 10.0  # Below this, ecosystem collapses
    episode_length: int = 200
    obs_dim: int = 4  # Agent position (2) + local resource (1) + global resource (1)

    def __post_init__(self):
        self.agent_pos = None
        self.resource_level = None
        self.step_count = 0

    def reset(self) -> np.ndarray:
        """Reset environment."""
        self.agent_pos = np.array([self.grid_size // 2, self.grid_size // 2], dtype=float)
        self.resource_level = self.initial_resource
        self.step_count = 0
        return self._get_observation()

    def _get_observation(self) -> np.ndarray:
        """Get current observation."""
        return np.array([
            self.agent_pos[0] / self.grid_size,
            self.agent_pos[1] / self.grid_size,
            min(1.0, self.resource_level / self.initial_resource),  # Normalized resource
            1.0 if self.resource_level > self.collapse_threshold else 0.0,  # Healthy indicator
        ])

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, Dict]:
        """Execute action (movement + harvest)."""
        self.step_count += 1

        # Action[0:2] = movement, action[2] = harvest rate (if available)
        if len(action) >= 2:
            direction = action[:2]
            harvest_rate = abs(action[2]) if len(action) > 2 else 0.5
        else:
            direction = np.concatenate([action, np.zeros(2 - len(action))])
            harvest_rate = 0.5

        # Move
        direction = direction / (np.linalg.norm(direction) + 1e-8)
        self.agent_pos = self.agent_pos + direction * 0.5
        self.agent_pos = np.clip(self.agent_pos, 0, self.grid_size - 1)

        # Harvest (capped by available resources)
        harvest_rate = np.clip(harvest_rate, 0, 1)
        harvest = min(harvest_rate * 2, self.resource_level)  # Max 2 units per step
        self.resource_level -= harvest
        reward = harvest

        # Resource regeneration (logistic growth)
        carrying_capacity = self.initial_resource
        growth = self.regeneration_rate * self.resource_level * (1 - self.resource_level / carrying_capacity)
        self.resource_level = max(0, self.resource_level + growth)

        # Check for collapse
        collapsed = self.resource_level < self.collapse_threshold
        done = self.step_count >= self.episode_length or collapsed

        info = {
            "step": self.step_count,
            "resource_level": self.resource_level,
            "collapsed": collapsed,
            "harvest": harvest,
            "sustainable_rate": self.regeneration_rate * self.resource_level * (1 - self.resource_level / carrying_capacity),
        }

        return self._get_observation(), float(reward), done, info

    def get_sustainable_harvest_rate(self) -> float:
        """Return the sustainable harvest rate at current resource level."""
        carrying_capacity = self.initial_resource
        return self.regeneration_rate * self.resource_level * (1 - self.resource_level / carrying_capacity)


# =============================================================================
# AGENTS
# =============================================================================

@dataclass
class RandomAgent:
    """Random agent (baseline, low K expected)."""

    action_dim: int = 10

    def get_action_probs(self, obs: np.ndarray) -> np.ndarray:
        """Return uniform action probabilities."""
        return np.ones(self.action_dim) / self.action_dim

    def select_action(self, obs: np.ndarray) -> np.ndarray:
        """Select random action."""
        return np.random.randn(self.action_dim)

    def update(self, *args, **kwargs):
        """No learning."""
        pass


@dataclass
class LinearAgent:
    """Simple linear policy agent."""

    obs_dim: int = 20
    action_dim: int = 10
    learning_rate: float = 0.01

    def __post_init__(self):
        self.W = np.random.randn(self.action_dim, self.obs_dim) * 0.1
        self.b = np.zeros(self.action_dim)

    def get_action_probs(self, obs: np.ndarray) -> np.ndarray:
        """Compute softmax action probabilities."""
        logits = self.W @ obs + self.b
        # Softmax
        exp_logits = np.exp(logits - logits.max())
        probs = exp_logits / exp_logits.sum()
        return probs

    def select_action(self, obs: np.ndarray) -> np.ndarray:
        """Select action from policy."""
        return np.tanh(self.W @ obs + self.b)

    def update(self, obs: np.ndarray, action: np.ndarray, reward: float):
        """Simple gradient update."""
        grad_W = np.outer(reward * action, obs)
        grad_b = reward * action
        self.W += self.learning_rate * grad_W
        self.b += self.learning_rate * grad_b


@dataclass
class CMAESAgent:
    """CMA-ES optimized agent (high K expected, from G8 methodology)."""

    obs_dim: int = 20
    action_dim: int = 10
    population: int = 20
    sigma: float = 0.5

    def __post_init__(self):
        self.W = np.random.randn(self.action_dim, self.obs_dim) * 0.1
        self.b = np.zeros(self.action_dim)
        self.mean = np.concatenate([self.W.flatten(), self.b])
        self.generation = 0

    def get_action_probs(self, obs: np.ndarray) -> np.ndarray:
        """Compute softmax action probabilities."""
        logits = self.W @ obs + self.b
        exp_logits = np.exp(logits - logits.max())
        probs = exp_logits / exp_logits.sum()
        return probs

    def select_action(self, obs: np.ndarray) -> np.ndarray:
        """Select action from policy."""
        return np.tanh(self.W @ obs + self.b)

    def sample_population(self) -> List[np.ndarray]:
        """Sample population for CMA-ES."""
        population = []
        for _ in range(self.population):
            sample = self.mean + self.sigma * np.random.randn(len(self.mean))
            population.append(sample)
        return population

    def update_from_population(self, population: List[np.ndarray], fitnesses: List[float]):
        """Update mean from best individuals."""
        # Sort by fitness (descending)
        indices = np.argsort(fitnesses)[::-1]
        elite_count = self.population // 5
        elite = [population[i] for i in indices[:elite_count]]

        # Update mean
        self.mean = np.mean(elite, axis=0)

        # Update parameters
        n_w = self.action_dim * self.obs_dim
        self.W = self.mean[:n_w].reshape(self.action_dim, self.obs_dim)
        self.b = self.mean[n_w:]

        self.generation += 1

    def update(self, *args, **kwargs):
        """CMA-ES doesn't use per-step updates."""
        pass


@dataclass
class RecurrentAgent:
    """
    Simple recurrent agent that maintains hidden state.

    This agent uses a simple GRU-like update to maintain temporal memory,
    which should result in non-zero K_M values (unlike feedforward agents).

    Architecture:
    - hidden_state h_t = tanh(W_h @ h_{t-1} + W_o @ obs_t)
    - action = tanh(W_a @ concat(h_t, obs_t))

    Paper 9 Phase 2 validation: Tests K_M (temporal depth).
    """

    obs_dim: int = 20
    action_dim: int = 10
    hidden_dim: int = 16
    learning_rate: float = 0.01

    def __post_init__(self):
        # Hidden-to-hidden weights
        self.W_h = np.random.randn(self.hidden_dim, self.hidden_dim) * 0.3
        # Observation-to-hidden weights
        self.W_o = np.random.randn(self.hidden_dim, self.obs_dim) * 0.3
        # Hidden+obs to action weights
        self.W_a = np.random.randn(self.action_dim, self.hidden_dim + self.obs_dim) * 0.3
        self.b_a = np.zeros(self.action_dim)
        # Hidden state
        self.hidden = np.zeros(self.hidden_dim)
        # For learning: track recent states
        self.recent_obs = []
        self.recent_hidden = []

    def reset_hidden(self):
        """Reset hidden state at episode start."""
        self.hidden = np.zeros(self.hidden_dim)
        self.recent_obs = []
        self.recent_hidden = []

    def get_action_probs(self, obs: np.ndarray) -> np.ndarray:
        """Compute softmax action probabilities (for compatibility)."""
        combined = np.concatenate([self.hidden, obs])
        logits = self.W_a @ combined + self.b_a
        exp_logits = np.exp(logits - logits.max())
        probs = exp_logits / exp_logits.sum()
        return probs

    def select_action(self, obs: np.ndarray) -> np.ndarray:
        """Select action from recurrent policy."""
        # Update hidden state (GRU-like)
        h_input = self.W_h @ self.hidden + self.W_o @ obs
        self.hidden = np.tanh(h_input)

        # Store for potential learning
        self.recent_obs.append(obs.copy())
        self.recent_hidden.append(self.hidden.copy())

        # Compute action from hidden + current obs
        combined = np.concatenate([self.hidden, obs])
        action = np.tanh(self.W_a @ combined + self.b_a)
        return action

    def update(self, obs: np.ndarray, action: np.ndarray, reward: float):
        """Simple gradient update (approximate)."""
        # Simple REINFORCE-style update for the action weights
        combined = np.concatenate([self.hidden, obs])
        grad_W_a = np.outer(reward * action, combined)
        grad_b_a = reward * action
        self.W_a += self.learning_rate * grad_W_a
        self.b_a += self.learning_rate * grad_b_a

        # Small update to hidden dynamics based on reward
        if len(self.recent_obs) > 1:
            prev_obs = self.recent_obs[-2]
            grad_W_o = np.outer(reward * self.hidden, prev_obs) * 0.1
            self.W_o += self.learning_rate * grad_W_o


# =============================================================================
# EPISODE RUNNER
# =============================================================================

def run_episode(
    env: CoordinationEnvironment,
    agent,
    collect_probs: bool = True,
    coherence_formula: str = "original",
    compute_kosmic: bool = False,
    agent_B=None,  # For K_S (social coherence) in multi-agent settings
) -> Dict[str, Any]:
    """
    Run single episode and collect metrics.

    Args:
        env: Environment to run in
        agent: Primary agent
        collect_probs: Whether to collect action probabilities
        coherence_formula: Formula for unified coherence
        compute_kosmic: If True, compute full 7D Kosmic K-vector (Paper 9)
        agent_B: Optional second agent for K_S computation

    Returns:
        Dictionary with observations, actions, rewards, and computed indices.
        If compute_kosmic=True, includes 'kosmic_k' with full K-vector.
    """
    obs = env.reset()

    # Reset recurrent agent hidden state if applicable
    if hasattr(agent, 'reset_hidden'):
        agent.reset_hidden()

    observations = []
    actions = []
    action_probs = []
    rewards = []

    done = False
    while not done:
        # Get action probabilities and select action
        probs = agent.get_action_probs(obs)
        action = agent.select_action(obs)

        # Step environment
        next_obs, reward, done, info = env.step(action)

        # Store data
        observations.append(obs.copy())
        actions.append(action.copy())
        if collect_probs:
            action_probs.append(probs.copy())
        rewards.append(reward)

        # Update agent
        agent.update(obs, action, reward)

        obs = next_obs

    # Convert to arrays
    observations = np.array(observations)
    actions = np.array(actions)
    action_probs = np.array(action_probs) if collect_probs else None
    rewards = np.array(rewards)

    # Compute metrics
    obs_norms = np.linalg.norm(observations, axis=1)
    act_norms = np.linalg.norm(actions, axis=1)

    k_index = compute_k_index(obs_norms, act_norms)
    or_index = compute_or_index(actions, observations)  # Paper 6 methodology
    coherence = compute_unified_coherence(k_index, or_index, formula=coherence_formula)

    result = {
        "observations": observations,
        "actions": actions,
        "action_probs": action_probs,
        "rewards": rewards,
        "obs_norms": obs_norms,
        "act_norms": act_norms,
        "k_index": k_index,
        "or_index": or_index,
        "coherence": coherence,
        "total_reward": float(rewards.sum()),
        "mean_reward": float(rewards.mean()),
    }

    # Compute Kosmic K-vector (Paper 9: 7D framework)
    if compute_kosmic and HAS_KOSMIC:
        # Prepare actions_B for K_S if agent_B provided
        actions_B = None
        if agent_B is not None:
            # Run agent_B on same observations (for correlation)
            actions_B_list = []
            for obs_t in observations:
                action_B = agent_B.select_action(obs_t)
                actions_B_list.append(action_B)
            actions_B = np.array(actions_B_list)

        # Get normative reference if environment supports it
        normative_ref = get_sustainability_reference(env) if hasattr(env, 'regeneration_rate') else None

        kosmic_result = compute_kosmic_index(
            observations=observations,
            actions=actions,
            actions_B=actions_B,
            normative_reference=normative_ref,
            history_len=5,
        )
        result["kosmic_k"] = kosmic_result

    return result


def get_sustainability_reference(env) -> callable:
    """
    Create a sustainability-based normative reference for K_H in Commons environment.

    The ideal sustainable action maintains the resource at steady state:
    - Harvest rate = Regeneration rate
    - optimal_harvest = resource * regeneration_rate

    Returns:
        Callable that takes observation and returns ideal action
    """
    if not hasattr(env, 'regeneration_rate'):
        return None

    def normative_action(obs: np.ndarray) -> np.ndarray:
        """Return sustainable action based on current resource level."""
        # For Commons: obs[0] = resource level (normalized)
        # Ideal: harvest at regeneration rate to maintain steady state
        resource = obs[0] if len(obs) > 0 else 0.5

        # Sustainable harvest: small constant extraction
        # Action = [move_x, move_y, harvest_rate, ...]
        action_dim = getattr(env, 'action_dim', 4)
        ideal = np.zeros(action_dim)

        # Conservative harvesting (stay in place, minimal extraction)
        if action_dim >= 3:
            ideal[2] = 0.1 * resource  # Scale harvest to resource
        else:
            ideal = np.ones(action_dim) * 0.1 * resource

        return ideal

    return normative_action


def run_multiagent_episode(
    env,
    agent_A,
    agent_B,
    compute_kosmic: bool = True,
) -> Dict[str, Any]:
    """
    Run multi-agent episode for K_S (Social Coherence) validation.

    Two agents interact with the same environment simultaneously.
    K_S measures how coordinated their actions are.

    Paper 9 Phase 3: Multi-agent K_S experiments.
    """
    obs = env.reset()

    # Reset agents if they have hidden state
    if hasattr(agent_A, 'reset_hidden'):
        agent_A.reset_hidden()
    if hasattr(agent_B, 'reset_hidden'):
        agent_B.reset_hidden()

    observations = []
    actions_A = []
    actions_B = []
    rewards_A = []
    rewards_B = []

    done = False
    while not done:
        # Both agents observe same state
        action_a = agent_A.select_action(obs)
        action_b = agent_B.select_action(obs)

        # Average actions for environment step (simple coordination model)
        avg_action = (action_a + action_b) / 2
        next_obs, reward, done, info = env.step(avg_action)

        # Store data
        observations.append(obs.copy())
        actions_A.append(action_a.copy())
        actions_B.append(action_b.copy())
        rewards_A.append(reward)
        rewards_B.append(reward)

        # Update both agents
        agent_A.update(obs, action_a, reward)
        agent_B.update(obs, action_b, reward)

        obs = next_obs

    # Convert to arrays
    observations = np.array(observations)
    actions_A = np.array(actions_A)
    actions_B = np.array(actions_B)

    # Compute K_S (social coherence)
    obs_norms = np.linalg.norm(observations, axis=1)
    act_norms_A = np.linalg.norm(actions_A, axis=1)
    act_norms_B = np.linalg.norm(actions_B, axis=1)

    # Action magnitude correlation between agents
    if np.std(act_norms_A) > 1e-10 and np.std(act_norms_B) > 1e-10:
        k_s, _ = pearsonr(act_norms_A, act_norms_B)
        k_s = abs(k_s) if not np.isnan(k_s) else 0.0
    else:
        k_s = 0.0

    result = {
        "observations": observations,
        "actions_A": actions_A,
        "actions_B": actions_B,
        "K_S": k_s,
        "total_reward": float(np.sum(rewards_A)),
    }

    # Full Kosmic K-vector with K_S
    if compute_kosmic and HAS_KOSMIC:
        kosmic_result = compute_kosmic_index(
            observations=observations,
            actions=actions_A,
            actions_B=actions_B,
            normative_reference=get_sustainability_reference(env),
            history_len=5,
        )
        result["kosmic_k"] = kosmic_result

    return result


# =============================================================================
# TRACK L1: CORRELATION STUDY
# =============================================================================

def run_track_l1(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Track L1: Correlation study between K-Index and O/R Index.

    Generates agents across K-Index spectrum and measures correlation.
    """
    print("\n" + "=" * 60)
    print("🔗 TRACK L1: K-Index ↔ O/R Index Correlation Study")
    print("=" * 60)

    l1_config = config.get("track_l1", {})
    n_episodes = l1_config.get("episodes", 200)

    env_config = l1_config.get("environment", {})
    env = CoordinationEnvironment(
        obs_dim=env_config.get("observations", 20),
        action_dim=env_config.get("actions", 10),
        episode_length=env_config.get("episode_length", 200),
    )

    # Generate diverse agent population
    agents = []

    # Random agents (50)
    for _ in range(50):
        agents.append(("random", RandomAgent(action_dim=env.action_dim)))

    # Linear agents with varying learning rates (50)
    for lr in np.linspace(0.001, 0.1, 50):
        agents.append(("linear", LinearAgent(
            obs_dim=env.obs_dim,
            action_dim=env.action_dim,
            learning_rate=lr,
        )))

    # CMA-ES style agents (50)
    for sigma in np.linspace(0.1, 1.0, 50):
        agent = CMAESAgent(
            obs_dim=env.obs_dim,
            action_dim=env.action_dim,
            sigma=sigma,
        )
        agents.append(("cmaes", agent))

    # Pre-trained linear agents (50)
    for _ in range(50):
        agent = LinearAgent(obs_dim=env.obs_dim, action_dim=env.action_dim)
        # Pre-train for 100 steps
        for _ in range(100):
            obs = env.reset()
            for _ in range(50):
                action = agent.select_action(obs)
                next_obs, reward, done, _ = env.step(action)
                agent.update(obs, action, reward)
                if done:
                    break
                obs = next_obs
        agents.append(("pretrained", agent))

    print(f"📊 Generated {len(agents)} agents across K-Index spectrum")

    # Collect K and O/R for each agent
    results = []
    for i, (agent_type, agent) in enumerate(agents):
        if i % 20 == 0:
            print(f"  Running agent {i+1}/{len(agents)}...")

        episode_result = run_episode(env, agent)
        results.append({
            "agent_type": agent_type,
            "agent_idx": i,
            "k_index": episode_result["k_index"],
            "or_index": episode_result["or_index"],
            "coherence": episode_result["coherence"],
            "total_reward": episode_result["total_reward"],
        })

    # Extract arrays for correlation analysis
    k_values = np.array([r["k_index"] for r in results])
    or_values = np.array([r["or_index"] for r in results])
    coherence_values = np.array([r["coherence"] for r in results])
    reward_values = np.array([r["total_reward"] for r in results])

    # Remove NaN values
    valid_mask = ~(np.isnan(k_values) | np.isnan(or_values))
    k_valid = k_values[valid_mask]
    or_valid = or_values[valid_mask]
    coherence_valid = coherence_values[valid_mask]
    reward_valid = reward_values[valid_mask]

    # Compute correlations
    r_pearson, p_pearson = pearsonr(k_valid, or_valid)
    r_spearman, p_spearman = spearmanr(k_valid, or_valid)
    tau, p_kendall = kendalltau(k_valid, or_valid)

    # K vs performance
    r_k_perf, p_k_perf = pearsonr(k_valid, reward_valid)
    # O/R vs performance
    r_or_perf, p_or_perf = pearsonr(or_valid, reward_valid)
    # Coherence vs performance
    r_coh_perf, p_coh_perf = pearsonr(coherence_valid, reward_valid)

    print("\n" + "-" * 40)
    print("📈 CORRELATION RESULTS")
    print("-" * 40)
    print(f"K ↔ O/R (Pearson):   r = {r_pearson:.4f}, p = {p_pearson:.6f}")
    print(f"K ↔ O/R (Spearman):  ρ = {r_spearman:.4f}, p = {p_spearman:.6f}")
    print(f"K ↔ O/R (Kendall):   τ = {tau:.4f}, p = {p_kendall:.6f}")
    print()
    print(f"K → Performance:     r = {r_k_perf:.4f}, p = {p_k_perf:.6f}")
    print(f"O/R → Performance:   r = {r_or_perf:.4f}, p = {p_or_perf:.6f}")
    print(f"Coherence → Perf:    r = {r_coh_perf:.4f}, p = {p_coh_perf:.6f}")
    print("-" * 40)

    # Determine if hypothesis confirmed
    hypothesis_confirmed = abs(r_pearson) > 0.3 and p_pearson < 0.001

    return {
        "phase": "L1",
        "n_agents": len(agents),
        "n_valid": int(valid_mask.sum()),
        "correlations": {
            "k_or_pearson": {"r": r_pearson, "p": p_pearson},
            "k_or_spearman": {"rho": r_spearman, "p": p_spearman},
            "k_or_kendall": {"tau": tau, "p": p_kendall},
            "k_performance": {"r": r_k_perf, "p": p_k_perf},
            "or_performance": {"r": r_or_perf, "p": p_or_perf},
            "coherence_performance": {"r": r_coh_perf, "p": p_coh_perf},
        },
        "statistics": {
            "k_mean": float(k_valid.mean()),
            "k_std": float(k_valid.std()),
            "or_mean": float(or_valid.mean()),
            "or_std": float(or_valid.std()),
            "coherence_mean": float(coherence_valid.mean()),
            "coherence_std": float(coherence_valid.std()),
        },
        "hypothesis_confirmed": hypothesis_confirmed,
        "agent_results": results,
    }


# =============================================================================
# TRACK L2: UNIFIED INDEX VALIDATION
# =============================================================================

def run_track_l2(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Track L2: Compare predictive power of K, O/R, and unified index.
    """
    print("\n" + "=" * 60)
    print("🔗 TRACK L2: Unified Index Validation")
    print("=" * 60)

    l2_config = config.get("track_l2", {})
    n_episodes = l2_config.get("episodes", 300)

    env = CoordinationEnvironment(
        obs_dim=20,
        action_dim=10,
        episode_length=200,
    )

    # Generate agents and collect data
    all_data = []

    for i in range(n_episodes):
        if i % 50 == 0:
            print(f"  Running episode {i+1}/{n_episodes}...")

        # Randomly select agent type
        agent_type = np.random.choice(["random", "linear", "pretrained"])

        if agent_type == "random":
            agent = RandomAgent(action_dim=env.action_dim)
        elif agent_type == "linear":
            agent = LinearAgent(
                obs_dim=env.obs_dim,
                action_dim=env.action_dim,
                learning_rate=np.random.uniform(0.001, 0.1),
            )
        else:
            agent = LinearAgent(obs_dim=env.obs_dim, action_dim=env.action_dim)
            # Pre-train
            for _ in range(50):
                obs = env.reset()
                for _ in range(30):
                    action = agent.select_action(obs)
                    next_obs, reward, done, _ = env.step(action)
                    agent.update(obs, action, reward)
                    if done:
                        break
                    obs = next_obs

        result = run_episode(env, agent)
        all_data.append({
            "k": result["k_index"],
            "or": result["or_index"],
            "coherence": result["coherence"],
            "performance": result["total_reward"],
        })

    # Convert to arrays
    k = np.array([d["k"] for d in all_data])
    or_idx = np.array([d["or"] for d in all_data])
    coherence = np.array([d["coherence"] for d in all_data])
    performance = np.array([d["performance"] for d in all_data])

    # Remove invalid
    valid = ~(np.isnan(k) | np.isnan(or_idx) | np.isnan(coherence))
    k, or_idx, coherence, performance = k[valid], or_idx[valid], coherence[valid], performance[valid]

    # Compute R² for each predictor
    def compute_r_squared(x, y):
        """Compute R² (coefficient of determination)."""
        ss_res = np.sum((y - x) ** 2)
        ss_tot = np.sum((y - y.mean()) ** 2)
        return 1 - ss_res / ss_tot if ss_tot > 0 else 0

    # Simple correlation-based prediction
    r_k, _ = pearsonr(k, performance)
    r_or, _ = pearsonr(or_idx, performance)
    r_coh, _ = pearsonr(coherence, performance)

    # R² values (approximation via r²)
    r2_k = r_k ** 2
    r2_or = r_or ** 2
    r2_coh = r_coh ** 2

    print("\n" + "-" * 40)
    print("📊 PREDICTIVE POWER COMPARISON")
    print("-" * 40)
    print(f"K-Index alone:      r = {r_k:.4f}, R² = {r2_k:.4f}")
    print(f"O/R Index alone:    r = {r_or:.4f}, R² = {r2_or:.4f}")
    print(f"Unified Coherence:  r = {r_coh:.4f}, R² = {r2_coh:.4f}")
    print("-" * 40)

    best_predictor = "coherence" if r2_coh >= max(r2_k, r2_or) else ("k" if r2_k > r2_or else "or")
    improvement = r2_coh - max(r2_k, r2_or)

    print(f"\n✨ Best predictor: {best_predictor}")
    print(f"   Unified improvement: {improvement:.4f} R²")

    return {
        "phase": "L2",
        "n_valid": int(valid.sum()),
        "r_squared": {
            "k_only": r2_k,
            "or_only": r2_or,
            "unified_coherence": r2_coh,
        },
        "correlations": {
            "k_perf": r_k,
            "or_perf": r_or,
            "coherence_perf": r_coh,
        },
        "best_predictor": best_predictor,
        "unified_improvement": improvement,
        "hypothesis_confirmed": improvement > 0.05,
    }


# =============================================================================
# TRACK L4: UNIFIED OPTIMIZATION
# =============================================================================

def run_track_l4(config: Dict[str, Any], formula: str = "original") -> Dict[str, Any]:
    """
    Track L4: Optimize for unified coherence using CMA-ES.

    Goal: Cross K > 1.5 threshold via unified optimization.

    Args:
        config: Configuration dict
        formula: Coherence formula to use (original, multiplicative, k_only, etc.)
    """
    print("\n" + "=" * 60)
    print(f"🔗 TRACK L4: Unified Optimization (CMA-ES) - Formula: {formula}")
    print("=" * 60)

    l4_config = config.get("track_l4", {})
    algo_config = l4_config.get("algorithm", {})

    population_size = algo_config.get("population", 20)
    n_generations = algo_config.get("generations", 100)
    episodes_per_candidate = 3

    env = CoordinationEnvironment(
        obs_dim=20,
        action_dim=10,
        episode_length=200,
    )

    # Initialize CMA-ES
    param_dim = env.action_dim * env.obs_dim + env.action_dim
    mean = np.zeros(param_dim)
    sigma = 0.5
    cov = np.eye(param_dim)

    best_k = 0.0
    best_coherence = 0.0
    best_params = None
    history = []

    for gen in range(n_generations):
        # Sample population
        population = []
        for _ in range(population_size):
            sample = mean + sigma * np.random.randn(param_dim)
            population.append(sample)

        # Evaluate each candidate
        fitnesses = []
        k_values = []
        coherence_values = []

        for params in population:
            # Create agent from parameters
            n_w = env.action_dim * env.obs_dim
            W = params[:n_w].reshape(env.action_dim, env.obs_dim)
            b = params[n_w:]

            agent = LinearAgent(obs_dim=env.obs_dim, action_dim=env.action_dim)
            agent.W = W
            agent.b = b

            # Evaluate over multiple episodes
            episode_coherences = []
            episode_ks = []

            for _ in range(episodes_per_candidate):
                result = run_episode(env, agent, coherence_formula=formula)
                if not np.isnan(result["coherence"]):
                    episode_coherences.append(result["coherence"])
                    episode_ks.append(result["k_index"])

            mean_coherence = np.mean(episode_coherences) if episode_coherences else 0.0
            mean_k = np.mean(episode_ks) if episode_ks else 0.0

            fitnesses.append(mean_coherence)
            k_values.append(mean_k)
            coherence_values.append(mean_coherence)

        # Update CMA-ES (simple version: use elite mean)
        elite_count = population_size // 5
        elite_indices = np.argsort(fitnesses)[-elite_count:]
        elite = [population[i] for i in elite_indices]
        mean = np.mean(elite, axis=0)

        # Track best
        gen_best_idx = np.argmax(fitnesses)
        gen_best_k = k_values[gen_best_idx]
        gen_best_coh = coherence_values[gen_best_idx]

        if gen_best_coh > best_coherence:
            best_coherence = gen_best_coh
            best_k = gen_best_k
            best_params = population[gen_best_idx].copy()

        history.append({
            "generation": gen,
            "best_k": gen_best_k,
            "best_coherence": gen_best_coh,
            "mean_k": np.mean(k_values),
            "mean_coherence": np.mean(coherence_values),
        })

        if gen % 10 == 0:
            print(f"  Gen {gen:3d}: best_K = {gen_best_k:.4f}, best_coh = {gen_best_coh:.4f}, "
                  f"all-time best_K = {best_k:.4f}")

        # Check if threshold crossed
        if best_k >= 1.5:
            print(f"\n🎉 THRESHOLD CROSSED at generation {gen}!")
            break

    print("\n" + "-" * 40)
    print("📊 UNIFIED OPTIMIZATION RESULTS")
    print("-" * 40)
    print(f"Best K-Index:     {best_k:.4f}")
    print(f"Best Coherence:   {best_coherence:.4f}")
    print(f"Threshold (1.5):  {'✅ CROSSED' if best_k >= 1.5 else '❌ Not crossed'}")
    print("-" * 40)

    return {
        "phase": "L4",
        "formula": formula,
        "n_generations": len(history),
        "best_k_index": best_k,
        "best_coherence": best_coherence,
        "threshold_crossed": best_k >= 1.5,
        "history": history,
    }


# =============================================================================
# TRACK L4b: PAPER 6-STYLE O/R USAGE (Regularization & Adaptive)
# =============================================================================

def run_track_l4_paper6_style(
    config: Dict[str, Any],
    mode: str = "regularization"
) -> Dict[str, Any]:
    """
    Track L4b: Use O/R in Paper 6 style (regularization or adaptive).

    Paper 6 approaches:
    - "regularization": fitness = K - λ * penalty(O/R)
      Like CR-REINFORCE: penalize high O/R (inconsistent behavior)
    - "adaptive": Use O/R to adjust CMA-ES hyperparameters
      Like OR-PPO: adapt exploration based on O/R levels

    Args:
        config: Configuration dict
        mode: "regularization" or "adaptive"
    """
    print("\n" + "=" * 60)
    print(f"🔗 TRACK L4b: Paper 6-Style O/R Usage - Mode: {mode}")
    print("=" * 60)

    l4_config = config.get("track_l4", {})
    algo_config = l4_config.get("algorithm", {})

    population_size = algo_config.get("population", 20)
    n_generations = algo_config.get("generations", 100)
    episodes_per_candidate = 3

    # Regularization parameters (like CR-REINFORCE)
    or_lambda = 0.1  # Regularization strength
    or_target = 0.0  # Target O/R (0 = neutral, negative = consistent)

    env = CoordinationEnvironment(
        obs_dim=20,
        action_dim=10,
        episode_length=200,
    )

    # Initialize CMA-ES
    param_dim = env.action_dim * env.obs_dim + env.action_dim
    mean = np.zeros(param_dim)
    sigma = 0.5
    base_sigma = 0.5
    cov = np.eye(param_dim)

    best_k = 0.0
    best_or = 0.0
    best_fitness = -np.inf
    best_params = None
    history = []

    for gen in range(n_generations):
        # Sample population
        population = []
        for _ in range(population_size):
            sample = mean + sigma * np.random.randn(param_dim)
            population.append(sample)

        # Evaluate each candidate
        fitnesses = []
        k_values = []
        or_values = []

        for params in population:
            # Create agent from parameters
            n_w = env.action_dim * env.obs_dim
            W = params[:n_w].reshape(env.action_dim, env.obs_dim)
            b = params[n_w:]

            agent = LinearAgent(obs_dim=env.obs_dim, action_dim=env.action_dim)
            agent.W = W
            agent.b = b

            # Evaluate over multiple episodes
            episode_ks = []
            episode_ors = []

            for _ in range(episodes_per_candidate):
                result = run_episode(env, agent, coherence_formula="k_only")
                if not np.isnan(result["k_index"]):
                    episode_ks.append(result["k_index"])
                if not np.isnan(result["or_index"]):
                    episode_ors.append(result["or_index"])

            mean_k = np.mean(episode_ks) if episode_ks else 0.0
            mean_or = np.mean(episode_ors) if episode_ors else 0.0

            # Compute fitness based on mode
            if mode == "regularization":
                # CR-REINFORCE style: K with O/R penalty
                # Penalize when O/R is high (inconsistent behavior)
                or_penalty = max(0, mean_or - or_target)
                fitness = mean_k - or_lambda * or_penalty
            else:
                # For adaptive mode, fitness is just K
                # O/R affects hyperparameters, not fitness
                fitness = mean_k

            fitnesses.append(fitness)
            k_values.append(mean_k)
            or_values.append(mean_or)

        # Adaptive mode: adjust sigma based on population O/R
        if mode == "adaptive":
            pop_mean_or = np.mean(or_values)
            # High O/R (inconsistent) → increase exploration
            # Low O/R (consistent) → decrease exploration (exploit)
            if pop_mean_or > 1.0:
                sigma = min(base_sigma * 1.5, sigma * 1.1)  # Increase exploration
            elif pop_mean_or < -0.5:
                sigma = max(base_sigma * 0.5, sigma * 0.9)  # Decrease exploration
            # Else keep sigma stable

        # Update CMA-ES (simple version: use elite mean)
        elite_count = population_size // 5
        elite_indices = np.argsort(fitnesses)[-elite_count:]
        elite = [population[i] for i in elite_indices]
        mean = np.mean(elite, axis=0)

        # Track best by K (our ultimate goal)
        gen_best_idx = np.argmax(k_values)
        gen_best_k = k_values[gen_best_idx]
        gen_best_or = or_values[gen_best_idx]
        gen_best_fitness = fitnesses[gen_best_idx]

        if gen_best_k > best_k:
            best_k = gen_best_k
            best_or = gen_best_or
            best_fitness = gen_best_fitness
            best_params = population[gen_best_idx].copy()

        history.append({
            "generation": gen,
            "best_k": gen_best_k,
            "best_or": gen_best_or,
            "best_fitness": gen_best_fitness,
            "mean_k": np.mean(k_values),
            "mean_or": np.mean(or_values),
            "sigma": sigma if mode == "adaptive" else base_sigma,
        })

        if gen % 10 == 0:
            sigma_str = f", σ={sigma:.3f}" if mode == "adaptive" else ""
            print(f"  Gen {gen:3d}: best_K = {gen_best_k:.4f}, O/R = {gen_best_or:.2f}, "
                  f"all-time best_K = {best_k:.4f}{sigma_str}")

        # Check if threshold crossed
        if best_k >= 1.5:
            print(f"\n🎉 THRESHOLD CROSSED at generation {gen}!")
            break

    print("\n" + "-" * 40)
    print(f"📊 PAPER 6-STYLE RESULTS ({mode.upper()})")
    print("-" * 40)
    print(f"Best K-Index:     {best_k:.4f}")
    print(f"Best O/R Index:   {best_or:.4f}")
    print(f"Threshold (1.5):  {'✅ CROSSED' if best_k >= 1.5 else '❌ Not crossed'}")
    print("-" * 40)

    return {
        "phase": "L4b",
        "mode": mode,
        "n_generations": len(history),
        "best_k_index": best_k,
        "best_or_index": best_or,
        "best_fitness": best_fitness,
        "threshold_crossed": best_k >= 1.5,
        "history": history,
    }


# =============================================================================
# TRACK L6: KOSMIC K-VECTOR VALIDATION (Paper 9)
# =============================================================================

def run_track_l6(config: Dict[str, Any], environment: str = "coordination") -> Dict[str, Any]:
    """
    Track L6: Validate the 7D Kosmic K-Vector framework.

    Tests whether the 7D K-vector distinguishes agent types better than K_R alone.
    This implements Phase 1 of the experimental design from Paper 9.

    Key hypotheses:
    - H1: K_R alone is necessary but insufficient
    - H2: K_A adds predictive power beyond K_R
    - H3: K_P distinguishes good from great agents

    Args:
        config: Configuration dict
        environment: Which environment to use:
            - "coordination": Standard Track L environment
            - "simple": Simplified env (achieves K > 1.9)
            - "delayed": Delayed foraging (tests K_M)
            - "commons": Commons environment (tests K_H)
    """
    if not HAS_KOSMIC:
        print("\n❌ ERROR: kosmic_k_index.py not available. Cannot run L6.")
        return {"phase": "L6", "error": "kosmic_k_index not available"}

    print("\n" + "=" * 60)
    print(f"🌌 TRACK L6: Kosmic K-Vector Validation [{environment.upper()}]")
    print("=" * 60)
    print("Testing 7D K-vector: (K_R, K_A, K_I, K_P, K_M, K_S, K_H)")

    l6_config = config.get("track_l6", {})
    n_agents_per_type = l6_config.get("agents_per_type", 30)

    # Select environment
    if environment == "simple":
        env = SimpleEnvironment(obs_dim=20, action_dim=10, episode_length=200)
    elif environment == "delayed":
        env = DelayedForagingEnvironment(grid_size=10, n_food=5, delay=10, episode_length=100)
    elif environment == "commons":
        env = CommonsEnvironment(grid_size=20, episode_length=200)
    else:  # coordination (default)
        env = CoordinationEnvironment(obs_dim=20, action_dim=10, episode_length=200)

    # Get dimensions from environment
    obs_dim = getattr(env, 'obs_dim', 8)  # Default for grid-based envs
    action_dim = getattr(env, 'action_dim', 4)  # Default for movement envs

    # Generate diverse agent population (same as L1 but compute full K-vector)
    agent_configs = [
        ("random", lambda: RandomAgent(action_dim=action_dim)),
        ("linear_untrained", lambda: LinearAgent(
            obs_dim=obs_dim, action_dim=action_dim, learning_rate=0.01)),
        ("linear_trained", lambda: _train_linear_agent(env, obs_dim, action_dim, n_episodes=50)),
        ("cmaes", lambda: CMAESAgent(
            obs_dim=obs_dim, action_dim=action_dim, sigma=0.5)),
        # Recurrent agent for K_M validation (Paper 9 Phase 2)
        ("recurrent", lambda: RecurrentAgent(
            obs_dim=obs_dim, action_dim=action_dim, hidden_dim=16, learning_rate=0.01)),
    ]

    results = []
    for agent_type, agent_factory in agent_configs:
        print(f"\n📊 Testing {agent_type} agents ({n_agents_per_type})...")

        for i in range(n_agents_per_type):
            agent = agent_factory()
            episode_result = run_episode(env, agent, compute_kosmic=True)

            if "kosmic_k" in episode_result:
                kosmic = episode_result["kosmic_k"]
                k_vec = kosmic["K_vector"]

                # Extract values from descriptive keys
                def get_k(key_prefix):
                    for k, v in k_vec.items():
                        if k.startswith(key_prefix):
                            return v if v is not None else 0.0
                    return 0.0

                results.append({
                    "agent_type": agent_type,
                    "agent_idx": i,
                    # Original metrics
                    "k_index": episode_result["k_index"],
                    "or_index": episode_result["or_index"],
                    "total_reward": episode_result["total_reward"],
                    # 7D Kosmic K-vector
                    "K_R": get_k("K_R"),
                    "K_A": get_k("K_A"),
                    "K_I": get_k("K_I"),
                    "K_P": get_k("K_P"),
                    "K_M": get_k("K_M"),
                    "K_S": get_k("K_S"),
                    "K_H": get_k("K_H"),
                    "K_sigma": kosmic["K_sigma"],
                    "K_geo": kosmic["K_geo"],
                })
            else:
                print(f"  ⚠️  Agent {i} failed to compute kosmic_k")

    # Analysis: Compare agent types across K dimensions
    print("\n" + "-" * 60)
    print("📈 KOSMIC K-VECTOR RESULTS BY AGENT TYPE")
    print("-" * 60)

    k_dims = ["K_R", "K_A", "K_I", "K_P", "K_M", "K_S", "K_H"]
    agent_types = list(set(r["agent_type"] for r in results))

    # Compute means per agent type
    type_stats = {}
    for agent_type in agent_types:
        type_results = [r for r in results if r["agent_type"] == agent_type]
        type_stats[agent_type] = {
            dim: {
                "mean": np.mean([r[dim] for r in type_results]),
                "std": np.std([r[dim] for r in type_results]),
            }
            for dim in k_dims
        }
        type_stats[agent_type]["total_reward"] = {
            "mean": np.mean([r["total_reward"] for r in type_results]),
            "std": np.std([r["total_reward"] for r in type_results]),
        }

    # Print comparison table
    print(f"\n{'Agent Type':<18} {'K_R':<8} {'K_A':<8} {'K_I':<8} {'K_P':<8} {'K_M':<8} {'Reward':<10}")
    print("-" * 70)
    for agent_type in sorted(agent_types):
        stats = type_stats[agent_type]
        print(f"{agent_type:<18} "
              f"{stats['K_R']['mean']:.3f}    "
              f"{stats['K_A']['mean']:.3f}    "
              f"{stats['K_I']['mean']:.3f}    "
              f"{stats['K_P']['mean']:.3f}    "
              f"{stats['K_M']['mean']:.3f}    "
              f"{stats['total_reward']['mean']:.2f}")

    # Test hypotheses
    print("\n" + "-" * 60)
    print("🧪 HYPOTHESIS TESTING")
    print("-" * 60)

    # H1: K_R alone insufficient - check if high K_R agents can have low reward
    k_r_values = np.array([r["K_R"] for r in results])
    rewards = np.array([r["total_reward"] for r in results])
    r_kr_reward, p_kr_reward = pearsonr(k_r_values, rewards)
    print(f"H1: K_R → Reward correlation: r = {r_kr_reward:.4f}, p = {p_kr_reward:.6f}")

    # H2: K_A adds predictive power
    k_a_values = np.array([r["K_A"] for r in results])
    r_ka_reward, p_ka_reward = pearsonr(k_a_values, rewards)
    print(f"H2: K_A → Reward correlation: r = {r_ka_reward:.4f}, p = {p_ka_reward:.6f}")

    # H3: K_P distinguishes good from great
    k_p_values = np.array([r["K_P"] for r in results])
    r_kp_reward, p_kp_reward = pearsonr(k_p_values, rewards)
    print(f"H3: K_P → Reward correlation: r = {r_kp_reward:.4f}, p = {p_kp_reward:.6f}")

    # Check if multi-dimensional K-vector outperforms K_R alone
    # Use simple regression: K_R alone vs K_R + K_A + K_P
    from numpy.linalg import lstsq

    # K_R alone
    X_kr = np.column_stack([np.ones(len(k_r_values)), k_r_values])
    coef_kr, residuals_kr, _, _ = lstsq(X_kr, rewards, rcond=None)
    ss_res_kr = np.sum((rewards - X_kr @ coef_kr) ** 2)
    ss_tot = np.sum((rewards - rewards.mean()) ** 2)
    r2_kr = 1 - ss_res_kr / ss_tot if ss_tot > 0 else 0

    # K_R + K_A + K_P (tetrad minus K_I)
    X_multi = np.column_stack([np.ones(len(k_r_values)), k_r_values, k_a_values, k_p_values])
    coef_multi, _, _, _ = lstsq(X_multi, rewards, rcond=None)
    ss_res_multi = np.sum((rewards - X_multi @ coef_multi) ** 2)
    r2_multi = 1 - ss_res_multi / ss_tot if ss_tot > 0 else 0

    print(f"\nR² (K_R alone):      {r2_kr:.4f}")
    print(f"R² (K_R + K_A + K_P): {r2_multi:.4f}")
    print(f"Improvement:         {r2_multi - r2_kr:.4f}")

    # Key discovery: Does the "thermostat" pattern emerge?
    print("\n" + "-" * 60)
    print("🌡️ THERMOSTAT DETECTION (High K_R, Low K_A/K_M)")
    print("-" * 60)

    # Find agents with high K_R but low K_A (potential "thermostats")
    high_kr_threshold = np.percentile(k_r_values, 75)
    low_ka_threshold = np.percentile(k_a_values, 25)
    low_km_threshold = np.percentile([r["K_M"] for r in results], 25)

    thermostats = [r for r in results
                   if r["K_R"] > high_kr_threshold
                   and r["K_A"] < low_ka_threshold
                   and r["K_M"] < low_km_threshold]

    print(f"Potential thermostats found: {len(thermostats)}")
    if thermostats:
        print(f"  - Agent types: {[t['agent_type'] for t in thermostats[:5]]}")
        avg_reward_therm = np.mean([t["total_reward"] for t in thermostats])
        avg_reward_all = np.mean(rewards)
        print(f"  - Avg reward (thermostats): {avg_reward_therm:.2f}")
        print(f"  - Avg reward (all agents):  {avg_reward_all:.2f}")

    print("-" * 60)

    return {
        "phase": "L6",
        "environment": environment,
        "n_agents": len(results),
        "agent_types": agent_types,
        "type_statistics": type_stats,
        "hypothesis_tests": {
            "H1_kr_reward": {"r": r_kr_reward, "p": p_kr_reward},
            "H2_ka_reward": {"r": r_ka_reward, "p": p_ka_reward},
            "H3_kp_reward": {"r": r_kp_reward, "p": p_kp_reward},
        },
        "regression": {
            "r2_kr_only": r2_kr,
            "r2_multi": r2_multi,
            "improvement": r2_multi - r2_kr,
        },
        "thermostat_detection": {
            "count": len(thermostats),
            "agents": thermostats[:10] if thermostats else [],
        },
        "agent_results": results,
    }


def _train_linear_agent(env, obs_dim: int, action_dim: int, n_episodes: int = 50) -> LinearAgent:
    """Helper to create a pre-trained linear agent."""
    agent = LinearAgent(obs_dim=obs_dim, action_dim=action_dim, learning_rate=0.01)
    for _ in range(n_episodes):
        obs = env.reset()
        done = False
        while not done:
            action = agent.select_action(obs)
            next_obs, reward, done, _ = env.step(action)
            agent.update(obs, action, reward)
            obs = next_obs
    return agent


# =============================================================================
# MAIN
# =============================================================================

def load_config(config_path: Optional[str]) -> Dict[str, Any]:
    """Load configuration from YAML file or return defaults."""
    if config_path and HAS_YAML and Path(config_path).exists():
        with open(config_path) as f:
            return yaml.safe_load(f)

    # Default config
    return {
        "experiment": {
            "name": "track_l_unified_indices",
            "output_dir": "logs/track_l/",
        },
        "track_l1": {
            "episodes": 200,
            "environment": {
                "observations": 20,
                "actions": 10,
                "episode_length": 200,
            },
        },
        "track_l2": {
            "episodes": 300,
        },
        "track_l4": {
            "algorithm": {
                "population": 20,
                "generations": 100,
            },
        },
        "track_l6": {
            "agents_per_type": 30,  # 30 agents per type = 120 total
        },
    }


def save_results(results: Dict[str, Any], config: Dict[str, Any]) -> Path:
    """Save results to JSON file."""
    exp_cfg = config.get("experiment", {})
    output_dir = Path(exp_cfg.get("output_dir", "logs/track_l")).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    phase = str(results.get("phase", "unknown")).lower()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = output_dir / f"track_l_{phase}_{ts}.json"

    # Convert numpy types for JSON serialization
    def to_serializable(obj):
        if isinstance(obj, dict):
            return {k: to_serializable(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [to_serializable(v) for v in obj]
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        return obj

    out.write_text(json.dumps(to_serializable(results), indent=2))
    print(f"\n💾 Results saved → {out}")
    return out


def main():
    parser = argparse.ArgumentParser(
        description="Track L: K-Index ↔ O/R Index Bridge Study"
    )
    parser.add_argument(
        "--phase",
        choices=["l1", "l2", "l3", "l4", "l4b", "l5", "l6", "all"],
        default="l1",
        help="Which track phase to run (l4b = Paper 6-style O/R usage, l6 = Kosmic K-Vector)",
    )
    parser.add_argument(
        "--kosmic",
        action="store_true",
        help="Enable Kosmic K-Vector computation (for phases that support it)",
    )
    parser.add_argument(
        "--environment",
        type=str,
        choices=["coordination", "simple", "delayed", "commons", "all"],
        default="coordination",
        help="Environment for L6 experiments (all = run comparison across all)",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to YAML config file",
    )
    parser.add_argument(
        "--episodes",
        type=int,
        default=None,
        help="Override number of episodes",
    )
    parser.add_argument(
        "--generations",
        type=int,
        default=None,
        help="Override number of CMA-ES generations (L4)",
    )
    parser.add_argument(
        "--formula",
        type=str,
        choices=["original", "multiplicative", "additive", "geometric", "log_scaled", "k_only", "or_only"],
        default="original",
        help="Coherence formula for L4 optimization (or_only = control condition)",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["regularization", "adaptive"],
        default="regularization",
        help="O/R usage mode for L4b (regularization=CR-REINFORCE style, adaptive=OR-PPO style)",
    )
    parser.add_argument(
        "--compare-formulas",
        action="store_true",
        help="Run L4 with all formulas and compare results",
    )
    parser.add_argument(
        "--compare-modes",
        action="store_true",
        help="Run L4b with both modes and compare to K-only baseline",
    )

    args = parser.parse_args()

    # Load config
    config = load_config(args.config)

    # Apply overrides
    if args.episodes:
        if "track_l1" in config:
            config["track_l1"]["episodes"] = args.episodes
        if "track_l2" in config:
            config["track_l2"]["episodes"] = args.episodes

    if args.generations and "track_l4" in config:
        config["track_l4"]["algorithm"]["generations"] = args.generations

    print("=" * 60)
    print("🔗 TRACK L: Unified Indices of Machine Consciousness")
    print("=" * 60)
    print(f"Phase: {args.phase.upper()}")
    print(f"Config: {args.config or 'default'}")

    # Run requested phase(s)
    results = {}

    if args.phase in ["l1", "all"]:
        results["l1"] = run_track_l1(config)
        save_results(results["l1"], config)

    if args.phase in ["l2", "all"]:
        results["l2"] = run_track_l2(config)
        save_results(results["l2"], config)

    if args.phase in ["l4", "all"]:
        if args.compare_formulas:
            # Run all formulas and compare (including or_only control)
            formulas = ["k_only", "or_only", "original", "multiplicative", "additive", "log_scaled"]
            print("\n" + "=" * 60)
            print("📊 COMPARING ALL COHERENCE FORMULAS")
            print("=" * 60)
            comparison_results = []
            for formula in formulas:
                result = run_track_l4(config, formula=formula)
                save_results(result, config)
                comparison_results.append({
                    "formula": formula,
                    "best_k": result["best_k_index"],
                    "best_coherence": result["best_coherence"],
                    "crossed": result["threshold_crossed"],
                })
            # Print comparison summary
            print("\n" + "=" * 60)
            print("📈 FORMULA COMPARISON SUMMARY")
            print("=" * 60)
            print(f"{'Formula':<15} {'Best K':<10} {'Coherence':<12} {'1.5 Crossed'}")
            print("-" * 50)
            for r in sorted(comparison_results, key=lambda x: x["best_k"], reverse=True):
                crossed = "✅" if r["crossed"] else "❌"
                print(f"{r['formula']:<15} {r['best_k']:.4f}     {r['best_coherence']:.4f}       {crossed}")
            results["l4_comparison"] = comparison_results
        else:
            results["l4"] = run_track_l4(config, formula=args.formula)
            save_results(results["l4"], config)

    if args.phase in ["l4b"]:
        if args.compare_modes:
            # Run both modes and compare to K-only baseline
            print("\n" + "=" * 60)
            print("📊 COMPARING PAPER 6-STYLE O/R USAGE MODES")
            print("=" * 60)
            comparison_results = []

            # First run K-only baseline
            result = run_track_l4(config, formula="k_only")
            save_results(result, config)
            comparison_results.append({
                "mode": "k_only (baseline)",
                "best_k": result["best_k_index"],
                "best_or": "N/A",
                "crossed": result["threshold_crossed"],
            })

            # Then run both Paper 6 modes
            for mode in ["regularization", "adaptive"]:
                result = run_track_l4_paper6_style(config, mode=mode)
                save_results(result, config)
                comparison_results.append({
                    "mode": mode,
                    "best_k": result["best_k_index"],
                    "best_or": result["best_or_index"],
                    "crossed": result["threshold_crossed"],
                })

            # Print comparison summary
            print("\n" + "=" * 60)
            print("📈 PAPER 6-STYLE MODE COMPARISON SUMMARY")
            print("=" * 60)
            print(f"{'Mode':<20} {'Best K':<10} {'Best O/R':<12} {'1.5 Crossed'}")
            print("-" * 55)
            for r in sorted(comparison_results, key=lambda x: x["best_k"], reverse=True):
                crossed = "✅" if r["crossed"] else "❌"
                or_str = f"{r['best_or']:.2f}" if isinstance(r['best_or'], float) else r['best_or']
                print(f"{r['mode']:<20} {r['best_k']:.4f}     {or_str:<12} {crossed}")
            results["l4b_comparison"] = comparison_results
        else:
            results["l4b"] = run_track_l4_paper6_style(config, mode=args.mode)
            save_results(results["l4b"], config)

    if args.phase in ["l6", "all"]:
        if args.environment == "all":
            # Run L6 across all environments for comprehensive comparison
            print("\n" + "=" * 70)
            print("🌌 COMPREHENSIVE KOSMIC K-VECTOR VALIDATION")
            print("=" * 70)
            environments = ["coordination", "simple", "delayed", "commons"]
            l6_results = {}
            for env_name in environments:
                print(f"\n{'='*60}")
                print(f"Running L6 on {env_name.upper()} environment...")
                l6_results[env_name] = run_track_l6(config, environment=env_name)
                save_results(l6_results[env_name], config)

            # Print cross-environment comparison
            print("\n" + "=" * 70)
            print("📊 CROSS-ENVIRONMENT K-VECTOR COMPARISON")
            print("=" * 70)
            print(f"\n{'Environment':<15} {'Best K_R':<10} {'Avg K_A':<10} {'Avg K_P':<10} {'R² Improve':<12}")
            print("-" * 60)
            for env_name, result in l6_results.items():
                if "error" not in result:
                    stats = result.get("type_statistics", {})
                    # Get stats from trained agent type
                    trained_stats = stats.get("linear_trained", stats.get("cmaes", {}))
                    k_r = trained_stats.get("K_R", {}).get("mean", 0)
                    k_a = trained_stats.get("K_A", {}).get("mean", 0)
                    k_p = trained_stats.get("K_P", {}).get("mean", 0)
                    r2_imp = result.get("regression", {}).get("improvement", 0)
                    print(f"{env_name:<15} {k_r:<10.3f} {k_a:<10.3f} {k_p:<10.3f} {r2_imp:<12.4f}")

            results["l6_comparison"] = l6_results
        else:
            results["l6"] = run_track_l6(config, environment=args.environment)
            save_results(results["l6"], config)

    if args.phase in ["l3", "l5"]:
        print(f"\n⚠️  Phase {args.phase.upper()} not yet implemented.")
        print("   See PAPER_8_UNIFIED_INDICES_PROPOSAL.md for design.")

    print("\n" + "=" * 60)
    print("✅ Track L execution complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
