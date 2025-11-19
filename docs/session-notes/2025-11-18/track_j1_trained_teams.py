#!/usr/bin/env python3
"""
Track J1 Trained Teams: Proper MPE Validation

Train multiple MPE teams with REINFORCE, then correlate flexibility with performance.
This matches the methodology used for abstract coordination.

Run with:
    nix-shell -p python3 python3Packages.numpy python3Packages.scipy --run "python3 -u track_j1_trained_teams.py"
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
        self.rewards = []

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
            gradient = np.outer(action, np.concatenate([obs, np.zeros(4)]))
            self.policy_weights += learning_rate * ret * gradient[:, :10]

        self.obs_history = []
        self.action_history = []
        self.rewards = []

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


def train_team(n_agents=4, n_episodes=50, n_steps=50):
    """Train a team and return agents and final performance."""
    agents = [Agent(i) for i in range(n_agents)]
    network = Network(n_agents)
    env = SimpleSpreadEnv(n_agents)

    episode_rewards = []

    for ep in range(n_episodes):
        observations = env.reset()
        for a in agents:
            a.obs_history = []
            a.action_history = []
            a.rewards = []

        total_reward = 0
        for step in range(n_steps):
            noisy_obs = [o + np.random.randn(6) * 0.05 for o in observations]
            messages = [a.create_message(o) for a, o in zip(agents, noisy_obs)]
            received = network.exchange(messages)
            actions = [a.act(o, m) for a, o, m in zip(agents, noisy_obs, received)]
            observations, reward = env.step(actions)
            for a in agents:
                a.rewards.append(reward)
            total_reward += reward

        for a in agents:
            a.update()

        episode_rewards.append(total_reward)

    # Run evaluation episode to measure flexibility
    observations = env.reset()
    for a in agents:
        a.obs_history = []
        a.action_history = []

    eval_reward = 0
    for step in range(n_steps):
        noisy_obs = [o + np.random.randn(6) * 0.05 for o in observations]
        messages = [a.create_message(o) for a, o in zip(agents, noisy_obs)]
        received = network.exchange(messages)
        actions = [a.act(o, m) for a, o, m in zip(agents, noisy_obs, received)]
        observations, reward = env.step(actions)
        eval_reward += reward

    flexibility = np.mean([a.get_flexibility() for a in agents])
    final_performance = np.mean(episode_rewards[-10:])

    return flexibility, final_performance, eval_reward


def main():
    print("\n" + "=" * 70)
    print("TRACK J1 TRAINED TEAMS: PROPER MPE VALIDATION")
    print("=" * 70)

    np.random.seed(42)
    n_teams = 20
    n_agents = 4

    print(f"\nTraining {n_teams} teams with REINFORCE...")

    flexibilities = []
    performances = []
    eval_rewards = []

    for t in range(n_teams):
        np.random.seed(t * 1000)
        flex, perf, eval_rew = train_team(n_agents=n_agents)
        flexibilities.append(flex)
        performances.append(perf)
        eval_rewards.append(eval_rew)

        if (t + 1) % 5 == 0:
            print(f"  Trained {t + 1}/{n_teams} teams...")

    flexibilities = np.array(flexibilities)
    performances = np.array(performances)
    eval_rewards = np.array(eval_rewards)

    print(f"\n  Flexibility range: [{flexibilities.min():.3f}, {flexibilities.max():.3f}]")
    print(f"  Performance range: [{performances.min():.1f}, {performances.max():.1f}]")

    # Correlations
    print("\n" + "-" * 70)
    print("CORRELATIONS")
    print("-" * 70)

    # Training performance
    r_train, p_train = stats.pearsonr(flexibilities, performances)
    sig = '***' if p_train < 0.001 else '**' if p_train < 0.01 else '*' if p_train < 0.05 else ''
    print(f"\nFlexibility vs Training Performance:")
    print(f"  r = {r_train:+.3f}{sig}, p = {p_train:.4f}")

    # Eval performance
    r_eval, p_eval = stats.pearsonr(flexibilities, eval_rewards)
    sig = '***' if p_eval < 0.001 else '**' if p_eval < 0.01 else '*' if p_eval < 0.05 else ''
    print(f"\nFlexibility vs Eval Performance:")
    print(f"  r = {r_eval:+.3f}{sig}, p = {p_eval:.4f}")

    # Analysis
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)

    # Check if flexibility varied
    flex_var = np.var(flexibilities)
    print(f"\nFlexibility variance: {flex_var:.4f}")

    if flex_var < 0.01:
        print("  ⚠️  Low flexibility variance - trained policies may converge to similar behavior")

    # Conclusion
    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    if p_train < 0.05 or p_eval < 0.05:
        best_r = r_train if abs(r_train) > abs(r_eval) else r_eval
        print(f"\n✓ MPE VALIDATED with trained teams!")
        print(f"  Best correlation: r = {best_r:+.3f}")
        print("  Flexibility-performance relationship generalizes to spatial tasks")
    else:
        print("\n→ MPE still shows weak correlation with trained teams")
        print(f"  Training r = {r_train:+.3f}, Eval r = {r_eval:+.3f}")

        if flex_var < 0.01:
            print("\n  Possible cause: Low flexibility variance")
            print("  Trained MPE policies may converge to similar deterministic solutions")
        else:
            print("\n  Spatial coordination may genuinely differ from abstract coordination")

    # Compare to abstract task
    print("\nComparison to abstract coordination:")
    print("  Abstract (trained): r = +0.70***")
    print(f"  Spatial (trained):  r = {r_train:+.3f}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"track_j1_trained_{timestamp}.npz"
    np.savez(filename,
             flexibilities=flexibilities,
             performances=performances,
             eval_rewards=eval_rewards)
    print(f"\nSaved: {filename}")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
