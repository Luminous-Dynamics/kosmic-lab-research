#!/usr/bin/env python3
"""Extract final metrics from all GPU training logs"""

import re
from pathlib import Path

def extract_metrics(log_file):
    """Extract key metrics from a training log"""
    with open(log_file) as f:
        lines = f.readlines()
    
    # Find final episode line (Episode 999)
    final_line = None
    for line in reversed(lines):
        if "Episode  999" in line or "Episode 999" in line:
            final_line = line
            break
    
    if not final_line:
        return None
    
    # Extract metrics using regex
    metrics = {}
    
    # Episode number
    match = re.search(r'Episode\s+(\d+)', final_line)
    if match:
        metrics['episode'] = int(match.group(1))
    
    # Steps
    match = re.search(r'Steps:\s+(\d+)', final_line)
    if match:
        metrics['steps'] = int(match.group(1))
    
    # Mean Reward
    match = re.search(r'Mean Reward:\s+(-?\d+\.\d+)', final_line)
    if match:
        metrics['mean_reward'] = float(match.group(1))
    
    # Alpha (SAC only)
    match = re.search(r'Alpha:\s+(\d+\.\d+)', final_line)
    if match:
        metrics['alpha'] = float(match.group(1))
    
    return metrics

# Process all log files
algorithms = ['sac', 'mappo']
seeds = [42, 123, 456]

print("=== GPU Training Results Summary ===\n")

for algo in algorithms:
    print(f"\n{algo.upper()} Results:")
    print("-" * 60)
    
    rewards = []
    for seed in seeds:
        log_file = f"logs/{algo}_gpu_seed_{seed}.log"
        metrics = extract_metrics(log_file)
        
        if metrics:
            print(f"Seed {seed:3d}: Final Reward = {metrics['mean_reward']:7.2f} | "
                  f"Steps = {metrics['steps']:5d}", end="")
            if 'alpha' in metrics:
                print(f" | Alpha = {metrics['alpha']:.2f}")
            else:
                print()
            rewards.append(metrics['mean_reward'])
        else:
            print(f"Seed {seed:3d}: ERROR - Could not extract metrics")
    
    if rewards:
        print(f"\nMean ± Std: {sum(rewards)/len(rewards):.2f} ± {(max(rewards)-min(rewards))/2:.2f}")
        print(f"Range: [{min(rewards):.2f}, {max(rewards):.2f}]")

print("\n" + "=" * 60)
print("\nCheckpoint Summary:")
print(f"  - 10 episode checkpoints (100, 200, ..., 1000)")
print(f"  - 3 agents per checkpoint")
print(f"  - Total: 30 checkpoint files (.pt)")
print(f"  - Final checkpoints: ~3.2 MB each")

