# Old Papers Update & Next Experiments Plan

**Date**: November 19, 2025
**Context**: Paper 6 (O/R Index) ready for ICML 2026 submission

---

## Part 1: Old Papers Update Strategy

### Current Paper Series Status

| Paper | Track | Title (Working) | Issue | Recommended Action |
|-------|-------|-----------------|-------|-------------------|
| 1 | B+C | Coherence-Guided Control | K-Index claimed to predict performance (not validated) | **Reframe** as behavioral diversity study |
| 2 | A | Baseline Studies | Same issue | **Reframe** or **Merge** with Paper 1 |
| 3 | D | Topology of Collective Coherence | K-Index as performance predictor | **Major reframe** - topology effects on behavior |
| 4 | E | Developmental Learning | K → training progress, not performance | **Reframe** as training dynamics metric |
| 5 | F/Unified | Adversarial Robustness / Unified Theory | Synthesis depends on flawed Papers 1-4 | **Hold** until Papers 1-4 fixed |
| **6** | **New** | **O/R Index Validation** | **None - properly validated** | **Submit to ICML 2026** |

### Recommended Update Strategy

#### Option A: Sequential Reframe (Conservative)
1. Reframe Papers 1-4 following PAPER_REFRAMING_GUIDE.md
2. Update all "performance prediction" claims to "behavioral measurement"
3. Add limitations sections acknowledging lack of external validation
4. Then update Paper 5 synthesis to reflect corrected findings

**Timeline**: 4-6 weeks per paper = 16-24 weeks total
**Pros**: Complete, thorough correction
**Cons**: Slow, Papers may be outdated by publication

#### Option B: Paper 6 First (Recommended)
1. **Submit Paper 6** (O/R Index) to ICML 2026 immediately
2. Reference Papers 1-5 as "prior exploration" in related work
3. Selectively update Papers 3 and 5 (strongest) after Paper 6 accepted
4. Archive Papers 1, 2, 4 as technical reports rather than publications

**Timeline**: Paper 6 now, selective updates over 6 months
**Pros**: Gets validated work published quickly, builds credibility
**Cons**: Some prior work remains unpublished

#### Option C: New Direction (Bold)
1. Submit Paper 6 (O/R Index) to ICML 2026
2. Treat Papers 1-5 as exploration that led to O/R Index discovery
3. Write Paper 7 as "From K-Index to O/R Index: Lessons in Metric Validation"
4. This meta-paper becomes the complete story

**Timeline**: Paper 6 now, Paper 7 in 3-4 months
**Pros**: Honest about scientific process, good story
**Cons**: Requires writing additional paper

### My Recommendation: Option B

Paper 6 is ready and properly validated. Submit it immediately. The older papers can be:
- Paper 3 (Topology): Reframe as "how topology affects behavioral diversity" - still interesting
- Paper 5 (Unified): Update after Paper 6 accepted, incorporating validated O/R Index
- Papers 1, 2, 4: Archive as technical reports for transparency

---

## Part 2: Next Experiments Plan

### Immediate Extensions (Before ICML Deadline: Jan 29)

#### 1. Real MARL Environments
**Goal**: Validate O/R Index in established benchmarks
**Environments**:
- Multi-Agent Particle Environment (MPE) - spread, adversary
- StarCraft Multi-Agent Challenge (SMAC)
- Google Research Football

**Expected Timeline**: 2-3 weeks
**Priority**: HIGH - strengthens Paper 6

#### 2. Communication Analysis
**Goal**: Test if O/R Index relates to communication effectiveness
**Experiments**:
- Measure message entropy vs O/R Index
- Test in CommNet / TarMAC architectures
- Communication ablation studies

**Expected Timeline**: 1-2 weeks
**Priority**: MEDIUM - good for supplementary

### Post-ICML Extensions (Paper 7+)

#### 3. O/R Index in Competitive Settings
**Goal**: Extend to mixed cooperative-competitive games
**Hypothesis**: Flexibility helps in competitive coordination
**Environments**: Predator-prey, adversarial tag

**Potential Paper 7**: "Behavioral Flexibility in Multi-Agent Competition"

#### 4. Transfer Learning Prediction
**Goal**: Does O/R Index predict transfer success?
**Experiments**:
- Train in environment A, test in B
- Correlate O/R with transfer performance
- Test generalization bounds

**Potential Paper 8**: "O/R Index Predicts Multi-Agent Transfer"

#### 5. O/R Regularization Curriculum
**Goal**: Optimize the λ schedule for flexibility training
**Experiments**:
- Early high λ, decay over time
- Task-dependent λ adjustment
- Meta-learning λ

**Enhancement for Paper 6 or 7**

#### 6. Theoretical Grounding
**Goal**: Connect O/R Index to information theory
**Analysis**:
- Relationship to mutual information decomposition
- Connection to intrinsic motivation literature
- Bounds on coordination capacity

**Potential Paper**: Theory venue (NeurIPS, ICML theory track)

### Experiment Priority Matrix

| Experiment | Impact | Effort | Timeline | Paper |
|------------|--------|--------|----------|-------|
| MPE Validation | HIGH | LOW | 1 week | Paper 6 supp |
| SMAC Validation | HIGH | MEDIUM | 2 weeks | Paper 6 supp |
| Communication Analysis | MEDIUM | MEDIUM | 2 weeks | Paper 6 supp |
| Competitive Settings | MEDIUM | MEDIUM | 3 weeks | Paper 7 |
| Transfer Learning | HIGH | HIGH | 4 weeks | Paper 8 |
| O/R Curriculum | MEDIUM | LOW | 1 week | Paper 6/7 |
| Theoretical | HIGH | HIGH | 6 weeks | Paper 9 |

---

## Part 3: Recommended Immediate Actions

### This Week (Nov 19-26)

1. **Finalize Paper 6 LaTeX** (in progress)
   - Complete PDF generation
   - Review formatting
   - Double-check all numbers

2. **Run MPE Validation**
   - Install PettingZoo/MPE (confirm gym>=0.26)
   - Test O/R Index in simple_spread
   - Add results to supplementary

3. **Generate Final Figures** ✅
   - Regenerated all with O/R Index labels
   - Publication quality confirmed

### Next Week (Nov 27 - Dec 3)

4. **Internal Review**
   - Complete read-through
   - Check statistical claims
   - Verify code matches text

5. **SMAC Validation**
   - Test in 2-3 SMAC scenarios (e.g., 3m map)
   - Use cloud compute (AWS) if local is slow
   - Aim for n=50+ per condition

6. **External Beta Read**
   - Post to arXiv as preprint
   - Solicit feedback from MARL community

### December (Dec 4-31)

7. **Polish and Format**
   - ICML 2026 template compliance
   - Reference formatting
   - Figure placement

8. **Code Repository**
   - Clean up experiment scripts
   - Add documentation
   - Release O/R-eval repo with MPE/SMAC wrappers

9. **Additional Experiments (if time)**
   - LLM-Agent Hybrids: Test Grok-like LLMs for decision-making in MPE
   - Ethical Dilemmas (quick supp): O/R in cooperative games with fairness penalties

### January (Jan 1-28)

10. **Final Submission Prep**
    - Abstract submission: **Jan 23, 2026** (AoE/UTC-0)
    - Paper submission: **Jan 28-29, 2026**
    - Supplementary materials
    - Prepare rebuttal materials (ICML has rebuttals)

---

## Part 4: Long-Term Research Direction

### The O/R Index Research Program

**Vision**: Establish O/R Index as a standard metric for MARL coordination quality

**Year 1 Goals**:
- Paper 6: Initial validation (ICML 2026)
- Paper 7: Competitive/mixed settings
- Paper 8: Transfer prediction
- Establish benchmark suite

**Year 2 Goals**:
- Theoretical foundations
- Real-world robotics validation
- Open-source toolkit release
- Workshop organization

**Success Metrics**:
- Citations to Paper 6
- Adoption in MARL papers
- Use in competitions/benchmarks

---

## Summary

1. **Submit Paper 6 (O/R Index) to ICML 2026** - ready now
2. **Archive Papers 1-2-4** as technical reports
3. **Selectively update Papers 3 and 5** after Paper 6 accepted
4. **Run MPE/SMAC validation** this week to strengthen supplementary
5. **Plan Papers 7-8** for competitive and transfer settings

The O/R Index provides a solid foundation for a productive research program. Paper 6 is the first validated contribution - build from there.

---

*"Start with what you can prove. The rest will follow."*
