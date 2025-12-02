#!/usr/bin/env python3
"""
K_M Memory-Required Task Investigation

The previous K_M architecture validation showed weak discrimination (ratio=0.96×).
This experiment tests tasks that REQUIRE memory to succeed:

1. T-Maze: Must remember which arm was cued
2. Sequence Matching: Must remember and reproduce a sequence
3. Delayed XOR: XOR of observations separated by N steps

Hypothesis: In memory-REQUIRED tasks, recurrent agents should show
significantly higher K_M than feedforward agents.
"""

import numpy as np
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
from scipy.stats import pearsonr, ttest_ind


@dataclass
class TMazeConfig:
    """T-Maze environment requiring memory of cue."""
    corridor_length: int = 5
    max_steps: int = 20
    cue_duration: int = 1  # Steps cue is visible


class TMazeEnvironment:
    """
    T-Maze: Agent starts in corridor, sees cue (left/right),
    must navigate to correct arm at the junction.

    Memory required: Cue visible only at start, must be remembered.
    """

    def __init__(self, config: TMazeConfig = None):
        self.config = config or TMazeConfig()
        self.reset()

    def reset(self) -> np.ndarray:
        self.position = 0  # Start of corridor
        self.correct_arm = np.random.choice([-1, 1])  # -1=left, 1=right
        self.step_count = 0
        self.done = False
        self.at_junction = False
        self.chose_arm = None
        self.observation_history = []
        self.action_history = []
        return self._get_observation()

    def _get_observation(self) -> np.ndarray:
        # Cue only visible at start
        if self.step_count < self.config.cue_duration:
            cue = float(self.correct_arm)
        else:
            cue = 0.0

        # Position encoding
        pos_norm = self.position / self.config.corridor_length
        at_junction = 1.0 if self.position >= self.config.corridor_length else 0.0

        obs = np.array([cue, pos_norm, at_junction,
                       float(self.step_count) / self.config.max_steps],
                      dtype=np.float32)
        self.observation_history.append(obs.copy())
        return obs

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, dict]:
        if self.done:
            return self._get_observation(), 0.0, True, {}

        # Action: 0=forward, <0=left, >0=right
        action_val = float(action[0]) if hasattr(action, '__len__') else float(action)
        self.action_history.append(np.array([action_val]))

        reward = -0.01  # Small step penalty

        if not self.at_junction:
            # In corridor - move forward
            if action_val > -0.3 and action_val < 0.3:  # Forward
                self.position += 1

            if self.position >= self.config.corridor_length:
                self.at_junction = True
        else:
            # At junction - choose arm
            if action_val < -0.3:  # Left
                self.chose_arm = -1
            elif action_val > 0.3:  # Right
                self.chose_arm = 1

            if self.chose_arm is not None:
                if self.chose_arm == self.correct_arm:
                    reward = 1.0  # Correct!
                else:
                    reward = -1.0  # Wrong arm
                self.done = True

        self.step_count += 1
        if self.step_count >= self.config.max_steps:
            self.done = True
            reward = -0.5  # Timeout penalty

        info = {
            "correct_arm": self.correct_arm,
            "chose_arm": self.chose_arm,
            "success": self.chose_arm == self.correct_arm if self.chose_arm else False,
        }

        return self._get_observation(), reward, self.done, info


@dataclass
class SequenceMatchConfig:
    """Sequence matching environment."""
    sequence_length: int = 4
    vocab_size: int = 3
    max_steps: int = 20


class SequenceMatchEnvironment:
    """
    Sequence Matching: See sequence, then reproduce it.

    Memory required: Must remember entire sequence during show phase.
    """

    def __init__(self, config: SequenceMatchConfig = None):
        self.config = config or SequenceMatchConfig()
        self.reset()

    def reset(self) -> np.ndarray:
        self.sequence = np.random.randint(0, self.config.vocab_size,
                                          size=self.config.sequence_length)
        self.phase = "show"  # "show" or "reproduce"
        self.show_idx = 0
        self.reproduce_idx = 0
        self.step_count = 0
        self.done = False
        self.correct_count = 0
        self.observation_history = []
        self.action_history = []
        return self._get_observation()

    def _get_observation(self) -> np.ndarray:
        if self.phase == "show":
            if self.show_idx < self.config.sequence_length:
                current = self.sequence[self.show_idx] / self.config.vocab_size
            else:
                current = -1.0  # End of show phase marker
        else:
            current = -0.5  # Reproduce phase marker

        phase_indicator = 1.0 if self.phase == "show" else 0.0
        progress = self.show_idx / self.config.sequence_length if self.phase == "show" \
                   else self.reproduce_idx / self.config.sequence_length

        obs = np.array([current, phase_indicator, progress,
                       float(self.step_count) / self.config.max_steps],
                      dtype=np.float32)
        self.observation_history.append(obs.copy())
        return obs

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, dict]:
        if self.done:
            return self._get_observation(), 0.0, True, {}

        action_val = float(action[0]) if hasattr(action, '__len__') else float(action)
        self.action_history.append(np.array([action_val]))

        reward = 0.0

        if self.phase == "show":
            self.show_idx += 1
            if self.show_idx >= self.config.sequence_length:
                self.phase = "reproduce"
        else:
            # Reproduce phase - check if action matches expected
            expected = self.sequence[self.reproduce_idx]
            predicted = int(np.clip(action_val * self.config.vocab_size,
                                   0, self.config.vocab_size - 1))

            if predicted == expected:
                reward = 0.25  # Partial reward per correct
                self.correct_count += 1
            else:
                reward = -0.1

            self.reproduce_idx += 1
            if self.reproduce_idx >= self.config.sequence_length:
                self.done = True
                if self.correct_count == self.config.sequence_length:
                    reward += 1.0  # Bonus for perfect

        self.step_count += 1
        if self.step_count >= self.config.max_steps:
            self.done = True

        info = {
            "correct_count": self.correct_count,
            "sequence_length": self.config.sequence_length,
            "accuracy": self.correct_count / self.config.sequence_length,
        }

        return self._get_observation(), reward, self.done, info


@dataclass
class DelayedXORConfig:
    """Delayed XOR environment."""
    delay: int = 10
    max_steps: int = 50


class DelayedXOREnvironment:
    """
    Delayed XOR: Output XOR of current input and input from N steps ago.

    Memory required: Must remember observation from N steps ago.
    """

    def __init__(self, config: DelayedXORConfig = None):
        self.config = config or DelayedXORConfig()
        self.reset()

    def reset(self) -> np.ndarray:
        self.inputs = []
        self.step_count = 0
        self.done = False
        self.correct_count = 0
        self.total_scored = 0
        self.observation_history = []
        self.action_history = []
        return self._get_observation()

    def _get_observation(self) -> np.ndarray:
        current_input = np.random.choice([0.0, 1.0])
        self.inputs.append(current_input)

        obs = np.array([current_input,
                       float(self.step_count) / self.config.max_steps,
                       float(len(self.inputs) >= self.config.delay),
                       float(self.config.delay) / 20.0],
                      dtype=np.float32)
        self.observation_history.append(obs.copy())
        return obs

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, dict]:
        if self.done:
            return self._get_observation(), 0.0, True, {}

        action_val = float(action[0]) if hasattr(action, '__len__') else float(action)
        self.action_history.append(np.array([action_val]))

        reward = 0.0

        # Only score after delay period
        if len(self.inputs) > self.config.delay:
            current = self.inputs[-1]
            delayed = self.inputs[-self.config.delay - 1]
            expected_xor = int(current) ^ int(delayed)

            predicted = 1 if action_val > 0.5 else 0

            if predicted == expected_xor:
                reward = 0.1
                self.correct_count += 1
            else:
                reward = -0.05

            self.total_scored += 1

        self.step_count += 1
        if self.step_count >= self.config.max_steps:
            self.done = True

        accuracy = self.correct_count / self.total_scored if self.total_scored > 0 else 0.0

        info = {
            "correct_count": self.correct_count,
            "total_scored": self.total_scored,
            "accuracy": accuracy,
        }

        return self._get_observation(), reward, self.done, info


def compute_km(observation_history: List[np.ndarray],
               action_history: List[np.ndarray]) -> float:
    """Compute K_M (temporal memory utilization)."""
    if len(observation_history) < 20 or len(action_history) < 20:
        return 0.0

    obs = np.array(observation_history)
    acts = np.array(action_history).flatten()

    # Markov loss: predict action from current observation only
    try:
        from sklearn.linear_model import LinearRegression
        HAS_SKLEARN = True
    except ImportError:
        HAS_SKLEARN = False

    if not HAS_SKLEARN:
        # Simple linear regression
        X_markov = obs[:-1]
        y = acts[1:len(X_markov)+1] if len(acts) > len(X_markov) else acts[:len(X_markov)]

        if len(y) != len(X_markov):
            min_len = min(len(y), len(X_markov))
            X_markov = X_markov[:min_len]
            y = y[:min_len]

        # Markov prediction (current obs only)
        X_markov_bias = np.column_stack([np.ones(len(X_markov)), X_markov])
        try:
            coeffs_markov = np.linalg.lstsq(X_markov_bias, y, rcond=None)[0]
            pred_markov = X_markov_bias @ coeffs_markov
            loss_markov = np.mean((y - pred_markov) ** 2)
        except:
            loss_markov = np.var(y)

        # History prediction (current + previous obs)
        history_len = 5
        if len(obs) > history_len:
            X_history = []
            for i in range(history_len, len(obs) - 1):
                history_features = obs[i-history_len:i+1].flatten()
                X_history.append(history_features)
            X_history = np.array(X_history)
            y_history = y[history_len:len(X_history)+history_len]

            if len(y_history) != len(X_history):
                min_len = min(len(y_history), len(X_history))
                X_history = X_history[:min_len]
                y_history = y_history[:min_len]

            if len(X_history) > 0:
                X_history_bias = np.column_stack([np.ones(len(X_history)), X_history])
                try:
                    coeffs_history = np.linalg.lstsq(X_history_bias, y_history, rcond=None)[0]
                    pred_history = X_history_bias @ coeffs_history
                    loss_history = np.mean((y_history - pred_history) ** 2)
                except:
                    loss_history = loss_markov
            else:
                loss_history = loss_markov
        else:
            loss_history = loss_markov
    else:
        # Use sklearn
        X_markov = obs[:-1]
        y = acts[1:len(X_markov)+1] if len(acts) > len(X_markov) else acts[:len(X_markov)]

        if len(y) != len(X_markov):
            min_len = min(len(y), len(X_markov))
            X_markov = X_markov[:min_len]
            y = y[:min_len]

        reg_markov = LinearRegression()
        reg_markov.fit(X_markov, y)
        loss_markov = np.mean((y - reg_markov.predict(X_markov)) ** 2)

        history_len = 5
        if len(obs) > history_len:
            X_history = []
            for i in range(history_len, len(obs) - 1):
                history_features = obs[i-history_len:i+1].flatten()
                X_history.append(history_features)
            X_history = np.array(X_history)
            y_history = y[history_len:len(X_history)+history_len]

            if len(y_history) != len(X_history):
                min_len = min(len(y_history), len(X_history))
                X_history = X_history[:min_len]
                y_history = y_history[:min_len]

            if len(X_history) > 0:
                reg_history = LinearRegression()
                reg_history.fit(X_history, y_history)
                loss_history = np.mean((y_history - reg_history.predict(X_history)) ** 2)
            else:
                loss_history = loss_markov
        else:
            loss_history = loss_markov

    km = (loss_markov - loss_history) / (loss_markov + 1e-10)
    return float(np.clip(km, 0, 1))


# Agent implementations
class FeedforwardAgent:
    """Memoryless feedforward agent."""
    name = "feedforward"
    has_memory = False

    def __init__(self, obs_dim: int, hidden_dim: int = 16):
        self.W1 = np.random.randn(obs_dim, hidden_dim) * 0.1
        self.W2 = np.random.randn(hidden_dim, 1) * 0.1

    def act(self, obs: np.ndarray) -> np.ndarray:
        h = np.tanh(obs @ self.W1)
        out = np.tanh(h @ self.W2)
        return out.flatten()

    def reset(self):
        pass


class LSTMAgent:
    """LSTM agent with memory."""
    name = "lstm"
    has_memory = True

    def __init__(self, obs_dim: int, hidden_dim: int = 16):
        self.hidden_dim = hidden_dim
        self.obs_dim = obs_dim

        # LSTM weights (simplified)
        self.Wf = np.random.randn(obs_dim + hidden_dim, hidden_dim) * 0.1
        self.Wi = np.random.randn(obs_dim + hidden_dim, hidden_dim) * 0.1
        self.Wc = np.random.randn(obs_dim + hidden_dim, hidden_dim) * 0.1
        self.Wo = np.random.randn(obs_dim + hidden_dim, hidden_dim) * 0.1
        self.Wy = np.random.randn(hidden_dim, 1) * 0.1

        self.reset()

    def reset(self):
        self.h = np.zeros(self.hidden_dim)
        self.c = np.zeros(self.hidden_dim)

    def act(self, obs: np.ndarray) -> np.ndarray:
        combined = np.concatenate([obs.flatten(), self.h])

        f = self._sigmoid(combined @ self.Wf)
        i = self._sigmoid(combined @ self.Wi)
        c_tilde = np.tanh(combined @ self.Wc)
        self.c = f * self.c + i * c_tilde
        o = self._sigmoid(combined @ self.Wo)
        self.h = o * np.tanh(self.c)

        out = np.tanh(self.h @ self.Wy)
        return out.flatten()

    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))


class GRUAgent:
    """GRU agent with memory."""
    name = "gru"
    has_memory = True

    def __init__(self, obs_dim: int, hidden_dim: int = 16):
        self.hidden_dim = hidden_dim

        self.Wz = np.random.randn(obs_dim + hidden_dim, hidden_dim) * 0.1
        self.Wr = np.random.randn(obs_dim + hidden_dim, hidden_dim) * 0.1
        self.Wh = np.random.randn(obs_dim + hidden_dim, hidden_dim) * 0.1
        self.Wy = np.random.randn(hidden_dim, 1) * 0.1

        self.reset()

    def reset(self):
        self.h = np.zeros(self.hidden_dim)

    def act(self, obs: np.ndarray) -> np.ndarray:
        combined = np.concatenate([obs.flatten(), self.h])

        z = self._sigmoid(combined @ self.Wz)
        r = self._sigmoid(combined @ self.Wr)

        combined_r = np.concatenate([obs.flatten(), r * self.h])
        h_tilde = np.tanh(combined_r @ self.Wh)

        self.h = (1 - z) * self.h + z * h_tilde

        out = np.tanh(self.h @ self.Wy)
        return out.flatten()

    def _sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))


def run_episode(env, agent) -> Dict:
    """Run single episode."""
    obs = env.reset()
    agent.reset()
    total_reward = 0
    done = False

    while not done:
        action = agent.act(obs)
        obs, reward, done, info = env.step(action)
        total_reward += reward

    km = compute_km(env.observation_history, env.action_history)

    return {
        "agent": agent.name,
        "has_memory": agent.has_memory,
        "total_reward": total_reward,
        "K_M": km,
        "info": info,
    }


def run_km_memory_required_investigation(n_episodes: int = 30):
    """Run K_M investigation on memory-required tasks."""
    print("=" * 70)
    print("K_M MEMORY-REQUIRED TASK INVESTIGATION")
    print("=" * 70)
    print()
    print("Testing whether K_M discriminates memory architectures in")
    print("tasks that REQUIRE memory to succeed.")
    print()

    environments = [
        ("T-Maze", TMazeEnvironment, TMazeConfig()),
        ("Sequence Match", SequenceMatchEnvironment, SequenceMatchConfig(sequence_length=4)),
        ("Delayed XOR (d=5)", DelayedXOREnvironment, DelayedXORConfig(delay=5)),
        ("Delayed XOR (d=10)", DelayedXOREnvironment, DelayedXORConfig(delay=10)),
        ("Delayed XOR (d=20)", DelayedXOREnvironment, DelayedXORConfig(delay=20)),
    ]

    agents_configs = [
        (FeedforwardAgent, "feedforward"),
        (LSTMAgent, "lstm"),
        (GRUAgent, "gru"),
    ]

    all_results = []
    env_summaries = {}

    for env_name, EnvClass, env_config in environments:
        print(f"\n--- {env_name} ---")
        env_results = {name: [] for _, name in agents_configs}

        for AgentClass, agent_name in agents_configs:
            print(f"  Testing {agent_name}...", end=" ")

            for _ in range(n_episodes):
                env = EnvClass(env_config)
                obs_dim = 4  # All environments have 4-dim observations
                agent = AgentClass(obs_dim)

                result = run_episode(env, agent)
                result["environment"] = env_name
                env_results[agent_name].append(result)
                all_results.append(result)

            km_vals = [r["K_M"] for r in env_results[agent_name]]
            acc_vals = [r["info"].get("accuracy", r["info"].get("success", 0))
                       for r in env_results[agent_name]]
            print(f"K_M = {np.mean(km_vals):.3f} ± {np.std(km_vals):.3f}, "
                  f"Acc = {np.mean(acc_vals):.3f}")

        # Environment summary
        memory_km = [r["K_M"] for r in all_results
                    if r["environment"] == env_name and r["has_memory"]]
        nomemory_km = [r["K_M"] for r in all_results
                      if r["environment"] == env_name and not r["has_memory"]]

        if memory_km and nomemory_km:
            ratio = np.mean(memory_km) / (np.mean(nomemory_km) + 1e-10)
            t_stat, p_value = ttest_ind(memory_km, nomemory_km)
        else:
            ratio = 0
            t_stat, p_value = 0, 1

        env_summaries[env_name] = {
            "memory_km_mean": float(np.mean(memory_km)) if memory_km else 0,
            "nomemory_km_mean": float(np.mean(nomemory_km)) if nomemory_km else 0,
            "ratio": float(ratio),
            "t_stat": float(t_stat),
            "p_value": float(p_value),
        }

    # Overall summary
    print()
    print("-" * 70)
    print("K_M DISCRIMINATION SUMMARY")
    print("-" * 70)
    print()
    print(f"{'Environment':<20} {'Memory K_M':>12} {'NoMem K_M':>12} {'Ratio':>8} {'p-value':>10}")
    print("-" * 70)

    for env_name, summary in env_summaries.items():
        sig = "***" if summary["p_value"] < 0.001 else "**" if summary["p_value"] < 0.01 else "*" if summary["p_value"] < 0.05 else ""
        print(f"{env_name:<20} {summary['memory_km_mean']:>12.3f} "
              f"{summary['nomemory_km_mean']:>12.3f} {summary['ratio']:>8.2f}× "
              f"{summary['p_value']:>10.4f}{sig}")

    # Aggregate analysis
    all_memory_km = [r["K_M"] for r in all_results if r["has_memory"]]
    all_nomemory_km = [r["K_M"] for r in all_results if not r["has_memory"]]

    overall_ratio = np.mean(all_memory_km) / (np.mean(all_nomemory_km) + 1e-10)
    overall_t, overall_p = ttest_ind(all_memory_km, all_nomemory_km)

    pooled_var = (np.var(all_memory_km) + np.var(all_nomemory_km)) / 2
    cohens_d = (np.mean(all_memory_km) - np.mean(all_nomemory_km)) / np.sqrt(pooled_var) if pooled_var > 1e-10 else 0

    print()
    print("-" * 70)
    print("OVERALL RESULTS")
    print("-" * 70)
    print(f"Memory architectures K_M:    {np.mean(all_memory_km):.3f} ± {np.std(all_memory_km):.3f}")
    print(f"No-memory architectures K_M: {np.mean(all_nomemory_km):.3f} ± {np.std(all_nomemory_km):.3f}")
    print(f"Overall ratio: {overall_ratio:.2f}×")
    print(f"t-statistic: {overall_t:.3f}")
    print(f"p-value: {overall_p:.6f}")
    print(f"Cohen's d: {cohens_d:.3f}")
    print()

    if overall_ratio > 1.5 and overall_p < 0.05:
        print("CONCLUSION: K_M DISCRIMINATES memory architectures in memory-required tasks")
    elif overall_ratio > 1.2 and overall_p < 0.1:
        print("CONCLUSION: WEAK discrimination - ratio > 1.2 but effect small")
    else:
        print("CONCLUSION: K_M still fails to discriminate - deeper investigation needed")

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "n_episodes": n_episodes,
        "environment_summaries": env_summaries,
        "overall": {
            "memory_km_mean": float(np.mean(all_memory_km)),
            "nomemory_km_mean": float(np.mean(all_nomemory_km)),
            "ratio": float(overall_ratio),
            "t_stat": float(overall_t),
            "p_value": float(overall_p),
            "cohens_d": float(cohens_d),
        },
        "discriminates": bool(overall_ratio > 1.5 and overall_p < 0.05),
    }

    log_dir = Path("logs/km_memory_required")
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"km_memory_required_{timestamp}.json"

    with open(log_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved: {log_file}")

    return output


if __name__ == "__main__":
    run_km_memory_required_investigation(n_episodes=30)
