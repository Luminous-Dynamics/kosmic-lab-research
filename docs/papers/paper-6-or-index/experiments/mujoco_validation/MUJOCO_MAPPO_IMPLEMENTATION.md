# MuJoCo MAPPO Implementation - Technical Documentation

**Created**: November 27, 2025
**Status**: ✅ Implementation Complete - Ready for Testing
**File**: `mujoco_mappo_trainer.py` (600+ lines)

---

## Overview

Multi-Agent PPO adapted for **continuous control** in Multi-Agent MuJoCo environments with integrated **O/R Index** computation at training checkpoints.

### Key Achievements

- ✅ **Continuous Action Support**: Gaussian policy (Normal distribution) instead of Categorical
- ✅ **O/R Integration**: `ContinuousORMetric` integrated into training loop
- ✅ **Checkpoint-Based Measurement**: O/R computed every 50K steps (10 measurements per 500K run)
- ✅ **Syntax Validated**: Python compilation successful

---

## Architecture Overview

### Class Structure

```python
1. ContinuousAgent(nn.Module)
   - Shared feature extractor (256 → 256)
   - Actor head: mean + log_std (Gaussian policy)
   - Critic head: value function

2. ContinuousRolloutBuffer
   - Stores continuous actions (float32, not int64)
   - Handles multi-dimensional action vectors
   - On-policy storage for PPO updates

3. MultiAgentMuJoCoTrainer
   - Manages multiple independent agents
   - Integrates O/R metric computation
   - Handles training loop + checkpointing
```

---

## Key Adaptations from Discrete MAPPO

### 1. Network Architecture

**Before (Discrete)**:
```python
self.actor = nn.Linear(128, action_dim)  # Logits
probs = Categorical(logits=logits)
```

**After (Continuous)**:
```python
self.actor_mean = nn.Linear(256, action_dim)  # Gaussian mean
self.actor_logstd = nn.Parameter(torch.zeros(action_dim))  # Learnable std
action_std = torch.clamp(self.actor_logstd.exp(), min=1e-3, max=1.0)
probs = Normal(action_mean, action_std)
```

**Why**: Continuous actions require modeling a distribution over ℝ^d, not discrete probabilities.

### 2. Action Storage

**Before (Discrete)**:
```python
self.actions = np.zeros(size, dtype=np.int64)  # Discrete actions
```

**After (Continuous)**:
```python
self.actions = np.zeros((size, action_dim), dtype=np.float32)  # Continuous vectors
```

**Why**: MuJoCo actions are multi-dimensional continuous vectors (e.g., joint torques).

### 3. Log Probability Computation

**Before (Discrete)**:
```python
logprob = probs.log_prob(action)  # Single value
```

**After (Continuous)**:
```python
logprob = probs.log_prob(action).sum(-1)  # Sum over action dimensions
```

**Why**: Independent Gaussian per dimension requires summing log probabilities.

### 4. Environment Interface

**Before (Discrete)**:
```python
from pettingzoo.mpe import simple_spread_v3
env = simple_spread_v3.parallel_env(...)
```

**After (Continuous)**:
```python
from multiagent_mujoco.mujoco_multi import MujocoMulti
env = MujocoMulti(env_args={
    "scenario": "ManyAgentAnt",
    "agent_conf": "2x4",  # 2 agents, 4 legs each
    "agent_obsk": 1,
    "episode_limit": 1000
})
```

**Why**: Multi-Agent MuJoCo has different API than PettingZoo.

---

## O/R Integration

### Computation Points

```python
# Every 50K steps (10 measurements for 500K run)
if self.global_step % self.args.or_checkpoint_freq == 0:
    self.compute_or_index()
```

### Data Collection

```python
# During environment interaction
for i in range(self.args.num_agents):
    agent_id = f"agent_{i}"
    action, logprob, value = self.get_action_and_value(agent_id, obs[i])

    # Add to O/R metric
    self.or_metric.add_transition(obs[i], action)
```

### Measurement Output

```json
{
  "timestep": 50000,
  "or_index": -0.3740,
  "observation_consistency": 0.6500,
  "reward_consistency": 1.0383,
  "n_samples": 10000
}
```

### Results Storage

- **During Training**: `or_history` list accumulates measurements
- **After Training**: Saved to `results/or_results_seed42_500000steps.json`

---

## Training Configuration

### Default Hyperparameters

```python
@dataclass
class Args:
    # Environment
    env_name: str = "ManyAgentAnt"
    num_agents: int = 2
    agent_conf: str = "2x4"
    max_cycles: int = 1000

    # Training
    total_timesteps: int = 500_000  # Week 1 target
    learning_rate: float = 3e-4
    num_epochs: int = 10
    num_minibatches: int = 32
    gamma: float = 0.99
    gae_lambda: float = 0.95

    # PPO
    clip_coef: float = 0.2
    ent_coef: float = 0.01
    vf_coef: float = 0.5
    max_grad_norm: float = 0.5

    # O/R
    or_checkpoint_freq: int = 50_000  # 10 measurements
    or_window_size: int = 10_000  # Samples per measurement
```

### Expected Performance

- **Training Duration**: ~6-12 hours for 500K steps (GPU)
- **Memory Usage**: ~2-4 GB GPU RAM
- **Measurements**: 10 O/R values at 50K, 100K, ..., 500K steps

---

## Usage

### Basic Training Run

```bash
cd experiments/mujoco_validation

# Using Poetry + Nix (recommended)
nix develop --command bash -c "
  poetry run python mujoco_mappo_trainer.py \
    --seed 42 \
    --total-timesteps 500000 \
    --env-name ManyAgentAnt \
    --cuda
"
```

### Pilot Run (50K steps, ~1 hour)

```bash
nix develop --command bash -c "
  poetry run python mujoco_mappo_trainer.py \
    --seed 42 \
    --total-timesteps 50000 \
    --env-name ManyAgentAnt \
    --or-checkpoint-freq 10000
"
```

### Output Files

```
checkpoints/
  checkpoint_50000.pt
  checkpoint_100000.pt
  ...
  checkpoint_500000.pt

results/
  or_results_seed42_500000steps.json

logs/
  (training logs)
```

---

## Expected O/R Behavior

### Hypothesis

**O/R should decrease during training** as agents learn coordinated policies:

```
Early Training (0-100K):
  O/R ≈ 2.0 - 3.0 (high variance, poor coordination)

Mid Training (100K-300K):
  O/R ≈ 0.5 - 1.5 (decreasing variance, improving coordination)

Late Training (300K-500K):
  O/R ≈ -0.5 - 0.5 (low variance, strong coordination)
```

### Validation Criteria

For the paper, we need:
1. **Negative correlation**: O/R ↓ as performance ↑
2. **Statistical significance**: r < -0.60, p < 0.001
3. **10 measurements**: Sufficient for correlation analysis

---

## Dependencies

### Required Packages

```bash
# Core
mujoco>=3.0.0
gymnasium[mujoco]>=0.29.0
torch>=2.0.0

# Multi-Agent
git+https://github.com/schroederdewitt/multiagent_mujoco

# Analysis
numpy>=1.24.0
scikit-learn>=1.7.0  # For k-means in O/R
```

### Installation

```bash
# Option 1: Poetry (recommended)
cd experiments/mujoco_validation
nix develop
poetry install

# Option 2: Direct pip
pip install -r requirements.txt
pip install git+https://github.com/schroederdewitt/multiagent_mujoco
```

---

## Verification Checklist

### Pre-Training ✅
- [x] Syntax check passed
- [x] ContinuousAgent network defined
- [x] ContinuousRolloutBuffer handles float32 actions
- [x] O/R metric integrated
- [ ] Environment loads successfully (pending test)
- [ ] Import test with dependencies (pending)

### During Training 📋
- [ ] Agents learn (reward increases over time)
- [ ] O/R measurements computed at checkpoints
- [ ] Checkpoints saved correctly
- [ ] No memory leaks or crashes

### Post-Training 📋
- [ ] 10 O/R measurements obtained
- [ ] Results JSON file created
- [ ] Correlation: O/R vs performance negative
- [ ] Validation: r < -0.60, p < 0.001

---

## Next Steps (Week 1)

### Day 2 Remaining (Nov 27)
- [ ] Test environment loading in nix shell
- [ ] Verify import with all dependencies
- [ ] Fix any import errors

### Day 3 (Nov 28)
- [ ] Run pilot training (50K steps, ~1 hour)
- [ ] Verify O/R computation works
- [ ] Check checkpoint saving

### Day 4-5 (Nov 29-30)
- [ ] Launch full training (seed 42, 500K steps)
- [ ] Monitor progress (6-12 hours)
- [ ] Collect 10 O/R measurements

### Weekend (Dec 1-2)
- [ ] Analyze results
- [ ] Compute correlation
- [ ] Prepare for Week 1 checkpoint

---

## Technical Notes

### Why 256-256 Network?

Larger than discrete (128-128) because:
- Continuous control requires more capacity
- MuJoCo observations are high-dimensional (e.g., joint angles, velocities)
- Standard in MuJoCo benchmarks (Haarnoja et al. 2018)

### Why Clamp Log Std?

```python
action_std = torch.clamp(self.actor_logstd.exp(), min=1e-3, max=1.0)
```

**Reasons**:
- Prevents numerical instability (exp can explode)
- Ensures minimum exploration (std ≥ 1e-3)
- Prevents over-exploration (std ≤ 1.0)

### Why Independent Agents?

Could use centralized critic, but:
- **Simplicity**: Independent easier to implement
- **Comparison**: Matches discrete MAPPO baseline
- **Scalability**: Works for any number of agents

---

## Potential Issues and Solutions

### Issue 1: Multi-Agent MuJoCo Not Installing

**Error**: `ModuleNotFoundError: No module named 'multiagent_mujoco'`

**Solution**:
```bash
pip install git+https://github.com/schroederdewitt/multiagent_mujoco
```

### Issue 2: Environment Loading Fails

**Error**: `Unknown scenario: ManyAgentAnt`

**Solution**: Check available scenarios:
```python
from multiagent_mujoco import get_env_info
print(get_env_info())
```

### Issue 3: OOM (Out of Memory)

**Error**: `RuntimeError: CUDA out of memory`

**Solution**: Reduce buffer size or batch size:
```python
args.num_minibatches = 16  # Was 32
buffer_size = args.max_cycles * 5  # Was * 10
```

### Issue 4: Training Too Slow

**Problem**: 500K steps taking > 24 hours

**Solution**: Reduce to 250K steps:
```python
args.total_timesteps = 250_000
args.or_checkpoint_freq = 25_000  # Still get 10 measurements
```

---

## Code Quality Metrics

- **Lines of Code**: 600+
- **Syntax Check**: ✅ PASSED
- **Type Hints**: Partial (dataclass + numpy types)
- **Docstrings**: Complete for all classes
- **Comments**: Key sections documented

---

## Comparison to Discrete MAPPO

| Aspect | Discrete MAPPO | Continuous MAPPO (This) |
|--------|----------------|-------------------------|
| **Actions** | Categorical(logits) | Normal(mean, std) |
| **Storage** | int64 | float32 (multi-dim) |
| **Log Prob** | scalar | sum over dimensions |
| **Network Size** | 128-128 | 256-256 |
| **Environment** | PettingZoo MPE | Multi-Agent MuJoCo |
| **O/R Metric** | Discrete variance | Continuous covariance |

---

## References

- **PPO**: Schulman et al. (2017) - Proximal Policy Optimization
- **MAPPO**: Yu et al. (2021) - The Surprising Effectiveness of MAPPO
- **Multi-Agent MuJoCo**: Schroeder de Witt et al. (2020)
- **Continuous O/R**: Our formulation (Section 3 of paper)

---

**Status**: ✅ IMPLEMENTATION COMPLETE - Ready for environment testing and pilot run

**Next**: Test environment loading with poetry dependencies (Day 2-3)
