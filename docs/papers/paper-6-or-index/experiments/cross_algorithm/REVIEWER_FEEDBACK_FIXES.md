# Reviewer Feedback Fixes - Immediate Action Items

**Date**: November 26, 2025
**Status**: Ready to implement
**Priority**: HIGH - These fixes address concrete reviewer concerns

---

## 🎯 Summary of Issues

**Critical Fixes** (Must do before submission):
1. Fix 4 undefined cross-references
2. Clarify "higher vs lower O/R" language
3. Add explicit "null reward, non-null structure" point
4. Make PPO paradox cross-reference explicit
5. Soften "naive" language in limitations

**Status**: All issues identified with exact line numbers and fix solutions ready

---

## 1. Fix Undefined Cross-References (4 issues) ⚠️ CRITICAL

### Issue 1.1: Missing label for "Main Finding" subsection
**Location**: Line 393
**Problem**: `\ref{subsec:main_finding}` undefined
**Fix**: Add label after subsection title

```latex
\subsection{Main Finding: O/R Index Predicts Coordination}
\label{subsec:main_finding}

Across 1,200 teams, lower \ORIndex{} (more consistent behavior) strongly predicts coordination success...
```

### Issue 1.2: Missing label for "Metric Computation Details" subsection
**Location**: Line 239
**Problem**: `\ref{subsec:computation}` undefined
**Fix**: Add label after subsection title

```latex
\subsection{Metric Computation Details}
\label{subsec:computation}

To compute O/R Index from trajectory data...
```

### Issue 1.3: Missing label for "Statistical Power" subsection
**Location**: Line 544
**Problem**: `\ref{subsec:power}` undefined
**Fix**: Add label after subsection title

```latex
\subsection{Statistical Power}
\label{subsec:power}

All correlations reported in this paper are Pearson correlations...
```

### Issue 1.4: Wrong appendix reference
**Location**: Line 644 (in Limitations section)
**Problem**: `\ref{app:continuous}` should be `\ref{app:continuous_or}`
**Current**:
```latex
The theoretical extension to continuous actions (Appendix~\ref{app:continuous}) provides a foundation...
```
**Fixed**:
```latex
The theoretical extension to continuous actions (Appendix~\ref{app:continuous_or}) provides a foundation...
```

**Impact**: All 4 "??" in PDF will resolve to proper section numbers

---

## 2. Clarify "Higher vs Lower O/R" Language 🔍

### Issue: Confusing sign interpretation
**Reviewer Comment**:
> "OR-PPO achieves a higher final O/R Index (−0.0371 vs −0.0384)" is technically correct but confusing since −0.0371 is "higher" than −0.0384 but represents better consistency

### Fix: Use "less negative" consistently

**Search for this pattern** in OR-PPO section (around lines 640-750):
```bash
grep -n "higher.*O/R\|higher final O/R" paper_6_or_index.tex
```

**Replace instances like**:
```latex
OR-PPO achieves a higher final O/R Index (−0.0371 vs −0.0384), indicating more organized and more stable coordination policies.
```

**With**:
```latex
OR-PPO achieves a less negative O/R Index (−0.0371 vs −0.0384, i.e., closer to zero), indicating more organized and more stable coordination policies.
```

**Or add clarifying parenthetical**:
```latex
OR-PPO achieves a higher (i.e., less negative) O/R Index (−0.0371 vs −0.0384), indicating more organized and more stable coordination policies.
```

**Also add reminder in Overcooked section** (around line 690):
```latex
\paragraph{Interpretation.}
Recall that in this normalization, less negative O/R corresponds to more consistent behavior (Section~\ref{subsec:theory_properties}). OR-PPO achieves...
```

---

## 3. Make "Null Reward, Non-Null Structure" Explicit 💡

### Issue: Underplaying key insight
**Reviewer Comment**:
> "This is a key advantage of O/R-based control: it can improve coordination structure and stability even when coarse reward metrics are saturated"

### Fix: Add explicit paragraph in OR-PPO section

**Location**: After Table 7 interpretation (around line 720)

**Add**:
```latex
This resulted in identical task performance but revealed important differences in policy structure. \textbf{This illustrates a key advantage of O/R-based control: it can improve coordination structure and stability even when coarse reward metrics are saturated.} In many real-world multi-agent systems, reward-level performance may plateau while coordination quality continues to vary—O/R Index captures these structural differences that reward alone cannot detect.
```

---

## 4. Make PPO Paradox Cross-Reference Explicit 🔗

### Issue: Missing narrative loop
**Reviewer Comment**:
> "You already reference the paradox earlier in Section 5.4 (PPO row with r = −0.34, n.s.), but the OR-PPO section should tie back directly"

### Fix: Add explicit cross-reference in OR-PPO section

**Location**: In OR-PPO introduction (around line 640-650)

**Current** (approximately):
```latex
This automatic adaptation addresses the 'PPO paradox'...
```

**Enhanced**:
```latex
This automatic adaptation addresses the 'PPO paradox' identified in Section~\ref{subsec:algorithm_gen}, where standard PPO showed weak correlation with O/R (r = −0.34, n.s.) compared to REINFORCE (r = −0.71***), by restoring dynamic range in O/R while preserving PPO's stability benefits.
```

---

## 5. Soften "Naive" Language in Limitations 🎨

### Issue: Underselling own contribution
**Reviewer Comment**:
> "Don't call your own method 'naive' in quite such a blunt way"

### Fix: Reframe language

**Location**: Limitations section, OR-PPO Generalization paragraph (around line 660-670)

**Current** (approximately):
```latex
The null result on final reward, while scientifically valuable, suggests that naive adaptive control may not always improve performance.
```

**Fixed**:
```latex
The null result on final reward, while scientifically valuable, suggests that this first OR-PPO instantiation may not always improve reward-level performance, and that more sophisticated adaptation schemes or environments with richer reward signals may be needed.
```

---

## 6. Interpret Small Effect Size Positively ✨

### Issue: Preempt "is 3.5% meaningful?" question
**Location**: After reporting OR-PPO results (around line 725)

**Add qualifying clause**:
```latex
Although the absolute difference in O/R is modest (3.5%), it is consistent across seeds and accompanied by a 14% reduction in variance, indicating more reliably coordinated behavior.
```

---

## 📋 Implementation Checklist

### Step 1: Add Missing Labels (5 minutes)
- [ ] Add `\label{subsec:main_finding}` after line 393
- [ ] Add `\label{subsec:computation}` after line 239
- [ ] Add `\label{subsec:power}` after line 544
- [ ] Change `\ref{app:continuous}` to `\ref{app:continuous_or}` at line 644

### Step 2: Clarify O/R Language (10 minutes)
- [ ] Find all "higher O/R" instances in OR-PPO section
- [ ] Replace with "less negative" or add "(i.e., less negative)" parenthetical
- [ ] Add reminder paragraph in Overcooked interpretation

### Step 3: Strengthen Messaging (10 minutes)
- [ ] Add "null reward, non-null structure" paragraph after Table 7
- [ ] Add PPO paradox cross-reference in OR-PPO intro
- [ ] Interpret 3.5% effect size positively

### Step 4: Polish Limitations (5 minutes)
- [ ] Replace "naive" with "this first instantiation"
- [ ] Add constructive framing

### Step 5: Recompile and Verify (5 minutes)
```bash
cd /srv/luminous-dynamics/kosmic-lab
nix develop
cd docs/papers/paper-6-or-index

# Full compilation
pdflatex -interaction=nonstopmode paper_6_or_index.tex
bibtex paper_6_or_index
pdflatex -interaction=nonstopmode paper_6_or_index.tex
pdflatex -interaction=nonstopmode paper_6_or_index.tex

# Verify no undefined references
grep "undefined" paper_6_or_index.log | grep -i "reference\|label"
# Should be empty!
```

### Step 6: Final Check
- [ ] All "??" replaced with section numbers
- [ ] O/R sign language clear and consistent
- [ ] PPO paradox narrative loop complete
- [ ] Limitations section constructive, not self-deprecating

---

## 🎯 Expected Impact

**Before fixes**:
- 4 undefined references showing as "??" (unprofessional)
- Confusing O/R sign interpretation
- Underselling key insights
- Self-deprecating limitations

**After fixes**:
- All cross-references resolve properly
- Clear, consistent language throughout
- Key insights explicitly stated
- Honest but constructive limitations

**Paper Quality**: Remains 9.7/10, but presentation becomes publication-ready

**Reviewer Perception**:
- Before: "Good paper with some sloppiness"
- After: "Polished, professional contribution ready for publication"

---

## 📊 Remaining Phase 2 Enhancements (Optional)

According to CLAUDE.md, 5/11 Phase 2 enhancements complete. The 6 remaining would bring paper from 9.7/10 → 9.8-9.9/10:

**Completed** (Already in paper):
1. ✅ A.1: Causal Intervention (Section 5.1.1)
2. ✅ C.1: Intuition Figure (Section 3.2)
3. ✅ B.1: Information-Theoretic Connection (Proposition 3)
4. ✅ C.2: Learning Phase Diagram (Section 5.2)
5. ✅ C.3: Decision Tree (Section 6.2)

**Remaining** (Would add further polish but not required):
1. A.2: Intervention Analysis visualization
2. A.3: Mediation path figure
3. B.2: Formal comparison table with MI/Entropy
4. B.3: When each metric excels
5. C.4: Algorithm selection flowchart
6. C.5: Interactive diagnostic tool description

**Recommendation**: Apply the 6 critical fixes above FIRST, then consider remaining enhancements if time permits.

---

*All fixes ready for immediate implementation. Estimated total time: 35 minutes.*
