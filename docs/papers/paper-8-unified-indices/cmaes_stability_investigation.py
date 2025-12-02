#!/usr/bin/env python3
"""
CMA-ES Stability Investigation: Why Does K Peak Early and Degrade?

This script investigates the puzzling phenomenon where:
- Best K-Index is achieved at generation 0-10
- K degrades by 30-50% over subsequent generations
- This is backwards from normal optimization behavior

Hypotheses to test:
1. Sharp, unstable peaks in K fitness landscape
2. CMA-ES covariance collapse
3. K measures something fragile (small param changes destroy it)
4. Random initialization luck vs systematic optimization

Author: Claude + Human collaboration
Date: November 28, 2025
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import json
from datetime import datetime
import os

# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class InvestigationConfig:
    """Configuration for stability investigation."""
    n_seeds: int = 10  # Multiple seeds to check consistency
    n_generations: int = 50
    population_size: int = 20
    obs_dim: int = 20
    action_dim: int = 10
    episode_length: int = 200

    # CMA-ES variants to test
    sigma_variants: List[float] = field(default_factory=lambda: [0.1, 0.3, 0.5, 1.0])

    # Alternative optimizers
    test_alternatives: bool = True


# =============================================================================
# K-INDEX COMPUTATION (from track_l_runner.py)
# =============================================================================

def compute_k_index(observations: np.ndarray, actions: np.ndarray) -> float:
    """Compute K-Index: magnitude coupling between observations and actions."""
    if len(observations) < 2:
        return np.nan

    obs_magnitudes = np.linalg.norm(observations, axis=1)
    action_magnitudes = np.linalg.norm(actions, axis=1)

    if np.std(obs_magnitudes) < 1e-8 or np.std(action_magnitudes) < 1e-8:
        return 0.0

    correlation = np.corrcoef(obs_magnitudes, action_magnitudes)[0, 1]
    k_index = 2 * abs(correlation)

    return float(k_index) if not np.isnan(k_index) else 0.0


# =============================================================================
# SIMPLE ENVIRONMENT
# =============================================================================

class SimpleEnv:
    """Minimal environment for K-Index optimization."""

    def __init__(self, obs_dim: int = 20, action_dim: int = 10):
        self.obs_dim = obs_dim
        self.action_dim = action_dim
        self.state = None

    def reset(self) -> np.ndarray:
        self.state = np.random.randn(self.obs_dim)
        return self.state.copy()

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, dict]:
        # Simple dynamics
        self.state = 0.9 * self.state + 0.1 * np.random.randn(self.obs_dim)
        reward = np.dot(action[:min(len(action), self.obs_dim)],
                       self.state[:min(len(action), self.obs_dim)])
        return self.state.copy(), reward, False, {}


# =============================================================================
# POLICY (Linear for simplicity)
# =============================================================================

class LinearPolicy:
    """Simple linear policy: action = W @ obs + b"""

    def __init__(self, obs_dim: int, action_dim: int):
        self.obs_dim = obs_dim
        self.action_dim = action_dim
        self.n_params = obs_dim * action_dim + action_dim

    def get_params(self, flat_params: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        W = flat_params[:self.obs_dim * self.action_dim].reshape(self.action_dim, self.obs_dim)
        b = flat_params[self.obs_dim * self.action_dim:]
        return W, b

    def forward(self, obs: np.ndarray, flat_params: np.ndarray) -> np.ndarray:
        W, b = self.get_params(flat_params)
        return W @ obs + b


# =============================================================================
# EVALUATION
# =============================================================================

def evaluate_policy(policy: LinearPolicy, params: np.ndarray,
                   env: SimpleEnv, n_episodes: int = 5,
                   episode_length: int = 200) -> Dict:
    """Evaluate policy and compute K-Index with detailed metrics."""

    all_obs = []
    all_actions = []
    total_reward = 0

    for _ in range(n_episodes):
        obs = env.reset()
        for _ in range(episode_length):
            action = policy.forward(obs, params)
            all_obs.append(obs)
            all_actions.append(action)
            obs, reward, _, _ = env.step(action)
            total_reward += reward

    observations = np.array(all_obs)
    actions = np.array(all_actions)

    k_index = compute_k_index(observations, actions)

    # Additional diagnostics
    obs_mags = np.linalg.norm(observations, axis=1)
    action_mags = np.linalg.norm(actions, axis=1)

    return {
        'k_index': k_index,
        'reward': total_reward / n_episodes,
        'obs_mag_mean': float(np.mean(obs_mags)),
        'obs_mag_std': float(np.std(obs_mags)),
        'action_mag_mean': float(np.mean(action_mags)),
        'action_mag_std': float(np.std(action_mags)),
        'param_norm': float(np.linalg.norm(params)),
    }


# =============================================================================
# CMA-ES IMPLEMENTATION WITH DIAGNOSTICS
# =============================================================================

class DiagnosticCMAES:
    """CMA-ES with detailed internal state tracking."""

    def __init__(self, n_params: int, sigma: float = 0.5, population_size: int = 20):
        self.n_params = n_params
        self.sigma = sigma
        self.population_size = population_size

        # Initialize mean and covariance
        self.mean = np.random.randn(n_params) * 0.1
        self.C = np.eye(n_params)  # Covariance matrix
        self.pc = np.zeros(n_params)  # Evolution path for C
        self.ps = np.zeros(n_params)  # Evolution path for sigma

        # Hyperparameters
        self.mu = population_size // 2
        self.weights = np.log(self.mu + 0.5) - np.log(np.arange(1, self.mu + 1))
        self.weights = self.weights / self.weights.sum()
        self.mueff = 1.0 / (self.weights ** 2).sum()

        self.cc = 4.0 / (n_params + 4)
        self.cs = (self.mueff + 2) / (n_params + self.mueff + 3)
        self.c1 = 2.0 / ((n_params + 1.3) ** 2 + self.mueff)
        self.cmu = min(1 - self.c1,
                      2 * (self.mueff - 2 + 1/self.mueff) / ((n_params + 2) ** 2 + self.mueff))
        self.damps = 1 + 2 * max(0, np.sqrt((self.mueff - 1) / (n_params + 1)) - 1) + self.cs

        self.chiN = np.sqrt(n_params) * (1 - 1/(4*n_params) + 1/(21*n_params**2))

        # Tracking
        self.generation = 0
        self.history = []

    def sample(self) -> np.ndarray:
        """Sample population."""
        # Eigendecomposition for sampling
        eigenvalues, eigenvectors = np.linalg.eigh(self.C)
        eigenvalues = np.maximum(eigenvalues, 1e-10)

        samples = []
        for _ in range(self.population_size):
            z = np.random.randn(self.n_params)
            sample = self.mean + self.sigma * eigenvectors @ (np.sqrt(eigenvalues) * z)
            samples.append(sample)

        return np.array(samples)

    def update(self, samples: np.ndarray, fitnesses: np.ndarray):
        """Update CMA-ES state and record diagnostics."""
        # Sort by fitness (descending - higher is better)
        indices = np.argsort(fitnesses)[::-1]
        samples = samples[indices]
        fitnesses = fitnesses[indices]

        # Select elite
        elite = samples[:self.mu]

        # Update mean
        old_mean = self.mean.copy()
        self.mean = np.sum(self.weights[:, None] * elite, axis=0)

        # Eigendecomposition
        eigenvalues, eigenvectors = np.linalg.eigh(self.C)
        eigenvalues = np.maximum(eigenvalues, 1e-10)
        invsqrtC = eigenvectors @ np.diag(1.0 / np.sqrt(eigenvalues)) @ eigenvectors.T

        # Update evolution paths
        self.ps = (1 - self.cs) * self.ps + \
                  np.sqrt(self.cs * (2 - self.cs) * self.mueff) * invsqrtC @ (self.mean - old_mean) / self.sigma

        hsig = np.linalg.norm(self.ps) / np.sqrt(1 - (1 - self.cs) ** (2 * (self.generation + 1))) < \
               (1.4 + 2 / (self.n_params + 1)) * self.chiN

        self.pc = (1 - self.cc) * self.pc + \
                  hsig * np.sqrt(self.cc * (2 - self.cc) * self.mueff) * (self.mean - old_mean) / self.sigma

        # Update covariance
        artmp = (elite - old_mean) / self.sigma
        self.C = (1 - self.c1 - self.cmu) * self.C + \
                 self.c1 * np.outer(self.pc, self.pc) + \
                 self.cmu * artmp.T @ np.diag(self.weights) @ artmp

        # Ensure symmetry and positive definiteness
        self.C = (self.C + self.C.T) / 2
        eigenvalues_new = np.linalg.eigvalsh(self.C)
        if np.min(eigenvalues_new) < 1e-10:
            self.C += (1e-10 - np.min(eigenvalues_new)) * np.eye(self.n_params)

        # Update sigma
        self.sigma = self.sigma * np.exp((self.cs / self.damps) * (np.linalg.norm(self.ps) / self.chiN - 1))
        self.sigma = np.clip(self.sigma, 1e-10, 10.0)

        # Record diagnostics
        eigenvalues_C = np.linalg.eigvalsh(self.C)
        self.history.append({
            'generation': self.generation,
            'sigma': float(self.sigma),
            'mean_norm': float(np.linalg.norm(self.mean)),
            'C_condition': float(np.max(eigenvalues_C) / max(np.min(eigenvalues_C), 1e-10)),
            'C_max_eigenvalue': float(np.max(eigenvalues_C)),
            'C_min_eigenvalue': float(np.min(eigenvalues_C)),
            'ps_norm': float(np.linalg.norm(self.ps)),
            'pc_norm': float(np.linalg.norm(self.pc)),
            'best_fitness': float(fitnesses[0]),
            'mean_fitness': float(np.mean(fitnesses)),
            'fitness_std': float(np.std(fitnesses)),
        })

        self.generation += 1

    def get_diagnostics(self) -> List[Dict]:
        return self.history


# =============================================================================
# INVESTIGATION EXPERIMENTS
# =============================================================================

def run_single_optimization(config: InvestigationConfig, seed: int,
                           initial_sigma: float) -> Dict:
    """Run single CMA-ES optimization with full diagnostics."""

    np.random.seed(seed)

    env = SimpleEnv(config.obs_dim, config.action_dim)
    policy = LinearPolicy(config.obs_dim, config.action_dim)
    cmaes = DiagnosticCMAES(policy.n_params, sigma=initial_sigma,
                           population_size=config.population_size)

    results = {
        'seed': seed,
        'initial_sigma': initial_sigma,
        'generations': [],
        'best_k_ever': 0.0,
        'best_k_generation': 0,
        'final_k': 0.0,
        'degradation': 0.0,
    }

    best_k_ever = 0.0
    best_k_gen = 0

    for gen in range(config.n_generations):
        # Sample population
        samples = cmaes.sample()

        # Evaluate
        fitnesses = []
        k_values = []
        for params in samples:
            metrics = evaluate_policy(policy, params, env, n_episodes=3,
                                     episode_length=config.episode_length)
            fitnesses.append(metrics['k_index'])
            k_values.append(metrics['k_index'])

        fitnesses = np.array(fitnesses)

        # Update CMA-ES
        cmaes.update(samples, fitnesses)

        # Track best
        gen_best_k = np.max(k_values)
        if gen_best_k > best_k_ever:
            best_k_ever = gen_best_k
            best_k_gen = gen

        # Record
        results['generations'].append({
            'gen': gen,
            'best_k': float(gen_best_k),
            'mean_k': float(np.mean(k_values)),
            'std_k': float(np.std(k_values)),
            'best_k_ever': float(best_k_ever),
        })

        if gen % 10 == 0:
            print(f"  Gen {gen}: best_K={gen_best_k:.4f}, all-time={best_k_ever:.4f}, sigma={cmaes.sigma:.4f}")

    # Final metrics
    final_k = results['generations'][-1]['best_k']
    results['best_k_ever'] = best_k_ever
    results['best_k_generation'] = best_k_gen
    results['final_k'] = final_k
    results['degradation'] = (best_k_ever - final_k) / best_k_ever if best_k_ever > 0 else 0
    results['cmaes_diagnostics'] = cmaes.get_diagnostics()

    return results


def run_random_search(config: InvestigationConfig, seed: int) -> Dict:
    """Run random search as baseline comparison."""

    np.random.seed(seed)

    env = SimpleEnv(config.obs_dim, config.action_dim)
    policy = LinearPolicy(config.obs_dim, config.action_dim)

    results = {
        'seed': seed,
        'method': 'random_search',
        'generations': [],
        'best_k_ever': 0.0,
        'best_k_generation': 0,
    }

    best_k_ever = 0.0
    best_k_gen = 0
    best_params = None

    for gen in range(config.n_generations):
        # Random samples
        k_values = []
        for _ in range(config.population_size):
            params = np.random.randn(policy.n_params) * 0.5
            metrics = evaluate_policy(policy, params, env, n_episodes=3,
                                     episode_length=config.episode_length)
            k_values.append(metrics['k_index'])

            if metrics['k_index'] > best_k_ever:
                best_k_ever = metrics['k_index']
                best_k_gen = gen
                best_params = params

        results['generations'].append({
            'gen': gen,
            'best_k': float(np.max(k_values)),
            'mean_k': float(np.mean(k_values)),
            'best_k_ever': float(best_k_ever),
        })

        if gen % 10 == 0:
            print(f"  Gen {gen}: best_K={np.max(k_values):.4f}, all-time={best_k_ever:.4f}")

    results['best_k_ever'] = best_k_ever
    results['best_k_generation'] = best_k_gen
    results['final_k'] = results['generations'][-1]['best_k']

    return results


def run_elitist_evolution(config: InvestigationConfig, seed: int) -> Dict:
    """Run (1+λ)-ES: always keep the best, never degrade."""

    np.random.seed(seed)

    env = SimpleEnv(config.obs_dim, config.action_dim)
    policy = LinearPolicy(config.obs_dim, config.action_dim)

    results = {
        'seed': seed,
        'method': 'elitist_es',
        'generations': [],
        'best_k_ever': 0.0,
        'best_k_generation': 0,
    }

    # Initialize
    best_params = np.random.randn(policy.n_params) * 0.3
    best_metrics = evaluate_policy(policy, best_params, env, n_episodes=5,
                                   episode_length=config.episode_length)
    best_k = best_metrics['k_index']
    best_k_gen = 0

    sigma = 0.3

    for gen in range(config.n_generations):
        # Generate offspring
        k_values = [best_k]
        candidates = [best_params]

        for _ in range(config.population_size - 1):
            # Mutate from best
            offspring = best_params + sigma * np.random.randn(policy.n_params)
            metrics = evaluate_policy(policy, offspring, env, n_episodes=3,
                                     episode_length=config.episode_length)
            k_values.append(metrics['k_index'])
            candidates.append(offspring)

        # Select best (elitist - never get worse)
        best_idx = np.argmax(k_values)
        if k_values[best_idx] >= best_k:
            best_params = candidates[best_idx]
            best_k = k_values[best_idx]
            best_k_gen = gen

        results['generations'].append({
            'gen': gen,
            'best_k': float(best_k),
            'offspring_best': float(np.max(k_values[1:])) if len(k_values) > 1 else 0,
            'offspring_mean': float(np.mean(k_values[1:])) if len(k_values) > 1 else 0,
        })

        if gen % 10 == 0:
            print(f"  Gen {gen}: best_K={best_k:.4f}, offspring_best={np.max(k_values[1:]):.4f}")

    results['best_k_ever'] = best_k
    results['best_k_generation'] = best_k_gen
    results['final_k'] = best_k  # Elitist never degrades
    results['degradation'] = 0.0

    return results


# =============================================================================
# MAIN INVESTIGATION
# =============================================================================

def run_investigation():
    """Run full stability investigation."""

    print("=" * 70)
    print("🔬 CMA-ES STABILITY INVESTIGATION")
    print("=" * 70)
    print("\nHypothesis: CMA-ES peaks early due to covariance collapse or")
    print("            K-Index having a fragile fitness landscape.\n")

    config = InvestigationConfig()
    all_results = {
        'timestamp': datetime.now().isoformat(),
        'config': {
            'n_seeds': config.n_seeds,
            'n_generations': config.n_generations,
            'population_size': config.population_size,
        },
        'experiments': {}
    }

    # ==========================================================================
    # Experiment 1: Multiple seeds with default CMA-ES
    # ==========================================================================
    print("\n" + "=" * 60)
    print("📊 EXPERIMENT 1: CMA-ES Consistency Across Seeds")
    print("=" * 60)

    cmaes_results = []
    for seed in range(config.n_seeds):
        print(f"\n--- Seed {seed} ---")
        result = run_single_optimization(config, seed, initial_sigma=0.5)
        cmaes_results.append(result)
        print(f"  Best K: {result['best_k_ever']:.4f} at gen {result['best_k_generation']}")
        print(f"  Final K: {result['final_k']:.4f}")
        print(f"  Degradation: {result['degradation']*100:.1f}%")

    # Analyze
    best_ks = [r['best_k_ever'] for r in cmaes_results]
    best_gens = [r['best_k_generation'] for r in cmaes_results]
    degradations = [r['degradation'] for r in cmaes_results]

    print(f"\n📈 SUMMARY (n={config.n_seeds} seeds):")
    print(f"  Best K: {np.mean(best_ks):.4f} ± {np.std(best_ks):.4f}")
    print(f"  Best gen: {np.mean(best_gens):.1f} ± {np.std(best_gens):.1f}")
    print(f"  Degradation: {np.mean(degradations)*100:.1f}% ± {np.std(degradations)*100:.1f}%")
    print(f"  Early peak (gen < 10): {sum(g < 10 for g in best_gens)}/{config.n_seeds}")

    all_results['experiments']['cmaes_default'] = {
        'results': cmaes_results,
        'summary': {
            'best_k_mean': float(np.mean(best_ks)),
            'best_k_std': float(np.std(best_ks)),
            'best_gen_mean': float(np.mean(best_gens)),
            'degradation_mean': float(np.mean(degradations)),
            'early_peak_rate': sum(g < 10 for g in best_gens) / config.n_seeds,
        }
    }

    # ==========================================================================
    # Experiment 2: Random Search Baseline
    # ==========================================================================
    print("\n" + "=" * 60)
    print("📊 EXPERIMENT 2: Random Search Baseline")
    print("=" * 60)

    random_results = []
    for seed in range(config.n_seeds):
        print(f"\n--- Seed {seed} ---")
        result = run_random_search(config, seed)
        random_results.append(result)
        print(f"  Best K: {result['best_k_ever']:.4f} at gen {result['best_k_generation']}")

    random_best_ks = [r['best_k_ever'] for r in random_results]
    print(f"\n📈 SUMMARY:")
    print(f"  Best K: {np.mean(random_best_ks):.4f} ± {np.std(random_best_ks):.4f}")
    print(f"  vs CMA-ES: {'CMA-ES better' if np.mean(best_ks) > np.mean(random_best_ks) else 'Random better!'}")

    all_results['experiments']['random_search'] = {
        'results': random_results,
        'summary': {
            'best_k_mean': float(np.mean(random_best_ks)),
            'best_k_std': float(np.std(random_best_ks)),
        }
    }

    # ==========================================================================
    # Experiment 3: Elitist ES (never degrades)
    # ==========================================================================
    print("\n" + "=" * 60)
    print("📊 EXPERIMENT 3: Elitist (1+λ)-ES (Never Degrades)")
    print("=" * 60)

    elitist_results = []
    for seed in range(config.n_seeds):
        print(f"\n--- Seed {seed} ---")
        result = run_elitist_evolution(config, seed)
        elitist_results.append(result)
        print(f"  Best K: {result['best_k_ever']:.4f} at gen {result['best_k_generation']}")

    elitist_best_ks = [r['best_k_ever'] for r in elitist_results]
    print(f"\n📈 SUMMARY:")
    print(f"  Best K: {np.mean(elitist_best_ks):.4f} ± {np.std(elitist_best_ks):.4f}")
    print(f"  vs CMA-ES: {'Elitist better' if np.mean(elitist_best_ks) > np.mean(best_ks) else 'CMA-ES better'}")

    all_results['experiments']['elitist_es'] = {
        'results': elitist_results,
        'summary': {
            'best_k_mean': float(np.mean(elitist_best_ks)),
            'best_k_std': float(np.std(elitist_best_ks)),
        }
    }

    # ==========================================================================
    # Final Analysis
    # ==========================================================================
    print("\n" + "=" * 70)
    print("🔍 FINAL ANALYSIS")
    print("=" * 70)

    print("\n📊 Method Comparison:")
    print(f"  {'Method':<20} {'Best K':<15} {'Notes'}")
    print(f"  {'-'*50}")
    print(f"  {'CMA-ES':<20} {np.mean(best_ks):.4f} ± {np.std(best_ks):.4f}   Degrades {np.mean(degradations)*100:.0f}%")
    print(f"  {'Random Search':<20} {np.mean(random_best_ks):.4f} ± {np.std(random_best_ks):.4f}   No learning")
    print(f"  {'Elitist ES':<20} {np.mean(elitist_best_ks):.4f} ± {np.std(elitist_best_ks):.4f}   Never degrades")

    # Diagnose the issue
    print("\n🔬 DIAGNOSIS:")

    if np.mean(best_ks) > np.mean(random_best_ks):
        print("  ✓ CMA-ES DOES find better K than random search")
        print("    → The optimization is working initially")
    else:
        print("  ✗ CMA-ES doesn't beat random search!")
        print("    → K landscape may be too noisy for optimization")

    if np.mean(degradations) > 0.2:
        print(f"  ✗ Significant degradation ({np.mean(degradations)*100:.0f}%) after peak")
        print("    → CMA-ES covariance adaptation hurts K")

    if np.mean(elitist_best_ks) > np.mean(best_ks):
        print("  ✓ Elitist ES beats CMA-ES!")
        print("    → Solution: Use elitist selection to prevent degradation")

    early_peak_pct = sum(g < 10 for g in best_gens) / config.n_seeds * 100
    if early_peak_pct > 50:
        print(f"  ! {early_peak_pct:.0f}% of runs peak before gen 10")
        print("    → K's best solutions are found early, then lost")

    # Save results
    os.makedirs('/srv/luminous-dynamics/kosmic-lab/logs/stability', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f'/srv/luminous-dynamics/kosmic-lab/logs/stability/investigation_{timestamp}.json'

    # Convert numpy types for JSON
    def convert_numpy(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, dict):
            return {k: convert_numpy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy(v) for v in obj]
        return obj

    with open(output_path, 'w') as f:
        json.dump(convert_numpy(all_results), f, indent=2)

    print(f"\n💾 Results saved to: {output_path}")

    return all_results


if __name__ == '__main__':
    run_investigation()
