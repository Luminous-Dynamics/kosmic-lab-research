#!/usr/bin/env python3
"""
Investigate MPE Inversion Phenomenon

Why does the flexibility-reward correlation DECREASE with more steps in MPE?
Hypotheses:
1. Random policies exhaust useful flexibility quickly
2. Spatial tasks have faster feedback (immediate position feedback)
3. Different metric behavior in spatial vs abstract domains

Run with:
    nix-shell -p python3 python3Packages.numpy python3Packages.scipy --run "python3 -u investigate_mpe_inversion.py"
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

    def get_flexibility_at_step(self, step):
        """Flexibility up to given step."""
        if step < 10:
            return 0.0
        obs = np.array(self.obs_history[:step]).flatten()
        actions = np.array(self.action_history[:step]).flatten()
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


def main():
    print("\n" + "=" * 70)
    print("INVESTIGATE MPE INVERSION PHENOMENON")
    print("=" * 70)

    np.random.seed(42)
    n_episodes = 100
    n_agents = 4

    # Test 1: Correlation at different checkpoints within same episode
    print("\n" + "-" * 70)
    print("TEST 1: FLEXIBILITY-REWARD AT CHECKPOINTS")
    print("-" * 70)

    checkpoints = [25, 50, 75, 100, 150, 200, 300]
    checkpoint_results = {t: [] for t in checkpoints}

    print("\nRunning episodes with checkpoint measurements...")

    for ep in range(n_episodes):
        agents = [Agent(i) for i in range(n_agents)]
        network = Network(n_agents)
        env = SimpleSpreadEnv(n_agents)

        observations = env.reset()
        cumulative = 0

        for step in range(max(checkpoints)):
            noisy_obs = [o + np.random.randn(6) * 0.05 for o in observations]
            messages = [a.create_message(o) for a, o in zip(agents, noisy_obs)]
            received = network.exchange(messages)
            actions = [a.act(o, m) for a, o, m in zip(agents, noisy_obs, received)]
            observations, reward = env.step(actions)
            cumulative += reward

            if (step + 1) in checkpoints:
                flex = np.mean([a.get_flexibility_at_step(step + 1) for a in agents])
                checkpoint_results[step + 1].append((flex, cumulative))

    print("\nCheckpoint Analysis:")
    for t in checkpoints:
        data = checkpoint_results[t]
        flex = np.array([x[0] for x in data])
        rew = np.array([x[1] for x in data])
        r, p = stats.pearsonr(flex, rew)
        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
        print(f"  Step {t:3d}: r = {r:+.3f}, p = {p:.4f}{sig}")

    # Test 2: Compare with original task dynamics
    print("\n" + "-" * 70)
    print("TEST 2: REWARD ACCUMULATION PATTERN")
    print("-" * 70)

    # Run one episode and track reward per step
    agents = [Agent(i) for i in range(n_agents)]
    network = Network(n_agents)
    env = SimpleSpreadEnv(n_agents)

    observations = env.reset()
    rewards_per_step = []

    for step in range(300):
        noisy_obs = [o + np.random.randn(6) * 0.05 for o in observations]
        messages = [a.create_message(o) for a, o in zip(agents, noisy_obs)]
        received = network.exchange(messages)
        actions = [a.act(o, m) for a, o, m in zip(agents, noisy_obs, received)]
        observations, reward = env.step(actions)
        rewards_per_step.append(reward)

    # Check if rewards diminish over time
    early_rewards = np.mean(rewards_per_step[:50])
    late_rewards = np.mean(rewards_per_step[-50:])

    print(f"\n  Early steps (0-50):   mean reward = {early_rewards:.3f}")
    print(f"  Late steps (250-300): mean reward = {late_rewards:.3f}")

    if late_rewards < early_rewards:
        print("  → Rewards DIMINISH over time (positions saturate)")
    else:
        print("  → Rewards stable or increase over time")

    # Test 3: Flexibility variance over time
    print("\n" + "-" * 70)
    print("TEST 3: FLEXIBILITY VARIANCE OVER TIME")
    print("-" * 70)

    flex_variances = []
    for t in checkpoints:
        data = checkpoint_results[t]
        flex = np.array([x[0] for x in data])
        flex_variances.append(np.var(flex))
        print(f"  Step {t:3d}: flex variance = {np.var(flex):.4f}")

    # Conclusion
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    # Check if correlation decays
    early_r = stats.pearsonr(
        np.array([x[0] for x in checkpoint_results[50]]),
        np.array([x[1] for x in checkpoint_results[50]])
    )[0]
    late_r = stats.pearsonr(
        np.array([x[0] for x in checkpoint_results[300]]),
        np.array([x[1] for x in checkpoint_results[300]])
    )[0]

    print(f"\n  Early (50 steps): r = {early_r:+.3f}")
    print(f"  Late (300 steps): r = {late_r:+.3f}")

    if early_r > late_r:
        print("\n  CONFIRMED: Effect decays over time in MPE")

        if late_rewards < early_rewards:
            print("\n  HYPOTHESIS: Spatial saturation")
            print("  - Agents reach positions quickly")
            print("  - Further adaptation doesn't improve reward")
            print("  - Flexibility becomes noise after initial positioning")
        else:
            print("\n  HYPOTHESIS: Flexibility exhaustion")
            print("  - Random policies use up useful flexibility early")
            print("  - Later steps just add noise to the metric")
    else:
        print("\n  Effect does NOT decay - may be sampling variance")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"mpe_inversion_{timestamp}.npz"
    np.savez(filename, checkpoint_results=checkpoint_results)
    print(f"\nSaved: {filename}")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
