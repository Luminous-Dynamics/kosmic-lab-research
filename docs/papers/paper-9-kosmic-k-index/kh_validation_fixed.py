#!/usr/bin/env python3
"""
K_H Validation - Fixed Implementation

Fixes issues identified in the original run_kh_validation.py:
1. Sustainable agent harvested 0 (logic error)
2. Cohen's d overflow (division by zero)
3. Better normalization of K_H

This version ensures all agents behave as expected and produces
valid statistical comparisons.
"""

import numpy as np
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
from scipy.stats import pearsonr, ttest_ind


@dataclass
class CommonsConfig:
    """Configuration for The Commons environment."""
    initial_resources: float = 100.0
    regeneration_rate: float = 0.05
    carrying_capacity: float = 100.0
    collapse_threshold: float = 10.0
    max_steps: int = 200
    max_harvest_fraction: float = 0.15


class TheCommonsEnvironment:
    """
    The Commons: Resource sustainability environment.

    Logistic growth with harvesting:
        dR/dt = r * R * (1 - R/K) - harvest
    """

    def __init__(self, config: CommonsConfig = None):
        self.config = config or CommonsConfig()
        self.reset()

    def reset(self) -> np.ndarray:
        self.resources = self.config.initial_resources
        self.step_count = 0
        self.collapsed = False
        self.harvest_history = []
        self.resource_history = [self.resources]
        return self._get_observation()

    def _get_observation(self) -> np.ndarray:
        trend = 0.0
        if len(self.resource_history) > 1:
            trend = self.resource_history[-1] - self.resource_history[-2]

        sustainable_harvest = self._sustainable_harvest_rate()

        return np.array([
            self.resources / self.config.carrying_capacity,
            np.clip(trend / 10.0, -1, 1),
            1.0 - (self.step_count / self.config.max_steps),
            sustainable_harvest,
        ], dtype=np.float32)

    def _sustainable_harvest_rate(self) -> float:
        """Calculate current sustainable harvest rate."""
        r = self.config.regeneration_rate
        K = self.config.carrying_capacity
        R = self.resources

        # Current growth rate
        growth = r * R * (1 - R / K) if R > 0 else 0
        return float(np.clip(growth / K, 0, 0.1))  # Normalized

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, dict]:
        if self.collapsed:
            return self._get_observation(), 0.0, True, {"collapsed": True}

        # Interpret action as harvest rate [0, 1]
        harvest_rate = np.clip(float(action[0]) if hasattr(action, '__len__') else float(action), 0, 1)

        # Calculate harvest
        max_harvest = self.resources * self.config.max_harvest_fraction
        actual_harvest = harvest_rate * max_harvest

        # Apply harvest
        self.resources -= actual_harvest
        self.harvest_history.append(actual_harvest)

        # Apply regeneration
        r = self.config.regeneration_rate
        K = self.config.carrying_capacity
        regeneration = r * self.resources * (1 - self.resources / K)
        self.resources += regeneration

        self.resources = np.clip(self.resources, 0, K)
        self.resource_history.append(self.resources)

        # Check collapse
        if self.resources < self.config.collapse_threshold:
            self.collapsed = True

        self.step_count += 1
        done = self.collapsed or self.step_count >= self.config.max_steps

        # Reward is harvest (creates tragedy of the commons)
        reward = actual_harvest

        info = {
            "resources": self.resources,
            "harvest": actual_harvest,
            "regeneration": regeneration,
            "collapsed": self.collapsed,
            "sustainable_rate": self._sustainable_harvest_rate(),
        }

        return self._get_observation(), reward, done, info


def compute_kh(harvest_history: List[float], resource_history: List[float],
               config: CommonsConfig, alpha: float = 1.5) -> float:
    """
    Compute K_H (Harmonic/Normative alignment).

    K_H measures how well the agent's harvesting aligns with sustainability.
    High K_H = sustainable harvesting (resources maintained)
    Low K_H = over-harvesting (resources depleted)
    """
    if len(harvest_history) < 10 or len(resource_history) < 10:
        return 0.5  # Neutral

    # Method 1: Resource maintenance ratio
    initial = resource_history[0]
    final = resource_history[-1]
    maintenance_ratio = final / initial if initial > 0 else 0

    # Method 2: Deviation from sustainable harvest
    sustainable_harvests = []
    for i, R in enumerate(resource_history[:-1]):
        r = config.regeneration_rate
        K = config.carrying_capacity
        growth = r * R * (1 - R / K) if R > 0 else 0
        sustainable_harvests.append(growth)

    if len(sustainable_harvests) == len(harvest_history):
        deviations = []
        for h, s in zip(harvest_history, sustainable_harvests):
            if s > 0.01:  # Avoid division by near-zero
                dev = abs(h - s) / s
                deviations.append(min(dev, 2.0))  # Cap at 2x deviation
            else:
                deviations.append(0.0 if h < 0.01 else 1.0)

        mean_deviation = np.mean(deviations)
        sustainability_score = np.exp(-alpha * mean_deviation)
    else:
        sustainability_score = 0.5

    # Combine both measures
    kh = 0.4 * maintenance_ratio + 0.6 * sustainability_score

    return float(np.clip(kh, 0, 1))


class GreedyAgent:
    """Always harvests maximum."""
    name = "greedy"

    def act(self, obs: np.ndarray) -> np.ndarray:
        return np.array([1.0])


class ConservativeAgent:
    """Always harvests minimum."""
    name = "conservative"

    def act(self, obs: np.ndarray) -> np.ndarray:
        return np.array([0.1])


class SustainableAgent:
    """Tries to match sustainable harvest rate."""
    name = "sustainable"

    def act(self, obs: np.ndarray) -> np.ndarray:
        # obs[3] is sustainable rate hint (normalized)
        sustainable_hint = obs[3]
        # Scale to action space and add small margin
        target = np.clip(sustainable_hint * 8.0, 0.1, 0.9)
        return np.array([target])


class AdaptiveAgent:
    """Adapts based on resource trends."""
    name = "adaptive"

    def act(self, obs: np.ndarray) -> np.ndarray:
        resources = obs[0]
        trend = obs[1]

        base_rate = 0.4

        # Reduce harvest if declining
        if trend < -0.02:
            rate = base_rate * 0.5
        elif trend > 0.02:
            rate = base_rate * 1.1
        else:
            rate = base_rate

        # Adjust for resource level
        if resources < 0.4:
            rate *= 0.5
        elif resources > 0.8:
            rate *= 1.1

        return np.array([np.clip(rate, 0.05, 0.95)])


class RandomAgent:
    """Random harvest rate."""
    name = "random"

    def act(self, obs: np.ndarray) -> np.ndarray:
        return np.array([np.random.uniform(0.1, 0.9)])


class MyopicAgent:
    """Harvests proportional to current resources."""
    name = "myopic"

    def act(self, obs: np.ndarray) -> np.ndarray:
        resources = obs[0]
        return np.array([np.clip(resources * 0.7, 0.1, 0.95)])


def run_episode(env: TheCommonsEnvironment, agent) -> Dict:
    """Run single episode."""
    obs = env.reset()
    total_reward = 0
    done = False

    while not done:
        action = agent.act(obs)
        obs, reward, done, info = env.step(action)
        total_reward += reward

    kh = compute_kh(env.harvest_history, env.resource_history, env.config)

    return {
        "agent": agent.name,
        "total_reward": total_reward,
        "steps_survived": env.step_count,
        "collapsed": env.collapsed,
        "final_resources": env.resources,
        "K_H": kh,
        "mean_harvest": np.mean(env.harvest_history) if env.harvest_history else 0,
    }


def run_kh_validation_fixed(n_episodes: int = 50):
    """Run fixed K_H validation."""
    print("=" * 70)
    print("🌱 K_H VALIDATION (FIXED IMPLEMENTATION)")
    print("=" * 70)
    print()
    print("Testing K_H as sustainability/normative alignment metric")
    print()

    agents = [
        GreedyAgent(),
        MyopicAgent(),
        RandomAgent(),
        AdaptiveAgent(),
        ConservativeAgent(),
        SustainableAgent(),
    ]

    config = CommonsConfig(
        max_steps=200,
        initial_resources=100.0,
        regeneration_rate=0.05,
        collapse_threshold=10.0,
    )

    results = {agent.name: [] for agent in agents}

    for agent in agents:
        print(f"  Testing {agent.name}...", end=" ")

        for _ in range(n_episodes):
            env = TheCommonsEnvironment(config)
            result = run_episode(env, agent)
            results[agent.name].append(result)

        kh_vals = [r["K_H"] for r in results[agent.name]]
        print(f"K_H = {np.mean(kh_vals):.3f} ± {np.std(kh_vals):.3f}")

    # Summary
    print()
    print("-" * 70)
    print("📈 K_H VALIDATION SUMMARY")
    print("-" * 70)
    print()

    summary = {}
    print(f"{'Agent':<15} {'K_H':>10} {'Survival':>10} {'Collapse%':>10} {'Reward':>10}")
    print("-" * 60)

    for agent in agents:
        eps = results[agent.name]
        kh = [e["K_H"] for e in eps]
        survival = [e["steps_survived"] for e in eps]
        collapse = sum(1 for e in eps if e["collapsed"]) / len(eps)
        reward = [e["total_reward"] for e in eps]

        summary[agent.name] = {
            "K_H_mean": np.mean(kh),
            "K_H_std": np.std(kh),
            "survival_mean": np.mean(survival),
            "collapse_rate": collapse,
            "reward_mean": np.mean(reward),
        }

        print(f"{agent.name:<15} {np.mean(kh):>10.3f} {np.mean(survival):>10.1f} "
              f"{collapse*100:>10.1f} {np.mean(reward):>10.1f}")

    # Statistical analysis
    print()
    print("-" * 70)
    print("🧪 HYPOTHESIS TESTING")
    print("-" * 70)
    print()

    # Collect all data
    all_kh = []
    all_survival = []
    all_collapsed = []
    all_reward = []

    for name, eps in results.items():
        for e in eps:
            all_kh.append(e["K_H"])
            all_survival.append(e["steps_survived"])
            all_collapsed.append(1 if e["collapsed"] else 0)
            all_reward.append(e["total_reward"])

    # H9: K_H predicts survival
    r_survival, p_survival = pearsonr(all_kh, all_survival)
    print(f"H9: K_H → Survival: r = {r_survival:.3f}, p = {p_survival:.6f}")
    if r_survival > 0.3 and p_survival < 0.05:
        print("✅ SUPPORTED: Higher K_H predicts longer survival")
    else:
        print("⚠️ WEAK/NOT SUPPORTED")

    # H10: K_H differentiates agent types
    greedy_kh = [e["K_H"] for e in results["greedy"]]
    sustainable_kh = [e["K_H"] for e in results["sustainable"]]

    t_stat, p_value = ttest_ind(sustainable_kh, greedy_kh)
    ratio = np.mean(sustainable_kh) / (np.mean(greedy_kh) + 1e-10)

    # Safe Cohen's d
    pooled_var = (np.var(sustainable_kh) + np.var(greedy_kh)) / 2
    if pooled_var > 1e-10:
        cohens_d = (np.mean(sustainable_kh) - np.mean(greedy_kh)) / np.sqrt(pooled_var)
    else:
        cohens_d = 0.0

    print()
    print(f"H10: Sustainable vs Greedy K_H:")
    print(f"  Sustainable: {np.mean(sustainable_kh):.3f} ± {np.std(sustainable_kh):.3f}")
    print(f"  Greedy: {np.mean(greedy_kh):.3f} ± {np.std(greedy_kh):.3f}")
    print(f"  Ratio: {ratio:.2f}×")
    print(f"  t = {t_stat:.3f}, p = {p_value:.6f}")
    print(f"  Cohen's d = {cohens_d:.3f}")

    if ratio > 1.5 and p_value < 0.05:
        print("✅ SUPPORTED: Sustainable agents have significantly higher K_H")
    else:
        print("⚠️ WEAK/NOT SUPPORTED")

    # H11: K_H negatively correlates with collapse
    r_collapse, p_collapse = pearsonr(all_kh, all_collapsed)
    print()
    print(f"H11: K_H → Collapse: r = {r_collapse:.3f}, p = {p_collapse:.6f}")
    if r_collapse < -0.3 and p_collapse < 0.05:
        print("✅ SUPPORTED: Higher K_H predicts lower collapse probability")
    else:
        print("⚠️ WEAK/NOT SUPPORTED")

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "config": {
            "n_episodes": n_episodes,
            "max_steps": config.max_steps,
            "regeneration_rate": config.regeneration_rate,
        },
        "summary": summary,
        "statistics": {
            "kh_survival_r": float(r_survival),
            "kh_survival_p": float(p_survival),
            "kh_collapse_r": float(r_collapse),
            "kh_collapse_p": float(p_collapse),
            "sustainable_greedy_ratio": float(ratio),
            "cohens_d": float(cohens_d),
            "t_stat": float(t_stat),
            "p_value": float(p_value),
        },
        "hypotheses": {
            "H9_kh_predicts_survival": bool(r_survival > 0.3 and p_survival < 0.05),
            "H10_sustainable_higher_kh": bool(ratio > 1.5 and p_value < 0.05),
            "H11_kh_prevents_collapse": bool(r_collapse < -0.3 and p_collapse < 0.05),
        }
    }

    log_dir = Path("logs/kh_validation")
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"kh_validation_fixed_{timestamp}.json"

    with open(log_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n💾 Results saved → {log_file}")

    return output


if __name__ == "__main__":
    run_kh_validation_fixed(n_episodes=50)
