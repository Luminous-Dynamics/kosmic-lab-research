#!/usr/bin/env python3
"""Test SC2 parsing fix on a single replay"""

import sys
from pathlib import Path

# Import the fixed parsing functions
from parse_sc2_replays_simple import parse_replay_metadata, process_replay

def test_single_replay():
    """Test parsing on first available replay"""
    replay_dir = Path("data/Replays")
    replays = list(replay_dir.glob("*.SC2Replay"))

    if not replays:
        print("❌ No replays found!")
        return False

    test_replay = replays[0]
    print(f"Testing with: {test_replay.name}")
    print()

    # Test 1: Parse metadata
    print("Test 1: parse_replay_metadata...")
    try:
        metadata = parse_replay_metadata(test_replay)
        if metadata is None:
            print("  ❌ Returned None")
            return False
        print(f"  ✅ Duration: {metadata['duration']}s")
        print(f"  ✅ Map: {metadata['map_name']}")
        print(f"  ✅ Players: {len(metadata['players'])}")
        for i, p in enumerate(metadata['players'], 1):
            print(f"    Player {i}: {p['name']} ({p['race']}) - APM: {p['apm']}")
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 2: Process full replay
    print()
    print("Test 2: process_replay...")
    try:
        metrics = process_replay(test_replay)
        if metrics is None:
            print("  ❌ Returned None")
            return False
        print(f"  ✅ O: {metrics.observation_consistency:.3f}")
        print(f"  ✅ R: {metrics.reward_consistency:.3f}")
        print(f"  ✅ O/R: {metrics.or_index:.3f}")
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

    print()
    print("✅ All tests passed!")
    return True

if __name__ == "__main__":
    success = test_single_replay()
    sys.exit(0 if success else 1)
