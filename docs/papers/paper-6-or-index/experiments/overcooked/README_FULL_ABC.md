# Full A+B+C Validation for O/R Index

**Status**: Ready to run
**Estimated Time**: 6-8 hours (GPU) or 120-180 hours (CPU)
**Output**: 720 trajectories across 6 scenarios

---

## Overview

This directory contains the complete validation pipeline for the O/R Index on Overcooked coordination tasks, covering:

- **3 layouts**: cramped_room, asymmetric_advantages, coordination_ring
- **2 horizons per layout**: 400, 800 timesteps
- **4 policies per scenario**: random, ppo_5k (125 eps), ppo_50k (1250 eps), ppo_200k (5000 eps)
- **30 seeds per policy**: For statistical robustness
- **Total**: 6 scenarios × 4 policies × 30 seeds = **720 trajectories**

---

## Quick Start

### 1. Train all policies (6-8 hours GPU)
```bash
cd /srv/luminous-dynamics/kosmic-lab/docs/papers/paper-6-or-index/experiments/overcooked
nix develop
python train_full_abc_validation.py > /tmp/full_abc_training.log 2>&1 &
```

Monitor progress:
```bash
tail -f /tmp/full_abc_training.log
```

### 2. Collect trajectories (5-10 minutes)
```bash
python collect_full_abc.py
```

### 3. Analyze and generate figures (5-10 minutes)
```bash
python analyze_full_abc.py
```

Results will be in `outputs/full_abc/`:
- `or_index_results.csv` - Complete numerical results
- `scenario_comparison.pdf` - O/R Index across scenarios
- `training_curves.pdf` - Learning curves for each scenario
- `horizon_comparison.pdf` - Effect of horizon length

---

## Simplified Validation (Already Complete ✅)

For quick pipeline testing, we already completed:
- **1 scenario**: cramped_room (h=400)
- **4 policies**: random, ppo_5k, ppo_50k, ppo_200k
- **30 seeds**: Per policy
- **Results**: `outputs/or_index_results_simple.csv`

See `COMPLETION_REPORT.md` for details.

---

## File Structure

```
overcooked/
├── train_overcooked_gpu_simple.py    # Simplified training (DONE ✅)
├── collect_overcooked_simple.py      # Simplified collection (DONE ✅)
├── analyze_overcooked_simple.py      # Simplified analysis (DONE ✅)
├── train_full_abc_validation.py      # Full A+B+C training (NEW)
├── collect_full_abc.py                # Full collection (TODO)
├── analyze_full_abc.py                # Full analysis (TODO)
├── env_overcooked.py                  # Environment wrapper (FIXED ✅)
├── SESSION_SUMMARY.md                 # Session achievements
├── COMPLETION_REPORT.md               # Simplified validation report
├── README_FULL_ABC.md                 # This file
├── models/
│   └── overcooked/
│       ├── cramped_room_h400_baseline_gpu/  (DONE ✅)
│       ├── cramped_room_h400_full_abc/      (TODO)
│       ├── cramped_room_h800_full_abc/      (TODO)
│       ├── asymmetric_advantages_h400_full_abc/  (TODO)
│       ├── asymmetric_advantages_h800_full_abc/  (TODO)
│       ├── coordination_ring_h400_full_abc/      (TODO)
│       └── coordination_ring_h800_full_abc/      (TODO)
├── trajectories/
│   ├── cramped_room_h400_baseline_gpu/  (DONE ✅)
│   └── [6 more scenario directories will be created]
└── outputs/
    ├── or_index_results_simple.csv    (DONE ✅)
    ├── scatter_or_vs_coord_simple.pdf (DONE ✅)
    ├── training_evolution_simple.pdf  (DONE ✅)
    └── full_abc/  (TODO - will contain comprehensive results)
```

---

## Scenarios

### A. Cramped Room
- **Layout**: cramped_room
- **Description**: Narrow corridors, requires careful coordination
- **Horizons**: 400, 800
- **Difficulty**: Medium

### B. Asymmetric Advantages
- **Layout**: asymmetric_advantages
- **Description**: Unequal starting positions, requires role differentiation
- **Horizons**: 400, 800
- **Difficulty**: Hard

### C. Coordination Ring
- **Layout**: coordination_ring
- **Description**: Circular layout, requires precise timing
- **Horizons**: 400, 800
- **Difficulty**: Medium-Hard

---

## Training Checkpoints

| Checkpoint | Episodes | Training Time (GPU) | Purpose |
|------------|----------|---------------------|---------|
| random | 0 | 0s | Baseline (no learning) |
| ppo_5k | 125 | ~2-3 min | Minimal training |
| ppo_50k | 1250 | ~20-30 min | Medium training |
| ppo_200k | 5000 | ~60-90 min | Full training |

**Total per scenario**: ~1.5-2 hours
**Total for 6 scenarios**: ~9-12 hours (with MotionPlanner overhead)

---

## Expected Outcomes

### If REINFORCE learns coordination:
- O/R Index increases with training
- ppo_200k >> ppo_50k > ppo_5k > random
- Positive coordination success rates
- Non-zero episode returns

### If REINFORCE fails (current observation):
- O/R Index ≈ 0 across all checkpoints
- No clear learning trend
- Zero coordination success
- Zero episode returns
- **Conclusion**: Need better algorithms (PPO with value functions, reward shaping, curriculum learning)

---

## Troubleshooting

### Training takes too long
- Reduce episodes: Change `ppo_200k` from 5000 to 2500
- Skip checkpoints: Only train random + ppo_200k
- Use fewer seeds: Reduce from 30 to 10 per policy

### Out of memory
- Reduce batch size (currently 1 episode)
- Reduce network size (256→128 hidden units)
- Use CPU (very slow but works)

### MotionPlanner initialization hangs
- Already bypassed in `env_overcooked.py` with `use_motion_planner=True` flag
- If still slow, set to `False` (may hurt policy quality)

---

## Next Steps After Full Validation

1. **Analyze results**: Check if O/R Index correlates with coordination
2. **Write paper**: Include figures and tables from `outputs/full_abc/`
3. **Improve algorithms** (if needed):
   - Implement PPO with value function
   - Add reward shaping
   - Try curriculum learning
4. **Scale to more scenarios**: Add forced_coordination, counter_circuit, etc.

---

**Last Updated**: 2025-11-21
**Status**: Ready for full training
