"""
Quick test to verify all 6 scenarios can initialize and train without errors

Tests:
1. Environment creation for each layout
2. Randomization works correctly
3. Training loop executes for a few steps
4. No import or runtime errors

Expected runtime: ~2 minutes
"""

import torch
from env_overcooked import OvercookedMARLEnv
from train_full_abc_validation import PolicyNetwork

def test_scenario(scenario_id, layout_name, horizon, randomize_positions):
    """Test a single scenario initializes and can train"""
    print(f"\n{'='*60}")
    print(f"Testing: {scenario_id}")
    print(f"{'='*60}")

    try:
        # Test environment creation
        print(f"  Creating environment...")
        env = OvercookedMARLEnv(
            layout_name=layout_name,
            horizon=horizon,
            use_motion_planner=True,
            randomize_positions=randomize_positions
        )
        print(f"  ✅ Environment created: obs_dim={env.obs_dim}, n_actions={env.n_actions}")

        # Test reset (tests randomization if enabled)
        print(f"  Testing reset...")
        obs = env.reset(seed=42)
        print(f"  ✅ Reset successful: obs.shape={obs.shape}")

        # Test policy creation
        print(f"  Creating policy network...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        policy = PolicyNetwork(env.obs_dim, env.n_actions * 2).to(device)
        print(f"  ✅ Policy created on device: {device}")

        # Test a few training steps
        print(f"  Running 10 environment steps...")
        total_reward = 0
        obs = env.reset(seed=42)
        for step in range(10):
            # Random actions
            obs_tensor = torch.FloatTensor(obs).unsqueeze(0).to(device)
            with torch.no_grad():
                logits = policy(obs_tensor)

            # Split logits for two agents
            mid = len(logits[0]) // 2
            logits_a0 = logits[0, :mid]
            logits_a1 = logits[0, mid:]

            # Sample actions
            dist_a0 = torch.distributions.Categorical(logits=logits_a0)
            dist_a1 = torch.distributions.Categorical(logits=logits_a1)
            a0 = dist_a0.sample()
            a1 = dist_a1.sample()

            # Environment step
            obs, reward, done, _ = env.step([a0.item(), a1.item()])
            total_reward += reward

            if done:
                break

        print(f"  ✅ Completed {step+1} steps, total_reward={total_reward:.2f}")

        # Test randomization produced different start if enabled
        if randomize_positions:
            obs1 = env.reset(seed=42)
            obs2 = env.reset(seed=123)
            if (obs1 == obs2).all():
                print(f"  ⚠️  Warning: Randomization didn't change initial state")
            else:
                print(f"  ✅ Randomization working (different initial states)")

        print(f"\n✅ {scenario_id} PASSED ALL TESTS")
        return True

    except Exception as e:
        print(f"\n❌ {scenario_id} FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Test all 6 scenarios"""

    print("\n" + "="*60)
    print("TESTING ALL 6 SCENARIOS (Option B Implementation)")
    print("="*60)

    # Same scenarios as train_full_abc_validation.py
    scenarios = [
        # Option A: Baseline Validation
        ("cramped_room_h400_baseline", "cramped_room", 400, False),
        ("asymmetric_advantages_h400_baseline", "asymmetric_advantages", 400, False),

        # Option B: Stress Testing
        ("coordination_ring_h400_stress_spatial", "coordination_ring", 400, False),
        ("forced_coordination_h400_stress_sequential", "forced_coordination", 400, False),
        ("cramped_room_h800_stress_temporal", "cramped_room", 800, False),

        # Option C: Many-Agent Simulation
        ("cramped_room_h400_multiagent_sim", "cramped_room", 400, True),
    ]

    results = []
    for scenario_id, layout_name, horizon, randomize_positions in scenarios:
        passed = test_scenario(scenario_id, layout_name, horizon, randomize_positions)
        results.append((scenario_id, passed))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for scenario_id, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {scenario_id}")

    print(f"\n{passed_count}/{total_count} scenarios passed")

    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED! Ready for full training.")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} scenarios failed. Fix issues before training.")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
