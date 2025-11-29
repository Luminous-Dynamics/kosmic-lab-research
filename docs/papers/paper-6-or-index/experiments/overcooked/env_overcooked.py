"""
Overcooked MARL Environment Wrapper
Minimal interface for training and trajectory collection
"""

import numpy as np
from overcooked_ai_py.mdp.overcooked_mdp import OvercookedGridworld
from overcooked_ai_py.mdp.overcooked_env import OvercookedEnv


class OvercookedMARLEnv:
    """
    Simple MARL-style wrapper for Overcooked-AI.
    Two agents, joint reward, fixed horizon.
    """

    def __init__(self, layout_name: str, horizon: int = 400):
        self.layout_name = layout_name
        mdp = OvercookedGridworld.from_layout_name(layout_name)
        self.env = OvercookedEnv(mdp, horizon=horizon)
        self.horizon = horizon

        # Cache action space size (Overcooked uses a fixed small discrete set)
        self.n_actions = self.env.mdp.num_actions

        # For O/R computation, we need obs dimension
        dummy_state = self.env.reset()
        self.obs_dim = len(self._obs_from_state(dummy_state))

    def reset(self, seed: int | None = None):
        if seed is not None:
            np.random.seed(seed)
        state = self.env.reset()
        return self._obs_from_state(state)

    def step(self, joint_action):
        """
        joint_action: (2,) array-like of discrete action indices (a0, a1)
        Returns: obs, reward, done, info
        """
        a0, a1 = int(joint_action[0]), int(joint_action[1])
        next_state, reward, done, info = self.env.step((a0, a1))
        obs = self._obs_from_state(next_state)

        # Info can be extended later with collisions/drops if available
        if not isinstance(info, dict):
            info = {}
        info.setdefault("reward", reward)
        info.setdefault("done", done)

        return obs, reward, done, info

    def _obs_from_state(self, state):
        """
        Simple representation: concatenate agent-centric encodings for both agents.
        This gives you a fixed-length vector per timestep you can feed into PCA/binning.
        """
        mdp = self.env.mdp
        s0 = mdp.lossless_state_encoding(state, 0)
        s1 = mdp.lossless_state_encoding(state, 1)
        return np.concatenate([s0, s1], axis=-1)


if __name__ == "__main__":
    # Test the wrapper
    print("Testing Overcooked MARL wrapper...")

    for layout in ["cramped_room", "asymmetric_advantages"]:
        print(f"\nTesting layout: {layout}")
        env = OvercookedMARLEnv(layout, horizon=400)

        print(f"  Observation dim: {env.obs_dim}")
        print(f"  Action space: {env.n_actions} discrete actions per agent")

        # Run a few steps
        obs = env.reset(seed=42)
        print(f"  Initial obs shape: {obs.shape}")

        total_reward = 0
        for step in range(10):
            actions = np.random.randint(0, env.n_actions, size=2)
            obs, reward, done, info = env.step(actions)
            total_reward += reward

            if done:
                break

        print(f"  Ran {step+1} steps, total reward: {total_reward:.2f}")

    print("\n✓ Wrapper test passed!")
