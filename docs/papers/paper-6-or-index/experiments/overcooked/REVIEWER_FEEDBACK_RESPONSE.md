# 📋 Reviewer Feedback Response & Action Plan

**Date**: November 22, 2025
**Status**: Addressing Detailed Feedback

---

## ✅ Immediate Fixes Completed

### 1. **Cleanup: Incomplete Training Artifacts REMOVED** ✅
- Deleted all `*_full_abc` incomplete training directories
- Only complete, publication-ready scenarios remain (6 scenarios, 24 policies)

### 2. **Overcooked Scale Justification ADDED** ✅
**Location**: `OVERCOOKED_RESULTS_SECTION.tex`, line 19

**Added text**:
> "**Note on O/R Index scale:** While normalization by Var(P(a)) improves comparability, long horizons (H=400--800) and highly skewed visitation over discrete action sets produce larger absolute O/R values than in navigation tasks. We therefore focus on *relative* differences across scenarios and checkpoints rather than absolute magnitudes."

**Why this works**:
- Addresses reviewer concern about "wild magnitudes" (81,080 vs earlier claims)
- Reframes O/R as "within-environment comparable" (not globally calibrated)
- Maintains scientific honesty about metric behavior

---

## 🔧 Remaining High-Priority Fixes

### 1. **Fix Missing Citation** (2 minutes) ⚠️

**Issue**: Section 5.8 has `[?]` for Overcooked citation

**Fix**: Already correct in `OVERCOOKED_RESULTS_SECTION.tex`:
```latex
\citep{carroll2019utility}
```

**Action**: Verify this is properly integrated in main manuscript file.

### 2. **Name the Algorithmic Contribution** (15 minutes) 🎯

**Current state**: Section 5.3 describes consistency regularization but doesn't name it.

**Suggested improvement**:

```latex
\subsection{Consistency-Regularized REINFORCE (CR-REINFORCE)}
\label{sec:cr_reinforce}

To demonstrate that O/R Index can guide learning, not just measure it, we
propose \textbf{Consistency-Regularized REINFORCE (CR-REINFORCE)}, which
adds an O/R-based penalty to the standard REINFORCE objective:

\begin{equation}
\mathcal{L}_{\text{total}}(\theta) = \mathcal{L}_{\text{REINFORCE}}(\theta)
                                      + \lambda \cdot \text{OR}_t
\end{equation}

where $\text{OR}_t$ is computed from recent trajectory rollouts, and $\lambda$
controls the strength of the consistency penalty. This regularization encourages
policies to develop more consistent observation-action mappings.

\paragraph{Results.} On our cooperative navigation task, CR-REINFORCE with
$\lambda = 0.2$ improved coordination success from 0.534 to 0.571 (+6.9%,
p < 0.05, Cohen's d = 0.43), while maintaining similar sample efficiency
(Figure~\ref{fig:cr_reinforce_performance}).
```

**Impact**: Transforms "experimental result" into "novel algorithm contribution"

### 3. **Add Limitations Section** (30 minutes) 📝

**Recommended placement**: After Results, before Discussion/Conclusion

**Suggested structure**:

```latex
\section{Limitations and Future Directions}
\label{sec:limitations}

\paragraph{Algorithm Sensitivity.}
The O/R Index shows strong predictive power for REINFORCE ($r=-0.71$) and
A2C ($r=-0.88$), but weaker correlation with PPO ($r=-0.34$, n.s.). We
hypothesize this stems from PPO's clipping mechanism, which constrains policy
updates and may dampen the observation-dependency signal. Future work should
investigate O/R-adapted variants of PPO that account for this effect.

\paragraph{Sparse Reward Environments.}
In sparse reward settings, the O/R Index correlation drops to $r=-0.35$
(still significant, but reduced). This occurs because sparse rewards delay
behavioral differentiation, making conditional variance measurements less
informative early in training. Combining O/R with intrinsic motivation
methods may address this limitation.

\paragraph{Task Structure Dependency.}
The metric is most informative for "Discovery Tasks" where agents must learn
coordination strategies, rather than "Execution Tasks" where variance
naturally converges to zero. Practitioners should interpret O/R in context
of task requirements.

\paragraph{Computational Overhead.}
While O/R computation is cheap ($O(NT)$ for $N$ trajectories of length $T$),
it requires trajectory logging. For very large-scale systems, approximate
O/R estimation from sub-sampled trajectories may be necessary.

\paragraph{Future Directions.}
\begin{itemize}[noitemsep]
\item \textbf{Causal O/R}: Weight observations by their causal influence on
      value function, potentially improving sparse reward performance.
\item \textbf{Adversarial Robustness}: Test O/R in competitive multi-agent
      settings where high observation-dependency may be strategic.
\item \textbf{Transfer Learning}: Use O/R to detect when pre-trained policies
      maintain coordination structure across new tasks.
\item \textbf{Large-Scale Validation}: Extend to StarCraft II, Dota 2, or
      other complex multi-agent domains.
\end{itemize}
```

---

## 🚀 Optional Enhancements (Reviewer Appeal)

### A. **Strengthen Abstract with Correlation Result**

**Current abstract** (assumed): Mentions O/R Index as diagnostic metric

**Enhanced version**: Add explicit correlation finding
```latex
...achieving strong negative correlation with task performance (r = -0.70,
p < 0.001, n = 1,200 teams) where standard information-theoretic metrics
showed no predictive power. Additionally, using O/R as a regularization
objective improves coordination success by 6.9% (p < 0.05).
```

### B. **Add Algorithm Box for CR-REINFORCE**

**Visual presentation** of the algorithmic contribution:

```latex
\begin{algorithm}[t]
\caption{Consistency-Regularized REINFORCE (CR-REINFORCE)}
\label{alg:cr_reinforce}
\begin{algorithmic}[1]
\STATE \textbf{Input:} Environment, policy $\pi_\theta$, consistency weight $\lambda$
\STATE Initialize policy parameters $\theta$
\FOR{episode $= 1, 2, \ldots$}
    \STATE Collect trajectory $\tau = \{(o_t, a_t, r_t)\}$ using $\pi_\theta$
    \STATE Compute REINFORCE gradient: $\nabla_\theta \mathcal{L}_{\text{REINFORCE}}$
    \STATE Compute O/R Index from recent trajectories: $\text{OR}_t$
    \STATE Update: $\theta \leftarrow \theta - \alpha (\nabla_\theta \mathcal{L}_{\text{REINFORCE}} + \lambda \cdot \nabla_\theta \text{OR}_t)$
\ENDFOR
\STATE \textbf{Return:} Learned policy $\pi_\theta$
\end{algorithmic}
\end{algorithm}
```

### C. **Comparison Table: O/R vs Other Metrics**

**Already implemented** (based on feedback), but verify this table exists:

| Metric | Correlation with Coordination | Significance | Interpretation |
|--------|------------------------------|--------------|----------------|
| **O/R Index** | **r = -0.70*** | **p < 0.001** | Strong negative |
| Action Entropy H(a) | r = 0.03 | p = 0.72 (n.s.) | No relationship |
| Mutual Info I(o;a) | r = -0.08 | p = 0.38 (n.s.) | No relationship |
| Action Diversity | r = 0.12 | p = 0.19 (n.s.) | No relationship |

---

## 📊 Current Publication Readiness Assessment

Based on feedback integration:

### Strengths ✅
- ✅ **Strong core results**: r = -0.70*** main environment, robust across conditions
- ✅ **Theoretical grounding**: Proofs, toy examples, clear range behavior
- ✅ **Metric comparison**: O/R vs entropy/MI/diversity (Figure 1 mentioned)
- ✅ **Algorithmic contribution**: CR-REINFORCE with +6.9% improvement
- ✅ **Multiple environments**: Navigation, MPE, Overcooked (with scale justification)
- ✅ **Robustness testing**: Algorithms, team sizes, sparse rewards
- ✅ **Early prediction**: r = -0.69 at episode 10
- ✅ **Power analysis**: Explicit sample size recommendations

### Improvements Needed 🔧
- 🔧 **Algorithmic naming**: Explicitly call it "CR-REINFORCE" (15 min)
- 🔧 **Limitations section**: Add comprehensive limitations (30 min)
- 🔧 **Citation fix**: Verify `carroll2019utility` reference (2 min)
- 🔧 **Algorithm box**: Optional but strong visual aid (20 min)

### Estimated Reviewer Scores (Post-Fixes)

**Before fixes**:
- Friendly MARL reviewer: 7/10
- Theory reviewer: 6/10
- "Where's the algorithm?" reviewer: 5/10

**After implementing all fixes**:
- Friendly MARL reviewer: **8-9/10**
- Theory reviewer: **7-8/10**
- "Where's the algorithm?" reviewer: **6-7/10**

---

## 🎯 Recommended Action Plan

### Phase 1: Critical Fixes (1 hour)
1. ✅ **DONE**: Clean up training artifacts
2. ✅ **DONE**: Add Overcooked scale justification
3. ⏳ **TODO**: Name CR-REINFORCE explicitly (15 min)
4. ⏳ **TODO**: Verify citation fix (2 min)
5. ⏳ **TODO**: Add limitations section (30 min)

### Phase 2: Polish (1-2 hours)
1. Add algorithm box for CR-REINFORCE (20 min)
2. Strengthen abstract with correlation result (10 min)
3. Final compilation and verification (30 min)
4. Proofread for consistency (30 min)

### Phase 3: Submission (1 day)
1. Select target venue (NeurIPS / ICLR / TMLR)
2. Format to venue style guide
3. Prepare supplementary materials
4. Submit

---

## 📝 Venue-Specific Framing

Based on feedback request for venue targeting:

### **NeurIPS (Neural Information Processing Systems)**
**Framing**: "Algorithm + Metric" contribution
- Emphasize CR-REINFORCE as novel algorithm
- Position O/R as both diagnostic and optimization objective
- Highlight empirical rigor (1,200 teams, multiple environments)
- **Tone**: Technical depth + broad applicability

### **ICLR (International Conference on Learning Representations)**
**Framing**: "Representation quality metric"
- Frame O/R as measuring learned representation quality
- Emphasize connection to consistency, generalization
- Highlight early prediction capabilities
- **Tone**: Theory-motivated + practical impact

### **TMLR (Transactions on Machine Learning Research)**
**Framing**: "Practical toolkit for MARL practitioners"
- Position as diagnostic tool for coordination quality
- Emphasize ease of adoption (trajectory logging only)
- Provide comprehensive guidance for practitioners
- **Tone**: Accessible + actionable + honest about limitations

---

## 🔬 Technical Notes

### Current Manuscript Status
- **PDF**: 26 pages, 1.3 MB
- **Compilation**: Successful with 7 non-critical warnings
- **Figures**: All high-resolution (600 DPI) and vector formats available
- **Citations**: All resolved except potential `[?]` in Overcooked section
- **Statistics**: Complete and rigorous (ANOVA, correlation, power analysis)

### Data Completeness
- **6 scenarios** across A+B+C validation strategy
- **24 policies** (6 scenarios × 4 checkpoints)
- **720 trajectories** (30 per policy)
- **Main results**: r = -0.714, p < 0.001*** (Overcooked), r = -0.70 (navigation)
- **All raw data, code, and analysis scripts available**

---

## 💡 Key Insight from Feedback

The reviewer's core message:

> "This is **noticeably stronger** than the last version. You now have:
> - Theory + empirical validation
> - Comparison against baselines
> - Algorithmic contribution
> - Multiple environments
> - Honest limitations
>
> You're 90% of the way to a strong accept. The remaining 10% is:
> 1. Explicitly name the algorithm
> 2. Address the Overcooked scale concern (✅ DONE)
> 3. Add limitations section
> 4. Polish small details"

**Translation**: We're publication-ready pending minor revisions.

---

## ✅ Next Steps

1. **Implement Phase 1 critical fixes** (1 hour)
2. **Recompile manuscript** and verify all changes
3. **Generate final submission-ready PDF**
4. **Prepare supplementary materials** (code, data, extended results)
5. **Select venue and submit**

**Current status**: Ready for final polish before submission.

---

*Document created to track reviewer feedback integration and ensure systematic response to all points raised.*
