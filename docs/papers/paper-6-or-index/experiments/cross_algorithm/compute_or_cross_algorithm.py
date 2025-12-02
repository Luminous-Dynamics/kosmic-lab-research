#!/usr/bin/env python3
"""Cross-Algorithm O/R Index Computation (simplified for pipeline testing)"""

import numpy as np
import json
from dataclasses import dataclass, asdict
from pettingzoo.mpe import simple_spread_v3

@dataclass
class ORMetrics:
    """O/R Index metrics"""
    observation_consistency: float
    reward_consistency: float
    or_index: float
    mean_reward: float
    algorithm: str
    seed: int
    episode: int

def compute_observation_consistency(observations):
    """O = 1 - mean(|| obs[t] - obs[t-1] || / || obs[t] ||)"""
    if len(observations) < 2:
        return 0.0
    
    differences = []
    for t in range(1, len(observations)):
        obs_prev, obs_curr = observations[t-1], observations[t]
        diff_norm = np.linalg.norm(obs_curr - obs_prev)
        obs_norm = np.linalg.norm(obs_curr)
        if obs_norm > 1e-8:
            differences.append(diff_norm / obs_norm)
    
    return max(0.0, 1.0 - np.mean(differences)) if differences else 0.0

def compute_reward_consistency(rewards):
    """R = 1 - (std(rewards) / (|mean(rewards)| + epsilon))"""
    if len(rewards) < 2:
        return 0.0
    
    std_reward = np.std(rewards)
    mean_reward = np.mean(rewards)
    normalized_std = std_reward / (abs(mean_reward) + 1e-8)
    
    return max(0.0, 1.0 - normalized_std)

def evaluate_random_policy(num_episodes=10, seed=42):
    """Evaluate random policy to test O/R computation pipeline"""
    env = simple_spread_v3.parallel_env(N=3, max_cycles=25, continuous_actions=False)
    
    all_observations = []
    all_rewards = []
    
    for ep in range(num_episodes):
        observations_dict, info = env.reset(seed=seed + ep)  # Fixed: unpack tuple
        agents = env.possible_agents
        done = False
        
        while not done:
            # Store concatenated observations
            obs_concat = np.concatenate([observations_dict[agent] for agent in agents])
            all_observations.append(obs_concat)
            
            # Random actions
            actions = {agent: env.action_space(agent).sample() for agent in agents}
            
            observations_dict, rewards_dict, terminations, truncations, _ = env.step(actions)
            
            mean_reward = np.mean([rewards_dict[agent] for agent in agents])
            all_rewards.append(mean_reward)
            
            done = all(terminations.values()) or all(truncations.values())
    
    env.close()
    return all_observations, all_rewards

def main():
    """Test O/R computation with random policies"""
    print("=" * 80)
    print("Cross-Algorithm O/R Index Computation (Pipeline Test)")
    print("=" * 80)
    print("\nNote: Using random policies to test O/R computation.")
    print("Next step: Add actual checkpoint loading.\n")
    
    algorithms = ["DQN", "SAC", "MAPPO"]
    seeds = [42, 123, 456]
    episodes = [100, 500, 1000]
    
    all_metrics = []
    
    for algo in algorithms:
        print(f"\n{algo} (Random Policy Test):")
        print("-" * 80)
        
        for seed in seeds:
            for ep in episodes:
                print(f"  Testing O/R for {algo} seed {seed} episode {ep}...")
                
                observations, rewards = evaluate_random_policy(num_episodes=5, seed=seed)
                
                O = compute_observation_consistency(observations)
                R = compute_reward_consistency(rewards)
                OR = O / (R + 1e-8) if R > 1e-8 else 0.0
                
                metrics = ORMetrics(
                    observation_consistency=O,
                    reward_consistency=R,
                    or_index=OR,
                    mean_reward=np.mean(rewards),
                    algorithm=algo,
                    seed=seed,
                    episode=ep
                )
                
                all_metrics.append(metrics)
                print(f"    O={O:.3f}, R={R:.3f}, O/R={OR:.3f}, Reward={np.mean(rewards):.2f}")
    
    # Save results
    results_file = "or_random_baseline.json"
    results = {
        "metadata": {
            "note": "Random policy baseline for O/R computation testing",
            "algorithms": algorithms,
            "seeds": seeds,
            "episodes": episodes,
            "total_measurements": len(all_metrics)
        },
        "metrics": [asdict(m) for m in all_metrics]
    }
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Baseline results saved to {results_file}")
    print(f"📊 Total measurements: {len(all_metrics)}")
    
    # Summary
    print("\n" + "=" * 80)
    print("Summary (Random Policy Baseline):")
    print("=" * 80)
    
    all_O = [m.observation_consistency for m in all_metrics]
    all_R = [m.reward_consistency for m in all_metrics]
    all_OR = [m.or_index for m in all_metrics]
    
    print(f"\nO (Observation Consistency): {np.mean(all_O):.3f} ± {np.std(all_O):.3f}")
    print(f"R (Reward Consistency):       {np.mean(all_R):.3f} ± {np.std(all_R):.3f}")
    print(f"O/R Index:                    {np.mean(all_OR):.3f} ± {np.std(all_OR):.3f}")
    
    print("\n✅ Pipeline test complete!")
    print("📋 Next: Add checkpoint loading for trained policies")

if __name__ == "__main__":
    main()
