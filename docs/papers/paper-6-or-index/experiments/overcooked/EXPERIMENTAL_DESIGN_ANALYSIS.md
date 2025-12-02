# Experimental Design Analysis: Paper vs Implementation

**Date**: 2025-11-21
**Status**: ⚠️ MISALIGNMENT DETECTED - Training Incomplete

---

## Executive Summary

**Critical Findings**:
1. ❌ **Training incomplete** - Only random policies saved (no trained models)
2. ❌ **Scenario mismatch** - Implementation uses different scenarios than paper specification
3. ❌ **Checkpoint bug** - Directory creation failed, preventing model saves

**Recommendation**: Fix bugs and align with paper before proceeding to collection/analysis.

---

## 1. Saved Models Analysis

### What Actually Exists

All 6 scenarios contain only:
- `random.pth` - Untrained random policy (2.3-4.9 MB)
- `random_meta.json` - Metadata for random policy

**Missing**:
- `ppo_5k.pth` - Early training checkpoint (125 episodes)
- `ppo_50k.pth` - Mid training checkpoint (1250 episodes)
- `ppo_200k.pth` - Full training checkpoint (5000 episodes)

### Why Training Failed

**Root Cause**: Line 127 in `train_full_abc_validation.py`

```python
checkpoint_path = save_path / f"checkpoint_{episode + 1}.pth"
torch.save({...}, checkpoint_path)
```

**Error**: `Parent directory models/overcooked/{scenario}/checkpoints/{policy} does not exist`

**Impact**:
- Training script continued despite errors (try/except caught the exception)
- Only the first checkpoint (random) was saved since it doesn't require training
- Trained models (ppo_5k, ppo_50k, ppo_200k) were NEVER saved

**Fix Required**:
```python
# Add before checkpoint_path assignment:
if save_path:
    save_path.mkdir(parents=True, exist_ok=True)
```

---

## 2. Scenario Design Comparison

### Paper Specification (EXPERIMENTAL_DESIGN.md)

| ID | Scenario | Purpose | Horizon | Coordination Challenge |
|----|----------|---------|---------|------------------------|
| 1 | cramped_room_h400_baseline | Baseline A | 400 | Spatial navigation |
| 2 | asymmetric_advantages_h400_baseline | Baseline A | 400 | Role specialization |
| 3 | coordination_ring_h400_stress_spatial | Stress Test B | 400 | **Spatial complexity** |
| 4 | forced_coordination_h400_stress_sequential | Stress Test B | 400 | **Sequential dependencies** |
| 5 | cramped_room_h800_stress_temporal | Stress Test B | 800 | **Temporal decay** |
| 6 | cramped_room_h400_multiagent_sim | Many-Agent C | 400 | **Randomized positions** |

### Implementation (train_full_abc_validation.py lines 245-252)

| ID | Scenario | Purpose | Horizon | Naming |
|----|----------|---------|---------|--------|
| 1 | cramped_room | Generic | 400 | cramped_room_h400_full_abc |
| 2 | cramped_room | Generic | 800 | cramped_room_h800_full_abc |
| 3 | asymmetric_advantages | Generic | 400 | asymmetric_advantages_h400_full_abc |
| 4 | asymmetric_advantages | Generic | 800 | asymmetric_advantages_h800_full_abc |
| 5 | coordination_ring | Generic | 400 | coordination_ring_h400_full_abc |
| 6 | coordination_ring | Generic | 800 | coordination_ring_h800_full_abc |

---

## 3. Critical Misalignments

### Missing Scenarios

#### A. forced_coordination Layout ❌
- **Paper Requirement**: Scenario 4 - tests sequential dependencies
- **Implementation**: Not included at all
- **Impact**: Missing entire "sequential stress test" from validation

#### B. Randomized Initial Positions ❌
- **Paper Requirement**: Scenario 6 - simulates many-agent complexity
- **Implementation**: Standard fixed positions used
- **Impact**: Missing "many-agent simulation" validation component

### Wrong Horizon Distribution

**Paper Distribution**:
- 5 scenarios with h=400
- 1 scenario with h=800 (temporal decay stress test)

**Implementation Distribution**:
- 3 scenarios with h=400
- 3 scenarios with h=800 (no clear stress test purpose)

### Generic Naming Convention

**Paper**: Descriptive IDs indicating purpose
- `cramped_room_h400_baseline` (clearly baseline)
- `coordination_ring_h400_stress_spatial` (clearly stress test)

**Implementation**: Generic naming
- `cramped_room_h400_full_abc` (no indication of purpose)
- `coordination_ring_h400_full_abc` (missing stress test designation)

---

## 4. Impact on Results

### If We Proceed with Current Implementation

**Missing Coverage**:
- ❌ No "forced_coordination" layout (sequential dependencies untested)
- ❌ No randomized positions (many-agent simulation untested)
- ❌ Wrong balance of baseline vs stress scenarios

**Consequences**:
1. Paper claims "A+B+C validation" but only has partial A + partial B
2. Missing critical stress tests that distinguish O/R Index robustness
3. Figures/tables won't match paper methodology section
4. Reviewers will notice scenario mismatch

### If We Fix to Match Paper

**Required Changes**:
1. Add `forced_coordination` layout to environment wrapper
2. Implement randomized initial positions for cramped_room
3. Adjust horizon distribution (5×h400, 1×h800)
4. Use paper's naming convention
5. Fix checkpoint directory bug
6. Retrain all scenarios (~16-24 hours)

---

## 5. Recommendations

### Option A: Quick Fix (Use Current 6 Scenarios) ⚠️

**Pros**:
- Faster (just fix checkpoint bug and retrain ~6-8 hours)
- Still demonstrates O/R Index across multiple scenarios
- Simpler implementation

**Cons**:
- ❌ Doesn't match paper specification
- ❌ Missing forced_coordination and randomized positions
- ❌ Weaker scientific validation (missing stress tests)
- ❌ Potential reviewer criticism

**If Chosen**: Update EXPERIMENTAL_DESIGN.md to match implementation, not vice versa

### Option B: Full Paper Alignment (RECOMMENDED) ✅

**Pros**:
- ✅ Matches paper methodology exactly
- ✅ Complete A+B+C validation as claimed
- ✅ Stronger scientific rigor (includes all stress tests)
- ✅ No reviewer concerns about methodology mismatch

**Cons**:
- Requires forced_coordination layout implementation (2-3 hours)
- Requires randomized positions implementation (1-2 hours)
- Full retraining (~16-24 hours)

**Required Steps**:
1. Add `forced_coordination` layout to env_overcooked.py
2. Add `randomize_initial_positions` flag to env_overcooked.py
3. Update train_full_abc_validation.py scenarios to match paper
4. Fix checkpoint directory bug
5. Retrain all 6 scenarios with correct specification

### Option C: Hybrid Approach ⚙️

**Approach**:
- Use current 6 scenarios as "preliminary results"
- Implement forced_coordination + randomization separately
- Present current results as "subset validation"

**Best For**: Time-constrained submission where partial results acceptable

---

## 6. Bug Fixes Required (All Options)

### Fix 1: Checkpoint Directory Creation

**File**: `train_full_abc_validation.py`
**Location**: Lines 125-135

```python
# Current (BROKEN):
if save_path and (episode + 1) % save_every == 0:
    checkpoint_path = save_path / f"checkpoint_{episode + 1}.pth"
    torch.save({...}, checkpoint_path)  # FAILS - directory doesn't exist

# Fixed:
if save_path and (episode + 1) % save_every == 0:
    save_path.mkdir(parents=True, exist_ok=True)  # Create directory first
    checkpoint_path = save_path / f"checkpoint_{episode + 1}.pth"
    torch.save({...}, checkpoint_path)
```

### Fix 2: Final Model Save Path

**File**: `train_full_abc_validation.py`
**Location**: Line 201

```python
# Current (works but inconsistent):
final_path = save_dir / f"{checkpoint_name}.pth"

# Ensure directory exists:
save_dir.mkdir(parents=True, exist_ok=True)
final_path = save_dir / f"{checkpoint_name}.pth"
```

---

## 7. Next Steps

### Immediate Actions Required:

1. **Decide on Option A, B, or C** (see recommendations above)
2. **Fix checkpoint directory bug** (both options need this)
3. **Update implementation to match choice**:
   - Option A: Update EXPERIMENTAL_DESIGN.md to match current code
   - Option B: Update code to match EXPERIMENTAL_DESIGN.md
   - Option C: Document partial validation approach

### If Choosing Option B (Full Alignment):

**Implementation Checklist**:
- [ ] Add forced_coordination layout to OvercookedMARLEnv
- [ ] Add randomize_initial_positions parameter to OvercookedMARLEnv
- [ ] Update train_full_abc_validation.py scenarios list
- [ ] Fix checkpoint directory bug
- [ ] Update scenario naming to match paper convention
- [ ] Retrain all 6 scenarios
- [ ] Verify all .pth files saved correctly
- [ ] Proceed to collection (collect_full_abc.py)
- [ ] Proceed to analysis (analyze_full_abc.py)

**Time Estimate**:
- Implementation: 3-5 hours
- Training: 16-24 hours
- Collection: 15-20 minutes
- Analysis: 2-3 minutes
- **Total**: ~1.5-2 days

---

## 8. Verification Checklist

Before proceeding to collection, verify:

- [ ] All 6 scenarios match paper specification
- [ ] Each scenario has 4 .pth files (random, ppo_5k, ppo_50k, ppo_200k)
- [ ] Each .pth file has corresponding _meta.json
- [ ] Scenario naming matches paper convention
- [ ] forced_coordination layout working correctly
- [ ] Randomized positions creating diverse initial states
- [ ] Training logs show completion without errors

---

**Recommendation**: Choose **Option B (Full Paper Alignment)** for scientifically rigorous validation that matches the paper's methodology and withstands reviewer scrutiny.

**Next Action**: Await user decision on which option to proceed with.
