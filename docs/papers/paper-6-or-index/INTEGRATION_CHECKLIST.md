# Paper 6 Enhancement: Integration Checklist

## 🎯 Week 1 Theory Integration

### ✅ Day 1-2: LaTeX Integration (15-20 minutes)

**Pre-Integration:**
- [ ] Read `README_ENHANCEMENTS.md` for orientation
- [ ] Read `THEORY_INTEGRATION_GUIDE.md` for detailed steps
- [ ] Backup current `paper_6_or_index.tex` (copy to `paper_6_or_index.tex.backup`)

**Section 3.5 Integration:**
- [ ] Open `paper_6_or_index.tex` in editor
- [ ] Find line 227 (end of Section 3.4)
- [ ] Copy contents of `theory_section_integration.tex`
- [ ] Paste after Section 3.4
- [ ] Verify section numbering: 3.1, 3.2, 3.3, 3.4, **3.5** ✓

**Appendix B Integration:**
- [ ] Find line 596 (after Appendix A.7, before "Supplementary Figures")
- [ ] Copy contents of `appendix_b_theory.tex`
- [ ] Paste between Appendix A and old Appendix B
- [ ] Verify appendix structure: A, **B (new)**, C (was B), D (was C) ✓

**Appendix Renumbering:**
- [ ] Change line ~597: `\section{Supplementary Figures}` stays same, just now "Appendix C"
- [ ] Change line ~611: `\section{Code Availability}` stays same, just now "Appendix D"
- [ ] Search and replace any `\ref{app:supplementary_figures}` → update if found
- [ ] Search and replace any `\ref{app:code_availability}` → update if found

**Compilation:**
- [ ] Run: `pdflatex paper_6_or_index.tex` (first pass)
- [ ] Run: `pdflatex paper_6_or_index.tex` (second pass for cross-refs)
- [ ] Check output for errors (ignore warnings about multiply-defined labels on first pass)
- [ ] Verify PDF opens correctly

**Verification:**
- [ ] Section 3.5 "Theoretical Properties" visible after Section 3.4
- [ ] Proposition 1 (Range and Extremes) appears in Section 3.5
- [ ] Proposition 2 (Monotonicity under Noise Mixing) appears in Section 3.5
- [ ] Toy example (2×2 matrix game) appears in Section 3.5
- [ ] Appendix B "Theoretical Details and Proofs" appears
- [ ] Appendix B.1 "Proofs for Discrete O/R Index" appears
- [ ] Appendix B.2 "Extension to Continuous Action Spaces" appears
- [ ] Algorithm 1 (Continuous O/R estimator) appears in B.2
- [ ] Cross-reference `\ref{prop:range_extremes}` resolves correctly
- [ ] Cross-reference `\ref{app:proofs_discrete}` resolves correctly
- [ ] Page count increased by ~4-5 pages (now ~22-23 pages)
- [ ] All existing figures still display correctly

**Success Criteria:**
✅ PDF compiles without errors
✅ All new sections visible and properly numbered
✅ Page count ~22-23 pages (from original ~18)
✅ Cross-references resolve (second pdflatex run)

---

### 📝 Day 3-4: Matrix Game Implementation (Optional, 8 hours)

**Setup:**
- [ ] Create directory: `experiments/matrix_game/`
- [ ] Create file: `matrix_game.py`

**Implementation:**
- [ ] Define `CoordinationGame` class (2×2 matrix)
- [ ] Implement `policy_deterministic(obs)` function
- [ ] Implement `policy_noisy(obs, noise_level)` function
- [ ] Create trajectory collection function
- [ ] Implement O/R computation for toy example

**Validation Experiment:**
- [ ] Run experiment with noise levels: [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
- [ ] Verify O/R increases monotonically with noise
- [ ] Expected: O/R(0.0) = -1.0, O/R(0.5) ≈ 1.35
- [ ] Generate figure: `figure_matrix_game.png`

**Paper Update:**
- [ ] Add figure to Appendix B.3 (new subsection)
- [ ] Write caption explaining validation of Proposition 2
- [ ] Update Section 3.5 to reference Appendix B.3 validation

**Success Criteria:**
✅ Matrix game O/R increases with noise (validates Proposition 2)
✅ Figure integrated into Appendix B
✅ Experimental validation mentioned in main text

---

### 📊 Day 5-7: Optional Enhancements (6 hours)

**Abstract Update (Optional):**
- [ ] Find abstract (line ~49)
- [ ] Add sentence: "We provide formal characterization of O/R's theoretical properties..."
- [ ] Update final sentence to mention "theoretically grounded diagnostic"

**Contributions Update (Optional):**
- [ ] Find Section 1.1 (line ~107)
- [ ] Add bullet: "Theoretical grounding: formal characterization of O/R properties..."

**Discussion Update (Optional):**
- [ ] Find Section 6.3 Future Work (line ~397)
- [ ] Add item: "Validate continuous O/R extension (Appendix B.2) in continuous control..."

**Final Compilation:**
- [ ] Run pdflatex twice
- [ ] Check all cross-references
- [ ] Verify page count
- [ ] Proofread new sections for typos

**Success Criteria:**
✅ Abstract mentions theory
✅ Contributions list includes theory
✅ All sections flow naturally
✅ No LaTeX errors or undefined references

---

## 🔄 Week 2-3: Overcooked Validation (Optional)

**Only do this if you decided on Medium or Full track!**

See `PAPER_6_ENHANCEMENT_MASTER_PLAN.md` Week 2-3 section for:
- [ ] Environment setup (Day 8-9)
- [ ] Policy training (Day 10-11)
- [ ] Trajectory collection (Day 12-14)
- [ ] O/R computation (Day 15-16)
- [ ] Analysis and writing (Day 17-21)

**Expected Output:**
- New Section 5.X "Overcooked Validation"
- Figure showing r ≈ -0.60 correlation
- 240 trajectories analyzed

---

## 🎮 Week 4-5: Continuous Control (Optional)

**Only do this if you decided on Full track!**

See `PAPER_6_ENHANCEMENT_MASTER_PLAN.md` Week 4-5 section for:
- [ ] Continuous MPE setup (Day 22-23)
- [ ] Policy training (Day 24-27)
- [ ] Continuous O/R computation (Day 28-30)
- [ ] Analysis and writing (Day 31-35)

**Expected Output:**
- New Section 5.Y "Continuous Control"
- Validation of Algorithm 1 (Appendix B.2)
- Correlation r ≈ -0.40

---

## 🎨 Week 6-8: Final Polish (Optional)

**Only do this if you're going for Full track submission!**

See `PAPER_6_ENHANCEMENT_MASTER_PLAN.md` Week 6-8 section for:
- [ ] Integration (Week 6)
- [ ] Figure generation (Week 7)
- [ ] Final polish and submission prep (Week 8)

**Expected Output:**
- 40-page paper (25 main + 15 appendix)
- All figures publication-quality
- NeurIPS checklist complete
- Ready for submission

---

## 🎯 Decision Points

### After Day 2 (Theory Integration Complete)

**Option A: Submit with Theory Only**
- ✅ Pro: Fast (1 week total), solid enhancement
- ⚠️ Con: Doesn't address "narrow environment scope" critique
- **Choose if:** Deadline is soon, theory enhancement is sufficient

**Option B: Continue to Overcooked (Medium Track)**
- ✅ Pro: Strong generalization story, addresses environment diversity
- ⚠️ Con: 3 weeks total, requires Overcooked setup
- **Choose if:** 3-4 weeks before deadline, want robust validation

**Option C: Go Full Enhancement (Full Track)**
- ✅ Pro: Definitive comprehensive work, best possible paper
- ⚠️ Con: 8 weeks total, substantial time investment
- **Choose if:** 2+ months to deadline, aiming for top-tier publication

### After Day 7 (Week 1 Complete)

**Checkpoint Questions:**
- [ ] Does theory section read well?
- [ ] Do propositions add value?
- [ ] Is matrix game validation convincing?
- [ ] Do you have time for Overcooked (3 more weeks)?
- [ ] Do you have compute resources for experiments?

**Go/No-Go Decision:**
- **GO to Week 2:** If answered yes to most questions above
- **STOP and submit:** If theory enhancement alone is sufficient

---

## 📋 Quick Status Check

**Current Status (Check one):**
- [ ] Haven't started (read `README_ENHANCEMENTS.md` first!)
- [ ] Theory integration in progress (follow `THEORY_INTEGRATION_GUIDE.md`)
- [ ] Theory integration complete (verify checklist above)
- [ ] Matrix game implementation in progress
- [ ] Week 1 complete, deciding on next steps
- [ ] Week 2-3 Overcooked in progress
- [ ] Week 4-5 Continuous in progress
- [ ] Week 6-8 Final polish in progress
- [ ] Paper submitted! 🎉

**Time Invested So Far:**
- Theory integration: ____ hours (expected: 0.5h)
- Matrix game: ____ hours (expected: 8h)
- Overcooked: ____ hours (expected: 25h)
- Continuous: ____ hours (expected: 25h)
- Final polish: ____ hours (expected: 30h)
- **Total: ____ hours**

**Estimated Completion Date:**
- Theory only (Option A): ____
- + Overcooked (Option B): ____
- + Continuous (Option C): ____

---

## 💡 Tips & Troubleshooting

### LaTeX Won't Compile
1. Check for unmatched braces `{}` in pasted content
2. Run `pdflatex` twice (first run may have ref errors)
3. Check log file for specific error line number
4. Verify all `\label{}` commands are unique

### Cross-References Show "??"
- This is normal on first pdflatex run
- Run pdflatex a second time to resolve
- If still "??", check that `\label{}` exists

### Page Count Seems Wrong
- Ensure you're looking at the final PDF, not aux file
- Theory should add ~4.5 pages
- If much different, check formatting issues

### Figures Don't Display
- Verify figure files exist in `figures/` directory
- Check `\graphicspath{{figures/}}` is set
- Ensure figure filenames match exactly (case-sensitive)

### Want to Pause Mid-Integration
- Save your work in progress
- Commit to git: `git add . && git commit -m "WIP: theory integration"`
- Resume anytime by checking where you left off in this checklist

---

## 🎉 Completion Celebration Points

- [🎯] **Theory integrated** - Paper now has formal theoretical grounding!
- [🎮] **Matrix game works** - Propositions validated empirically!
- [🥘] **Overcooked complete** - Ecological diversity demonstrated!
- [🎮] **Continuous validated** - Action-space generalization proven!
- [📄] **Paper submitted** - Outstanding work ready for review!

---

**Current Next Step:**
Check your status above and follow the corresponding section of this checklist.

**Most Common Starting Point:**
If you just opened this file, start with Day 1-2 "LaTeX Integration" and follow `THEORY_INTEGRATION_GUIDE.md`.

**Questions?**
- Technical: Check `THEORY_INTEGRATION_GUIDE.md`
- Planning: Check `PAPER_6_ENHANCEMENT_MASTER_PLAN.md`
- Overview: Check `README_ENHANCEMENTS.md`

---

*Good luck with your enhancement! This is going to be an outstanding paper.* 🚀
