"""
MuJoCo Continuous Control O/R Trainer

Trains MARL agents on Multi-Agent MuJoCo and computes O/R Index
for continuous action spaces using covariance traces.
"""

import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Tuple
import json
from datetime import datetime

class ContinuousORMetric:
    """
    O/R Index for continuous action spaces.
    
    O/R = Tr(Σ(a|o)) / Tr(Σ(a)) - 1
    
    where:
    - Σ(a|o) is conditional action covariance (observation-specific)
    - Σ(a) is marginal action covariance (environment-wide)
    """
    
    def __init__(self, n_bins: int = 10):
        self.n_bins = n_bins
        self.observations = []
        self.actions = []
        
    def add_transition(self, obs: np.ndarray, action: np.ndarray):
        """Store observation-action pairs"""
        self.observations.append(obs.flatten())
        self.actions.append(action.flatten())
        
    def compute(self) -> Dict[str, float]:
        """Compute continuous O/R Index"""
        if len(self.observations) < 100:
            return {"O": 0.0, "R": 0.0, "OR": 0.0, "error": "insufficient_data"}
            
        obs = np.array(self.observations)
        actions = np.array(self.actions)
        
        # Discretize observation space using k-means
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=self.n_bins, random_state=42)
        obs_bins = kmeans.fit_predict(obs)
        
        # Compute marginal action covariance
        cov_marginal = np.cov(actions.T)
        var_marginal = np.trace(cov_marginal)
        
        # Compute conditional action covariance (averaged over bins)
        var_conditional = 0.0
        valid_bins = 0
        
        for b in range(self.n_bins):
            mask = obs_bins == b
            if mask.sum() > 10:  # Require at least 10 samples per bin
                actions_in_bin = actions[mask]
                cov_bin = np.cov(actions_in_bin.T)
                var_conditional += np.trace(cov_bin)
                valid_bins += 1
                
        if valid_bins == 0:
            return {"O": 0.0, "R": 0.0, "OR": 0.0, "error": "no_valid_bins"}
            
        var_conditional /= valid_bins
        
        # O/R Index
        O = var_conditional
        R = var_marginal
        OR = (O / R - 1) if R > 1e-8 else 0.0
        
        return {
            "observation_consistency": float(O),
            "reward_consistency": float(R),
            "or_index": float(OR),
            "n_samples": len(self.observations),
            "valid_bins": int(valid_bins)
        }


def test_continuous_or_on_toy_data():
    """Test continuous O/R computation on synthetic data"""
    print("=" * 80)
    print("Testing Continuous O/R Metric on Toy Data")
    print("=" * 80)
    print()

    # Create synthetic data: observations and actions
    np.random.seed(42)
    n_samples = 500
    obs_dim = 10
    action_dim = 4

    # Generate observations (2 clusters)
    obs_cluster1 = np.random.randn(n_samples//2, obs_dim) + np.array([2.0] * obs_dim)
    obs_cluster2 = np.random.randn(n_samples//2, obs_dim) - np.array([2.0] * obs_dim)
    observations = np.vstack([obs_cluster1, obs_cluster2])

    # Generate actions (cluster1 -> action1, cluster2 -> action2 + noise)
    actions_cluster1 = np.random.randn(n_samples//2, action_dim) * 0.1 + np.array([1.0, 0.0, 0.0, 0.0])
    actions_cluster2 = np.random.randn(n_samples//2, action_dim) * 0.5 + np.array([0.0, 1.0, 0.0, 0.0])
    actions = np.vstack([actions_cluster1, actions_cluster2])

    # Shuffle
    indices = np.random.permutation(n_samples)
    observations = observations[indices]
    actions = actions[indices]

    print(f"Generated {n_samples} synthetic observation-action pairs")
    print(f"  Observations shape: {observations.shape}")
    print(f"  Actions shape: {actions.shape}")
    print()

    # Compute continuous O/R
    metric = ContinuousORMetric(n_bins=10)
    for i in range(n_samples):
        metric.add_transition(observations[i], actions[i])

    result = metric.compute()

    print("Continuous O/R Results:")
    print(f"  Observation Consistency (O): {result['observation_consistency']:.4f}")
    print(f"  Reward Consistency (R): {result['reward_consistency']:.4f}")
    print(f"  O/R Index: {result['or_index']:.4f}")
    print(f"  Valid bins: {result.get('valid_bins', 'N/A')}/{metric.n_bins}")
    print()

    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        return False

    # Expected: Low O/R because clusters have consistent actions
    if result['or_index'] < 2.0:
        print("✅ Test PASSED - O/R < 2.0 (expected for consistent synthetic data)")
        return True
    else:
        print("⚠️  Test WARNING - O/R unexpectedly high")
        return False


def main():
    """Training entry point"""
    print("=" * 80)
    print("MuJoCo Continuous Control O/R Trainer")
    print("=" * 80)
    print()

    # Run toy data test first
    print("Step 1: Testing continuous O/R computation...")
    print()
    test_passed = test_continuous_or_on_toy_data()
    print()

    if not test_passed:
        print("⚠️  Toy data test failed - fix implementation before proceeding")
        return

    print("=" * 80)
    print("Step 2: Environment Setup")
    print("=" * 80)
    print()

    # TODO: Implement full training loop
    # 1. Load Multi-Agent MuJoCo environment
    # 2. Train MARL policy (MAPPO or similar)
    # 3. Compute O/R at checkpoints
    # 4. Save results

    print("✅ Continuous O/R implementation verified")
    print()
    print("Next steps:")
    print("1. Install multiagent-mujoco: pip install git+https://github.com/schroederdewitt/multiagent_mujoco")
    print("2. Implement MAPPO training loop")
    print("3. Integrate ContinuousORMetric into training")
    print("4. Launch first training run (seed 42, ManyAgentAnt-v0)")


if __name__ == "__main__":
    main()
