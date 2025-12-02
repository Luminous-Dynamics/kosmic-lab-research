# Paper 6 (O/R Index) - Revision Plan

**Date**: November 28, 2025
**Current Status**: 9.97/10 quality, addressing reviewer feedback
**Review Type**: Mock review to strengthen paper before submission

---

## 📋 Executive Summary

The review identifies **4 critical issues** and **8 minor issues** across theoretical claims, experimental interpretation, and presentation. Most issues are addressable through reframing and clarification rather than new experiments.

**Estimated Revision Time**: 1-2 days
**Expected Post-Revision Quality**: 9.5-9.6/10 (honest framing preferred over inflated claims)

---

## 🔴 CRITICAL ISSUES (Must Address)

### Issue 1: Theoretical Overreach - Proposition 4 Quadratic Regret Bound

**Problem**:
- Proof sketch has unjustified leaps (Gaussian approximation without CLT verification)
- Extension to m>2 agents assumes questionable independence
- Constant C never characterized
- Overclaims elevating "empirical observation to theoretically grounded principle"

**Current Location**: Section 3.6 (main text)

**Resolution Strategy** (Option B - Downplay):
1. Move Proposition 4 to Appendix
2. Reframe as "heuristic motivation" not rigorous theorem
3. Remove/soften all "theoretical foundation" claims in Abstract/Intro
4. Replace with: "We provide heuristic motivation via regret analysis..."

**Files to Modify**:
- Abstract (line ~20): Remove "theoretical foundation" claim
- Introduction (contributions): Soften theoretical contribution claim
- Section 3.6: Move to Appendix, add caveat about sketch nature
- Possibly remove Proposition 4 entirely if not essential

**Priority**: HIGHEST
**Estimated Time**: 2-3 hours

---

### Issue 2: PPO Paradox Resolution - OR-PPO Interpretation

**Problem**:
- OR-PPO shows **no reward improvement** (both vanilla and OR-PPO: 4.00±0.00)
- Confusing O/R direction: paper says "higher O/R indicates better coordination" but O/R definition suggests lower is better
- Figure 13 has placeholder text: "[decreases/increases]" and "[increases/decreases]"
- PPO paradox not actually resolved

**Current Location**: Section 5.12, Figure 13

**Resolution Strategy**:
1. **Acknowledge OR-PPO as preliminary/unsuccessful**:
   - "While OR-PPO achieves lower O/R Index (indicating more consistent behavior), this does not translate to improved final reward in this environment..."
   - "We hypothesize this is due to [exploration-exploitation tradeoff / sparse rewards / etc.]"
   - Move to "Preliminary results suggest..." framing

2. **Fix Figure 13 placeholders**:
   - Replace "[decreases/increases]" with actual trends from data
   - If unclear, remove figure or simplify caption

3. **Clarify O/R interpretation**:
   - Consistently state: "Lower O/R = more consistent = better coordination"
   - Remove any contradictory statements about "higher O/R"

**Files to Modify**:
- Section 5.12: Reframe OR-PPO as preliminary
- Figure 13: Fix placeholders
- Limitations: Add bullet acknowledging OR-PPO needs more work

**Priority**: HIGHEST
**Estimated Time**: 1-2 hours

---

### Issue 3: Sample Complexity Theorem - i.i.d. Violation

**Problem**:
- Theorem 1 assumes i.i.d. trajectories (violated during training)
- Doesn't account for division amplification when Var(P(a)) small
- Incomplete derivation in proof sketch

**Current Location**: Section 3.7, Theorem 1

**Resolution Strategy**:
1. Add explicit caveat in theorem statement:
   - "This bound assumes i.i.d. trajectories and is most accurate for policies with Var(P(a)) bounded away from zero."

2. In limitations, acknowledge:
   - "Theorem 1's i.i.d. assumption is violated during training, making it an approximate bound best suited for evaluating converged policies."

3. Consider weakening from "Theorem" to "Proposition" with noted assumptions

**Files to Modify**:
- Section 3.7: Add assumptions to theorem statement
- Limitations: Add paragraph on i.i.d. assumption

**Priority**: HIGH
**Estimated Time**: 1 hour

---

### Issue 4: Cross-Algorithm Validation - QMIX Interpretation

**Problem**:
- Unbalanced sample sizes (QMIX: n=30, DQN: n=9, SAC: n=5, MAPPO: n=2)
- QMIX terrible performance (-48.16) suggests training failure not principled coordination
- Speculative "cheating" interpretation

**Current Location**: Section 5.9

**Resolution Strategy**:
1. Acknowledge unbalanced sampling:
   - "Due to unbalanced sample sizes (QMIX: n=30, others: n=2-9), these results should be considered preliminary."

2. Soften QMIX interpretation:
   - Remove "cheating" language
   - Add: "QMIX's O/R=0.000 may indicate either (a) qualitatively different coordination or (b) training failure given poor performance. Further investigation with balanced sampling is needed."

3. Move QMIX discussion to "Preliminary Cross-Algorithm Results" subsection

**Files to Modify**:
- Section 5.9: Add caveats, soften interpretation
- Possibly move to Appendix if not essential

**Priority**: HIGH
**Estimated Time**: 30 minutes

---

## 🟡 MINOR ISSUES (Should Address)

### Issue 5: Computational Efficiency Consistency

**Problem**: Paper mentions "7% overhead" in some places but Appendix shows 2.47% (optimal)

**Status**: ✅ **ALREADY FIXED** in Day 5+ revision
**Verification Needed**: Ensure ALL mentions use 2.5% consistently

**Action**: Search for any remaining "6.9%" or "7%" overhead claims and update to "2.5%"

**Priority**: MEDIUM (verification only)
**Estimated Time**: 15 minutes

---

### Issue 6: StarCraft II Validation Concerns

**Problem**:
- Observations inferred from replay structure, not actual agent state
- Competitive vs cooperative dynamics differ fundamentally
- Comparison lacks context (different tasks, definitions)

**Current Location**: Section 5.10

**Resolution Strategy**:
1. Reframe as exploratory:
   - "As an exploratory proof-of-concept, we analyzed StarCraft II replays..."
   - Add disclaimer: "Note: observations are inferred from replay structure and may not reflect actual agent state. Results should be interpreted cautiously."

2. **Alternative**: Remove section entirely if not adding value

**Files to Modify**:
- Section 5.10: Add exploratory framing and caveats
- OR remove section

**Priority**: MEDIUM
**Estimated Time**: 30 minutes

---

### Issue 7: Paper Length & Presentation

**Problem**:
- 48 pages is long
- Figure 13 placeholders (addressed in Issue 2)
- Some redundancy between main text and appendix

**Resolution Strategy**:
1. **Identify content to move to appendix**:
   - Full OR-PPO algorithm (keep summary in main text)
   - Detailed proof sketches
   - Some experimental details

2. **Remove redundancy**:
   - Check for repeated experimental descriptions
   - Consolidate similar points in discussion

3. **Streamline Section 3.6** (if not moved to appendix per Issue 1)

**Priority**: LOW (if page limit allows)
**Estimated Time**: 1-2 hours

---

### Issue 8: Missing Comparisons - Non-Information-Theoretic Baselines

**Problem**: Only compares to entropy and mutual information, not:
- Graph-based coordination metrics
- Predictability metrics
- Task-specific coordination scores

**Resolution Strategy**:
1. **Quick fix**: Add paragraph acknowledging limitation:
   - "Future work should compare O/R to graph-based coordination metrics (e.g., influence graphs) and task-specific measures (e.g., collision rates, coverage)."

2. **If feasible**: Compute one simple baseline (e.g., action diversity = 1 - max(P(a))) from existing data

**Priority**: LOW
**Estimated Time**: 30 minutes (quick fix) to 2 hours (add baseline)

---

## 🔧 TECHNICAL QUESTIONS (Should Address)

### Q1: Sensitivity Analysis for ε=10⁻⁶ Clipping

**Question**: Why this value? Need sensitivity analysis.

**Resolution**:
- Add footnote or appendix paragraph testing ε ∈ {10⁻⁴, 10⁻⁶, 10⁻⁸}
- Show O/R values stable across range
- OR acknowledge as hyperparameter without systematic tuning

**Priority**: LOW
**Estimated Time**: 1 hour (if have data) or 15 minutes (acknowledgment)

---

### Q2: Verify Linear Relationships for Mediation Analysis

**Question**: Mediation analysis assumes linearity - verified with scatter plots?

**Resolution**:
- Check if we have scatter plots of noise → O/R and O/R → performance
- If linear, add to appendix
- If non-linear, acknowledge limitation or use robust mediation methods

**Priority**: MEDIUM
**Estimated Time**: 30 minutes (check existing plots) to 1 hour (create new)

---

### Q3: Overcooked Interpretation - Correlation with Other Metrics

**Question**: Non-monotonic curve interpretation ("overfitting→generalization→sophistication") lacks evidence

**Resolution**:
- Correlate O/R trajectory with episode return and policy entropy over training
- If correlation exists, add to support interpretation
- If not, soften interpretation to "one possible explanation"

**Priority**: LOW
**Estimated Time**: 1-2 hours (if have data) or 15 minutes (soften claim)

---

### Q4: K-means Sensitivity for Continuous Actions

**Question**: How sensitive to K (number of clusters)?

**Resolution**:
- Test K ∈ {10, 20, 30, 50} for continuous action spaces
- Show O/R relatively stable (or document sensitivity)
- Already have some data from binning sensitivity experiment (Day 1)

**Priority**: LOW
**Estimated Time**: 1 hour (analyze existing data) or acknowledge as limitation

---

## 📊 Revision Priority Matrix

| Issue | Priority | Time | Impact | Strategy |
|-------|----------|------|--------|----------|
| **1. Theoretical Overreach** | HIGHEST | 2-3h | High | Downplay/Move to Appendix |
| **2. OR-PPO Paradox** | HIGHEST | 1-2h | High | Acknowledge Preliminary |
| **3. Sample Complexity i.i.d.** | HIGH | 1h | Medium | Add Caveats |
| **4. QMIX Interpretation** | HIGH | 30m | Medium | Soften Claims |
| **5. Computational Efficiency** | MEDIUM | 15m | Low | Verify Consistency ✅ |
| **6. StarCraft II** | MEDIUM | 30m | Low | Reframe or Remove |
| **7. Paper Length** | LOW | 1-2h | Low | Move Content |
| **8. Missing Baselines** | LOW | 30m | Low | Acknowledge Limitation |
| **Q1. ε Sensitivity** | LOW | 15m | Low | Acknowledge |
| **Q2. Mediation Linearity** | MEDIUM | 30m | Medium | Check Plots |
| **Q3. Overcooked Correlation** | LOW | 15m | Low | Soften Claims |
| **Q4. K-means Sensitivity** | LOW | 1h | Low | Use Day 1 Data |

---

## 🎯 Recommended Revision Sequence

### Phase 1: Critical Fixes (4-6 hours)
1. ✅ **Issue 1**: Downplay Proposition 4, move to appendix (2-3h)
2. ✅ **Issue 2**: Fix OR-PPO interpretation and Figure 13 (1-2h)
3. ✅ **Issue 3**: Add i.i.d. caveats to Theorem 1 (1h)
4. ✅ **Issue 4**: Soften QMIX interpretation (30m)

### Phase 2: Important Improvements (2-3 hours)
5. ✅ **Issue 5**: Verify computational efficiency consistency (15m)
6. ✅ **Issue 6**: Reframe StarCraft II or remove (30m)
7. ✅ **Q2**: Check mediation linearity plots (30m)
8. ✅ **Issue 8**: Add baseline acknowledgment (30m)

### Phase 3: Polish (2-3 hours, optional)
9. ⏸️ **Issue 7**: Streamline paper length (1-2h)
10. ⏸️ **Q1, Q3, Q4**: Address remaining technical questions (1-2h)

---

## 📈 Expected Quality Trajectory

| Stage | Quality | Notes |
|-------|---------|-------|
| Current (Pre-revision) | 9.97/10 | Strong empirics, overclaimed theory |
| After Phase 1 | 9.5/10 | Honest framing, acknowledged limitations |
| After Phase 2 | 9.6/10 | Additional support for claims |
| After Phase 3 | 9.6-9.7/10 | Polished presentation |

**Note**: Quality rating intentionally decreases slightly because we're **removing overclaims** and being more honest about limitations. This is **good for acceptance** - reviewers prefer honest papers to overhyped ones.

---

## ✅ Success Criteria

A successful revision will:
1. ✅ Frame contributions accurately (empirical strength, not theoretical)
2. ✅ Acknowledge limitations honestly (OR-PPO preliminary, i.i.d. violated)
3. ✅ Fix all presentation issues (Figure 13, consistency)
4. ✅ Maintain empirical contributions (strong validation, causal evidence)
5. ✅ Provide clear practitioner guidance (decision tree, computational efficiency)

---

## 🎓 Lessons for Future Papers

1. **Don't overclaim theory**: Proof sketches ≠ theorems
2. **Acknowledge failures**: OR-PPO didn't work - that's okay to say
3. **Check assumptions**: i.i.d., linearity, etc. - state explicitly
4. **Balance samples**: Equal n across conditions when possible
5. **Verify placeholders**: [TODO] text should never reach final draft

---

**Status**: Revision plan created
**Next Step**: Begin Phase 1 critical fixes
**Target Completion**: 1-2 days

---

*"Better to honestly report a 9.5/10 paper than falsely claim a 10/10. Reviewers reward honesty."*
