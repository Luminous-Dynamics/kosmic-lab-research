#!/usr/bin/env python3
"""
Simplified SC2 Replay Parser for O/R Index Computation

This parser extracts high-level metrics from StarCraft II replays without
requiring full PySC2 integration. It uses the replay metadata and basic
analysis to compute O/R metrics.

Approach:
1. Parse replay metadata (duration, winner, APM, etc.)
2. Compute action consistency metrics from replay structure
3. Compute O/R Index as a measure of player behavioral consistency
4. Correlate with game outcomes

Note: This is a simplified approach that treats the player's macro-level
decisions as "observations" and individual unit commands as "actions."
"""

import os
import json
import numpy as np
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple
import struct
import hashlib
from collections import defaultdict
import random

# Try to import sc2reader (fallback if PySC2 not available)
try:
    import sc2reader
    SC2READER_AVAILABLE = True
except ImportError:
    SC2READER_AVAILABLE = False
    print("⚠️  sc2reader not available. Install with: pip install sc2reader")


@dataclass
class ReplayMetrics:
    """Metrics extracted from a single replay"""
    replay_id: str
    duration_seconds: float
    winner: int  # 1 or 2
    player1_apm: float
    player2_apm: float
    player1_race: str
    player2_race: str
    map_name: str
    # O/R metrics (will be computed)
    observation_consistency: float = 0.0
    reward_consistency: float = 0.0
    or_index: float = 0.0
    # Additional features
    action_diversity: float = 0.0
    temporal_consistency: float = 0.0


def parse_replay_metadata(replay_path: Path) -> Dict:
    """
    Parse SC2 replay using sc2reader library.

    Returns:
        Dictionary with replay metadata and event streams
    """
    if not SC2READER_AVAILABLE:
        raise ImportError("sc2reader required for replay parsing")

    try:
        replay = sc2reader.load_replay(str(replay_path), load_level=4)

        # Extract basic metadata
        metadata = {
            'duration': replay.game_length.total_seconds(),
            'map_name': replay.map_name,
            'game_type': replay.game_type,
            'players': [],
            'events': [],
        }

        # Extract player info
        for player in replay.players:
            metadata['players'].append({
                'name': player.name,
                'pid': player.pid,
                'race': player.play_race,
                'result': player.result,
                'apm': player.apm,
                'avg_resource_collection_rate': getattr(player, 'avg_resource_collection_rate', 0),
            })

        # Extract events for temporal analysis
        # Sample events to avoid memory issues
        events = replay.events
        if len(events) > 10000:
            # Sample 10000 events uniformly
            step = len(events) // 10000
            events = events[::step]

        for event in events:
            if hasattr(event, 'player') and event.player:
                metadata['events'].append({
                    'frame': event.frame,
                    'second': event.second,
                    'player_id': event.player.pid,
                    'event_type': event.name,
                })

        return metadata

    except Exception as e:
        print(f"  ⚠️  Error parsing {replay_path.name}: {e}")
        return None


def compute_observation_consistency(events: List[Dict], player_id: int) -> float:
    """
    Compute observation consistency for a player.

    Observation consistency measures how similar the player's decision contexts
    are over time. We approximate this by:
    1. Grouping events into time windows
    2. Computing action distributions within each window
    3. Measuring variance in these distributions

    Returns:
        O: Observation consistency (0-1, higher = more consistent)
    """
    if not events:
        return 0.0

    # Filter events for this player
    player_events = [e for e in events if e['player_id'] == player_id]

    if len(player_events) < 10:
        return 0.0

    # Group events into 10-second windows
    window_size = 10  # seconds
    max_time = max(e['second'] for e in player_events)
    num_windows = int(max_time / window_size) + 1

    # Count event types per window
    window_distributions = []
    for i in range(num_windows):
        window_start = i * window_size
        window_end = (i + 1) * window_size

        window_events = [e for e in player_events
                        if window_start <= e['second'] < window_end]

        if window_events:
            # Count event types
            event_counts = defaultdict(int)
            for e in window_events:
                event_counts[e['event_type']] += 1

            # Normalize to distribution
            total = sum(event_counts.values())
            distribution = {k: v/total for k, v in event_counts.items()}
            window_distributions.append(distribution)

    if len(window_distributions) < 2:
        return 0.0

    # Compute variance across windows
    # Get all unique event types
    all_event_types = set()
    for dist in window_distributions:
        all_event_types.update(dist.keys())

    # Compute variance for each event type
    variances = []
    for event_type in all_event_types:
        probs = [dist.get(event_type, 0.0) for dist in window_distributions]
        variances.append(np.var(probs))

    # Average variance
    avg_variance = np.mean(variances) if variances else 0.0

    # Convert to consistency (1 - normalized variance)
    # Higher variance → lower consistency
    consistency = max(0.0, 1.0 - avg_variance * 10)  # Scale factor

    return consistency


def compute_reward_consistency(events: List[Dict], player_id: int, outcome: int) -> float:
    """
    Compute reward consistency for a player.

    Reward consistency measures how consistent the player's actions are
    with respect to the final outcome. We approximate this by:
    1. Looking at action patterns throughout the game
    2. Measuring how consistent they remain as the game progresses

    Returns:
        R: Reward consistency (0-1, higher = more consistent)
    """
    if not events:
        return 0.0

    # Filter events for this player
    player_events = [e for e in events if e['player_id'] == player_id]

    if len(player_events) < 10:
        return 0.0

    # Split game into early, mid, late phases
    max_time = max(e['second'] for e in player_events)
    phases = {
        'early': (0, max_time / 3),
        'mid': (max_time / 3, 2 * max_time / 3),
        'late': (2 * max_time / 3, max_time),
    }

    # Compute action distributions for each phase
    phase_distributions = {}
    for phase_name, (start, end) in phases.items():
        phase_events = [e for e in player_events
                       if start <= e['second'] < end]

        if phase_events:
            event_counts = defaultdict(int)
            for e in phase_events:
                event_counts[e['event_type']] += 1

            total = sum(event_counts.values())
            distribution = {k: v/total for k, v in event_counts.items()}
            phase_distributions[phase_name] = distribution

    if len(phase_distributions) < 2:
        return 0.0

    # Compute similarity between phases
    # Higher similarity → higher reward consistency
    all_event_types = set()
    for dist in phase_distributions.values():
        all_event_types.update(dist.keys())

    # Compute KL divergence between consecutive phases
    phases_list = ['early', 'mid', 'late']
    kl_divs = []

    for i in range(len(phases_list) - 1):
        if phases_list[i] in phase_distributions and phases_list[i+1] in phase_distributions:
            p = phase_distributions[phases_list[i]]
            q = phase_distributions[phases_list[i+1]]

            # Compute KL divergence
            kl = 0.0
            for event_type in all_event_types:
                p_val = p.get(event_type, 1e-10)
                q_val = q.get(event_type, 1e-10)
                if p_val > 0:
                    kl += p_val * np.log(p_val / q_val)

            kl_divs.append(kl)

    # Convert KL divergence to consistency
    # Lower KL → higher consistency
    avg_kl = np.mean(kl_divs) if kl_divs else 0.0
    consistency = max(0.0, 1.0 - avg_kl)

    return consistency


def compute_or_index(observation_consistency: float, reward_consistency: float) -> float:
    """Compute O/R Index"""
    if reward_consistency < 1e-8:
        return 0.0
    return observation_consistency / reward_consistency


def process_replay(replay_path: Path) -> ReplayMetrics:
    """
    Process a single replay and extract O/R metrics.

    Returns:
        ReplayMetrics object with all computed metrics
    """
    # Parse replay metadata
    metadata = parse_replay_metadata(replay_path)

    if metadata is None:
        return None

    # Extract basic info
    replay_id = replay_path.stem
    duration = metadata['duration']
    map_name = metadata['map_name']

    # Extract player info
    players = metadata['players']
    if len(players) != 2:
        print(f"  ⚠️  Skipping {replay_path.name}: Not a 1v1 game")
        return None

    player1 = players[0]
    player2 = players[1]

    # Determine winner
    winner = 1 if player1['result'] == 'Win' else 2

    # Compute O/R metrics for winner
    winner_id = player1['pid'] if winner == 1 else player2['pid']
    winner_events = metadata['events']

    O = compute_observation_consistency(winner_events, winner_id)
    R = compute_reward_consistency(winner_events, winner_id, winner)
    OR = compute_or_index(O, R)

    # Create metrics object
    metrics = ReplayMetrics(
        replay_id=replay_id,
        duration_seconds=duration,
        winner=winner,
        player1_apm=player1['apm'],
        player2_apm=player2['apm'],
        player1_race=player1['race'],
        player2_race=player2['race'],
        map_name=map_name,
        observation_consistency=O,
        reward_consistency=R,
        or_index=OR,
    )

    return metrics


def main():
    """Main processing pipeline"""
    print("=" * 80)
    print("SC2 Replay Parser for O/R Index Computation")
    print("=" * 80)
    print()

    # Check dependencies
    if not SC2READER_AVAILABLE:
        print("❌ sc2reader not available. Installing...")
        import subprocess
        subprocess.run(["pip", "install", "sc2reader"], check=True)
        print("✅ sc2reader installed. Please re-run the script.")
        return

    # Find replays
    replay_dir = Path("data/Replays")
    if not replay_dir.exists():
        print(f"❌ Replay directory not found: {replay_dir}")
        return

    replay_files = list(replay_dir.glob("*.SC2Replay"))
    print(f"📂 Found {len(replay_files):,} replay files")
    print()

    # Sample replays (process subset for efficiency)
    sample_size = min(1000, len(replay_files))
    sampled_replays = random.sample(replay_files, sample_size)

    print(f"📊 Sampling {sample_size} replays for analysis")
    print()

    # Process replays
    all_metrics = []
    failed_count = 0

    for i, replay_path in enumerate(sampled_replays, 1):
        if i % 100 == 0:
            print(f"  Progress: {i}/{sample_size} ({100*i/sample_size:.1f}%)")

        try:
            metrics = process_replay(replay_path)
            if metrics:
                all_metrics.append(metrics)
        except Exception as e:
            failed_count += 1
            if failed_count < 10:  # Only show first 10 errors
                print(f"  ⚠️  Error processing {replay_path.name}: {e}")

    print()
    print("=" * 80)
    print("Summary Statistics")
    print("=" * 80)
    print()

    if all_metrics:
        O_values = [m.observation_consistency for m in all_metrics]
        R_values = [m.reward_consistency for m in all_metrics]
        OR_values = [m.or_index for m in all_metrics]

        print(f"SC2 Replays (n={len(all_metrics)}):")
        print(f"  O:   {np.mean(O_values):.3f} ± {np.std(O_values):.3f}")
        print(f"  R:   {np.mean(R_values):.3f} ± {np.std(R_values):.3f}")
        print(f"  O/R: {np.mean(OR_values):.3f} ± {np.std(OR_values):.3f}")
        print()
        print(f"✅ Successfully processed: {len(all_metrics)}/{sample_size}")
        print(f"❌ Failed: {failed_count}")
        print()

        # Save results
        results = {
            "dataset": "StarCraft II Ladder Replays (3.16.1-Pack_1)",
            "total_replays": len(replay_files),
            "sampled": sample_size,
            "successfully_parsed": len(all_metrics),
            "metrics": [asdict(m) for m in all_metrics],
            "summary": {
                "n": len(all_metrics),
                "O_mean": float(np.mean(O_values)),
                "O_std": float(np.std(O_values)),
                "R_mean": float(np.mean(R_values)),
                "R_std": float(np.std(R_values)),
                "OR_mean": float(np.mean(OR_values)),
                "OR_std": float(np.std(OR_values)),
            }
        }

        output_file = "sc2_or_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"✅ Results saved to {output_file}")
        print(f"📊 Total measurements: {len(all_metrics)}")
    else:
        print("❌ No replays successfully processed!")

    print()
    print("✅ SC2 replay parsing complete!")


if __name__ == "__main__":
    main()
