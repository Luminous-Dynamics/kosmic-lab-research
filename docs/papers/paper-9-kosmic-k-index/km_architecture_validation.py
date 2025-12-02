#!/usr/bin/env python3
"""
K_M Architecture Validation: Comprehensive Multi-Architecture Analysis

Validates that K_M (temporal memory) is truly independent by testing across:
- Feedforward (no memory)
- Simple RNN
- GRU
- LSTM
- Transformer (attention-based memory)

Hypothesis: K_M should discriminate architectures by their memory capacity,
AND remain independent from other K dimensions across all architectures.
"""

import numpy as np
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from scipy.stats import pearsonr, ttest_ind
from dataclasses import dataclass


@dataclass
class ArchitectureConfig:
    """Configuration for different architectures."""
    name: str
    has_memory: bool
    memory_type: str
    expected_km_range: Tuple[float, float]


# Define architectures
ARCHITECTURES = [
    ArchitectureConfig("feedforward", False, "none", (0.0, 0.1)),
    ArchitectureConfig("simple_rnn", True, "recurrent", (0.1, 0.4)),
    ArchitectureConfig("gru", True, "gated_recurrent", (0.15, 0.5)),
    ArchitectureConfig("lstm", True, "gated_recurrent", (0.15, 0.5)),
    ArchitectureConfig("transformer", True, "attention", (0.1, 0.4)),
]


class DelayedRewardEnvironment:
    """
    Environment requiring temporal memory to solve optimally.

    A hint is given at timestep 0, and the correct action must be taken
    at timestep T (delay). Success requires remembering the hint.
    """

    def __init__(self, delay: int = 10, obs_dim: int = 4, action_dim: int = 2):
        self.delay = delay
        self.obs_dim = obs_dim
        self.action_dim = action_dim
        self.reset()

    def reset(self) -> np.ndarray:
        self.step_count = 0
        self.hint = np.random.randint(0, self.action_dim)
        self.max_steps = self.delay + 5
        return self._get_obs()

    def _get_obs(self) -> np.ndarray:
        obs = np.zeros(self.obs_dim)
        obs[0] = self.step_count / self.max_steps  # Time signal

        if self.step_count == 0:
            # Hint given at start
            obs[1] = (self.hint + 1) / self.action_dim  # Normalized hint
        else:
            obs[1] = 0.0  # No hint after first step

        obs[2] = 1.0 if self.step_count == self.delay else 0.0  # Decision time
        obs[3] = np.random.randn() * 0.1  # Noise

        return obs.astype(np.float32)

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, dict]:
        action_idx = int(np.argmax(action)) if len(action) > 1 else int(action[0] > 0)

        reward = 0.0
        if self.step_count == self.delay:
            # Decision time - reward for correct action
            if action_idx == self.hint:
                reward = 1.0
            else:
                reward = -0.5

        self.step_count += 1
        done = self.step_count >= self.max_steps

        return self._get_obs(), reward, done, {"hint": self.hint, "action": action_idx}


class FeedforwardAgent:
    """Simple feedforward agent (no memory)."""

    def __init__(self, obs_dim: int, action_dim: int, hidden_dim: int = 32):
        self.name = "feedforward"
        self.obs_dim = obs_dim
        self.action_dim = action_dim
        # Simple linear layers
        self.w1 = np.random.randn(obs_dim, hidden_dim) * 0.1
        self.w2 = np.random.randn(hidden_dim, action_dim) * 0.1

    def act(self, obs: np.ndarray) -> np.ndarray:
        h = np.tanh(obs @ self.w1)
        out = h @ self.w2
        return out


class SimpleRNNAgent:
    """Simple RNN with hidden state."""

    def __init__(self, obs_dim: int, action_dim: int, hidden_dim: int = 32):
        self.name = "simple_rnn"
        self.obs_dim = obs_dim
        self.action_dim = action_dim
        self.hidden_dim = hidden_dim

        self.w_ih = np.random.randn(obs_dim, hidden_dim) * 0.1
        self.w_hh = np.random.randn(hidden_dim, hidden_dim) * 0.1
        self.w_ho = np.random.randn(hidden_dim, action_dim) * 0.1
        self.h = np.zeros(hidden_dim)

    def reset(self):
        self.h = np.zeros(self.hidden_dim)

    def act(self, obs: np.ndarray) -> np.ndarray:
        self.h = np.tanh(obs @ self.w_ih + self.h @ self.w_hh)
        out = self.h @ self.w_ho
        return out


class GRUAgent:
    """GRU agent with gated memory."""

    def __init__(self, obs_dim: int, action_dim: int, hidden_dim: int = 32):
        self.name = "gru"
        self.obs_dim = obs_dim
        self.action_dim = action_dim
        self.hidden_dim = hidden_dim

        # GRU gates
        self.w_z = np.random.randn(obs_dim + hidden_dim, hidden_dim) * 0.1  # Update gate
        self.w_r = np.random.randn(obs_dim + hidden_dim, hidden_dim) * 0.1  # Reset gate
        self.w_h = np.random.randn(obs_dim + hidden_dim, hidden_dim) * 0.1  # Candidate
        self.w_o = np.random.randn(hidden_dim, action_dim) * 0.1
        self.h = np.zeros(hidden_dim)

    def reset(self):
        self.h = np.zeros(self.hidden_dim)

    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -20, 20)))

    def act(self, obs: np.ndarray) -> np.ndarray:
        combined = np.concatenate([obs, self.h])

        z = self._sigmoid(combined @ self.w_z)  # Update gate
        r = self._sigmoid(combined @ self.w_r)  # Reset gate

        combined_reset = np.concatenate([obs, r * self.h])
        h_candidate = np.tanh(combined_reset @ self.w_h)

        self.h = (1 - z) * self.h + z * h_candidate

        out = self.h @ self.w_o
        return out


class LSTMAgent:
    """LSTM agent with cell state memory."""

    def __init__(self, obs_dim: int, action_dim: int, hidden_dim: int = 32):
        self.name = "lstm"
        self.obs_dim = obs_dim
        self.action_dim = action_dim
        self.hidden_dim = hidden_dim

        # LSTM gates
        self.w_f = np.random.randn(obs_dim + hidden_dim, hidden_dim) * 0.1  # Forget gate
        self.w_i = np.random.randn(obs_dim + hidden_dim, hidden_dim) * 0.1  # Input gate
        self.w_c = np.random.randn(obs_dim + hidden_dim, hidden_dim) * 0.1  # Candidate
        self.w_o_gate = np.random.randn(obs_dim + hidden_dim, hidden_dim) * 0.1  # Output gate
        self.w_out = np.random.randn(hidden_dim, action_dim) * 0.1

        self.h = np.zeros(hidden_dim)
        self.c = np.zeros(hidden_dim)

    def reset(self):
        self.h = np.zeros(self.hidden_dim)
        self.c = np.zeros(self.hidden_dim)

    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -20, 20)))

    def act(self, obs: np.ndarray) -> np.ndarray:
        combined = np.concatenate([obs, self.h])

        f = self._sigmoid(combined @ self.w_f)  # Forget gate
        i = self._sigmoid(combined @ self.w_i)  # Input gate
        c_candidate = np.tanh(combined @ self.w_c)  # Candidate cell
        o = self._sigmoid(combined @ self.w_o_gate)  # Output gate

        self.c = f * self.c + i * c_candidate
        self.h = o * np.tanh(self.c)

        out = self.h @ self.w_out
        return out


class TransformerAgent:
    """Simplified transformer agent with attention-based memory."""

    def __init__(self, obs_dim: int, action_dim: int, hidden_dim: int = 32,
                 context_len: int = 15):
        self.name = "transformer"
        self.obs_dim = obs_dim
        self.action_dim = action_dim
        self.hidden_dim = hidden_dim
        self.context_len = context_len

        # Attention weights
        self.w_q = np.random.randn(obs_dim, hidden_dim) * 0.1
        self.w_k = np.random.randn(obs_dim, hidden_dim) * 0.1
        self.w_v = np.random.randn(obs_dim, hidden_dim) * 0.1
        self.w_o = np.random.randn(hidden_dim, action_dim) * 0.1

        self.context = []

    def reset(self):
        self.context = []

    def act(self, obs: np.ndarray) -> np.ndarray:
        self.context.append(obs.copy())
        if len(self.context) > self.context_len:
            self.context = self.context[-self.context_len:]

        # Stack context
        context_arr = np.array(self.context)  # (T, obs_dim)

        # Compute attention
        Q = obs @ self.w_q  # (hidden_dim,)
        K = context_arr @ self.w_k  # (T, hidden_dim)
        V = context_arr @ self.w_v  # (T, hidden_dim)

        # Attention scores
        scores = K @ Q / np.sqrt(self.hidden_dim)  # (T,)
        weights = np.exp(scores - np.max(scores))
        weights = weights / (np.sum(weights) + 1e-10)

        # Weighted sum
        attended = weights @ V  # (hidden_dim,)

        out = attended @ self.w_o
        return out


def compute_k_vector(observations: np.ndarray, actions: np.ndarray) -> Dict:
    """Compute full K-vector for a trajectory."""

    obs_mags = np.linalg.norm(observations, axis=1)
    act_mags = np.linalg.norm(actions, axis=1)

    # K_R: Reactivity
    if np.std(obs_mags) > 1e-10 and np.std(act_mags) > 1e-10:
        corr = np.corrcoef(obs_mags, act_mags)[0, 1]
        k_r = 2 * abs(corr) if not np.isnan(corr) else 0.0
    else:
        k_r = 0.0

    # K_A: Agency
    if len(observations) > 1:
        delta_obs = np.diff(obs_mags)
        if np.std(delta_obs) > 1e-10 and np.std(act_mags[:-1]) > 1e-10:
            corr = np.corrcoef(act_mags[:-1], delta_obs)[0, 1]
            k_a = abs(corr) if not np.isnan(corr) else 0.0
        else:
            k_a = 0.0
    else:
        k_a = 0.0

    # K_I: Integration (entropy matching)
    def entropy(data, bins=32):
        if len(data) < 2 or np.std(data) < 1e-10:
            return 0.0
        hist, _ = np.histogram(data, bins=bins, density=True)
        p = hist / (np.sum(hist) + 1e-12)
        p = p[p > 0]
        return -np.sum(p * np.log(p + 1e-12)) if len(p) > 0 else 0.0

    h_o = entropy(obs_mags)
    h_a = entropy(act_mags)
    k_i = 2 * min(h_o, h_a) / (h_o + h_a + 1e-10) if (h_o + h_a) > 0 else 0.0

    # K_P: Prediction accuracy
    if len(observations) > 2:
        pred_errors = []
        for t in range(1, len(observations)):
            pred = observations[t-1]
            actual = observations[t]
            pred_errors.append(np.linalg.norm(actual - pred))

        mean_error = np.mean(pred_errors)
        baseline = np.std(obs_mags) + 1e-10
        k_p = max(0, 1 - mean_error / (2 * baseline))
    else:
        k_p = 0.0

    # K_M: Memory utilization (key metric for this experiment)
    history_len = 5
    if len(actions) > history_len + 5:
        markov_errors = []
        history_errors = []

        for t in range(history_len, len(actions)):
            # Markov: predict action from current obs only
            current_obs = observations[t]
            markov_pred = current_obs[:actions.shape[1]] if observations.shape[1] >= actions.shape[1] else np.zeros(actions.shape[1])

            # History: predict from average of past observations
            hist_obs = observations[t-history_len:t]
            hist_avg = np.mean(hist_obs[:, :actions.shape[1]], axis=0) if hist_obs.shape[1] >= actions.shape[1] else np.zeros(actions.shape[1])

            actual = actions[t]
            markov_errors.append(np.linalg.norm(actual - markov_pred[:len(actual)]))
            history_errors.append(np.linalg.norm(actual - hist_avg[:len(actual)]))

        l_markov = np.mean(markov_errors)
        l_history = np.mean(history_errors)
        k_m = max(0, min(1, (l_markov - l_history) / (l_markov + 1e-10)))
    else:
        k_m = 0.0

    # K_H: Harmonic alignment (simplified)
    k_h = 0.5  # Neutral for this experiment

    return {
        "K_R": float(np.clip(k_r, 0, 2)),
        "K_A": float(np.clip(k_a, 0, 1)),
        "K_I": float(np.clip(k_i, 0, 1)),
        "K_P": float(np.clip(k_p, 0, 1)),
        "K_M": float(np.clip(k_m, 0, 1)),
        "K_H": float(np.clip(k_h, 0, 1)),
    }


def run_agent_episode(agent, env, max_steps: int = 50) -> Dict:
    """Run single episode and compute K-vector."""
    obs = env.reset()

    if hasattr(agent, 'reset'):
        agent.reset()

    observations = [obs.copy()]
    actions = []
    rewards = []

    for _ in range(max_steps):
        action = agent.act(obs)
        actions.append(action.copy())

        obs, reward, done, info = env.step(action)
        observations.append(obs.copy())
        rewards.append(reward)

        if done:
            break

    obs_arr = np.array(observations[:-1])
    act_arr = np.array(actions)

    k_vector = compute_k_vector(obs_arr, act_arr)
    k_vector["total_reward"] = sum(rewards)
    k_vector["agent"] = agent.name

    return k_vector


def run_km_architecture_validation(n_episodes: int = 30, delays: List[int] = [5, 10, 15]):
    """
    Run comprehensive K_M architecture validation.

    Tests hypothesis: K_M discriminates architectures by memory capacity
    AND remains independent from other dimensions.
    """
    print("=" * 70)
    print("📊 K_M ARCHITECTURE VALIDATION")
    print("=" * 70)
    print()
    print("Testing K_M independence across 5 architecture types")
    print(f"Episodes per architecture: {n_episodes}")
    print(f"Delay values tested: {delays}")
    print()

    results = {arch.name: [] for arch in ARCHITECTURES}

    for delay in delays:
        print(f"\n--- Delay = {delay} ---")
        env = DelayedRewardEnvironment(delay=delay)

        for arch in ARCHITECTURES:
            print(f"  Testing {arch.name}...", end=" ")

            # Create agent
            if arch.name == "feedforward":
                agent = FeedforwardAgent(env.obs_dim, env.action_dim)
            elif arch.name == "simple_rnn":
                agent = SimpleRNNAgent(env.obs_dim, env.action_dim)
            elif arch.name == "gru":
                agent = GRUAgent(env.obs_dim, env.action_dim)
            elif arch.name == "lstm":
                agent = LSTMAgent(env.obs_dim, env.action_dim)
            elif arch.name == "transformer":
                agent = TransformerAgent(env.obs_dim, env.action_dim)

            for ep in range(n_episodes):
                result = run_agent_episode(agent, env)
                result["delay"] = delay
                results[arch.name].append(result)

            # Quick stats
            km_values = [r["K_M"] for r in results[arch.name] if r["delay"] == delay]
            print(f"K_M = {np.mean(km_values):.3f} ± {np.std(km_values):.3f}")

    # Analyze results
    print()
    print("-" * 70)
    print("📈 K_M DISCRIMINATION ANALYSIS")
    print("-" * 70)
    print()

    # Overall K_M by architecture
    print("K_M by Architecture (all delays):")
    print(f"{'Architecture':<15} {'K_M Mean':>10} {'K_M Std':>10} {'Has Memory':>12}")
    print("-" * 50)

    arch_km = {}
    for arch in ARCHITECTURES:
        km_values = [r["K_M"] for r in results[arch.name]]
        arch_km[arch.name] = km_values
        print(f"{arch.name:<15} {np.mean(km_values):>10.4f} {np.std(km_values):>10.4f} {str(arch.has_memory):>12}")

    # Statistical tests: memory vs no-memory
    memory_km = []
    no_memory_km = []
    for arch in ARCHITECTURES:
        if arch.has_memory:
            memory_km.extend([r["K_M"] for r in results[arch.name]])
        else:
            no_memory_km.extend([r["K_M"] for r in results[arch.name]])

    t_stat, p_value = ttest_ind(memory_km, no_memory_km)
    ratio = np.mean(memory_km) / (np.mean(no_memory_km) + 1e-10)
    cohens_d = (np.mean(memory_km) - np.mean(no_memory_km)) / np.sqrt(
        (np.var(memory_km) + np.var(no_memory_km)) / 2 + 1e-10
    )

    print()
    print("Memory vs No-Memory Comparison:")
    print(f"  Memory architectures K_M:    {np.mean(memory_km):.4f} ± {np.std(memory_km):.4f}")
    print(f"  No-memory architectures K_M: {np.mean(no_memory_km):.4f} ± {np.std(no_memory_km):.4f}")
    print(f"  Ratio: {ratio:.2f}×")
    print(f"  t-statistic: {t_stat:.3f}")
    print(f"  p-value: {p_value:.6f}")
    print(f"  Cohen's d: {cohens_d:.3f}")

    # K_M independence analysis
    print()
    print("-" * 70)
    print("📈 K_M INDEPENDENCE FROM OTHER DIMENSIONS")
    print("-" * 70)
    print()

    # Collect all K-vectors
    all_results = []
    for arch_results in results.values():
        all_results.extend(arch_results)

    dimensions = ["K_R", "K_A", "K_I", "K_P", "K_M", "K_H"]
    km_correlations = {}

    km_values = [r["K_M"] for r in all_results]

    print("K_M correlations with other dimensions:")
    for dim in dimensions:
        if dim == "K_M":
            continue
        dim_values = [r[dim] for r in all_results]

        if np.std(km_values) > 1e-10 and np.std(dim_values) > 1e-10:
            r, p = pearsonr(km_values, dim_values)
            km_correlations[dim] = {"r": r, "p": p}

            status = "✅ Independent" if abs(r) < 0.3 else "⚠️ Correlated"
            print(f"  K_M ↔ {dim}: r = {r:+.3f}, p = {p:.4f} {status}")
        else:
            print(f"  K_M ↔ {dim}: insufficient variance")

    # Conclusions
    print()
    print("-" * 70)
    print("📋 CONCLUSIONS")
    print("-" * 70)

    if p_value < 0.05 and ratio > 1.5:
        print("✅ H1 SUPPORTED: K_M discriminates memory architectures")
        print(f"   Memory architectures have {ratio:.2f}× higher K_M (p < {p_value:.4f})")
    else:
        print("⚠️ H1 WEAK: K_M discrimination needs improvement")

    independent_count = sum(1 for dim, stats in km_correlations.items()
                           if abs(stats["r"]) < 0.3)
    total_dims = len(km_correlations)

    if independent_count == total_dims:
        print(f"✅ H2 SUPPORTED: K_M is independent from ALL other dimensions")
    elif independent_count >= total_dims - 1:
        print(f"~ H2 PARTIALLY SUPPORTED: K_M independent from {independent_count}/{total_dims} dimensions")
    else:
        print(f"⚠️ H2 NOT SUPPORTED: K_M correlated with {total_dims - independent_count} dimensions")

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "config": {
            "n_episodes": n_episodes,
            "delays": delays,
            "architectures": [a.name for a in ARCHITECTURES],
        },
        "km_by_architecture": {
            name: {
                "mean": float(np.mean(values)),
                "std": float(np.std(values)),
                "n": len(values)
            }
            for name, values in arch_km.items()
        },
        "memory_vs_nomemory": {
            "memory_mean": float(np.mean(memory_km)),
            "nomemory_mean": float(np.mean(no_memory_km)),
            "ratio": float(ratio),
            "t_stat": float(t_stat),
            "p_value": float(p_value),
            "cohens_d": float(cohens_d),
        },
        "km_independence": {
            dim: {"r": float(stats["r"]), "p": float(stats["p"])}
            for dim, stats in km_correlations.items()
        },
        "hypotheses": {
            "h1_km_discriminates": bool(p_value < 0.05 and ratio > 1.5),
            "h2_km_independent": bool(independent_count == total_dims),
        }
    }

    log_dir = Path("logs/km_architecture")
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"km_architecture_validation_{timestamp}.json"

    with open(log_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n💾 Results saved → {log_file}")

    return output


if __name__ == "__main__":
    run_km_architecture_validation(n_episodes=30, delays=[5, 10, 15])
