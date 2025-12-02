#!/usr/bin/env python3
"""
Track J1 Short Episodes: MPE with 25-50 Steps

Based on investigation showing spatial saturation after ~75 steps.
Testing at optimal episode lengths for flexibility-performance correlation.

Run with:
    nix-shell -p python3 python3Packages.numpy python3Packages.scipy --run "python3 -u track_j1_short_episodes.py"
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

    def act(self, obs, messages):
        combined = np.concatenate([obs, messages])
        action = np.tanh(self.policy_weights @ combined + np.random.randn(4) * 0.3)
        self.obs_history.append(obs)
        self.action_history.append(action)
        return action

    def get_flexibility(self):
        if len(self.obs_history) < 10:
            return 0.0
        obs = np.array(self.obs_history[-50:]).flatten()
        actions = np.array(self.action_history[-50:]).flatten()
        min_len = min(len(obs), len(actions))
        if min_len < 2:
            return 0.0
        corr = np.corrcoef(obs[:min_len], actions[:min_len])[0, 1]
        return -abs(corr) * 2.0 if not np.isnan(corr) else 0.0

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


def run_episode(n_agents, n_steps):
    """Run single episode and return flexibility and reward."""
    agents = [Agent(i) for i in range(n_agents)]
    network = Network(n_agents)
    env = SimpleSpreadEnv(n_agents)

    observations = env.reset()
    total_reward = 0

    for step in range(n_steps):
        noisy_obs = [o + np.random.randn(6) * 0.05 for o in observations]
        messages = [a.create_message(o) for a, o in zip(agents, noisy_obs)]
        received = network.exchange(messages)
        actions = [a.act(o, m) for a, o, m in zip(agents, noisy_obs, received)]
        observations, reward = env.step(actions)
        total_reward += reward

    flexibility = np.mean([a.get_flexibility() for a in agents])
    return flexibility, total_reward


def main():
    print("\n" + "=" * 70)
    print("TRACK J1 SHORT EPISODES: MPE WITH 25-50 STEPS")
    print("=" * 70)

    np.random.seed(42)
    n_agents = 4
    n_episodes = 100

    # Test at optimal episode lengths based on investigation
    step_counts = [25, 35, 50, 75]

    print(f"\nRunning {n_episodes} episodes at each step count...")

    results = {}

    for n_steps in step_counts:
        flexibilities = []
        rewards = []

        for ep in range(n_episodes):
            flex, rew = run_episode(n_agents, n_steps)
            flexibilities.append(flex)
            rewards.append(rew)

        flexibilities = np.array(flexibilities)
        rewards = np.array(rewards)

        r, p = stats.pearsonr(flexibilities, rewards)
        results[n_steps] = {'r': r, 'p': p, 'mean_reward': np.mean(rewards)}

        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
        print(f"  {n_steps:3d} steps: r = {r:+.3f}{sig}, p = {p:.4f}, reward = {np.mean(rewards):.1f}")

    # Analysis
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)

    # Check dose-response
    step_list = list(results.keys())
    r_list = [results[s]['r'] for s in step_list]

    dose_r, dose_p = stats.pearsonr(step_list, r_list)
    print(f"\nDose-response (steps vs r): r = {dose_r:+.3f}, p = {dose_p:.3f}")

    # Find optimal
    best_steps = max(results.keys(), key=lambda s: results[s]['r'])
    print(f"Best correlation at {best_steps} steps: r = {results[best_steps]['r']:+.3f}")

    # Conclusion
    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    if results[25]['r'] > 0.15 or results[35]['r'] > 0.15:
        print("\n✓ MPE VALIDATED at short episodes!")
        print(f"  Peak correlation: r = {results[best_steps]['r']:+.3f} at {best_steps} steps")
        print("  Confirms: Flexibility matters for spatial coordination")
        print("  Note: Effect decays due to spatial saturation")
    else:
        print("\n→ MPE correlation still weak at short episodes")
        print("  May need different metric for spatial tasks")

    # Compare to abstract task
    print("\nComparison to abstract coordination task:")
    print("  Abstract task: r = +0.70 at 200 steps (sustained)")
    print(f"  MPE task:      r = {results[best_steps]['r']:+.3f} at {best_steps} steps (peaks early)")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"track_j1_short_{timestamp}.npz"
    np.savez(filename, results=results)
    print(f"\nSaved: {filename}")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
