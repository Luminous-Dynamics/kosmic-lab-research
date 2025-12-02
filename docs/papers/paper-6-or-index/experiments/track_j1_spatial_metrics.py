#!/usr/bin/env python3
"""
Track J1 Spatial Metrics: Alternative Flexibility Measures for MPE

The obs-action correlation metric doesn't transfer to spatial tasks.
Testing alternative metrics more suited to position-based coordination.

Metrics tested:
1. Trajectory variance - How much agents explore the space
2. Velocity diversity - How varied are movement patterns
3. Message entropy - How much information in communication

Run with:
    nix-shell -p python3 python3Packages.numpy python3Packages.scipy --run "python3 -u track_j1_spatial_metrics.py"
"""

import numpy as np
from scipy import stats
from datetime import datetime


class Agent:
    def __init__(self, agent_id):
        self.id = agent_id
        self.policy_weights = np.random.randn(4, 10) * 0.1
        self.obs_history = []
        self.action_history = []
        self.position_history = []
        self.message_history = []

    def act(self, obs, messages):
        combined = np.concatenate([obs, messages])
        action = np.tanh(self.policy_weights @ combined + np.random.randn(4) * 0.3)
        self.obs_history.append(obs)
        self.action_history.append(action)
        return action

    def record_position(self, pos):
        self.position_history.append(pos.copy())

    def record_message(self, msg):
        self.message_history.append(msg.copy())

    def get_original_flexibility(self):
        """Original obs-action correlation metric."""
        if len(self.obs_history) < 10:
            return 0.0
        obs = np.array(self.obs_history).flatten()
        actions = np.array(self.action_history).flatten()
        min_len = min(len(obs), len(actions))
        if min_len < 2:
            return 0.0
        corr = np.corrcoef(obs[:min_len], actions[:min_len])[0, 1]
        return -abs(corr) * 2.0 if not np.isnan(corr) else 0.0

    def get_trajectory_variance(self):
        """How much the agent explores the space."""
        if len(self.position_history) < 10:
            return 0.0
        positions = np.array(self.position_history)
        # Total variance in position
        return np.var(positions)

    def get_velocity_diversity(self):
        """How varied the movement patterns are."""
        if len(self.action_history) < 10:
            return 0.0
        actions = np.array(self.action_history)
        # Variance in velocity commands
        return np.var(actions[:, :2])  # Only x,y velocity

    def get_message_entropy(self):
        """Information content in messages."""
        if len(self.message_history) < 10:
            return 0.0
        messages = np.array(self.message_history)
        # Use variance as proxy for entropy
        return np.var(messages)

    def create_message(self, obs):
        return obs[:4]


class Network:
    def __init__(self, n_agents):
        self.n_agents = n_agents

    def exchange(self, messages):
        avg = np.mean(messages, axis=0)
        return [avg for _ in range(self.n_agents)]


class SimpleSpreadEnv:
    def __init__(self, n_agents=4):
        self.n_agents = n_agents
        self.agents_pos = np.zeros((n_agents, 2))
        self.agents_vel = np.zeros((n_agents, 2))
        self.landmarks = np.zeros((n_agents, 2))

    def reset(self):
        self.agents_pos = np.random.randn(self.n_agents, 2) * 0.5
        self.agents_vel = np.zeros((self.n_agents, 2))
        self.landmarks = np.random.randn(self.n_agents, 2)
        return self._get_obs()

    def _get_obs(self):
        obs = []
        for i in range(self.n_agents):
            own = np.concatenate([self.agents_pos[i], self.agents_vel[i]])
            dists = np.linalg.norm(self.landmarks - self.agents_pos[i], axis=1)
            nearest = np.argmin(dists)
            rel_landmark = self.landmarks[nearest] - self.agents_pos[i]
            obs.append(np.concatenate([own, rel_landmark]))
        return obs

    def step(self, actions):
        for i in range(self.n_agents):
            self.agents_vel[i] = actions[i][:2] * 0.5
            self.agents_pos[i] += self.agents_vel[i] * 0.1

        reward = 0
        for landmark in self.landmarks:
            dists = np.linalg.norm(self.agents_pos - landmark, axis=1)
            reward -= np.min(dists)

        for i in range(self.n_agents):
            for j in range(i + 1, self.n_agents):
                dist = np.linalg.norm(self.agents_pos[i] - self.agents_pos[j])
                if dist < 0.2:
                    reward -= 0.5

        return self._get_obs(), reward

    def get_positions(self):
        return self.agents_pos.copy()


def run_episode(n_agents, n_steps):
    """Run single episode and return all metrics and reward."""
    agents = [Agent(i) for i in range(n_agents)]
    network = Network(n_agents)
    env = SimpleSpreadEnv(n_agents)

    observations = env.reset()
    total_reward = 0

    for step in range(n_steps):
        # Record positions
        positions = env.get_positions()
        for i, a in enumerate(agents):
            a.record_position(positions[i])

        noisy_obs = [o + np.random.randn(6) * 0.05 for o in observations]
        messages = [a.create_message(o) for a, o in zip(agents, noisy_obs)]

        # Record messages
        for a, m in zip(agents, messages):
            a.record_message(m)

        received = network.exchange(messages)
        actions = [a.act(o, m) for a, o, m in zip(agents, noisy_obs, received)]
        observations, reward = env.step(actions)
        total_reward += reward

    # Compute all metrics
    metrics = {
        'original': np.mean([a.get_original_flexibility() for a in agents]),
        'trajectory': np.mean([a.get_trajectory_variance() for a in agents]),
        'velocity': np.mean([a.get_velocity_diversity() for a in agents]),
        'message': np.mean([a.get_message_entropy() for a in agents]),
    }

    return metrics, total_reward


def main():
    print("\n" + "=" * 70)
    print("TRACK J1 SPATIAL METRICS: ALTERNATIVE FLEXIBILITY MEASURES")
    print("=" * 70)

    np.random.seed(42)
    n_agents = 4
    n_episodes = 100
    n_steps = 50  # Optimal based on investigation

    print(f"\nRunning {n_episodes} episodes with {n_steps} steps each...")

    all_metrics = {
        'original': [],
        'trajectory': [],
        'velocity': [],
        'message': [],
    }
    all_rewards = []

    for ep in range(n_episodes):
        metrics, reward = run_episode(n_agents, n_steps)
        for key in all_metrics:
            all_metrics[key].append(metrics[key])
        all_rewards.append(reward)

    all_rewards = np.array(all_rewards)

    # Compute correlations
    print("\nMetric-Performance Correlations:")
    print("-" * 50)

    results = {}
    for name, values in all_metrics.items():
        values = np.array(values)
        r, p = stats.pearsonr(values, all_rewards)
        results[name] = {'r': r, 'p': p}
        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
        print(f"  {name:12s}: r = {r:+.3f}{sig}, p = {p:.4f}")

    # Analysis
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)

    best_metric = max(results.keys(), key=lambda k: abs(results[k]['r']))
    best_r = results[best_metric]['r']
    best_p = results[best_metric]['p']

    print(f"\nBest metric: {best_metric}")
    print(f"  r = {best_r:+.3f}, p = {best_p:.4f}")

    # Conclusion
    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    if best_p < 0.05:
        print(f"\n✓ {best_metric.upper()} works for spatial tasks!")
        print(f"  Correlation: r = {best_r:+.3f} (p = {best_p:.4f})")
        if best_r > 0:
            print("  More variance → better performance")
        else:
            print("  Less variance → better performance")
    else:
        print("\n→ No metric achieved significance")
        print("  Spatial coordination may use different mechanisms")

    # Compare to abstract task
    print("\nComparison to abstract coordination:")
    print("  Abstract: obs-action correlation r = +0.70***")
    print(f"  Spatial:  {best_metric} r = {best_r:+.3f}")

    if abs(best_r) > 0.3 and best_p < 0.05:
        print("\n  ✓ Found valid spatial flexibility metric!")
    else:
        print("\n  → Spatial tasks may require task-specific metrics")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"track_j1_spatial_{timestamp}.npz"
    np.savez(filename, results=results, all_metrics=all_metrics, rewards=all_rewards)
    print(f"\nSaved: {filename}")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
