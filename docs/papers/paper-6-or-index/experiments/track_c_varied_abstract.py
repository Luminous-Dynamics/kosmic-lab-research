#!/usr/bin/env python3
"""
Track C Varied Abstract: Test K-Index Across Abstract Task Variants

Validate that K-Index transfers to different abstract coordination problems:
1. Different reward structures (sparse vs dense)
2. Different team sizes (2, 4, 6, 8)
3. Different state dimensions

Run with:
    nix-shell -p python3 python3Packages.numpy python3Packages.scipy --run "python3 -u track_c_varied_abstract.py"
"""

import numpy as np
from scipy import stats
from datetime import datetime


class Agent:
    def __init__(self, agent_id, obs_dim, action_dim):
        self.id = agent_id
        self.obs_dim = obs_dim
        self.action_dim = action_dim
        msg_dim = min(5, obs_dim)
        self.policy_weights = np.random.randn(action_dim, obs_dim + msg_dim) * 0.1
        self.obs_history = []
        self.action_history = []
        self.rewards = []
        self.msg_dim = msg_dim

    def act(self, obs, messages):
        combined = np.concatenate([obs, messages])
        action = np.tanh(self.policy_weights @ combined + np.random.randn(self.action_dim) * 0.3)
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
            gradient = np.outer(action, np.concatenate([obs, np.zeros(self.msg_dim)]))
            self.policy_weights += learning_rate * ret * gradient[:, :self.obs_dim + self.msg_dim]

        self.obs_history = []
        self.action_history = []
        self.rewards = []

    def create_message(self, obs):
        return obs[:self.msg_dim]


class Network:
    def __init__(self, n_agents, msg_dim):
        self.n_agents = n_agents
        self.msg_dim = msg_dim

    def exchange(self, messages):
        avg = np.mean(messages, axis=0)
        return [avg for _ in range(self.n_agents)]


class AbstractEnv:
    def __init__(self, n_agents, state_dim, sparse_reward=False):
        self.n_agents = n_agents
        self.state_dim = state_dim
        self.sparse_reward = sparse_reward
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

        if self.sparse_reward:
            # Only reward when close
            if dist < 0.5:
                reward = 10.0 + coord
            else:
                reward = coord * 0.1
        else:
            reward = -dist + 0.5 * coord

        return self.state, reward


def train_team(n_agents, state_dim, action_dim, sparse_reward, n_episodes=50, n_steps=100):
    msg_dim = min(5, state_dim)
    agents = [Agent(i, state_dim, action_dim) for i in range(n_agents)]
    network = Network(n_agents, msg_dim)
    env = AbstractEnv(n_agents, state_dim, sparse_reward)

    episode_rewards = []

    for ep in range(n_episodes):
        state = env.reset()
        for a in agents:
            a.obs_history = []
            a.action_history = []
            a.rewards = []

        total_reward = 0
        for step in range(n_steps):
            observations = [state + np.random.randn(state_dim) * 0.1 for _ in range(n_agents)]
            messages = [a.create_message(o) for a, o in zip(agents, observations)]
            received = network.exchange(messages)
            actions = [a.act(o, m) for a, o, m in zip(agents, observations, received)]
            state, reward = env.step(actions)
            for a in agents:
                a.rewards.append(reward)
            total_reward += reward

        for a in agents:
            a.update()

        episode_rewards.append(total_reward)

    # Evaluation
    state = env.reset()
    for a in agents:
        a.obs_history = []
        a.action_history = []

    for step in range(n_steps):
        observations = [state + np.random.randn(state_dim) * 0.1 for _ in range(n_agents)]
        messages = [a.create_message(o) for a, o in zip(agents, observations)]
        received = network.exchange(messages)
        actions = [a.act(o, m) for a, o, m in zip(agents, observations, received)]
        state, reward = env.step(actions)

    flexibility = np.mean([a.get_flexibility() for a in agents])
    final_performance = np.mean(episode_rewards[-10:])

    return flexibility, final_performance


def main():
    print("\n" + "=" * 70)
    print("TRACK C VARIED ABSTRACT: K-INDEX ACROSS TASK VARIANTS")
    print("=" * 70)

    np.random.seed(42)
    n_teams_per_condition = 15

    conditions = [
        {'name': 'baseline', 'n_agents': 4, 'state_dim': 10, 'action_dim': 10, 'sparse': False},
        {'name': 'small_team', 'n_agents': 2, 'state_dim': 10, 'action_dim': 10, 'sparse': False},
        {'name': 'large_team', 'n_agents': 8, 'state_dim': 10, 'action_dim': 10, 'sparse': False},
        {'name': 'sparse_reward', 'n_agents': 4, 'state_dim': 10, 'action_dim': 10, 'sparse': True},
        {'name': 'high_dim', 'n_agents': 4, 'state_dim': 20, 'action_dim': 20, 'sparse': False},
    ]

    results = {}

    for cond in conditions:
        print(f"\nTesting: {cond['name']}")

        flexibilities = []
        performances = []

        for t in range(n_teams_per_condition):
            np.random.seed(t * 1000 + hash(cond['name']) % 1000)
            flex, perf = train_team(
                n_agents=cond['n_agents'],
                state_dim=cond['state_dim'],
                action_dim=cond['action_dim'],
                sparse_reward=cond['sparse']
            )
            flexibilities.append(flex)
            performances.append(perf)

        flexibilities = np.array(flexibilities)
        performances = np.array(performances)

        r, p = stats.pearsonr(flexibilities, performances)
        results[cond['name']] = {
            'r': r, 'p': p,
            'flex_var': np.var(flexibilities),
            'mean_perf': np.mean(performances)
        }

        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
        print(f"  r = {r:+.3f}{sig}, p = {p:.4f}, var = {np.var(flexibilities):.3f}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print("\n{:<15} {:>8} {:>8} {:>8}".format("Condition", "r", "p", "sig"))
    print("-" * 45)

    all_significant = True
    for name, res in results.items():
        sig = '***' if res['p'] < 0.001 else '**' if res['p'] < 0.01 else '*' if res['p'] < 0.05 else ''
        print(f"{name:<15} {res['r']:+8.3f} {res['p']:8.4f} {sig}")
        if res['p'] >= 0.05:
            all_significant = False

    # Conclusion
    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    n_sig = sum(1 for r in results.values() if r['p'] < 0.05)

    if n_sig == len(conditions):
        print(f"\n✓ K-INDEX GENERALIZES ACROSS ALL {len(conditions)} CONDITIONS!")
        print("  Robust to team size, reward structure, and dimensionality")
    elif n_sig >= len(conditions) * 0.8:
        print(f"\n✓ K-Index generalizes to {n_sig}/{len(conditions)} conditions")
        failed = [n for n, r in results.items() if r['p'] >= 0.05]
        print(f"  Weaker in: {', '.join(failed)}")
    else:
        print(f"\n→ K-Index only significant in {n_sig}/{len(conditions)} conditions")
        print("  May be sensitive to task parameters")

    # Mean correlation
    mean_r = np.mean([r['r'] for r in results.values()])
    print(f"\nMean correlation across conditions: r = {mean_r:+.3f}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"track_c_varied_{timestamp}.npz"
    np.savez(filename, results=results)
    print(f"\nSaved: {filename}")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
