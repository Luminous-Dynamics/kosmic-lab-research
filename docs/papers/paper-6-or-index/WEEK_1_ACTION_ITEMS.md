# 📋 Week 1 Action Items (Nov 26 - Dec 3, 2025)

**Goal**: Launch all three tracks in parallel
**Deadline**: December 3, 2025
**Critical Success**: Theory Prop 4 drafted + MuJoCo 1 seed complete

---

## Track 1: Theory - Value Bound Theorem 🧮

### Day 1 (Nov 26) - TODAY
**Task**: Formalize assumptions and setup

- [ ] Read existing Proposition 1-3 in Section 3.5 of paper
- [ ] List explicit assumptions for local Taylor expansion
  - Local concavity of $J(\pi)$
  - Deterministic optimal policy $\pi^*$
  - Hessian boundedness
- [ ] Write assumption block in LaTeX
- [ ] Draft inequality statement: $\text{Regret}(\pi) \geq c \cdot (O/R(\pi) + 1)$

**Output**: `assumptions_draft.tex` (1 page)

### Day 2 (Nov 27)
**Task**: Taylor expansion derivation

- [ ] Write second-order Taylor expansion around $\pi^*$
- [ ] Show gradient term vanishes at optimum
- [ ] Express quadratic term as variance-weighted
- [ ] Connect $\text{Var}(P(a|o))$ to $\|\pi - \pi^*\|^2$

**Output**: Derivation notes (handwritten OK, will LaTeX later)

### Day 3 (Nov 28)
**Task**: Prove Proposition 4

- [ ] Define constant $c = \frac{\lambda_{\min}(H)}{2} \cdot \text{Var}(P(a))$
- [ ] Show Hessian bound: $(\pi - \pi^*)^T H (\pi - \pi^*) \leq -\lambda_{\min} \|\pi - \pi^*\|^2$
- [ ] Connect to O/R via $O/R + 1 = \text{Var}(P(a|o)) / \text{Var}(P(a))$
- [ ] Write proof sketch (1 page)

**Output**: Proposition 4 proof sketch

### Day 4 (Nov 29)
**Task**: Write interpretation paragraphs

- [ ] Explain why high O/R → high regret (intuition)
- [ ] Discuss limitations: LOCAL (not global), requires assumptions
- [ ] Frame as "diagnostic utility" not "universal theorem"

**Output**: Interpretation paragraphs for Section 3.6

### Day 5 (Nov 30)
**Task**: Internal review

- [ ] Re-read proof for logic errors
- [ ] Check inequality direction (≥ not ≤)
- [ ] Verify constant c is well-defined
- [ ] Ensure all assumptions stated explicitly

**Output**: Reviewed Proposition 4 (ready for Week 2 Bisimulation)

---

## Track 2: MuJoCo - Environment Setup 🤖

### Day 1 (Nov 26) - TODAY
**Task**: Install Multi-Agent MuJoCo

```bash
cd /srv/luminous-dynamics/kosmic-lab/docs/papers/paper-6-or-index/experiments/mujoco_validation

# Install dependencies
pip install mujoco>=3.0.0
pip install gymnasium[mujoco]>=0.29.0
pip install git+https://github.com/schroederdewitt/multiagent_mujoco

# Verify installation
python -c "import multiagent_mujoco; print('✅ MuJoCo installed')"
python -c "import mujoco; print('✅ MuJoCo base installed')"
```

**Checklist**:
- [ ] MuJoCo binary installed
- [ ] multiagent_mujoco package installed
- [ ] Can import without errors

**Output**: Installation verified

### Day 2 (Nov 27)
**Task**: Test environment loading

```python
import gymnasium as gym
import multiagent_mujoco

# Test loading
env = gym.make("ManyAgentAnt-v0")
obs = env.reset()
print(f"Observation space: {env.observation_space}")
print(f"Action space: {env.action_space}")
print(f"✅ Environment loads successfully")
```

**Checklist**:
- [ ] ManyAgentAnt-v0 loads without error
- [ ] Can reset() and get observations
- [ ] Observation/action spaces are correct

**Output**: Environment test script

### Day 3 (Nov 28)
**Task**: Implement continuous O/R computation

- [ ] Complete `ContinuousORMetric` class in `mujoco_or_trainer.py`
- [ ] Test on toy data (random observations + actions)
- [ ] Verify covariance trace computation
- [ ] Test k-means binning works

**Output**: Working continuous O/R computation (tested on toy data)

### Day 4-5 (Nov 29-30)
**Task**: Implement MAPPO trainer

- [ ] Copy MAPPO implementation from cross_algorithm experiments
- [ ] Adapt for MuJoCo environment
- [ ] Add O/R computation at checkpoints (every 50K steps)
- [ ] Test 1 training run (seed 42, 50K steps only)

**Output**: `mujoco_mappo_trainer.py` with working O/R logging

### Weekend (Dec 1-2)
**Task**: Launch first full training run

```bash
# Launch seed 42 (full 500K steps)
python mujoco_mappo_trainer.py --env ManyAgentAnt-v0 --seed 42 --steps 500000 --cuda

# Monitor progress
tail -f logs/mujoco_seed_42.log
```

**Deliverable**: 1 complete training run with 10 O/R measurements

---

## Track 3: IM Baseline - NOT STARTED YET ⏸️

**Start Date**: Week 2 (Dec 3)
**Reason**: MuJoCo has priority (Week 1 buffer needed)

---

## Week 1 Checkpoint (Dec 3)

### Success Criteria

**Track 1 (Theory)**: ✅ PASS if:
- [ ] Proposition 4 formally stated
- [ ] Proof sketch completed (1-2 pages)
- [ ] Assumptions explicitly listed
- [ ] Reviewed for correctness

**Track 2 (MuJoCo)**: ✅ PASS if:
- [ ] Environment installed and tested
- [ ] Continuous O/R computation working
- [ ] 1 training run complete (seed 42, 500K steps)
- [ ] 10 O/R measurements computed

**Track 3 (IM)**: ⏸️ Not started (expected)

---

## Contingency Plans

### If Theory is Hard
**Issue**: Proof logic error or unclear derivation
**Action**:
- Consult RL theory textbooks (Sutton & Barto, Szepesvári)
- Soften claim to "conjecture" with numerical evidence
- Move to appendix only

### If MuJoCo Installation Fails
**Issue**: MuJoCo binary license or installation error
**Action**:
- Use MuJoCo 2.3.7 (older, more stable)
- Try dm_control environments instead
- Fallback: Use PettingZoo MPE continuous (simple_push)

### If Training is Too Slow
**Issue**: 500K steps takes > 48 hours
**Action**:
- Reduce to 250K steps (5 checkpoints instead of 10)
- Use smaller environment (Swimmer instead of Ant)
- Accept fewer measurements (15 instead of 30)

---

## Daily Time Allocation

| Day | Theory | MuJoCo | Total |
|-----|--------|--------|-------|
| Nov 26 (Tue) | 3h | 3h | 6h |
| Nov 27 (Wed) | 4h | 3h | 7h |
| Nov 28 (Thu) | 4h | 4h | 8h |
| Nov 29 (Fri) | 3h | 5h | 8h |
| Nov 30 (Sat) | 3h | 2h | 5h |
| Dec 1 (Sun) | 2h | 3h | 5h |
| Dec 2 (Mon) | 1h | 2h | 3h |
| **Total** | **20h** | **22h** | **42h** |

---

## Communication

### Daily Stand-up (5 min each morning)
- What did I complete yesterday?
- What am I working on today?
- Any blockers?

### End-of-Week Review (Friday Dec 3)
- Track 1: Is Proposition 4 solid?
- Track 2: Is 1 seed complete?
- Decision: Continue with all 3 tracks or scale back?

---

## Files Created This Session ✅

1. **Theory**:
   - `experiments/theory/SECTION_3_6_THEORETICAL_ANALYSIS.tex` ✅
   - Template includes both Proposition 4 and Proposition 5

2. **MuJoCo**:
   - `experiments/mujoco_validation/README.md` ✅
   - `experiments/mujoco_validation/requirements.txt` ✅
   - `experiments/mujoco_validation/mujoco_or_trainer.py` ✅ (template)

3. **Planning**:
   - `FULL_ENHANCEMENT_ROADMAP_ICML2026.md` ✅ (comprehensive 8-week plan)
   - `WEEK_1_ACTION_ITEMS.md` ✅ (this file)

---

## Next Immediate Actions (RIGHT NOW)

### 1. Install MuJoCo (15 minutes)
```bash
cd /srv/luminous-dynamics/kosmic-lab/docs/papers/paper-6-or-index/experiments/mujoco_validation
pip install mujoco
pip install gymnasium[mujoco]
pip install git+https://github.com/schroederdewitt/multiagent_mujoco
python -c "import multiagent_mujoco; print('✅')"
```

### 2. Start Theory Draft (30 minutes)
- Open `SECTION_3_6_THEORETICAL_ANALYSIS.tex`
- Read current Section 3.5 (Theoretical Properties)
- List 3 assumptions explicitly
- Draft Proposition 4 statement

### 3. Test Environment (10 minutes)
```python
import gymnasium as gym
import multiagent_mujoco
env = gym.make("ManyAgentAnt-v0")
print(env.reset())
```

---

**Status**: Week 1 launched! 🚀
**Tracking**: Update this document daily with checkboxes
**Review**: Friday Dec 3 checkpoint meeting
