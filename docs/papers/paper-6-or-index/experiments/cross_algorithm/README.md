# Cross-Algorithm Robustness Experiments

**Goal**: Validate O/R Index generalizes across algorithm families
**Status**: Day 1 - Environment Setup
**Started**: November 25, 2025

---

## Directory Structure

```
cross_algorithm/
├── cleanrl/              # CleanRL implementations
├── venv/                 # Python virtual environment
├── configs/              # Experiment configurations
├── logs/                 # Training logs
├── checkpoints/          # Model checkpoints
├── results/              # Analysis results
└── README.md            # This file
```

---

## Setup Progress

### Day 1: Environment Setup - ✅ COMPLETE

**Completed**:
- [x] Created directory structure
- [x] Cloned CleanRL repository
- [x] Created Python virtual environment
- [x] Installed PyTorch 2.9.1+cpu
- [x] Installed Gymnasium 1.2.2
- [x] Installed PettingZoo[MPE] 1.24.3
- [x] Installed pygame 2.6.1
- [x] Fixed zlib library path issue (nix + venv integration)
- [x] Verified environment works (all tests pass)
- [x] Created multi-agent DQN trainer (300+ lines)
- [x] Created launch and kill scripts
- [x] **Launched DQN training - 3 seeds running in parallel**

**Current Status**: ✅ DQN Training Active (PIDs: 980809, 980811, 980813)
**Training Progress**: Episode 100+ reached on all seeds, first checkpoints saved

---

## Environments

### MPE Cooperative Navigation (simple_spread_v3)
- **Agents**: 3
- **Max cycles**: 25
- **Local ratio**: 0.5 (partial observability)
- **Task**: Navigate to landmarks without collisions

### SMAC 3m (Coming Day 2)
- **Agents**: 3 Marines
- **Task**: Defeat 3 enemy Marines
- **Framework**: StarCraft II micromanagement

---

## Algorithms to Test

### Status Overview
- [✅] **DQN** (Value-based) - Day 1 - **COMPLETE** (1000 episodes, 3 seeds)
- [ ] **SAC** (Off-policy AC) - Day 2
- [ ] **MAPPO** (On-policy multi-agent) - Day 2
- [ ] **QMIX** (Value decomposition) - Day 3

### DQN Training Results ✅
- **Seeds**: 42, 123, 456 (all completed)
- **Environment**: MPE simple_spread_v3 (3 agents, partial observability)
- **Episodes**: 1000 per seed (3,000 total)
- **Total steps**: 25,000 per seed (75,000 total)
- **Training time**: ~2 hours 15 minutes
- **Checkpoints**: 10 saved per seed (every 100 episodes)
- **Final rewards**: -18.41, -17.95, -28.80 (mean across 3 agents)

---

## Training Configuration

**Per Algorithm**:
- Seeds: 3 (42, 123, 456)
- Episodes: 1,000 per seed
- Save frequency: Every 100 episodes
- Logging: TensorBoard + console

**Total Training Runs**: 4 algorithms × 2 envs × 3 seeds = 24 runs

---

## Next Steps

1. Finish dependency installation
2. Test MPE environment loads
3. Adapt DQN for multi-agent
4. Launch first training runs

---

## Commands

### Activate Environment
```bash
source venv/bin/activate
```

### Monitor Training
```bash
# View logs
tail -f logs/dqn_seed42.log

# Check processes
ps aux | grep python | grep train

# TensorBoard
tensorboard --logdir runs/
```

### Kill Training
```bash
pkill -f "python.*train"
```

---

## Notes

(Add observations and issues as they arise)

---

*Last Updated*: Day 1 - November 25, 2025
