# Phase 0 Integration Checklist ✅

**Status**: Matrix game validation complete! Ready for paper integration.

**Validation Results**:
- ✅ Deterministic policy: O/R = -1.000 (perfect coordination)
- ✅ Random policy: O/R = 0.000 (no coordination)
- ✅ Monotonicity: Spearman ρ = 1.000, p < 0.001
- ✅ Matrix game: O/R ranges from -1.0 to ≈0.0 for this specific noise construction
- ✅ Proposition 1 (general case): O/R ∈ [-1, ∞), with -1 for deterministic and 0 for obs-independent
- ✅ Theory confirmed by user sanity check

---

## 📋 Integration Steps (15-20 minutes)

### Step 1: Add Theory Section to Main Text (Section 3.5)

**File**: `paper_6_or_index.tex`
**Location**: After Section 3.4 (around line 227)
**Source**: `theory_section_integration.tex`

**What to do**:
```latex
% After Section 3.4, add:

\subsection{Theoretical Properties}
\label{sec:theory}

[Paste entire contents of theory_section_integration.tex here]
```

**Contents includes**:
- Proposition 1: Range and Extremes (O/R ∈ [-1, ∞))
- Proposition 2: Monotonicity under Noise Mixing
- Proof sketches for both propositions
- 2×2 coordination game toy example with Table

**Estimated space**: ~1.5 pages (within NeurIPS 9-page limit)

---

### Step 2: Add Complete Proofs to Appendix

**File**: `paper_6_or_index.tex` (or separate appendix file)
**Location**: After Appendix A (around line 596)
**Source**: `appendix_b_theory.tex`

**What to do**:
```latex
% After Appendix A, add:

\section{Theoretical Properties: Complete Proofs}
\label{app:theory}

[Paste entire contents of appendix_b_theory.tex here]
```

**Contents includes**:
- Complete proof of Proposition 1 (with all edge cases)
- Complete proof of Proposition 2 (with ε-δ formulation)
- Extension to continuous action spaces (Appendix B.2)
- Algorithm 1: Continuous O/R computation
- Empirical validation figure reference

**Estimated space**: ~3 pages (appendix is unlimited)

---

### Step 3: Add Matrix Game Table to Main Text

**Location**: Within Section 3.5 (after Proposition 2)
**Source**: Output from `matrix_game_validation.py`

**Paste this LaTeX**:
```latex
\begin{table}[t]
\centering
\caption{O/R Index in 2×2 Coordination Game. We validate Proposition 2
empirically: as we increase noise level from 0 to 1, O/R increases smoothly
from -1.0 (deterministic) to 0.0 (random), with Spearman ρ = 1.0 (p < 0.001).}
\label{tab:toy_example}
\begin{tabular}{lcc}
\toprule
\textbf{Policy} & \textbf{O/R Index} & \textbf{Interpretation} \\
\midrule
Deterministic (optimal) & $-1.00$ & Strong coordination \\
Partially noisy (50\%) & $-0.25$ & Moderate coordination \\
Random & $0.00$ & No coordination \\
\bottomrule
\end{tabular}
\end{table}
```

**Supporting sentence in text**:
```latex
We validate Proposition 2 empirically in a 2×2 coordination game (Table~\ref{tab:toy_example}):
as we increase the noise level from 0 to 1, the O/R Index increases smoothly from −1.0
(deterministic policy) to approximately 0.0 (random policy), with Spearman ρ = 1.0 (p < 0.001);
see Appendix~\ref{app:theory} for complete validation results.
```

---

### Step 4: Add Validation Figure to Appendix B

**Location**: In Appendix B (after complete proofs)
**Source**: `figures/theory/figure_proposition2_validation.png`

**Paste this LaTeX**:
```latex
\begin{figure}[h]
\centering
\includegraphics[width=0.8\linewidth]{figures/theory/figure_proposition2_validation.png}
\caption{Empirical validation of Proposition 2 (Monotonicity under Noise Mixing)
in a 2×2 coordination game. The O/R Index increases smoothly from −1.0 (deterministic)
to ≈0.0 (random) as the noise level $\alpha$ increases, with Spearman $\rho = 1.0$
($p < 0.001$). Error bars show standard deviation across 10 trials.}
\label{fig:proposition2_validation}
\end{figure}
```

---

### Step 5: Update Abstract

**Location**: Abstract section (top of paper)
**Add one sentence**:

```latex
% Add after mentioning O/R Index definition:
We prove basic properties of the O/R Index (range, extremes, and monotonicity under
noise mixing) and validate generalization across spatial navigation and task-based
coordination environments.
```

---

### Step 6: Update Introduction (Contributions)

**Location**: Section 1 (Introduction), under "Contributions" list
**Add bullet point**:

```latex
\item We provide a theoretical characterization of the O/R Index, proving its range
$[-1, \infty)$ and monotonicity under noise mixing (Propositions 1–2), and validate
these properties empirically with a 2×2 coordination game.
```

---

### Step 7: Compile and Verify

```bash
# Navigate to paper directory
cd /srv/luminous-dynamics/kosmic-lab/docs/papers/paper-6-or-index

# Compile LaTeX (3 passes for cross-refs)
pdflatex paper_6_or_index.tex
bibtex paper_6_or_index
pdflatex paper_6_or_index.tex
pdflatex paper_6_or_index.tex

# Check output
evince paper_6_or_index.pdf  # or your PDF viewer
```

**Verify**:
- [ ] Section 3.5 appears with Propositions 1-2
- [ ] Table appears in main text
- [ ] Appendix B has complete proofs
- [ ] Figure appears in Appendix B
- [ ] All cross-references compile correctly (no "??")
- [ ] Page count: ≤9 pages main text + unlimited appendix
- [ ] No LaTeX errors or warnings

---

## 📊 Expected Impact on Paper

**Main Text**:
- Adds ~1.5 pages to Section 3 (theory)
- Adds 1 table (toy example)
- Adds 2 citations to appendix
- Total: Still within 9-page NeurIPS limit (can trim discussion if needed)

**Appendix**:
- Adds ~3 pages of complete proofs
- Adds 1 validation figure
- Total: No limit on appendix length

**Strengthens Paper**:
1. ✅ Addresses "lacks theoretical grounding" concern
2. ✅ Provides mathematical rigor (propositions with proofs)
3. ✅ Validates theory empirically (toy example)
4. ✅ Sets up continuous extension (Appendix B.2)
5. ✅ Makes O/R a "canonical object" for MARL coordination

---

## 🎯 Phase 0 Complete Checklist

- [x] **Theory section written** (theory_section_integration.tex)
- [x] **Appendix B written** (appendix_b_theory.tex)
- [x] **Matrix game implemented** (matrix_game_validation.py)
- [x] **Validation run** (perfect results: -1.0 → 0.0, ρ = 1.0)
- [x] **Sanity check passed** (user confirmed matches theory)
- [x] **LaTeX table generated** (ready to paste)
- [x] **Validation figure generated** (figures/theory/*.png)
- [ ] **Integrate into main paper** (this checklist)
- [ ] **Compile and verify** (LaTeX build succeeds)
- [ ] **Page count check** (≤9 pages main)

---

## 🚀 After Phase 0 Integration

Once paper compiles with theory section:

**Phase 1**: Overcooked validation (see `experiments/overcooked/README.md`)
```bash
cd experiments/overcooked
nix develop
make overcooked-all  # 4-6 hours GPU
```

**Phase 2**: Continuous control (optional stretch - see `PHASED_EXECUTION_PLAN.md`)

---

## 📝 Notes

- **Theory validated**: Matrix game shows perfect monotonicity (ρ = 1.0)
- **Ready for submission**: Phase 0 alone makes paper stronger
- **No blockers**: All files generated, just need copy-paste integration
- **Time estimate**: 15-20 minutes for integration + 5 minutes for compile check

---

**Status**: Phase 0 matrix game ✅ COMPLETE! Ready for paper integration.

**Next**: Copy-paste integration (this checklist) → Phase 1 Overcooked
