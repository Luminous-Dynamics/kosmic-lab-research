#!/usr/bin/env python3
"""
Track C: Discovery → Execution Transition

Design a task that transitions from discovery (novel coordination)
to execution (known solution). Track when K-Index stops mattering.

Task: Target changes from random to fixed after transition point.

Run with:
    nix-shell -p python3 python3Packages.numpy python3Packages.scipy --run "python3 -u track_c_discovery_execution.py"
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


class TransitionEnvironment:
    """Environment that transitions from discovery to execution."""

    def __init__(self, n_agents, transition_episode):
        self.n_agents = n_agents
        self.transition_episode = transition_episode
        self.state = np.zeros(10)
        self.target = np.zeros(10)
        self.fixed_target = np.random.randn(10)  # Fixed target after transition
        self.current_episode = 0

    def reset(self):
        self.state = np.random.randn(10) * 0.1

        if self.current_episode < self.transition_episode:
            # Discovery phase: random target each episode
            self.target = np.random.randn(10)
        else:
            # Execution phase: same target every episode
            self.target = self.fixed_target.copy()

        return self.state

    def step(self, actions):
        action_mean = np.mean(actions, axis=0)
        self.state += action_mean * 0.1
        dist = np.linalg.norm(self.state - self.target)
        coord = -np.mean([np.linalg.norm(a - action_mean) for a in actions])
        return self.state, -dist + 0.5 * coord

    def next_episode(self):
        self.current_episode += 1


def train_team(n_agents, transition_episode, n_episodes=80, n_steps=100):
    agents = [Agent(i) for i in range(n_agents)]
    network = Network(n_agents)
    env = TransitionEnvironment(n_agents, transition_episode)

    # Track flexibility and performance in each phase
    discovery_rewards = []
    execution_rewards = []

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

        if ep < transition_episode:
            discovery_rewards.append(total_reward)
        else:
            execution_rewards.append(total_reward)

        env.next_episode()

    # Final flexibility measurement
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

    flexibility = np.mean([a.get_flexibility() for a in agents])

    discovery_perf = np.mean(discovery_rewards[-10:]) if discovery_rewards else 0
    execution_perf = np.mean(execution_rewards[-10:]) if execution_rewards else 0

    return flexibility, discovery_perf, execution_perf


def main():
    print("\n" + "=" * 70)
    print("TRACK C: DISCOVERY → EXECUTION TRANSITION")
    print("=" * 70)

    np.random.seed(42)
    n_teams = 20
    n_agents = 4
    transition_episode = 40  # Transition at episode 40 of 80

    print(f"\nTraining {n_teams} teams with transition at episode {transition_episode}")
    print("(Random targets → Fixed target)")

    flexibilities = []
    discovery_perfs = []
    execution_perfs = []

    for t in range(n_teams):
        np.random.seed(t * 1000)
        flex, disc_perf, exec_perf = train_team(n_agents, transition_episode)
        flexibilities.append(flex)
        discovery_perfs.append(disc_perf)
        execution_perfs.append(exec_perf)

        if (t + 1) % 5 == 0:
            print(f"  Trained {t + 1}/{n_teams} teams...")

    flexibilities = np.array(flexibilities)
    discovery_perfs = np.array(discovery_perfs)
    execution_perfs = np.array(execution_perfs)

    # Correlations
    r_disc, p_disc = stats.pearsonr(flexibilities, discovery_perfs)
    r_exec, p_exec = stats.pearsonr(flexibilities, execution_perfs)

    print("\n" + "-" * 70)
    print("RESULTS")
    print("-" * 70)

    sig_disc = '***' if p_disc < 0.001 else '**' if p_disc < 0.01 else '*' if p_disc < 0.05 else ''
    sig_exec = '***' if p_exec < 0.001 else '**' if p_exec < 0.01 else '*' if p_exec < 0.05 else ''

    print(f"\nDiscovery Phase (random targets):")
    print(f"  r = {r_disc:+.3f}{sig_disc}, p = {p_disc:.4f}")

    print(f"\nExecution Phase (fixed target):")
    print(f"  r = {r_exec:+.3f}{sig_exec}, p = {p_exec:.4f}")

    # Conclusion
    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    if r_disc > r_exec and p_disc < 0.05:
        print(f"\n✓ DISCOVERY vs EXECUTION CONFIRMED!")
        print(f"  Discovery: r = {r_disc:+.3f}{sig_disc}")
        print(f"  Execution: r = {r_exec:+.3f}{sig_exec}")
        print("\n  Flexibility matters MORE in discovery phase")
        print("  Effect diminishes when solution becomes known")
    elif p_disc < 0.05 and p_exec < 0.05:
        print(f"\n→ Flexibility matters in BOTH phases")
        print(f"  Discovery: r = {r_disc:+.3f}, Execution: r = {r_exec:+.3f}")
    elif p_disc < 0.05:
        print(f"\n✓ Flexibility matters ONLY in discovery")
        print(f"  Discovery: r = {r_disc:+.3f}{sig_disc}")
        print(f"  Execution: r = {r_exec:+.3f} (not significant)")
    else:
        print(f"\n→ Neither phase shows significant correlation")

    # Theoretical interpretation
    print("\nTheoretical interpretation:")
    if r_disc > 0.3 and r_exec < 0.2:
        print("  Strong support for: Flexibility = adaptability for discovery")
        print("  Once solution known, flexibility becomes irrelevant")
    elif r_disc > r_exec:
        print("  Partial support: Flexibility more important during discovery")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"track_c_transition_{timestamp}.npz"
    np.savez(filename,
             flexibilities=flexibilities,
             discovery_perfs=discovery_perfs,
             execution_perfs=execution_perfs)
    print(f"\nSaved: {filename}")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
