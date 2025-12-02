#!/usr/bin/env python3
"""
Supplementary: Ablation Studies

Test K-Index sensitivity to:
- History window size (25, 50, 100 steps)
- Message dimension (3, 5, 10)
- Observation noise levels (0.05, 0.1, 0.3, 0.5)

Run with:
    nix-shell -p python3 python3Packages.numpy python3Packages.scipy --run "python3 -u supplementary_ablations.py"
"""

import numpy as np
from scipy import stats
from datetime import datetime


class Agent:
    def __init__(self, agent_id, obs_dim=10, action_dim=10, msg_dim=5):
        self.id = agent_id
        self.obs_dim = obs_dim
        self.action_dim = action_dim
        self.msg_dim = msg_dim
        self.policy_weights = np.random.randn(action_dim, obs_dim + msg_dim) * 0.1
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

    def get_flexibility(self, window=50):
        if len(self.obs_history) < 10:
            return 0.0
        obs = np.array(self.obs_history[-window:]).flatten()
        actions = np.array(self.action_history[-window:]).flatten()
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
            self.policy_weights += learning_rate * ret * gradient

        self.obs_history = []
        self.action_history = []
        self.rewards = []

    def create_message(self, obs):
        return obs[:self.msg_dim]


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


def train_team(n_agents=4, n_episodes=50, n_steps=150, msg_dim=5, obs_noise=0.1, history_window=50):
    agents = [Agent(i, msg_dim=msg_dim) for i in range(n_agents)]
    network = Network(n_agents)
    env = Environment(n_agents)

    for ep in range(n_episodes):
        state = env.reset()
        for a in agents:
            a.obs_history = []
            a.action_history = []
            a.rewards = []

        for step in range(n_steps):
            observations = [state + np.random.randn(10) * obs_noise for _ in range(n_agents)]
            messages = [a.create_message(o) for a, o in zip(agents, observations)]
            received = network.exchange(messages)
            actions = [a.act(o, m) for a, o, m in zip(agents, observations, received)]
            state, reward = env.step(actions)
            for a in agents:
                a.rewards.append(reward)

        for a in agents:
            a.update()

    # Evaluation
    state = env.reset()
    for a in agents:
        a.obs_history = []
        a.action_history = []

    eval_reward = 0
    for step in range(n_steps):
        observations = [state + np.random.randn(10) * obs_noise for _ in range(n_agents)]
        messages = [a.create_message(o) for a, o in zip(agents, observations)]
        received = network.exchange(messages)
        actions = [a.act(o, m) for a, o, m in zip(agents, observations, received)]
        state, reward = env.step(actions)
        eval_reward += reward

    flexibility = np.mean([a.get_flexibility(window=history_window) for a in agents])
    return flexibility, eval_reward


def run_ablation(name, param_name, values, default_kwargs, n_teams=20):
    """Run ablation study for a single parameter."""
    print(f"\n{'='*50}")
    print(f"ABLATION: {name}")
    print(f"{'='*50}")

    results = {}

    for value in values:
        kwargs = default_kwargs.copy()
        kwargs[param_name] = value

        flexibilities = []
        rewards = []

        for t in range(n_teams):
            np.random.seed(t * 1000)
            flex, reward = train_team(**kwargs)
            flexibilities.append(flex)
            rewards.append(reward)

        r, p = stats.pearsonr(flexibilities, rewards)
        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''

        results[value] = {'r': r, 'p': p, 'sig': sig}
        print(f"  {param_name}={value}: r = {r:+.3f}{sig}")

    return results


def main():
    print("\n" + "=" * 70)
    print("SUPPLEMENTARY: ABLATION STUDIES")
    print("=" * 70)

    np.random.seed(42)
    n_teams = 20

    all_results = {}

    # Ablation 1: History window size
    history_results = run_ablation(
        "History Window Size",
        "history_window",
        [25, 50, 100],
        {'msg_dim': 5, 'obs_noise': 0.1},
        n_teams
    )
    all_results['history_window'] = history_results

    # Ablation 2: Message dimension
    message_results = run_ablation(
        "Message Dimension",
        "msg_dim",
        [3, 5, 10],
        {'history_window': 50, 'obs_noise': 0.1},
        n_teams
    )
    all_results['msg_dim'] = message_results

    # Ablation 3: Observation noise
    noise_results = run_ablation(
        "Observation Noise",
        "obs_noise",
        [0.05, 0.1, 0.3, 0.5],
        {'history_window': 50, 'msg_dim': 5},
        n_teams
    )
    all_results['obs_noise'] = noise_results

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for param, results in all_results.items():
        print(f"\n{param}:")
        best_val = max(results.keys(), key=lambda k: results[k]['r'])
        worst_val = min(results.keys(), key=lambda k: results[k]['r'])

        all_sig = all(res['p'] < 0.05 for res in results.values())

        if all_sig:
            print(f"  ✓ All values significant")
        else:
            print(f"  → Some values not significant")

        print(f"  Best: {param}={best_val} (r = {results[best_val]['r']:+.3f})")
        print(f"  Worst: {param}={worst_val} (r = {results[worst_val]['r']:+.3f})")

        # Range
        r_range = max(r['r'] for r in results.values()) - min(r['r'] for r in results.values())
        print(f"  Range: {r_range:.3f}")

    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    # Check robustness
    all_robust = True
    for param, results in all_results.items():
        r_range = max(r['r'] for r in results.values()) - min(r['r'] for r in results.values())
        if r_range > 0.3:
            all_robust = False
            print(f"\n⚠ {param} shows high sensitivity (range = {r_range:.3f})")

    if all_robust:
        print("\n✓ K-INDEX IS ROBUST TO HYPERPARAMETER CHOICES")
        print("  Effect persists across reasonable parameter ranges")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"supplementary_ablations_{timestamp}.npz"
    np.savez(filename, results=all_results)
    print(f"\nSaved: {filename}")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
