"""
Overcooked MARL Environment Wrapper
Minimal interface for training and trajectory collection
"""

import numpy as np
from overcooked_ai_py.mdp.overcooked_mdp import OvercookedGridworld, Action
from overcooked_ai_py.mdp.overcooked_env import OvercookedEnv


class OvercookedMARLEnv:
    """
    Simple MARL-style wrapper for Overcooked-AI.
    Two agents, joint reward, fixed horizon.
    """

    def __init__(self, layout_name: str, horizon: int = 400, use_motion_planner: bool = True, randomize_positions: bool = False):
        self.layout_name = layout_name
        self.use_motion_planner = use_motion_planner
        self.randomize_positions = randomize_positions

        # Create MDP
        self.mdp = OvercookedGridworld.from_layout_name(layout_name)

        # Optionally disable MotionPlanner (speeds up initialization 100x)
        if not use_motion_planner:
            # Monkey-patch to skip expensive MotionPlanner computation
            # This is safe for policy learning (we don't need optimal planning heuristics)
            self.mdp.motion_planner = None

        self.env = OvercookedEnv.from_mdp(self.mdp, horizon=horizon)
        self.horizon = horizon

        # Pre-compute valid floor positions for randomization if needed
        if self.randomize_positions:
            self._valid_positions = self._get_valid_positions()

        # Cache action space size (Overcooked uses a fixed small discrete set)
        self.n_actions = Action.NUM_ACTIONS

        # For O/R computation, we need obs dimension
        # Get obs dim from the standard start state
        standard_start_state = self.mdp.get_standard_start_state()
        s0 = np.array(self.mdp.lossless_state_encoding(standard_start_state, 0))
        s1 = np.array(self.mdp.lossless_state_encoding(standard_start_state, 1))
        # Flatten before concatenating (lossless_state_encoding returns multi-dimensional arrays/tuples)
        self.obs_dim = len(np.concatenate([s0.flatten(), s1.flatten()]))

    def reset(self, seed: int | None = None):
        if seed is not None:
            np.random.seed(seed)
        # OvercookedEnv.reset() returns None and stores state in self.env.state
        self.env.reset()
        # Get state - either from self.env.state or manually from mdp
        state = self.env.state if self.env.state is not None else self.mdp.get_standard_start_state()

        # Randomize agent positions if enabled (many-agent simulation)
        if self.randomize_positions:
            state = self._randomize_agent_positions(state)
            self.env.state = state

        return self._obs_from_state(state)

    def step(self, joint_action):
        """
        joint_action: (2,) array-like of discrete action indices (a0, a1)
        Returns: obs, reward, done, info
        """
        # Convert action indices to Overcooked Action tuples
        a0_idx, a1_idx = int(joint_action[0]), int(joint_action[1])
        a0_tuple = Action.ALL_ACTIONS[a0_idx]
        a1_tuple = Action.ALL_ACTIONS[a1_idx]
        next_state, reward, done, info = self.env.step((a0_tuple, a1_tuple))
        obs = self._obs_from_state(next_state)

        # Info can be extended later with collisions/drops if available
        if not isinstance(info, dict):
            info = {}
        info.setdefault("reward", reward)
        info.setdefault("done", done)

        return obs, reward, done, info

    def _get_valid_positions(self):
        """
        Get all valid (empty floor) positions in the kitchen where agents can be placed.
        Returns list of (x, y) tuples.
        """
        valid_positions = []
        terrain = self.mdp.terrain_mtx
        for y in range(len(terrain)):
            for x in range(len(terrain[0])):
                if terrain[y][x] == ' ':  # Empty floor tile
                    valid_positions.append((x, y))
        return valid_positions

    def _randomize_agent_positions(self, state):
        """
        Randomize agent starting positions to simulate many-agent coordination complexity.
        Randomly places both agents on valid floor tiles.
        """
        # Sample 2 different random positions for the agents
        positions = np.random.choice(len(self._valid_positions), size=2, replace=False)
        pos0 = self._valid_positions[positions[0]]
        pos1 = self._valid_positions[positions[1]]

        # Create new state with randomized positions
        # Overcooked state has .players attribute which is a tuple of PlayerState objects
        from overcooked_ai_py.mdp.overcooked_mdp import PlayerState, OvercookedState

        # Get current player orientations and held objects (keep these)
        old_players = state.players
        orientation0 = old_players[0].orientation if hasattr(old_players[0], 'orientation') else (0, -1)
        orientation1 = old_players[1].orientation if hasattr(old_players[1], 'orientation') else (0, -1)
        held0 = old_players[0].held_object if hasattr(old_players[0], 'held_object') else None
        held1 = old_players[1].held_object if hasattr(old_players[1], 'held_object') else None

        # Create new player states with randomized positions
        player0 = PlayerState(pos0, orientation0, held0)
        player1 = PlayerState(pos1, orientation1, held1)

        # Create new state with randomized players
        new_state = OvercookedState(
            players=(player0, player1),
            objects=state.objects,
            order_list=state.order_list if hasattr(state, 'order_list') else None
        )

        return new_state

    def _obs_from_state(self, state):
        """
        Simple representation: concatenate agent-centric encodings for both agents.
        This gives you a fixed-length vector per timestep you can feed into PCA/binning.
        """
        mdp = self.env.mdp
        s0 = np.array(mdp.lossless_state_encoding(state, 0))
        s1 = np.array(mdp.lossless_state_encoding(state, 1))
        # Flatten and concatenate (lossless_state_encoding returns multi-dimensional arrays/tuples)
        return np.concatenate([s0.flatten(), s1.flatten()])


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
