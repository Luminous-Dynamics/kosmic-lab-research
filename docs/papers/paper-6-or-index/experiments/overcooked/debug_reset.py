"""Debug script to understand OvercookedEnv.reset() behavior"""

from overcooked_ai_py.mdp.overcooked_mdp import OvercookedGridworld
from overcooked_ai_py.mdp.overcooked_env import OvercookedEnv

# Create environment
mdp = OvercookedGridworld.from_layout_name("cramped_room")
env = OvercookedEnv.from_mdp(mdp, horizon=400)

print("Created environment")
print(f"Environment type: {type(env)}")
print(f"Environment attributes: {dir(env)}")

# Call reset
print("\nCalling env.reset()...")
result = env.reset()

print(f"Result type: {type(result)}")
print(f"Result value: {result}")

if isinstance(result, tuple):
    print(f"Tuple length: {len(result)}")
    for i, item in enumerate(result):
        print(f"  Item {i}: type={type(item)}, value={item}")
else:
    print(f"Not a tuple, direct value")

print("\nChecking if result has state attribute...")
if hasattr(result, 'state'):
    print(f"Has state attribute: {result.state}")
    print(f"State type: {type(result.state)}")
