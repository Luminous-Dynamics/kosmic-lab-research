#!/usr/bin/env python3
"""
Track A v2: Compare K-Index to Established Metrics (Fixed)

Fixed version with proper entropy and MI computation.

Run with:
    nix-shell -p python3 python3Packages.numpy python3Packages.scipy --run "python3 -u track_a_metric_comparison_v2.py"
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
        # Add noise for stochasticity
        action = np.tanh(logits + np.random.randn(self.action_dim) * 0.3)
        self.obs_history.append(obs)
        self.action_history.append(action)
        return action

    def get_kindex(self):
        """K-Index: negative obs-action correlation."""
        if len(self.obs_history) < 10:
            return 0.0
        obs = np.array(self.obs_history[-50:]).flatten()
        actions = np.array(self.action_history[-50:]).flatten()
        min_len = min(len(obs), len(actions))
        if min_len < 2:
            return 0.0
        corr = np.corrcoef(obs[:min_len], actions[:min_len])[0, 1]
        return -abs(corr) * 2.0 if not np.isnan(corr) else 0.0

    def get_policy_entropy(self):
        """Entropy of action distribution (differential entropy proxy)."""
        if len(self.action_history) < 10:
            return 0.0
        actions = np.array(self.action_history[-50:])
        # Differential entropy proxy: log of determinant of covariance
        # For multivariate Gaussian: H = 0.5 * log((2*pi*e)^d * det(Sigma))
        try:
            cov = np.cov(actions.T)
            if cov.ndim == 0:
                return np.log(cov + 1e-10)
            sign, logdet = np.linalg.slogdet(cov + np.eye(cov.shape[0]) * 1e-6)
            return logdet / actions.shape[1]  # Normalize by dimension
        except:
            return 0.0

    def get_action_diversity(self):
        """Diversity: total variance across time."""
        if len(self.action_history) < 10:
            return 0.0
        actions = np.array(self.action_history[-50:])
        return np.var(actions)

    def get_mi_proxy(self):
        """Mutual information proxy between obs and actions."""
        if len(self.obs_history) < 10:
            return 0.0
        obs = np.array(self.obs_history[-50:])
        actions = np.array(self.action_history[-50:])

        # MI proxy: sum of squared correlations (canonical correlation-like)
        # Higher correlation = higher MI
        total_r2 = 0
        n_pairs = 0
        for i in range(min(obs.shape[1], actions.shape[1])):
            try:
                r, _ = stats.pearsonr(obs[:, i], actions[:, i])
                if not np.isnan(r):
                    total_r2 += r ** 2
                    n_pairs += 1
            except:
                pass

        return total_r2 / n_pairs if n_pairs > 0 else 0.0

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

    # Evaluation
    state = env.reset()
    for a in agents:
        a.obs_history = []
        a.action_history = []

    for step in range(n_steps):
        observations = [state + np.random.randn(10) * 0.1 for _ in range(n_agents)]
        messages = [a.create_message(o) for a, o in zip(agents, observations)]
        received = network.exchange(messages)
        actions = [a.act(o, m) for a, o, m in zip(agents, observations, received)]
        state, reward = env.step(actions)

    # Compute all metrics
    metrics = {
        'kindex': np.mean([a.get_kindex() for a in agents]),
        'entropy': np.mean([a.get_policy_entropy() for a in agents]),
        'diversity': np.mean([a.get_action_diversity() for a in agents]),
        'mi_proxy': np.mean([a.get_mi_proxy() for a in agents]),
    }

    return metrics, total_reward


def main():
    print("\n" + "=" * 70)
    print("TRACK A v2: COMPARE K-INDEX TO ESTABLISHED METRICS (FIXED)")
    print("=" * 70)

    np.random.seed(42)
    n_teams = 30

    print(f"\nTraining {n_teams} teams and comparing metrics...")

    all_metrics = {
        'kindex': [],
        'entropy': [],
        'diversity': [],
        'mi_proxy': [],
    }
    all_rewards = []

    for t in range(n_teams):
        np.random.seed(t * 1000)
        metrics, reward = train_team()
        for key in all_metrics:
            all_metrics[key].append(metrics[key])
        all_rewards.append(reward)

        if (t + 1) % 10 == 0:
            print(f"  Trained {t + 1}/{n_teams} teams...")

    all_rewards = np.array(all_rewards)

    # Compute correlations with performance
    print("\n" + "-" * 70)
    print("METRIC-PERFORMANCE CORRELATIONS")
    print("-" * 70)

    results = {}
    for name, values in all_metrics.items():
        values = np.array(values)
        try:
            r, p = stats.pearsonr(values, all_rewards)
        except:
            r, p = 0.0, 1.0
        results[name] = {'r': r, 'p': p, 'values': values}
        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
        print(f"  {name:12s}: r = {r:+.3f}{sig}, p = {p:.4f}")

    # Inter-metric correlations
    print("\n" + "-" * 70)
    print("INTER-METRIC CORRELATIONS")
    print("-" * 70)

    metric_names = list(all_metrics.keys())
    for i, m1 in enumerate(metric_names):
        for m2 in metric_names[i+1:]:
            try:
                r, _ = stats.pearsonr(results[m1]['values'], results[m2]['values'])
            except:
                r = 0.0
            print(f"  {m1} vs {m2}: r = {r:+.3f}")

    # Conclusion
    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    # Find best metric
    valid_results = {k: v for k, v in results.items() if not np.isnan(v['r'])}
    if valid_results:
        best = max(valid_results.keys(), key=lambda k: abs(valid_results[k]['r']))
        best_r = valid_results[best]['r']

        print(f"\nBest predictor: {best} (r = {best_r:+.3f})")

        if best == 'kindex':
            print("\n✓ K-INDEX OUTPERFORMS ESTABLISHED METRICS!")
            print("  Simple obs-action correlation beats entropy/MI")
        else:
            kindex_r = results['kindex']['r']
            print(f"\n→ {best} outperforms K-Index ({valid_results[best]['r']:+.3f} vs {kindex_r:+.3f})")

        # Check if K-Index is competitive
        kindex_r = abs(results['kindex']['r'])
        others = [abs(results[k]['r']) for k in results if k != 'kindex' and not np.isnan(results[k]['r'])]
        if others and kindex_r >= max(others) * 0.9:
            print("\n✓ K-Index is competitive with existing metrics")
            print("  Advantage: simpler and more interpretable")

    # Ranking
    print("\nRanking by |r|:")
    ranked = sorted(results.items(), key=lambda x: abs(x[1]['r']) if not np.isnan(x[1]['r']) else 0, reverse=True)
    for i, (name, res) in enumerate(ranked, 1):
        print(f"  {i}. {name}: |r| = {abs(res['r']):.3f}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"track_a_v2_{timestamp}.npz"
    np.savez(filename, results=results, rewards=all_rewards)
    print(f"\nSaved: {filename}")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
