#!/usr/bin/env python3
"""
Track B: Zero-Shot Coordination Test

Test if K-Index predicts success when agents trained separately
must coordinate at test time without prior joint training.

Run with:
    nix-shell -p python3 python3Packages.numpy python3Packages.scipy --run "python3 -u track_b_zeroshot_coordination.py"
"""

import numpy as np
from scipy import stats
from datetime import datetime


class Agent:
    def __init__(self, agent_id):
        self.id = agent_id
        self.policy_weights = np.random.randn(10, 15) * 0.1
        self.obs_history = []
        self.action_history = []
        self.rewards = []

    def act(self, obs, messages):
        combined = np.concatenate([obs, messages])
        action = np.tanh(self.policy_weights @ combined + np.random.randn(10) * 0.3)
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
            self.policy_weights += learning_rate * ret * gradient[:, :15]

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
    def __init__(self, n_agents):
        self.n_agents = n_agents
        self.state = np.zeros(10)
        self.target = np.zeros(10)

    def reset(self):
        self.state = np.random.randn(10) * 0.1
        self.target = np.random.randn(10)
        return self.state

    def step(self, actions):
        action_mean = np.mean(actions, axis=0)
        self.state += action_mean * 0.1
        dist = np.linalg.norm(self.state - self.target)
        coord = -np.mean([np.linalg.norm(a - action_mean) for a in actions])
        return self.state, -dist + 0.5 * coord


def train_agent_solo(seed, n_episodes=40, n_steps=100):
    """Train a single agent in isolation with simulated partners."""
    np.random.seed(seed)
    agent = Agent(0)

    for ep in range(n_episodes):
        state = np.random.randn(10) * 0.1
        target = np.random.randn(10)

        agent.obs_history = []
        agent.action_history = []
        agent.rewards = []

        for step in range(n_steps):
            obs = state + np.random.randn(10) * 0.1
            # Simulated partner messages (random)
            messages = np.random.randn(5) * 0.5
            action = agent.act(obs, messages)

            # Simulated partner actions
            partner_actions = [np.random.randn(10) * 0.5 for _ in range(3)]
            all_actions = [action] + partner_actions
            action_mean = np.mean(all_actions, axis=0)

            state += action_mean * 0.1
            dist = np.linalg.norm(state - target)
            coord = -np.mean([np.linalg.norm(a - action_mean) for a in all_actions])
            reward = -dist + 0.5 * coord

            agent.rewards.append(reward)

        agent.update()

    # Measure flexibility
    state = np.random.randn(10) * 0.1
    agent.obs_history = []
    agent.action_history = []

    for step in range(n_steps):
        obs = state + np.random.randn(10) * 0.1
        messages = np.random.randn(5) * 0.5
        action = agent.act(obs, messages)
        state += action * 0.1

    return agent, agent.get_flexibility()


def test_zeroshot_team(agents, n_episodes=10, n_steps=100):
    """Test agents who never trained together."""
    n_agents = len(agents)
    network = Network(n_agents)
    env = Environment(n_agents)

    episode_rewards = []

    for ep in range(n_episodes):
        state = env.reset()
        for a in agents:
            a.obs_history = []
            a.action_history = []

        total_reward = 0
        for step in range(n_steps):
            observations = [state + np.random.randn(10) * 0.1 for _ in range(n_agents)]
            messages = [a.create_message(o) for a, o in zip(agents, observations)]
            received = network.exchange(messages)
            actions = [a.act(o, m) for a, o, m in zip(agents, observations, received)]
            state, reward = env.step(actions)
            total_reward += reward

        episode_rewards.append(total_reward)

    return np.mean(episode_rewards)


def main():
    print("\n" + "=" * 70)
    print("TRACK B: ZERO-SHOT COORDINATION TEST")
    print("=" * 70)

    np.random.seed(42)
    n_teams = 20
    n_agents = 4

    print(f"\nTraining {n_teams * n_agents} agents in isolation...")
    print("Then testing zero-shot coordination in random teams")

    # Train agents individually
    all_agents = []
    all_flexibilities = []

    for i in range(n_teams * n_agents):
        agent, flex = train_agent_solo(seed=i * 100)
        all_agents.append(agent)
        all_flexibilities.append(flex)

        if (i + 1) % 20 == 0:
            print(f"  Trained {i + 1}/{n_teams * n_agents} agents...")

    all_flexibilities = np.array(all_flexibilities)
    print(f"\n  Flexibility range: [{all_flexibilities.min():.3f}, {all_flexibilities.max():.3f}]")

    # Form random teams and test
    print(f"\nTesting {n_teams} random zero-shot teams...")

    team_flexibilities = []
    team_performances = []

    for t in range(n_teams):
        # Random team composition
        np.random.seed(t * 1000)
        indices = np.random.choice(len(all_agents), n_agents, replace=False)
        team = [all_agents[i] for i in indices]

        # Team flexibility = mean of individual flexibilities
        team_flex = np.mean([all_flexibilities[i] for i in indices])
        team_flexibilities.append(team_flex)

        # Test performance
        perf = test_zeroshot_team(team)
        team_performances.append(perf)

    team_flexibilities = np.array(team_flexibilities)
    team_performances = np.array(team_performances)

    # Correlation
    r, p = stats.pearsonr(team_flexibilities, team_performances)

    print("\n" + "-" * 70)
    print("RESULTS")
    print("-" * 70)

    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
    print(f"\nFlexibility-Performance Correlation:")
    print(f"  r = {r:+.3f}{sig}, p = {p:.4f}")

    # Conclusion
    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    if p < 0.05:
        print(f"\n✓ K-INDEX PREDICTS ZERO-SHOT COORDINATION!")
        print(f"  Flexible agents adapt better to novel partners")
        print(f"  Correlation: r = {r:+.3f}")
    else:
        print(f"\n→ Zero-shot correlation not significant (r = {r:+.3f}, p = {p:.3f})")
        print("  Flexibility may not transfer to completely novel partners")

    print("\nComparison to joint training:")
    print(f"  Joint training:  r = +0.70*** (same partners)")
    print(f"  Zero-shot:       r = {r:+.3f} (novel partners)")

    if r > 0.3 and p < 0.05:
        print("\n  ✓ Effect transfers to zero-shot setting")
    elif r > 0:
        print("\n  → Partial transfer (weaker than joint training)")
    else:
        print("\n  → No transfer to zero-shot setting")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"track_b_zeroshot_{timestamp}.npz"
    np.savez(filename,
             team_flexibilities=team_flexibilities,
             team_performances=team_performances,
             individual_flexibilities=all_flexibilities)
    print(f"\nSaved: {filename}")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
