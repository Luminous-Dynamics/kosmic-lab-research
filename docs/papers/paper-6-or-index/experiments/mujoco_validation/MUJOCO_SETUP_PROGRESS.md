# MuJoCo Environment Setup Progress

**Date**: November 27, 2025 (Evening - Day 4 Morning)
**Status**: ⚠️ **BLOCKER** - Python 3.13 incompatible with mujoco-py
**Next Step**: See "🔴 Critical Blocker" section below for solutions

---

## 🎯 Goal

Test Multi-Agent MuJoCo environment loading with poetry+nix to verify all dependencies are available before running pilot training.

---

## ✅ Completed Steps

### 1. Dependencies Added to pyproject.toml

**File Modified**: `/srv/luminous-dynamics/kosmic-lab/pyproject.toml`

**Changes**:
```toml
# MuJoCo continuous control dependencies (Paper 6 - O/R Index)
mujoco = "^3.0"
tensorboard = "^2.14"
```

**Location**: Added after pettingzoo dependency (line 47-50)

### 2. Initial Poetry Install Attempted

**Command**: `poetry install` (completed successfully)
**Result**: Exit code 0
**Issue**: Only installs dependencies already in poetry.lock

**Learning**: When adding new dependencies to pyproject.toml, need to:
1. Run `poetry lock --no-update` to add to lock file (faster), OR
2. Run `poetry update` to update lock file and install (comprehensive)

---

## 🔴 Critical Blocker: Python 3.13 + Cython 3.x + mujoco-py Incompatibility

### Problem Description

The Multi-Agent MuJoCo package (`multiagent_mujoco`) depends on the legacy `mujoco-py` package, which:
1. **Requires MuJoCo 210 binaries** (✅ INSTALLED at `~/.mujoco/mujoco210`)
2. **Incompatible with Python 3.13 + Cython 3.x** (❌ BLOCKER)

**Error**:
```
Cannot assign type 'void (const char *) except * nogil' to 'void (*)(const char *) noexcept nogil'.
Exception values are incompatible. Suggest adding 'noexcept' to the type of 'c_warning_callback'.
```

This is a **known incompatibility** between:
- Cython 3.x (introduces `noexcept` syntax)
- Python 3.13 (strict exception handling)
- mujoco-py (unmaintained, last update 2020)

### Solution Options (Ranked by Effort)

#### ✅ Option 1: Use Python 3.11 (FASTEST - 30 mins)
**Recommended for quick unblocking**

```bash
# Modify kosmic-lab/flake.nix to use python311
# Change line: python = pkgs.python313;
# To:         python = pkgs.python311;

nix develop --command poetry env use python3.11
nix develop --command poetry install
nix develop --command poetry run pip install mujoco tensorboard
nix develop --command poetry run pip install git+https://github.com/schroederdewitt/multiagent_mujoco
```

**Pros**: Quick fix, minimal changes
**Cons**: Locks us to Python 3.11

#### ⚠️ Option 2: Downgrade Cython < 3.0 (MEDIUM - 1-2 hours)
**If Python 3.13 is required**

```bash
nix develop --command poetry run pip uninstall Cython
nix develop --command poetry run pip install "Cython<3.0"
nix develop --command poetry run pip install git+https://github.com/schroederdewitt/multiagent_mujoco
```

**Pros**: Keeps Python 3.13
**Cons**: May have other 3.13 incompatibilities

#### 🔧 Option 3: Use Modern MuJoCo Alternative (BEST - 4-8 hours)
**Long-term solution** - Use modern `mujoco` package (not `mujoco-py`)

Find/create modern Multi-Agent MuJoCo wrapper:
- Use `mujoco` (version 3.3.7) - modern Python bindings
- Rewrite Multi-Agent environment adapter
- No legacy binary dependencies

**Pros**: Future-proof, modern stack
**Cons**: Requires environment adapter implementation

#### 🚫 Option 4: Patch mujoco-py (NOT RECOMMENDED - 8+ hours)
Fork and patch mujoco-py for Cython 3.x compatibility

**Pros**: Fixes root cause
**Cons**: High effort, unmaintained upstream

### Recommended Path Forward

**For Week 1 (ICML submission urgent)**:
1. Use **Option 1** (Python 3.11) to unblock immediately
2. Run pilot training with Python 3.11 environment
3. Collect O/R measurements and complete experiments

**For Future** (after Week 1):
- Investigate **Option 3** (modern MuJoCo wrapper)
- Contribute to ecosystem if needed

---

## 🔍 Current Status

### What We Have

**Existing Dependencies** (already working):
- ✅ gymnasium (^0.29)
- ✅ pettingzoo (^1.24)
- ✅ stable-baselines3 with torch extras
- ✅ numpy, pandas, matplotlib, seaborn, scipy, scikit-learn

**New Dependencies** (added to pyproject.toml, not yet locked):
- 🚧 mujoco (^3.0) - Added but not in poetry.lock
- 🚧 tensorboard (^2.14) - Added but not in poetry.lock

### What We Need

**Multi-Agent MuJoCo Package**:
- Source: https://github.com/schroederdewitt/multiagent_mujoco
- Installation: `poetry run pip install git+https://github.com/schroederdewitt/multiagent_mujoco`
- Note: Not available on PyPI, needs git install

---

## 🚀 Next Steps (Week 1 Day 3-4)

### Step 1: Update Poetry Lock File (5-10 min)

```bash
cd /srv/luminous-dynamics/kosmic-lab

# Option A: Fast (just lock new dependencies)
nix develop --command poetry lock --no-update

# Option B: Comprehensive (update all + lock new)
nix develop --command poetry update

# Then install
nix develop --command poetry install
```

**Expected Output**:
- poetry.lock updated with mujoco ^3.0 and tensorboard ^2.14
- Packages installed to virtual environment
- Can import mujoco and tensorboard

### Step 2: Install Multi-Agent MuJoCo (5 min)

```bash
cd /srv/luminous-dynamics/kosmic-lab

nix develop --command bash -c "
  poetry run pip install git+https://github.com/schroederdewitt/multiagent_mujoco
"
```

**Expected Output**:
- multiagent_mujoco package installed
- Can import multiagent_mujoco.mujoco_multi

### Step 3: Test Environment Loading (2 min)

```bash
cd /srv/luminous-dynamics/kosmic-lab

nix develop --command bash -c "
  poetry run python -c '
from multiagent_mujoco.mujoco_multi import MujocoMulti
import mujoco

print(f\"✅ MuJoCo version: {mujoco.__version__}\")

env = MujocoMulti(env_args={
    \"scenario\": \"ManyAgentAnt\",
    \"agent_conf\": \"2x4\",
    \"agent_obsk\": 1,
    \"episode_limit\": 1000
})

print(f\"✅ Environment created: {env}\")
print(f\"✅ Observation space: {env.observation_space}\")
print(f\"✅ Action space: {env.action_space}\")
'
"
```

**Expected Output**:
```
✅ MuJoCo version: 3.2.0
✅ Environment created: <MujocoMulti instance>
✅ Observation space: ...
✅ Action space: ...
```

### Step 4: Run Pilot Training (1-2 hours)

```bash
cd /srv/luminous-dynamics/kosmic-lab/docs/papers/paper-6-or-index/experiments/mujoco_validation

nix develop --command bash -c "
  poetry run python mujoco_mappo_trainer.py \
    --seed 42 \
    --total-timesteps 50000 \
    --env-name ManyAgentAnt \
    --or-checkpoint-freq 10000 \
    --cuda
"
```

**Expected Duration**: 1-2 hours for 50K steps
**Expected Outputs**:
- 5 O/R measurements (at 10K, 20K, 30K, 40K, 50K)
- Checkpoints saved in checkpoints/
- Results in results/or_results_seed42_50000steps.json

---

## 📊 Estimated Timeline

| Step | Duration | Status |
|------|----------|--------|
| Add dependencies to pyproject.toml | 2 min | ✅ Done |
| Run poetry lock/update | 5-10 min | 🚧 Next |
| Install multi-agent mujoco | 5 min | ⏳ Pending |
| Test environment loading | 2 min | ⏳ Pending |
| Run pilot training (50K steps) | 1-2 hours | ⏳ Pending |
| **Total** | **~2-3 hours** | **20% complete** |

---

## 🔧 Troubleshooting

### Issue 1: poetry.lock out of sync

**Symptom**: ModuleNotFoundError for mujoco even after adding to pyproject.toml
**Cause**: poetry.lock not updated after adding new dependencies
**Solution**: Run `poetry update` or `poetry lock --no-update`

### Issue 2: Multi-Agent MuJoCo not on PyPI

**Symptom**: Can't find multiagent-mujoco package
**Cause**: Package only available via Git
**Solution**: Install via `poetry run pip install git+https://...`

### Issue 3: Environment loading fails

**Symptom**: Unknown scenario error
**Cause**: Invalid scenario name or configuration
**Solution**: Check available scenarios, verify agent_conf matches

---

## 📝 Session Notes

### Key Learnings

1. **Poetry workflow**: Adding to pyproject.toml requires lock file update
2. **Background ops**: Long-running installs should use background processes
3. **Git packages**: Some packages not on PyPI need git install via pip

### Decisions Made

**Decision 1**: Add dependencies to pyproject.toml directly instead of `poetry add`
- **Rationale**: poetry add can timeout (>30s), direct edit faster
- **Trade-off**: Need manual lock update step

**Decision 2**: Defer environment testing to Day 4
- **Rationale**: Theory proof completion was higher priority
- **Trade-off**: Day 3 ends without environment verification

**Decision 3**: Document setup process thoroughly
- **Rationale**: Makes debugging easier if issues arise
- **Trade-off**: ~10 minutes documentation time

---

## 🎯 Success Criteria

**Environment Setup Complete When**:
- ✅ mujoco and tensorboard in poetry.lock
- ✅ Can import mujoco and multiagent_mujoco
- ✅ MujocoMulti environment loads successfully
- ✅ Observation and action spaces accessible

**Ready for Pilot Training When**:
- ✅ Environment setup complete
- ✅ mujoco_mappo_trainer.py imports work
- ✅ First few environment steps execute without errors

---

## 📄 Related Files

**Code**:
- `mujoco_mappo_trainer.py` - Complete MAPPO implementation (600+ lines)
- `MUJOCO_MAPPO_IMPLEMENTATION.md` - Technical documentation (14KB)

**Dependencies**:
- `/srv/luminous-dynamics/kosmic-lab/pyproject.toml` - Python dependencies
- `/srv/luminous-dynamics/kosmic-lab/poetry.lock` - Locked versions
- `/srv/luminous-dynamics/kosmic-lab/flake.nix` - Nix system dependencies

**Progress Tracking**:
- `WEEK_1_DAY_2_FINAL_SUMMARY.md` - Day 2 completion report
- `WEEK_1_DAY_3_SUMMARY.md` - Day 3 completion report
- `WEEK_1_ACTION_ITEMS.md` - Week 1 task breakdown

---

**Status**: ✅ Dependencies added, 🚧 Lock update needed

**Next Session**: Run `poetry update` → Install multi-agent mujoco → Test environment → Pilot run

**Estimated Completion**: End of Day 4 (Nov 28)
