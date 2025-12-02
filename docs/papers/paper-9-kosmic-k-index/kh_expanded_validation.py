#!/usr/bin/env python3
"""
K_H Expanded Validation

The initial K_H validation showed strong results (r=0.978 survival correlation).
This experiment expands validation to additional normative scenarios:

1. Prisoner's Dilemma: Cooperation vs defection norms
2. Public Goods Game: Contribution vs free-riding
3. Fairness Game: Equitable distribution norms
4. Long-term Planning: Delayed gratification norms

Each scenario tests whether K_H captures alignment with different normative frameworks.
"""

import numpy as np
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
from scipy.stats import pearsonr, ttest_ind


# =============================================================================
# ENVIRONMENT 1: Iterated Prisoner's Dilemma
# =============================================================================

@dataclass
class IPDConfig:
    """Iterated Prisoner's Dilemma configuration."""
    n_rounds: int = 50
    # Payoff matrix: (cooperate_A, cooperate_B) -> (payoff_A, payoff_B)
    cc_payoff: Tuple[float, float] = (3.0, 3.0)  # Both cooperate
    cd_payoff: Tuple[float, float] = (0.0, 5.0)  # A cooperates, B defects
    dc_payoff: Tuple[float, float] = (5.0, 0.0)  # A defects, B cooperates
    dd_payoff: Tuple[float, float] = (1.0, 1.0)  # Both defect


class IteratedPDEnvironment:
    """
    Iterated Prisoner's Dilemma against fixed opponent.

    Normative standard: Cooperative behavior (tit-for-tat like)
    """

    def __init__(self, config: IPDConfig = None, opponent_type: str = "tft"):
        self.config = config or IPDConfig()
        self.opponent_type = opponent_type
        self.reset()

    def reset(self) -> np.ndarray:
        self.round = 0
        self.agent_history = []
        self.opponent_history = []
        self.done = False
        return self._get_observation()

    def _get_observation(self) -> np.ndarray:
        # Last opponent action, cooperation rate, round progress
        last_opp = self.opponent_history[-1] if self.opponent_history else 0.5
        coop_rate = np.mean(self.agent_history) if self.agent_history else 0.5
        progress = self.round / self.config.n_rounds
        return np.array([last_opp, coop_rate, progress], dtype=np.float32)

    def _opponent_action(self) -> float:
        """Generate opponent action based on type."""
        if self.opponent_type == "tft":  # Tit-for-tat
            if not self.agent_history:
                return 1.0  # Start cooperating
            return self.agent_history[-1]
        elif self.opponent_type == "always_cooperate":
            return 1.0
        elif self.opponent_type == "always_defect":
            return 0.0
        elif self.opponent_type == "random":
            return float(np.random.random() > 0.5)
        else:
            return 0.5

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, dict]:
        if self.done:
            return self._get_observation(), 0.0, True, {}

        # Interpret action as cooperation probability
        agent_coop = float(action[0]) if hasattr(action, '__len__') else float(action)
        agent_coop = 1.0 if agent_coop > 0.5 else 0.0

        opp_coop = self._opponent_action()

        self.agent_history.append(agent_coop)
        self.opponent_history.append(opp_coop)

        # Determine payoff
        if agent_coop and opp_coop:
            reward = self.config.cc_payoff[0]
        elif agent_coop and not opp_coop:
            reward = self.config.cd_payoff[0]
        elif not agent_coop and opp_coop:
            reward = self.config.dc_payoff[0]
        else:
            reward = self.config.dd_payoff[0]

        self.round += 1
        if self.round >= self.config.n_rounds:
            self.done = True

        info = {
            "cooperation_rate": np.mean(self.agent_history),
            "mutual_cooperation": sum(1 for a, o in zip(self.agent_history, self.opponent_history)
                                     if a and o) / len(self.agent_history),
        }

        return self._get_observation(), reward, self.done, info


# =============================================================================
# ENVIRONMENT 2: Public Goods Game
# =============================================================================

@dataclass
class PublicGoodsConfig:
    """Public Goods Game configuration."""
    n_rounds: int = 30
    multiplier: float = 1.5  # Contributions multiplied
    n_players: int = 4
    initial_endowment: float = 10.0


class PublicGoodsEnvironment:
    """
    Public Goods Game with simulated other players.

    Normative standard: Contributing to public good
    """

    def __init__(self, config: PublicGoodsConfig = None):
        self.config = config or PublicGoodsConfig()
        self.reset()

    def reset(self) -> np.ndarray:
        self.round = 0
        self.done = False
        self.contributions = []
        self.other_contributions = []
        return self._get_observation()

    def _get_observation(self) -> np.ndarray:
        avg_contrib = np.mean(self.contributions) if self.contributions else 0.5
        avg_others = np.mean(self.other_contributions) if self.other_contributions else 0.5
        progress = self.round / self.config.n_rounds
        return np.array([avg_contrib, avg_others, progress], dtype=np.float32)

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, dict]:
        if self.done:
            return self._get_observation(), 0.0, True, {}

        # Agent's contribution (0 to 1 of endowment)
        contribution = np.clip(float(action[0]) if hasattr(action, '__len__')
                              else float(action), 0, 1)
        self.contributions.append(contribution)

        # Others contribute based on varying strategies
        others_mean = 0.4 + 0.1 * np.random.randn()  # Average around 40%
        self.other_contributions.append(others_mean)

        # Total pool
        total_contrib = contribution + others_mean * (self.config.n_players - 1)
        public_good = total_contrib * self.config.multiplier / self.config.n_players

        # Reward: kept portion + share of public good
        reward = (1 - contribution) + public_good

        self.round += 1
        if self.round >= self.config.n_rounds:
            self.done = True

        info = {
            "contribution_rate": np.mean(self.contributions),
            "public_good_total": total_contrib * self.config.multiplier,
        }

        return self._get_observation(), reward, self.done, info


# =============================================================================
# ENVIRONMENT 3: Fairness/Ultimatum Game
# =============================================================================

@dataclass
class FairnessConfig:
    """Fairness game configuration."""
    n_rounds: int = 30
    total_amount: float = 10.0


class FairnessEnvironment:
    """
    Repeated Ultimatum-like game (as proposer).

    Normative standard: Fair (50-50) splits
    Responder accepts based on fairness threshold.
    """

    def __init__(self, config: FairnessConfig = None):
        self.config = config or FairnessConfig()
        self.reset()

    def reset(self) -> np.ndarray:
        self.round = 0
        self.done = False
        self.offers = []
        self.acceptances = []
        return self._get_observation()

    def _get_observation(self) -> np.ndarray:
        avg_offer = np.mean(self.offers) if self.offers else 0.5
        accept_rate = np.mean(self.acceptances) if self.acceptances else 0.5
        progress = self.round / self.config.n_rounds
        return np.array([avg_offer, accept_rate, progress], dtype=np.float32)

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, dict]:
        if self.done:
            return self._get_observation(), 0.0, True, {}

        # Offer as fraction to give to responder (0 = keep all, 1 = give all)
        offer = np.clip(float(action[0]) if hasattr(action, '__len__')
                       else float(action), 0, 1)
        self.offers.append(offer)

        # Responder threshold varies (most reject < 20%)
        threshold = 0.2 + 0.1 * np.random.randn()
        accepted = offer >= threshold
        self.acceptances.append(float(accepted))

        if accepted:
            # Agent keeps (1-offer) of total
            reward = (1 - offer) * self.config.total_amount
        else:
            reward = 0.0  # Both get nothing

        self.round += 1
        if self.round >= self.config.n_rounds:
            self.done = True

        info = {
            "mean_offer": np.mean(self.offers),
            "acceptance_rate": np.mean(self.acceptances),
            "fairness_score": 1 - abs(np.mean(self.offers) - 0.5) * 2,  # 1 if fair
        }

        return self._get_observation(), reward, self.done, info


# =============================================================================
# ENVIRONMENT 4: Long-term Planning (Delayed Gratification)
# =============================================================================

@dataclass
class DelayedGratificationConfig:
    """Delayed gratification configuration."""
    n_rounds: int = 50
    discount_rate: float = 0.05  # Per-step discount


class DelayedGratificationEnvironment:
    """
    Investment/saving game: Save now for larger returns later.

    Normative standard: Patient, long-term oriented behavior
    """

    def __init__(self, config: DelayedGratificationConfig = None):
        self.config = config or DelayedGratificationConfig()
        self.reset()

    def reset(self) -> np.ndarray:
        self.round = 0
        self.done = False
        self.savings = 0.0
        self.consumptions = []
        return self._get_observation()

    def _get_observation(self) -> np.ndarray:
        income = 1.0  # Fixed income per round
        savings_norm = self.savings / (self.config.n_rounds + 1)
        progress = self.round / self.config.n_rounds
        return np.array([income, savings_norm, progress], dtype=np.float32)

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, dict]:
        if self.done:
            return self._get_observation(), 0.0, True, {}

        # Action: fraction to save (0 = consume all, 1 = save all)
        save_rate = np.clip(float(action[0]) if hasattr(action, '__len__')
                           else float(action), 0, 1)

        income = 1.0
        saved = income * save_rate
        consumed = income * (1 - save_rate)

        # Savings grow at discount rate
        self.savings = (self.savings + saved) * (1 + self.config.discount_rate)
        self.consumptions.append(consumed)

        # Immediate reward is consumption (delayed reward at end)
        reward = consumed

        self.round += 1
        if self.round >= self.config.n_rounds:
            self.done = True
            # Bonus: accumulated savings
            reward += self.savings

        info = {
            "savings": self.savings,
            "avg_save_rate": 1 - np.mean(self.consumptions),
            "final_wealth": self.savings if self.done else None,
        }

        return self._get_observation(), reward, self.done, info


# =============================================================================
# K_H COMPUTATION
# =============================================================================

def compute_kh_ipd(agent_history: List[float], opponent_type: str) -> float:
    """K_H for IPD: alignment with cooperative norm."""
    if not agent_history:
        return 0.5

    coop_rate = np.mean(agent_history)

    # Normative: TFT-like cooperation (cooperate on average)
    # High K_H = high cooperation rate
    return float(coop_rate)


def compute_kh_public_goods(contributions: List[float]) -> float:
    """K_H for Public Goods: alignment with contribution norm."""
    if not contributions:
        return 0.5

    # Normative: Full contribution is ideal
    return float(np.mean(contributions))


def compute_kh_fairness(offers: List[float]) -> float:
    """K_H for Fairness: alignment with fair split norm."""
    if not offers:
        return 0.5

    # Normative: 50-50 split is ideal
    fairness = 1 - abs(np.mean(offers) - 0.5) * 2
    return float(np.clip(fairness, 0, 1))


def compute_kh_delayed(consumptions: List[float]) -> float:
    """K_H for Delayed Gratification: alignment with patience norm."""
    if not consumptions:
        return 0.5

    # Normative: Higher saving rate is better
    save_rate = 1 - np.mean(consumptions)
    return float(save_rate)


# =============================================================================
# AGENTS
# =============================================================================

class NormativeAgent:
    """Agent that follows the normative standard."""
    name = "normative"

    def act(self, obs: np.ndarray) -> np.ndarray:
        # Always follows norm
        return np.array([0.8])  # High cooperation/contribution/fairness/saving


class GreedyAgent:
    """Agent that maximizes short-term gain."""
    name = "greedy"

    def act(self, obs: np.ndarray) -> np.ndarray:
        return np.array([0.1])  # Low cooperation/contribution/etc


class AdaptiveAgent:
    """Agent that adapts based on context."""
    name = "adaptive"

    def act(self, obs: np.ndarray) -> np.ndarray:
        # Mirror opponent/others behavior
        return np.array([obs[0] * 0.8 + 0.1])


class RandomAgent:
    """Random behavior."""
    name = "random"

    def act(self, obs: np.ndarray) -> np.ndarray:
        return np.array([np.random.uniform(0.2, 0.8)])


class MixedAgent:
    """Sometimes follows norm, sometimes exploits."""
    name = "mixed"

    def act(self, obs: np.ndarray) -> np.ndarray:
        if np.random.random() > 0.5:
            return np.array([0.7])  # Cooperative
        else:
            return np.array([0.2])  # Exploitative


# =============================================================================
# MAIN EXPERIMENT
# =============================================================================

def run_scenario(env_class, config, agents, n_episodes, kh_func, scenario_name):
    """Run validation for a single scenario."""
    print(f"\n--- {scenario_name} ---")

    results = {agent.name: [] for agent in agents}

    for agent in agents:
        print(f"  Testing {agent.name}...", end=" ")

        kh_values = []
        rewards = []

        for _ in range(n_episodes):
            env = env_class(config)
            obs = env.reset()
            total_reward = 0
            done = False

            while not done:
                action = agent.act(obs)
                obs, reward, done, info = env.step(action)
                total_reward += reward

            # Compute K_H based on scenario
            if hasattr(env, 'agent_history'):
                kh = kh_func(env.agent_history, getattr(env, 'opponent_type', None))
            elif hasattr(env, 'contributions'):
                kh = kh_func(env.contributions)
            elif hasattr(env, 'offers'):
                kh = kh_func(env.offers)
            elif hasattr(env, 'consumptions'):
                kh = kh_func(env.consumptions)
            else:
                kh = 0.5

            kh_values.append(kh)
            rewards.append(total_reward)

            results[agent.name].append({
                "K_H": kh,
                "reward": total_reward,
                "info": info,
            })

        print(f"K_H = {np.mean(kh_values):.3f} ± {np.std(kh_values):.3f}, "
              f"Reward = {np.mean(rewards):.1f}")

    return results


def run_kh_expanded_validation(n_episodes: int = 30):
    """Run expanded K_H validation across multiple scenarios."""
    print("=" * 70)
    print("K_H EXPANDED VALIDATION")
    print("=" * 70)
    print()
    print("Testing K_H across multiple normative scenarios")
    print()

    agents = [
        GreedyAgent(),
        RandomAgent(),
        MixedAgent(),
        AdaptiveAgent(),
        NormativeAgent(),
    ]

    all_results = {}

    # Scenario 1: IPD
    ipd_results = run_scenario(
        IteratedPDEnvironment, IPDConfig(),
        agents, n_episodes,
        compute_kh_ipd, "Prisoner's Dilemma (Cooperation)"
    )
    all_results["ipd"] = ipd_results

    # Scenario 2: Public Goods
    pg_results = run_scenario(
        PublicGoodsEnvironment, PublicGoodsConfig(),
        agents, n_episodes,
        compute_kh_public_goods, "Public Goods (Contribution)"
    )
    all_results["public_goods"] = pg_results

    # Scenario 3: Fairness
    fair_results = run_scenario(
        FairnessEnvironment, FairnessConfig(),
        agents, n_episodes,
        compute_kh_fairness, "Fairness (Equitable Split)"
    )
    all_results["fairness"] = fair_results

    # Scenario 4: Delayed Gratification
    dg_results = run_scenario(
        DelayedGratificationEnvironment, DelayedGratificationConfig(),
        agents, n_episodes,
        compute_kh_delayed, "Delayed Gratification (Patience)"
    )
    all_results["delayed_gratification"] = dg_results

    # Summary statistics
    print()
    print("-" * 70)
    print("VALIDATION SUMMARY")
    print("-" * 70)
    print()

    validation_stats = {}

    for scenario_name, scenario_results in all_results.items():
        # Collect K_H and rewards across all agents
        all_kh = []
        all_rewards = []
        for agent_name, episodes in scenario_results.items():
            for ep in episodes:
                all_kh.append(ep["K_H"])
                all_rewards.append(ep["reward"])

        # K_H - Reward correlation
        r, p = pearsonr(all_kh, all_rewards)

        # Normative vs Greedy comparison
        norm_kh = [ep["K_H"] for ep in scenario_results["normative"]]
        greedy_kh = [ep["K_H"] for ep in scenario_results["greedy"]]
        t_stat, t_p = ttest_ind(norm_kh, greedy_kh)
        ratio = np.mean(norm_kh) / (np.mean(greedy_kh) + 1e-10)

        validation_stats[scenario_name] = {
            "kh_reward_r": r,
            "kh_reward_p": p,
            "norm_greedy_ratio": ratio,
            "norm_greedy_t": t_stat,
            "norm_greedy_p": t_p,
        }

        print(f"{scenario_name}:")
        print(f"  K_H-Reward r = {r:.3f} (p = {p:.4f})")
        print(f"  Normative/Greedy K_H ratio: {ratio:.2f}×")

    # Overall assessment
    print()
    print("-" * 70)
    print("OVERALL ASSESSMENT")
    print("-" * 70)
    print()

    n_validated = sum(1 for v in validation_stats.values()
                     if v["norm_greedy_ratio"] > 1.5 and v["norm_greedy_p"] < 0.05)
    n_scenarios = len(validation_stats)

    print(f"Scenarios where K_H discriminates normative from greedy: {n_validated}/{n_scenarios}")
    print()

    if n_validated == n_scenarios:
        print("CONCLUSION: K_H STRONGLY VALIDATED across all normative scenarios")
    elif n_validated >= n_scenarios * 0.75:
        print("CONCLUSION: K_H VALIDATED in most scenarios")
    elif n_validated >= n_scenarios * 0.5:
        print("CONCLUSION: K_H PARTIALLY VALIDATED - works in some scenarios")
    else:
        print("CONCLUSION: K_H WEAKLY VALIDATED - needs refinement")

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "n_episodes": n_episodes,
        "scenarios": {
            name: {
                "kh_reward_r": float(stats["kh_reward_r"]),
                "kh_reward_p": float(stats["kh_reward_p"]),
                "norm_greedy_ratio": float(stats["norm_greedy_ratio"]),
                "validated": bool(stats["norm_greedy_ratio"] > 1.5 and stats["norm_greedy_p"] < 0.05),
            }
            for name, stats in validation_stats.items()
        },
        "n_validated": n_validated,
        "n_scenarios": n_scenarios,
    }

    log_dir = Path("logs/kh_expanded")
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"kh_expanded_validation_{timestamp}.json"

    with open(log_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {log_file}")

    return output


if __name__ == "__main__":
    run_kh_expanded_validation(n_episodes=30)
