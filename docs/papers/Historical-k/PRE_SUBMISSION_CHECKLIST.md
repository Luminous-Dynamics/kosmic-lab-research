# Pre-Submission Checklist - Historical K(t) Index

**Date Created**: November 25, 2025
**Submission Target**: Global Policy
**Manuscript Status**: 100% technically complete, awaiting author information

---

## ✅ Complete - Technical Requirements

All critical scientific and methodological requirements are complete:

- [x] All reviewer feedback addressed (2 rounds)
- [x] Perfect Methods-Results consistency
- [x] Numerical consistency (baselines explained)
- [x] Sign conventions explicit
- [x] Terminology aligned throughout
- [x] Figure references accurate
- [x] Statistical humility maintained
- [x] PDF compiled successfully (22 pages, 1.8 MB)
- [x] 0 critical LaTeX errors
- [x] All citations resolved
- [x] All figures embedded

---

## ⏳ Pending - Author Information (Required)

The following placeholders need to be filled before submission:

### 1. Author Names and Affiliations (Lines 43-46)

**Current**:
```latex
\author[1]{[Author Name]}
\author[2]{[Co-Author Name]}
\affil[1]{Department of [Department], [Institution]}
\affil[2]{Department of [Department], [Institution]}
```

**Required Information**:
- Primary author name
- Primary author department and institution
- Secondary author name (if applicable, or remove)
- Secondary author department and institution (if applicable, or remove)

**Example Format**:
```latex
\author[1]{Tristan Stoltz}
\affil[1]{Luminous Dynamics, Richardson, TX, USA}
```

OR if academic affiliation:
```latex
\author[1]{Tristan Stoltz}
\affil[1]{Department of Complex Systems, University Name}
```

---

### 2. Data Availability Statement (Line 490)

**Current**:
```latex
All data, code, and analysis scripts are available at [repository URL].
Processed datasets include: [list key datasets].
```

**Required Information**:
- GitHub repository URL (or OSF, Zenodo, etc.)
- List of key processed datasets

**Reviewer's Suggested Format**:
```latex
All data sources are publicly available as documented in Supplementary Table S1.
Processed time series data and analysis code are available at
https://github.com/[username]/historical-k-index
(or https://osf.io/[project-id]/).

Key processed datasets include:
- V-Dem v14 democracy and governance indicators (1810-2020)
- KOF Globalisation Index components (1970-2020)
- HYDE 3.2.1 demographic reconstructions (3000 BCE - 2020 CE)
- Harmonized reciprocity and innovation metrics (custom aggregations)
```

---

### 3. Author Contributions Statement (Line 494)

**Current**:
```latex
[To be added]
```

**Required Information**:
Statement of who did what

**Reviewer's Suggested Format** (single author):
```latex
T.S. conceived the project, designed the seven-harmony framework,
assembled the historical dataset, performed all analyses,
and wrote the manuscript.
```

**Alternative Format** (multiple authors):
```latex
T.S. and [Co-Author] conceived the project. T.S. designed the
framework and assembled the dataset. T.S. performed the analysis.
Both authors contributed to writing and approved the final manuscript.
```

---

### 4. Acknowledgments (Line 486)

**Current**:
```latex
[To be added]
```

**Optional but Recommended**:
- Funding sources (if any)
- Data providers to acknowledge
- Reviewers/advisors who provided feedback
- Computational resources used

**Example Format**:
```latex
We thank the Varieties of Democracy (V-Dem) Institute, the KOF Swiss
Economic Institute, and the HYDE historical database team for making
their data publicly available. We acknowledge [Name] for helpful
comments on an earlier draft. No specific funding supported this research.
```

**Alternative if self-funded**:
```latex
The author thanks the open-access data providers (V-Dem, KOF, HYDE, Seshat)
whose work made this analysis possible. No external funding supported this research.
```

---

## ⏳ Optional - Additional Enhancements

### 5. Normative-Constructive Statement (Reviewer Suggestion)

**Location**: Methods (Section 2) or Limitations (Section 4.5)

**Reviewer's Suggested Text**:
> "Our approach is explicitly normative-constructive: we begin from a theory of seven harmonies that a flourishing, co-creative civilization ought to exhibit, and we build K(t) as a measure of alignment with that theory. This is not a purely inductive discovery of latent dimensions from data. To mitigate arbitrariness, we (i) make our value assumptions transparent, (ii) test the harmony structure against the empirical covariance of indicators, and (iii) perform extensive sensitivity analyses over proxy and weight choices. We recommend reading K(t) primarily as a theory-guided diagnostic and early-warning tool rather than as a purely objective measure of 'civilizational quality'."

**Status**: Optional but signals methodological sophistication

---

### 6. Cover Letter for Global Policy

**Purpose**: Emphasize policy relevance and fit for journal

**Key Points to Include**:
1. **Hook**: 2020 as historical coherence peak, immediately followed by pandemic
2. **Policy Relevance**: Early warning system for civilizational fragmentation
3. **Methodological Rigor**: Multiple validation approaches, statistical humility
4. **Fit for Global Policy**: Precedent (Bostrom's Vulnerable World Hypothesis), interdisciplinary scope
5. **Timeliness**: Critical moment to understand coordination capacity

**Template**:
```
Dear Editors,

We submit "A Multi-Harmonic Index of Global Civilizational Coherence"
for consideration at Global Policy.

This paper introduces a novel metric for tracking humanity's collective
capacity for coordination and sense-making across seven dimensions.
Our historical reconstruction (1810-2020) reveals that global coherence
reached an unprecedented peak in 2020, immediately prior to the COVID-19
pandemic—providing a crucial baseline for understanding recent disruptions.

The K(t) index addresses a critical gap in policy discourse: how do we
measure our collective capacity to coordinate on existential challenges?
By aggregating 32 empirical indicators across governance, connectivity,
reciprocity, innovation, wisdom, wellbeing, and evolutionary progression,
we offer policymakers an early-warning diagnostic for institutional
fragmentation and coordination collapse.

This work fits Global Policy's mission of publishing rigorous,
policy-relevant research on global challenges. Like Bostrom's "Vulnerable
World Hypothesis" (published in your journal), we address civilizational
risk through a novel analytical framework backed by extensive empirical
validation.

We believe this index will be valuable for policymakers monitoring
institutional health, researchers studying long-term coordination dynamics,
and practitioners designing interventions to strengthen global cooperation.

Sincerely,
[Author Name]
```

---

## 📋 Pre-Submission Workflow

### Step 1: Gather Information (15 minutes)
- [ ] Decide on author name(s) and affiliation(s)
- [ ] Create or identify GitHub/OSF repository for data/code
- [ ] Draft author contributions statement
- [ ] Draft acknowledgments (if any)

### Step 2: Fill Placeholders (10 minutes)
- [ ] Update lines 43-46 (authors/affiliations)
- [ ] Update line 490 (data availability)
- [ ] Update line 494 (author contributions)
- [ ] Update line 486 (acknowledgments)
- [ ] Optional: Add normative-constructive statement

### Step 3: Final Compilation (5 minutes)
- [ ] Recompile PDF with author information
- [ ] Verify no new LaTeX errors
- [ ] Check PDF renders correctly (especially author names)

### Step 4: Prepare Submission Materials (30 minutes)
- [ ] Write cover letter
- [ ] Prepare supplementary tables as separate file
- [ ] Create figure files as separate high-resolution images
- [ ] Double-check journal submission guidelines

### Step 5: Submit (15 minutes)
- [ ] Create account on Global Policy submission portal
- [ ] Upload manuscript PDF
- [ ] Upload supplementary materials
- [ ] Upload figures
- [ ] Paste cover letter
- [ ] Fill submission form
- [ ] Submit!

**Total Time Estimate**: ~75 minutes once information is gathered

---

## 🎯 Decision Points

### Single Author vs Co-Author?

**Single Author** (Simpler):
- Pro: Clear attribution, no coordination needed
- Pro: Faster submission process
- Con: No institutional backing (if independent)

**Co-Author** (Academic Context):
- Pro: Institutional affiliation lends credibility
- Pro: Access to university resources/visibility
- Con: Requires coordination, IP agreement
- Con: May slow submission process

### Repository Hosting?

**GitHub** (Recommended):
- Pro: Standard for scientific code/data
- Pro: Easy versioning and updates
- Pro: Citeable with Zenodo DOI
- Example: https://github.com/luminous-dynamics/historical-k-index

**OSF (Open Science Framework)**:
- Pro: Designed for scientific reproducibility
- Pro: Automatic DOI generation
- Pro: Private during review, public after
- Example: https://osf.io/abc123/

**Institutional Repository**:
- Pro: Long-term preservation guaranteed
- Con: Requires institutional affiliation

---

## 📊 Current Status Summary

| Item | Status | Time to Complete |
|------|--------|------------------|
| **Technical content** | ✅ 100% complete | — |
| **Reviewer feedback** | ✅ All addressed | — |
| **PDF compilation** | ✅ Working (22 pages) | — |
| **Author information** | ⏳ Pending input | 15 min |
| **Data availability** | ⏳ Pending repository | 10 min |
| **Author contributions** | ⏳ Pending statement | 5 min |
| **Acknowledgments** | ⏳ Optional | 5 min |
| **Cover letter** | ⏳ Recommended | 30 min |
| **Final compilation** | ⏳ After info added | 5 min |

**Total time to submission-ready**: ~70 minutes (after information gathering)

---

## 🚀 Immediate Next Steps

**Option A: Minimal Path (Single Author, Self-Funded)**
1. Fill author name as "Tristan Stoltz" (or appropriate name)
2. Set affiliation as "Luminous Dynamics" or "Independent Researcher"
3. Upload code/data to GitHub repository
4. Update data availability with GitHub URL
5. Set author contributions to single-author template
6. Acknowledge open data providers
7. Recompile → Submit

**Estimated Time**: 45 minutes

**Option B: Academic Path (With Co-Author/Institution)**
1. Coordinate with co-author on attribution
2. Agree on author order and contributions
3. Get institutional approval if needed
4. Use institutional repository if available
5. Include funding acknowledgments if applicable
6. Draft collaborative cover letter
7. Recompile → Submit

**Estimated Time**: 2-3 hours (coordination dependent)

---

## ✅ What's Already Perfect

The manuscript itself is **100% submission-ready** scientifically:

- Perfect internal consistency
- All numerical issues resolved
- Statistical humility throughout
- Clear methodological transparency
- Comprehensive validation
- Well-structured narrative
- Publication-quality figures
- Complete supplementary materials

**Only administrative information is needed to submit.**

---

## 📞 Ready to Proceed?

Once you provide the following 3 pieces of information, we can complete the submission in under an hour:

1. **Author name(s) and affiliation(s)**
2. **Repository URL** (or I can create GitHub repo structure)
3. **Funding/acknowledgments** (if any, or "none")

Then optional:
4. Cover letter assistance (can provide template)

---

**Current Recommendation**: Minimal path (Option A) will get paper submitted today. Academic path (Option B) better for long-term citation/visibility but requires coordination.

The science is done. The polish is done. Only administrative details remain.

🎉 **Manuscript is truly ready - just needs your name on it!**
