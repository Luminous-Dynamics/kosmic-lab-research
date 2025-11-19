#!/usr/bin/env python3
"""
Supplementary: Algorithm Comparison

Test K-Index with REINFORCE, PPO-style, and A2C-style updates.

Run with:
    nix-shell -p python3 python3Packages.numpy python3Packages.scipy --run "python3 -u supplementary_algorithms.py"
"""

import numpy as np
from scipy import stats
from datetime import datetime


class BaseAgent:
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

    def create_message(self, obs):
        return obs[:5]

    def clear_history(self):
        self.obs_history = []
        self.action_history = []
        self.rewards = []


class REINFORCEAgent(BaseAgent):
    """Standard REINFORCE update."""

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

        self.clear_history()


class PPOAgent(BaseAgent):
    """PPO-style update with clipped objective."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.old_policy_weights = self.policy_weights.copy()
        self.clip_ratio = 0.2

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

        # Multiple epochs of updates (PPO-style)
        for epoch in range(3):
            for i in range(min(len(self.obs_history), len(returns))):
                obs = self.obs_history[i]
                action = self.action_history[i]
                ret = returns[i]

                combined = np.concatenate([obs, np.zeros(5)])

                # Compute ratio (simplified)
                new_logits = self.policy_weights @ combined
                old_logits = self.old_policy_weights @ combined

                # Simplified ratio computation
                ratio = np.exp(-0.5 * np.sum((action - np.tanh(new_logits))**2) +
                              0.5 * np.sum((action - np.tanh(old_logits))**2))
                ratio = np.clip(ratio, 0.1, 10.0)  # Numerical stability

                # Clipped objective
                clipped_ratio = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio)
                objective = min(ratio * ret, clipped_ratio * ret)

                gradient = np.outer(action, combined)
                self.policy_weights += learning_rate * objective * gradient

        self.old_policy_weights = self.policy_weights.copy()
        self.clear_history()


class A2CAgent(BaseAgent):
    """A2C-style update with value baseline."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value_weights = np.random.randn(1, 10 + 5) * 0.1

    def update(self, learning_rate=0.01):
        if not self.rewards:
            return

        returns = []
        G = 0
        for r in reversed(self.rewards):
            G = r + 0.99 * G
            returns.insert(0, G)
        returns = np.array(returns)

        for i in range(min(len(self.obs_history), len(returns))):
            obs = self.obs_history[i]
            action = self.action_history[i]
            ret = returns[i]

            combined = np.concatenate([obs, np.zeros(5)])

            # Value estimate
            value = (self.value_weights @ combined)[0]
            advantage = ret - value

            # Policy update
            gradient = np.outer(action, combined)
            self.policy_weights += learning_rate * advantage * gradient

            # Value update
            value_gradient = combined.reshape(1, -1)
            self.value_weights += learning_rate * 0.5 * (ret - value) * value_gradient

        self.clear_history()


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


def train_team(agent_class, n_agents=4, n_episodes=50, n_steps=150):
    agents = [agent_class(i) for i in range(n_agents)]
    network = Network(n_agents)
    env = Environment(n_agents)

    for ep in range(n_episodes):
        state = env.reset()
        for a in agents:
            a.clear_history()

        for step in range(n_steps):
            observations = [state + np.random.randn(10) * 0.1 for _ in range(n_agents)]
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
    print("SUPPLEMENTARY: ALGORITHM COMPARISON")
    print("=" * 70)

    np.random.seed(42)
    n_teams = 20  # Reduced for speed

    algorithms = {
        'REINFORCE': REINFORCEAgent,
        'PPO': PPOAgent,
        'A2C': A2CAgent
    }

    results = {}

    for algo_name, agent_class in algorithms.items():
        print(f"\nTraining {n_teams} teams with {algo_name}...")

        flexibilities = []
        rewards = []

        for t in range(n_teams):
            np.random.seed(t * 1000)
            flex, reward = train_team(agent_class)
            flexibilities.append(flex)
            rewards.append(reward)

            if (t + 1) % 10 == 0:
                print(f"  Trained {t + 1}/{n_teams} teams...")

        flexibilities = np.array(flexibilities)
        rewards = np.array(rewards)

        r, p = stats.pearsonr(flexibilities, rewards)
        results[algo_name] = {
            'r': r, 'p': p,
            'flexibilities': flexibilities,
            'rewards': rewards
        }

    print("\n" + "-" * 70)
    print("RESULTS BY ALGORITHM")
    print("-" * 70)

    for algo_name, res in results.items():
        sig = '***' if res['p'] < 0.001 else '**' if res['p'] < 0.01 else '*' if res['p'] < 0.05 else ''
        print(f"  {algo_name:12s}: r = {res['r']:+.3f}{sig}, p = {res['p']:.4f}")

    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    # Check if all algorithms show significant positive correlation
    all_significant = all(res['p'] < 0.05 and res['r'] > 0 for res in results.values())

    if all_significant:
        print("\n✓ K-INDEX GENERALIZES ACROSS ALGORITHMS!")
        print("  Effect is not specific to REINFORCE")
    else:
        print("\n→ Some algorithms show different patterns")

    # Find best and worst
    best = max(results.keys(), key=lambda k: results[k]['r'])
    worst = min(results.keys(), key=lambda k: results[k]['r'])
    print(f"\nStrongest: {best} (r = {results[best]['r']:+.3f})")
    print(f"Weakest: {worst} (r = {results[worst]['r']:+.3f})")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"supplementary_algorithms_{timestamp}.npz"
    np.savez(filename, **{f"{k}_{m}": v[m] for k, v in results.items() for m in ['r', 'p', 'flexibilities', 'rewards']})
    print(f"\nSaved: {filename}")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
