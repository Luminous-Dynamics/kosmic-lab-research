#!/usr/bin/env python3
"""Quick test to investigate action_space structure in Multi-Agent MuJoCo."""

from multiagent_mujoco.mujoco_multi import MujocoMulti

# Create environment using same method as trainer
env_args = {
    "scenario": "Ant-v2",
    "agent_conf": "2x4",
    "agent_obsk": 1,
    "episode_limit": 1000,
}
env = MujocoMulti(env_args=env_args)

# Get sample observation and action
sample_obs = env.reset()
print(f"\n=== Environment Investigation ===")
print(f"sample_obs type: {type(sample_obs)}")
print(f"sample_obs length: {len(sample_obs) if isinstance(sample_obs, (list, tuple)) else 'N/A'}")
if isinstance(sample_obs, list):
    print(f"sample_obs[0] shape: {sample_obs[0].shape}")

print(f"\n=== Action Space Investigation ===")
print(f"action_space type: {type(env.action_space)}")
print(f"action_space: {env.action_space}")

if isinstance(env.action_space, tuple):
    print(f"action_space length: {len(env.action_space)}")
    print(f"action_space[0] type: {type(env.action_space[0])}")
    print(f"action_space[0]: {env.action_space[0]}")
    if hasattr(env.action_space[0], 'shape'):
        print(f"action_space[0].shape: {env.action_space[0].shape}")
    elif hasattr(env.action_space[0], 'n'):
        print(f"action_space[0].n (discrete): {env.action_space[0].n}")

if isinstance(env.action_space, list):
    print(f"action_space length: {len(env.action_space)}")
    print(f"action_space[0] type: {type(env.action_space[0])}")
    if hasattr(env.action_space[0], 'shape'):
        print(f"action_space[0].shape: {env.action_space[0].shape}")

# Try taking a random action to see what format is expected
print(f"\n=== Sample Action ===")
sample_actions = [env.action_space[i].sample() for i in range(len(env.action_space))]
print(f"sample_actions type: {type(sample_actions)}")
print(f"sample_actions length: {len(sample_actions)}")
print(f"sample_actions[0] type: {type(sample_actions[0])}")
print(f"sample_actions[0] shape: {sample_actions[0].shape}")

# Test what env.step() returns
print(f"\n=== env.step() Return Values ===")
step_result = env.step(sample_actions)
print(f"step_result type: {type(step_result)}")
print(f"step_result length: {len(step_result)}")
for i, item in enumerate(step_result):
    print(f"step_result[{i}] type: {type(item)}")
    if isinstance(item, (list, tuple)):
        print(f"  length: {len(item)}")
        if len(item) > 0:
            print(f"  item[0] type: {type(item[0])}")
            if hasattr(item[0], 'shape'):
                print(f"  item[0] shape: {item[0].shape}")
    elif isinstance(item, dict):
        print(f"  dict keys: {list(item.keys())}")

# Try to unpack as (reward, done, info)
reward, done, info = step_result
print(f"\n=== Correct Unpacking: (reward, done, info) ===")
print(f"reward: {reward}")
print(f"done: {done}")
print(f"info keys: {list(info.keys())}")

# Check if env has methods to get observations
print(f"\n=== Check for observation methods ===")
if hasattr(env, 'get_obs'):
    print("env.get_obs() exists!")
    obs = env.get_obs()
    print(f"obs type: {type(obs)}")
    if isinstance(obs, list):
        print(f"obs length: {len(obs)}, obs[0] shape: {obs[0].shape}")
elif hasattr(env, 'get_agent_obs'):
    print("env.get_agent_obs() exists!")
else:
    print("No obvious observation getter method")
    print(f"Available methods: {[m for m in dir(env) if not m.startswith('_') and callable(getattr(env, m))][:20]}")

# Don't call close() since it raises NotImplementedError
