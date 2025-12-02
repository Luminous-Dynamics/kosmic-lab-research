# Experimental Design: Overcooked A+B+C Comprehensive Validation

## Overview

This document describes the complete experimental methodology for validating the O/R Index on the Overcooked-AI cooperative cooking environment with comprehensive A+B+C scenario coverage.

## Experimental Design Rationale

### Three-Tier Validation Strategy

**Option A: Baseline Validation**
- Standard difficulty coordination scenarios
- Validates O/R Index on typical MARL tasks
- Establishes baseline performance expectations

**Option B: Stress Testing**
- Harder coordination challenges testing robustness
- Spatial complexity, sequential dependencies, temporal decay
- Tests whether O/R Index generalizes beyond easy cases

**Option C: Many-Agent Simulation**
- Simulates coordination complexity of 3-4 agent teams
- Uses randomized initial positions to create uncertainty
- Tests O/R Index scalability to larger teams (within 2-player constraint)

## Scenarios

### Baseline Scenarios (Option A)

#### 1. Cramped Room (horizon=400)
- **Layout**: Small kitchen with narrow passages
- **Difficulty**: Medium
- **Coordination Challenge**: Spatial navigation, avoiding collisions
- **Expected Baseline**: Random ~0 reward, Expert ~200 reward
- **Scenario ID**: `cramped_room_h400_baseline`

#### 2. Asymmetric Advantages (horizon=400)
- **Layout**: Asymmetric kitchen layout with different agent capabilities
- **Difficulty**: Medium-Hard
- **Coordination Challenge**: Role specialization, complementary actions
- **Expected Baseline**: Random ~0 reward, Expert ~250 reward
- **Scenario ID**: `asymmetric_advantages_h400_baseline`

### Stress Test Scenarios (Option B)

#### 3. Coordination Ring (horizon=400)
- **Layout**: Circular kitchen requiring continuous coordination
- **Difficulty**: Hard
- **Coordination Challenge**: **Spatial complexity** - agents must navigate tight circular path
- **Expected Baseline**: Random ~0 reward, Expert ~150 reward (harder than baseline)
- **Scenario ID**: `coordination_ring_h400_stress_spatial`
- **Hypothesis**: Higher spatial coordination demand → Higher O/R values needed for success

#### 4. Forced Coordination (horizon=400)
- **Layout**: Tasks require strict sequential ordering
- **Difficulty**: Hard
- **Coordination Challenge**: **Sequential dependencies** - actions must occur in specific order
- **Expected Baseline**: Random ~0 reward, Expert ~180 reward
- **Scenario ID**: `forced_coordination_h400_stress_sequential`
- **Hypothesis**: Sequential constraints → Steeper O/R vs. coordination relationship

#### 5. Cramped Room Long Horizon (horizon=800)
- **Layout**: Same as baseline cramped_room
- **Difficulty**: Hard
- **Coordination Challenge**: **Temporal decay** - maintaining coordination over 2× longer episodes
- **Expected Baseline**: Random ~0 reward, Expert ~350 reward (2× horizon)
- **Scenario ID**: `cramped_room_h800_stress_temporal`
- **Hypothesis**: Longer horizons → More opportunities for coordination breakdown

### Many-Agent Simulation (Option C)

#### 6. Cramped Room with Randomized Positions (horizon=400)
- **Layout**: Cramped room with random initial agent positions
- **Difficulty**: Hard
- **Coordination Challenge**: **Uncertainty** - agents start in unpredictable configurations
- **Expected Baseline**: Random ~0 reward, Expert ~180 reward
- **Scenario ID**: `cramped_room_h400_multiagent_sim`
- **Hypothesis**: Positional uncertainty simulates 3-4 agent complexity
- **Rationale**: Overcooked-AI is hardcoded for 2 agents; randomization simulates the coordination complexity of larger teams

## Training Protocol

### Policy Checkpoints

Four training checkpoints per scenario to capture learning progression:

| Checkpoint | Episodes | Approx Timesteps | Purpose |
|------------|----------|------------------|---------|
| `random` | 0 | 0 | Untrained baseline |
| `ppo_5k` | 125 | ~5,000 | Early learning |
| `ppo_50k` | 1,250 | ~50,000 | Mid training |
| `ppo_200k` | 5,000 | ~200,000 | Near-convergence |

**Total Models**: 6 scenarios × 4 checkpoints = **24 trained policies**

### Training Algorithm

**Simple REINFORCE (Policy Gradient)**
- Lightweight, NixOS-friendly (no heavy frameworks)
- Independent policy per agent (IPPO-style)
- Shared reward signal

**Hyperparameters**:
```python
learning_rate: 3e-4
gamma: 0.99  # Discount factor
optimizer: Adam
architecture: [obs_dim → 128 → 64 → n_actions]
activation: ReLU
```

**Illegal Action Handling**:
- Overcooked-AI restricts certain actions in certain states
- Retry mechanism: Up to 5 attempts with random action fallback
- Penalty: -1.0 reward if max retries exceeded

### Training Environment

- **Platform**: NixOS with Nix flakes for reproducibility
- **Dependencies**: PyTorch, NumPy, Overcooked-AI-py
- **Horizon**: Variable (400 or 800 timesteps)
- **Action Space**: 6 discrete actions per agent (up, down, left, right, interact, stay)
- **Observation**: Lossless state encoding (2080-dim concatenated agent-centric views)

## Trajectory Collection

### Collection Protocol

For each of the 24 trained policy checkpoints:

1. **Load Policy**: Restore trained weights from checkpoint
2. **Rollout**: Execute 30 episodes with different random seeds
3. **Storage**: Save complete trajectory data per seed

**Seeds**: 0-29 (30 trajectories per checkpoint)
**Total Trajectories**: 6 scenarios × 4 checkpoints × 30 seeds = **720 trajectories**

### Trajectory Data Format

Each trajectory stored as NPZ file with:
```python
{
    'obs': (T, 2080),        # Observations per timestep
    'actions': (T, 2),        # Joint actions per timestep
    'rewards': (T,),          # Rewards per timestep
    'dones': (T,),            # Episode termination flags
    'ep_return': float,       # Cumulative episode return
    'ep_length': int,         # Episode length in timesteps
}
```

**Metadata** (JSON):
```json
{
    "scenario_id": "cramped_room_h400_baseline",
    "layout": "cramped_room",
    "horizon": 400,
    "policy_type": "ppo_50k",
    "seed": 15,
    "episode_return": 142.5,
    "episode_length": 387,
    "checkpoint_path": "../../models/overcooked/..."
}
```

## Analysis Pipeline

### 1. O/R Index Computation

For each trajectory:

```python
# Extract observations and joint actions
obs = trajectory['obs']  # (T, 2080)
actions = trajectory['actions']  # (T, 2)

# Compute O/R Index using PCA + binning
or_index = compute_or_index(obs, actions,
                             pca_components=10,
                             n_bins=10)
```

**O/R Index Formula**:
```
O/R(π) = [Var(P(a|o)) / Var(P(a))] - 1

where:
  P(a|o) = probability of action given observation
  P(a) = marginal probability of action
```

### 2. Coordination Success Metric

Normalize episode returns to [0, 1] coordination score:

```python
coord_success = (ep_return - baseline_random) /
                (baseline_expert - baseline_random)
```

Baselines defined per scenario (see table above).

### 3. Statistical Analysis

For each scenario:
- Compute mean ± std of O/R Index across 30 seeds
- Compute mean ± std of coordination success
- Perform linear regression: `coord_success ~ or_index`
- Report Pearson correlation and p-value

### 4. Visualization

**Figure 1: O/R vs Coordination (3×2 grid)**
- One subplot per scenario
- X-axis: O/R Index
- Y-axis: Coordination Success [0, 1]
- Color: Training checkpoint (random, 5k, 50k, 200k)
- Shows correlation strength per scenario

**Figure 2: Training Evolution (3-panel)**
- Panel A: Baseline scenarios
- Panel B: Stress test scenarios
- Panel C: Many-agent simulation
- X-axis: Training timesteps
- Y-axis: O/R Index (increasing with learning)

**Table 1: Quantitative Results**
- Rows: 6 scenarios
- Columns: Pearson r, p-value, slope, R²
- Grouped by scenario type (A/B/C)

## Expected Results

### Hypothesis 1: Positive O/R-Coordination Correlation
- **Prediction**: Higher O/R Index → Higher coordination success
- **Rationale**: Better observation-response coupling enables tighter coordination

### Hypothesis 2: Stress Tests Show Stronger Relationships
- **Prediction**: Steeper slopes for stress scenarios
- **Rationale**: Harder tasks demand better observation-response alignment

### Hypothesis 3: Many-Agent Simulation Generalizes
- **Prediction**: Similar O/R patterns to baseline despite randomization
- **Rationale**: O/R Index captures coordination complexity regardless of team size proxy

## Computational Resources

**Training**:
- Time: 16-24 hours (6 scenarios × 4 checkpoints)
- Parallelization: Sequential (single machine)
- Hardware: CPU-only (no GPU required)

**Collection**:
- Time: ~15-20 minutes (720 trajectories)
- Storage: ~500 MB total

**Analysis**:
- Time: ~2-3 minutes
- Output: 2 figures + 1 LaTeX table + CSV data

## Reproducibility

All experiments conducted with:
- **Nix Flakes**: Pinned dependencies for exact reproducibility
- **Random Seeds**: Explicit seeds (0-29) for deterministic trajectories
- **Checkpointing**: All models saved with metadata
- **Configuration**: Documented hyperparameters and environment settings

**Repository Structure**:
```
experiments/overcooked/
├── env_overcooked.py          # Environment wrapper
├── train_overcooked.py        # Training script
├── collect_overcooked.py      # Trajectory collection
├── analyze_overcooked.py      # Analysis and visualization
├── flake.nix                  # Nix reproducibility
├── flake.lock                 # Locked dependencies
└── EXPERIMENTAL_DESIGN.md     # This document
```

## Timeline

1. **Training**: 16-24 hours (in progress)
2. **Collection**: 15-20 minutes
3. **Analysis**: 2-3 minutes
4. **Paper Integration**: 2-3 hours

**Total**: ~1-2 days from experiment start to paper submission.
