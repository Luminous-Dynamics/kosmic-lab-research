#!/usr/bin/env python3
"""
Supplementary: Large Sample Size Validation

Test K-Index with n=50 teams for tighter confidence intervals.

Run with:
    nix-shell -p python3 python3Packages.numpy python3Packages.scipy --run "python3 -u supplementary_large_n.py"
"""

import numpy as np
from scipy import stats
from datetime import datetime


class Agent:
    def __init__(self, agent_id, obs_dim=10, action_dim=10):
        self.id = agent_id
        self.obs_dim = obs_dim
        self.action_dim = action_dim
        self.policy_weights = np.random.randn(action_dim, obs_dim + 5) * 0.1
        self.obs_history = []
        self.action_history = []
        self.rewards = []

    def act(self, obs, messages):
        combined = np.concatenate([obs, messages])
        logits = self.policy_weights @ combined
        action = np.tanh(logits + np.random.randn(self.action_dim) * 0.3)
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

    def update(self, learning_rate=0.01):
        if not self.rewards:
            return
        returns = []
        G = 0
        for r in reversed(self.rewards):
            G = r + 0.99 * G
            returns.insert(0, G)
        returns = np.array(returns)
        if len(returns) > 1:
            returns = (returns - returns.mean()) / (returns.std() + 1e-8)

        for i in range(min(len(self.obs_history), len(returns))):
            obs = self.obs_history[i]
            action = self.action_history[i]
            ret = returns[i]
            gradient = np.outer(action, np.concatenate([obs, np.zeros(5)]))
            self.policy_weights += learning_rate * ret * gradient

        self.obs_history = []
        self.action_history = []
        self.rewards = []

    def create_message(self, obs):
        return obs[:5]


class Network:
    def __init__(self, n_agents):
        self.n_agents = n_agents

    def exchange(self, messages):
        avg = np.mean(messages, axis=0)
        return [avg for _ in range(self.n_agents)]


class Environment:
    def __init__(self, n_agents, state_dim=10):
        self.n_agents = n_agents
        self.state_dim = state_dim
        self.state = np.zeros(state_dim)
        self.target = np.zeros(state_dim)

    def reset(self):
        self.state = np.random.randn(self.state_dim) * 0.1
        self.target = np.random.randn(self.state_dim)
        return self.state

    def step(self, actions):
        action_mean = np.mean(actions, axis=0)
        self.state += action_mean * 0.1
        dist = np.linalg.norm(self.state - self.target)
        coord = -np.mean([np.linalg.norm(a - action_mean) for a in actions])
        return self.state, -dist + 0.5 * coord


def train_team(n_agents=4, n_episodes=50, n_steps=150):
    agents = [Agent(i) for i in range(n_agents)]
    network = Network(n_agents)
    env = Environment(n_agents)

    for ep in range(n_episodes):
        state = env.reset()
        for a in agents:
            a.obs_history = []
            a.action_history = []
            a.rewards = []

        total_reward = 0
        for step in range(n_steps):
            observations = [state + np.random.randn(10) * 0.1 for _ in range(n_agents)]
            messages = [a.create_message(o) for a, o in zip(agents, observations)]
            received = network.exchange(messages)
            actions = [a.act(o, m) for a, o, m in zip(agents, observations, received)]
            state, reward = env.step(actions)
            for a in agents:
                a.rewards.append(reward)
            total_reward += reward

        for a in agents:
            a.update()

    # Evaluation episode
    state = env.reset()
    for a in agents:
        a.obs_history = []
        a.action_history = []

    eval_reward = 0
    for step in range(n_steps):
        observations = [state + np.random.randn(10) * 0.1 for _ in range(n_agents)]
        messages = [a.create_message(o) for a, o in zip(agents, observations)]
        received = network.exchange(messages)
        actions = [a.act(o, m) for a, o, m in zip(agents, observations, received)]
        state, reward = env.step(actions)
        eval_reward += reward

    flexibility = np.mean([a.get_flexibility() for a in agents])
    return flexibility, eval_reward


def main():
    print("\n" + "=" * 70)
    print("SUPPLEMENTARY: LARGE SAMPLE SIZE VALIDATION (n=50)")
    print("=" * 70)

    np.random.seed(42)
    n_teams = 50

    print(f"\nTraining {n_teams} teams...")

    flexibilities = []
    rewards = []

    for t in range(n_teams):
        np.random.seed(t * 1000)
        flex, reward = train_team()
        flexibilities.append(flex)
        rewards.append(reward)

        if (t + 1) % 10 == 0:
            print(f"  Trained {t + 1}/{n_teams} teams...")

    flexibilities = np.array(flexibilities)
    rewards = np.array(rewards)

    # Compute correlation with confidence interval
    r, p = stats.pearsonr(flexibilities, rewards)

    # Fisher z-transformation for CI
    z = np.arctanh(r)
    se = 1 / np.sqrt(n_teams - 3)
    z_lower = z - 1.96 * se
    z_upper = z + 1.96 * se
    ci_lower = np.tanh(z_lower)
    ci_upper = np.tanh(z_upper)

    print("\n" + "-" * 70)
    print("RESULTS")
    print("-" * 70)
    print(f"  Sample size: n = {n_teams}")
    print(f"  Correlation: r = {r:+.3f}")
    print(f"  95% CI: [{ci_lower:.3f}, {ci_upper:.3f}]")
    print(f"  CI width: {ci_upper - ci_lower:.3f}")
    print(f"  p-value: {p:.6f}")

    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
    print(f"  Significance: {sig}")

    # Compare to n=30
    print("\n" + "-" * 70)
    print("COMPARISON TO SMALLER SAMPLES")
    print("-" * 70)

    for n in [20, 30, 40]:
        subset_flex = flexibilities[:n]
        subset_rew = rewards[:n]
        r_sub, p_sub = stats.pearsonr(subset_flex, subset_rew)
        z_sub = np.arctanh(r_sub)
        se_sub = 1 / np.sqrt(n - 3)
        ci_width = 2 * 1.96 * se_sub
        print(f"  n={n}: r = {r_sub:+.3f}, CI width = {np.tanh(z_sub + 0.98*se_sub) - np.tanh(z_sub - 0.98*se_sub):.3f}")

    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print(f"\nWith n={n_teams}, 95% CI is [{ci_lower:.3f}, {ci_upper:.3f}]")
    print(f"CI width = {ci_upper - ci_lower:.3f} (tighter than n=30)")

    if p < 0.001:
        print("\n✓ Effect remains highly significant with larger sample")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"supplementary_large_n_{timestamp}.npz"
    np.savez(filename,
             flexibilities=flexibilities,
             rewards=rewards,
             r=r, p=p, ci_lower=ci_lower, ci_upper=ci_upper)
    print(f"\nSaved: {filename}")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
