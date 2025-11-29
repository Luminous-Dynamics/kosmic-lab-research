#!/usr/bin/env python3
"""
K_M (Temporal Depth) Validation Environment for Paper 9.

A POMDP where memory is ESSENTIAL for success:
- Agent sees a "hint" at t=0 indicating which action to take at t=T
- The hint disappears after t=0
- Only agents with memory can remember the hint and act correctly

This creates maximal separation between feedforward (K_M ~ 0) and recurrent (K_M > 0) agents.
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Dict, Any


@dataclass
class DelayedHintEnvironment:
    """
    Environment that tests temporal depth (K_M).

    At t=0: Shows hint in observation (e.g., target direction)
    At t>0: Hint is hidden, agent must remember it
    At t=T: Agent must act based on remembered hint

    Feedforward agents cannot solve this (no memory).
    Recurrent agents should show higher K_M.
    """

    obs_dim: int = 8
    action_dim: int = 4
    hint_delay: int = 10  # How many steps before hint matters
    episode_length: int = 20

    def __post_init__(self):
        self.t = 0
        self.hint = None
        self.max_steps = self.episode_length

    def reset(self) -> np.ndarray:
        """Reset environment and show hint."""
        self.t = 0
        # Random hint: which action to take at t=hint_delay
        self.hint = np.random.randint(0, self.action_dim)

        # Observation at t=0: hint is visible
        obs = np.zeros(self.obs_dim)
        obs[self.hint] = 1.0  # One-hot encode the hint
        obs[-1] = 0.0  # Time indicator: start

        return obs

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """Take a step in the environment."""
        self.t += 1

        # Observation at t>0: hint is hidden
        obs = np.zeros(self.obs_dim)
        obs[-1] = self.t / self.episode_length  # Time indicator

        # Reward only given at critical moment
        reward = 0.0
        if self.t == self.hint_delay:
            # Agent must select the remembered action
            selected_action = np.argmax(action)
            if selected_action == self.hint:
                reward = 10.0  # Large reward for remembering correctly
            else:
                reward = -1.0  # Penalty for wrong action

        done = self.t >= self.episode_length

        info = {
            "hint": self.hint,
            "t": self.t,
            "correct_action": self.hint,
            "selected_action": np.argmax(action),
        }

        return obs, reward, done, info


@dataclass
class SequenceRecallEnvironment:
    """
    Harder K_M test: Remember a SEQUENCE of hints.

    At t=0,1,2: Shows hints h0, h1, h2
    At t=10,11,12: Must output h0, h1, h2 in order

    Requires not just memory but sequential memory retrieval.
    """

    obs_dim: int = 8
    action_dim: int = 4
    sequence_length: int = 3
    recall_delay: int = 8

    def __post_init__(self):
        self.t = 0
        self.sequence = []
        self.max_steps = self.sequence_length + self.recall_delay + self.sequence_length

    def reset(self) -> np.ndarray:
        """Reset and show first hint."""
        self.t = 0
        self.sequence = [np.random.randint(0, self.action_dim) for _ in range(self.sequence_length)]
        self.recall_idx = 0

        obs = np.zeros(self.obs_dim)
        obs[self.sequence[0]] = 1.0  # Show first hint
        obs[-1] = 0.0
        obs[-2] = 1.0  # Phase indicator: showing hints

        return obs

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """Take a step."""
        self.t += 1
        obs = np.zeros(self.obs_dim)
        obs[-1] = self.t / self.max_steps

        reward = 0.0
        phase = "idle"

        if self.t < self.sequence_length:
            # Still showing hints
            obs[self.sequence[self.t]] = 1.0
            obs[-2] = 1.0  # Phase: showing
            phase = "showing"

        elif self.t >= self.sequence_length + self.recall_delay:
            # Recall phase
            recall_idx = self.t - self.sequence_length - self.recall_delay
            if recall_idx < self.sequence_length:
                obs[-2] = -1.0  # Phase: recall
                phase = "recall"

                # Check if action matches expected sequence
                selected = np.argmax(action)
                if selected == self.sequence[recall_idx]:
                    reward = 10.0 / self.sequence_length
                else:
                    reward = -1.0 / self.sequence_length
        else:
            # Delay phase - no hints visible
            obs[-2] = 0.0  # Phase: waiting
            phase = "waiting"

        done = self.t >= self.max_steps

        return obs, reward, done, {
            "phase": phase,
            "t": self.t,
            "sequence": self.sequence,
        }


def test_km_environments():
    """Test both K_M validation environments."""

    print("=" * 60)
    print("🧠 K_M VALIDATION ENVIRONMENT TEST")
    print("=" * 60)

    # Test DelayedHint
    print("\n📊 Testing DelayedHintEnvironment...")
    env = DelayedHintEnvironment()

    # Random agent (should fail)
    total_reward_random = 0
    for _ in range(10):
        obs = env.reset()
        done = False
        while not done:
            action = np.random.randn(env.action_dim)
            obs, reward, done, info = env.step(action)
            total_reward_random += reward
    print(f"  Random agent avg reward: {total_reward_random/10:.2f}")

    # "Oracle" agent that remembers (simulated)
    total_reward_oracle = 0
    for _ in range(10):
        obs = env.reset()
        remembered_hint = np.argmax(obs[:env.action_dim])  # Remember hint from t=0
        done = False
        while not done:
            action = np.zeros(env.action_dim)
            action[remembered_hint] = 1.0  # Always output remembered hint
            obs, reward, done, info = env.step(action)
            total_reward_oracle += reward
    print(f"  Oracle agent avg reward: {total_reward_oracle/10:.2f}")

    # Test SequenceRecall
    print("\n📊 Testing SequenceRecallEnvironment...")
    env2 = SequenceRecallEnvironment()

    # Random agent
    total_random = 0
    for _ in range(10):
        obs = env2.reset()
        done = False
        while not done:
            action = np.random.randn(env2.action_dim)
            obs, reward, done, info = env2.step(action)
            total_random += reward
    print(f"  Random agent avg reward: {total_random/10:.2f}")

    print("\n" + "=" * 60)
    print("✅ K_M environments ready for validation!")
    print("=" * 60)
    print("\nKey insight: Feedforward agents cannot solve these tasks")
    print("because they have no memory. Only recurrent agents with")
    print("true temporal depth (K_M > 0) can succeed.")


if __name__ == "__main__":
    test_km_environments()
