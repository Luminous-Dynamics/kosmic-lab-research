#!/usr/bin/env python3
"""
K_H (Harmonic/Normative) Validation Experiments

Hypothesis: K_H measures alignment with sustainable/normative behavior.
- High K_H agents maintain resources long-term
- Low K_H agents deplete resources quickly (tragedy of the commons)
- K_H predicts time-to-collapse in sustainability environments

Environment: "The Commons" - resource management with sustainability dynamics
"""

import numpy as np
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import warnings


@dataclass
class CommonsConfig:
    """Configuration for The Commons environment."""
    grid_size: int = 10
    initial_resources: float = 100.0
    regeneration_rate: float = 0.05  # Per timestep regeneration
    carrying_capacity: float = 100.0  # Max resources
    collapse_threshold: float = 10.0  # Below this = collapse
    max_steps: int = 500
    n_agents: int = 1


class TheCommonsEnvironment:
    """
    The Commons: A sustainability-focused environment.

    Resources regenerate logistically but can be depleted.
    Agents choose harvest rate. Over-harvesting leads to collapse.

    Dynamics:
        dR/dt = r * R * (1 - R/K) - total_harvest

    Where:
        R = current resources
        r = regeneration rate
        K = carrying capacity
    """

    def __init__(self, config: CommonsConfig = None):
        self.config = config or CommonsConfig()
        self.reset()

    def reset(self) -> np.ndarray:
        """Reset environment to initial state."""
        self.resources = self.config.initial_resources
        self.step_count = 0
        self.collapsed = False
        self.harvest_history = []
        self.resource_history = [self.resources]
        return self._get_observation()

    def _get_observation(self) -> np.ndarray:
        """
        Observation includes:
        - Current resource level (normalized)
        - Resource trend (recent change)
        - Steps remaining (normalized)
        - Sustainability indicator (how close to sustainable harvest)
        """
        trend = 0.0
        if len(self.resource_history) > 1:
            trend = self.resource_history[-1] - self.resource_history[-2]

        sustainable_harvest = self._sustainable_harvest_rate()

        return np.array([
            self.resources / self.config.carrying_capacity,  # Normalized resources
            np.clip(trend / 10.0, -1, 1),  # Trend
            1.0 - (self.step_count / self.config.max_steps),  # Time remaining
            sustainable_harvest,  # Sustainable rate hint
        ], dtype=np.float32)

    def _sustainable_harvest_rate(self) -> float:
        """Calculate maximum sustainable harvest rate."""
        # Logistic growth: dR/dt = r * R * (1 - R/K)
        # At equilibrium, harvest = growth
        r = self.config.regeneration_rate
        K = self.config.carrying_capacity
        R = self.resources

        # Maximum sustainable yield at R = K/2
        max_sustainable = r * K / 4  # MSY formula

        # Current sustainable given R
        current_growth = r * R * (1 - R / K) if R > 0 else 0

        return min(current_growth, max_sustainable) / 10.0  # Normalized

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, dict]:
        """
        Execute one step.

        Action: harvest_rate in [0, 1] - fraction of max possible harvest
        """
        if self.collapsed:
            return self._get_observation(), 0.0, True, {"collapsed": True}

        # Interpret action as harvest rate
        harvest_rate = np.clip(float(action[0]) if len(action.shape) > 0 else float(action), 0, 1)

        # Maximum harvest is proportional to resources
        max_harvest = self.resources * 0.2  # Can harvest up to 20% per step
        actual_harvest = harvest_rate * max_harvest

        # Apply harvest
        self.resources -= actual_harvest
        self.harvest_history.append(actual_harvest)

        # Apply regeneration (logistic growth)
        r = self.config.regeneration_rate
        K = self.config.carrying_capacity
        regeneration = r * self.resources * (1 - self.resources / K)
        self.resources += regeneration

        # Clamp resources
        self.resources = np.clip(self.resources, 0, K)
        self.resource_history.append(self.resources)

        # Check collapse
        if self.resources < self.config.collapse_threshold:
            self.collapsed = True

        self.step_count += 1
        done = self.collapsed or self.step_count >= self.config.max_steps

        # Reward is harvest (short-term incentive)
        reward = actual_harvest

        info = {
            "resources": self.resources,
            "harvest": actual_harvest,
            "regeneration": regeneration,
            "collapsed": self.collapsed,
            "sustainable_rate": self._sustainable_harvest_rate(),
        }

        return self._get_observation(), reward, done, info


def compute_kh_commons(harvest_history: List[float],
                       sustainable_rate: float,
                       alpha: float = 2.0) -> float:
    """
    Compute K_H for Commons environment.

    K_H = exp(-alpha * mean_deviation_from_sustainable)

    High K_H = harvesting close to sustainable rate
    Low K_H = over-harvesting or under-harvesting
    """
    if len(harvest_history) == 0:
        return 0.0

    harvest_array = np.array(harvest_history)

    # Deviation from sustainable (normalized)
    if sustainable_rate > 0:
        deviation = np.abs(harvest_array - sustainable_rate) / sustainable_rate
    else:
        deviation = harvest_array  # Any harvest is deviation if sustainable=0

    mean_deviation = np.mean(deviation)

    # Exponential decay based on deviation
    kh = np.exp(-alpha * mean_deviation)

    return float(np.clip(kh, 0, 1))


class GreedyAgent:
    """Always harvests maximum possible."""
    def __init__(self):
        self.name = "greedy"

    def act(self, obs: np.ndarray) -> np.ndarray:
        return np.array([1.0])  # Max harvest


class SustainableAgent:
    """Tries to match sustainable harvest rate."""
    def __init__(self):
        self.name = "sustainable"

    def act(self, obs: np.ndarray) -> np.ndarray:
        # obs[3] is sustainable rate hint
        sustainable_hint = obs[3]
        # Target slightly below sustainable to be safe
        target = sustainable_hint * 0.8
        return np.array([np.clip(target * 5, 0, 1)])  # Scale appropriately


class AdaptiveAgent:
    """Adapts harvest based on resource trends."""
    def __init__(self):
        self.name = "adaptive"

    def act(self, obs: np.ndarray) -> np.ndarray:
        resources = obs[0]  # Normalized resources
        trend = obs[1]  # Resource trend

        # If resources declining, reduce harvest
        # If resources stable/growing, can harvest more
        base_rate = 0.3

        if trend < -0.05:  # Declining
            rate = base_rate * 0.5
        elif trend > 0.05:  # Growing
            rate = base_rate * 1.2
        else:
            rate = base_rate

        # Also adjust for resource level
        if resources < 0.3:  # Low resources
            rate *= 0.5
        elif resources > 0.7:  # High resources
            rate *= 1.1

        return np.array([np.clip(rate, 0, 1)])


class RandomAgent:
    """Random harvest rate."""
    def __init__(self):
        self.name = "random"

    def act(self, obs: np.ndarray) -> np.ndarray:
        return np.array([np.random.random()])


class MyopicAgent:
    """Short-term optimizer - high harvest when resources high."""
    def __init__(self):
        self.name = "myopic"

    def act(self, obs: np.ndarray) -> np.ndarray:
        resources = obs[0]
        # Harvest proportional to current resources (exploit now)
        return np.array([resources * 0.8])


def run_episode(env: TheCommonsEnvironment,
                agent,
                compute_sustainable: bool = True) -> Dict:
    """Run single episode and compute K_H."""
    obs = env.reset()

    observations = [obs.copy()]
    actions = []
    rewards = []
    sustainable_rates = []

    done = False
    while not done:
        action = agent.act(obs)
        actions.append(action.copy())

        obs, reward, done, info = env.step(action)

        observations.append(obs.copy())
        rewards.append(reward)
        sustainable_rates.append(info["sustainable_rate"])

    # Compute K_H
    avg_sustainable = np.mean(sustainable_rates) if sustainable_rates else 0.1
    kh = compute_kh_commons(
        env.harvest_history,
        avg_sustainable * 10,  # Denormalize
        alpha=2.0
    )

    return {
        "agent": agent.name,
        "total_reward": sum(rewards),
        "steps_survived": env.step_count,
        "collapsed": env.collapsed,
        "final_resources": env.resources,
        "K_H": kh,
        "mean_harvest": np.mean(env.harvest_history),
        "resource_trajectory": env.resource_history,
    }


def run_kh_validation(n_episodes: int = 30, verbose: bool = True) -> Dict:
    """
    Run K_H validation experiments.

    Hypotheses:
    H9: K_H predicts long-term survival (time-to-collapse)
    H10: Greedy agents have low K_H, sustainable agents have high K_H
    H11: K_H negatively correlates with collapse probability
    """
    print("=" * 70)
    print("🌱 K_H (HARMONIC/NORMATIVE) VALIDATION EXPERIMENTS")
    print("=" * 70)
    print()
    print("Environment: The Commons (Resource Sustainability)")
    print("Hypothesis: K_H measures alignment with sustainable behavior")
    print()

    agents = [
        GreedyAgent(),
        MyopicAgent(),
        RandomAgent(),
        AdaptiveAgent(),
        SustainableAgent(),
    ]

    results = {agent.name: [] for agent in agents}

    config = CommonsConfig(
        max_steps=500,
        initial_resources=100.0,
        regeneration_rate=0.05,
        collapse_threshold=10.0,
    )

    for agent in agents:
        if verbose:
            print(f"📊 Testing {agent.name} agent ({n_episodes} episodes)...")

        for _ in range(n_episodes):
            env = TheCommonsEnvironment(config)
            episode_result = run_episode(env, agent)
            results[agent.name].append(episode_result)

    # Aggregate results
    summary = {}
    for agent_name, episodes in results.items():
        kh_values = [e["K_H"] for e in episodes]
        survival_times = [e["steps_survived"] for e in episodes]
        collapse_rate = sum(1 for e in episodes if e["collapsed"]) / len(episodes)
        total_rewards = [e["total_reward"] for e in episodes]

        summary[agent_name] = {
            "K_H_mean": np.mean(kh_values),
            "K_H_std": np.std(kh_values),
            "survival_mean": np.mean(survival_times),
            "survival_std": np.std(survival_times),
            "collapse_rate": collapse_rate,
            "reward_mean": np.mean(total_rewards),
            "reward_std": np.std(total_rewards),
        }

    # Print results
    print()
    print("-" * 70)
    print("📈 K_H VALIDATION SUMMARY")
    print("-" * 70)
    print()
    print(f"{'Agent':<15} {'K_H (mean)':<12} {'K_H (std)':<10} {'Survival':<10} {'Collapse%':<10} {'Reward':<10}")
    print("-" * 70)

    for agent_name in ["greedy", "myopic", "random", "adaptive", "sustainable"]:
        s = summary[agent_name]
        print(f"{agent_name:<15} {s['K_H_mean']:<12.3f} {s['K_H_std']:<10.3f} "
              f"{s['survival_mean']:<10.1f} {s['collapse_rate']*100:<10.1f} {s['reward_mean']:<10.1f}")

    # Statistical tests
    print()
    print("-" * 70)
    print("🧪 HYPOTHESIS TESTING")
    print("-" * 70)

    # H9: K_H predicts survival
    all_kh = []
    all_survival = []
    all_collapsed = []
    for agent_name, episodes in results.items():
        for e in episodes:
            all_kh.append(e["K_H"])
            all_survival.append(e["steps_survived"])
            all_collapsed.append(1 if e["collapsed"] else 0)

    # Correlation K_H vs survival
    from scipy.stats import pearsonr, spearmanr
    try:
        r_survival, p_survival = pearsonr(all_kh, all_survival)
        r_collapse, p_collapse = pearsonr(all_kh, all_collapsed)

        print(f"\nH9: K_H → Survival correlation: r = {r_survival:.3f}, p = {p_survival:.6f}")
        print(f"H11: K_H → Collapse correlation: r = {r_collapse:.3f}, p = {p_collapse:.6f}")

        if r_survival > 0.3 and p_survival < 0.05:
            print("✓ H9 SUPPORTED: Higher K_H predicts longer survival")
        else:
            print("✗ H9 NOT SUPPORTED: K_H-survival correlation weak")

        if r_collapse < -0.3 and p_collapse < 0.05:
            print("✓ H11 SUPPORTED: Higher K_H predicts lower collapse probability")
        else:
            print("✗ H11 NOT SUPPORTED: K_H-collapse correlation weak")

    except Exception as e:
        print(f"Statistical test error: {e}")
        r_survival, p_survival = 0, 1
        r_collapse, p_collapse = 0, 1

    # H10: Agent type differences
    greedy_kh = summary["greedy"]["K_H_mean"]
    sustainable_kh = summary["sustainable"]["K_H_mean"]
    kh_ratio = sustainable_kh / greedy_kh if greedy_kh > 0 else float('inf')

    print(f"\nH10: Sustainable K_H / Greedy K_H ratio: {kh_ratio:.2f}×")
    if kh_ratio > 1.5:
        print("✓ H10 SUPPORTED: Sustainable agents have significantly higher K_H")
    else:
        print("✗ H10 NOT SUPPORTED: K_H does not distinguish agent types well")

    # Effect size (Cohen's d)
    greedy_episodes = results["greedy"]
    sustainable_episodes = results["sustainable"]
    greedy_kh_values = [e["K_H"] for e in greedy_episodes]
    sustainable_kh_values = [e["K_H"] for e in sustainable_episodes]

    pooled_std = np.sqrt((np.var(greedy_kh_values) + np.var(sustainable_kh_values)) / 2)
    cohens_d = (np.mean(sustainable_kh_values) - np.mean(greedy_kh_values)) / pooled_std if pooled_std > 0 else 0

    print(f"\nEffect size (Cohen's d): {cohens_d:.2f}")
    if abs(cohens_d) > 0.8:
        print("✓ Large effect size (d > 0.8)")
    elif abs(cohens_d) > 0.5:
        print("~ Medium effect size (0.5 < d < 0.8)")
    else:
        print("✗ Small effect size (d < 0.5)")

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "config": {
            "n_episodes": n_episodes,
            "max_steps": config.max_steps,
            "regeneration_rate": config.regeneration_rate,
            "collapse_threshold": config.collapse_threshold,
        },
        "summary": summary,
        "statistics": {
            "kh_survival_correlation": r_survival,
            "kh_survival_p": p_survival,
            "kh_collapse_correlation": r_collapse,
            "kh_collapse_p": p_collapse,
            "sustainable_greedy_ratio": kh_ratio,
            "cohens_d": cohens_d,
        },
        "hypotheses": {
            "H9_supported": r_survival > 0.3 and p_survival < 0.05,
            "H10_supported": kh_ratio > 1.5,
            "H11_supported": r_collapse < -0.3 and p_collapse < 0.05,
        }
    }

    # Save to file
    log_dir = Path("logs/kh_validation")
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"kh_validation_{timestamp}.json"

    with open(log_file, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n💾 Results saved → {log_file}")

    return output


if __name__ == "__main__":
    results = run_kh_validation(n_episodes=30, verbose=True)
