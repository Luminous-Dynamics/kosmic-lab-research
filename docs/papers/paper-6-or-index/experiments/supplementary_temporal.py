#!/usr/bin/env python3
"""
Supplementary: Temporal Dynamics

Track how K-Index evolves during training.

Run with:
    nix-shell -p python3 python3Packages.numpy python3Packages.scipy --run "python3 -u supplementary_temporal.py"
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


def train_team_with_tracking(n_agents=4, n_episodes=50, n_steps=150, checkpoints=None):
    """Train team and track K-Index at checkpoints."""
    if checkpoints is None:
        checkpoints = [0, 10, 20, 30, 40, 50]

    agents = [Agent(i) for i in range(n_agents)]
    network = Network(n_agents)
    env = Environment(n_agents)

    flexibility_history = []
    reward_history = []

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

        # Record at checkpoints
        if ep in checkpoints:
            flex = np.mean([a.get_flexibility() for a in agents])
            flexibility_history.append(flex)
            reward_history.append(total_reward)

        for a in agents:
            a.update()

    return flexibility_history, reward_history


def main():
    print("\n" + "=" * 70)
    print("SUPPLEMENTARY: TEMPORAL DYNAMICS")
    print("=" * 70)

    np.random.seed(42)
    n_teams = 30
    checkpoints = [0, 5, 10, 20, 30, 40, 49]

    print(f"\nTraining {n_teams} teams with checkpoints at episodes {checkpoints}...")

    all_flex_histories = []
    all_reward_histories = []

    for t in range(n_teams):
        np.random.seed(t * 1000)
        flex_hist, reward_hist = train_team_with_tracking(checkpoints=checkpoints)
        all_flex_histories.append(flex_hist)
        all_reward_histories.append(reward_hist)

        if (t + 1) % 10 == 0:
            print(f"  Trained {t + 1}/{n_teams} teams...")

    all_flex_histories = np.array(all_flex_histories)
    all_reward_histories = np.array(all_reward_histories)

    print("\n" + "-" * 70)
    print("K-INDEX EVOLUTION DURING TRAINING")
    print("-" * 70)

    print(f"\n{'Episode':>8} {'Mean K-Index':>15} {'Std':>10} {'Change':>10}")
    print("-" * 45)

    prev_flex = None
    for i, ep in enumerate(checkpoints):
        mean_flex = np.mean(all_flex_histories[:, i])
        std_flex = np.std(all_flex_histories[:, i])

        if prev_flex is not None:
            change = mean_flex - prev_flex
            change_str = f"{change:+.3f}"
        else:
            change_str = "—"

        print(f"{ep:>8} {mean_flex:>15.3f} {std_flex:>10.3f} {change_str:>10}")
        prev_flex = mean_flex

    # Compute correlations at each checkpoint
    print("\n" + "-" * 70)
    print("FLEXIBILITY-PERFORMANCE CORRELATION BY EPISODE")
    print("-" * 70)

    for i, ep in enumerate(checkpoints):
        flex = all_flex_histories[:, i]
        rewards = all_reward_histories[:, i]
        r, p = stats.pearsonr(flex, rewards)
        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
        print(f"  Episode {ep:>3}: r = {r:+.3f}{sig}")

    # Early prediction of final performance
    print("\n" + "-" * 70)
    print("EARLY PREDICTION OF FINAL PERFORMANCE")
    print("-" * 70)

    final_rewards = all_reward_histories[:, -1]

    for i, ep in enumerate(checkpoints[:-1]):
        flex = all_flex_histories[:, i]
        r, p = stats.pearsonr(flex, final_rewards)
        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
        print(f"  Episode {ep:>3} flexibility → final reward: r = {r:+.3f}{sig}")

    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    # Check if flexibility increases
    initial_flex = np.mean(all_flex_histories[:, 0])
    final_flex = np.mean(all_flex_histories[:, -1])

    if final_flex > initial_flex:
        print(f"\n✓ Flexibility INCREASES during training")
        print(f"  Initial: {initial_flex:.3f} → Final: {final_flex:.3f}")
    else:
        print(f"\n→ Flexibility decreases during training")
        print(f"  Initial: {initial_flex:.3f} → Final: {final_flex:.3f}")

    # Check early prediction
    early_flex = all_flex_histories[:, 2]  # Episode 10
    r_early, p_early = stats.pearsonr(early_flex, final_rewards)

    if p_early < 0.05:
        print(f"\n✓ Early flexibility (ep 10) predicts final performance")
        print(f"  r = {r_early:+.3f}, p = {p_early:.4f}")
    else:
        print(f"\n→ Early flexibility does not predict final performance")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"supplementary_temporal_{timestamp}.npz"
    np.savez(filename,
             checkpoints=checkpoints,
             flex_histories=all_flex_histories,
             reward_histories=all_reward_histories)
    print(f"\nSaved: {filename}")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
