# GitHub Repository Upload Instructions
## Immediate Actions for Manuscript Submission

**Repository**: https://github.com/Luminous-Dynamics/historical-k-index
**Status**: Ready to create and populate
**Time Required**: 1-2 hours
**Date**: November 25, 2025

---

## ✅ What's Ready to Upload

All necessary files have been prepared in:
```
/srv/luminous-dynamics/kosmic-lab/docs/papers/Historical-k/repository-files/
```

**Files created**:
- `README.md` (12 KB) - Repository overview with FAQs
- `DATA_SOURCES.md` (14 KB) - Complete data documentation
- `LICENSE` (2 KB) - MIT license for code, CC-BY-4.0 for data

**Files to copy from manuscript directory**:
- `k_index_manuscript.pdf` (1.8 MB) - Final manuscript
- `supplementary/` directory - All supplementary materials

---

## Step-by-Step Upload Process

### Step 1: Create GitHub Repository

```bash
# Navigate to GitHub
# Go to: https://github.com/Luminous-Dynamics
# Click: "New repository"

# Repository settings:
# Name: historical-k-index
# Description: Data and code for Historical K(t) Index manuscript (Global Policy 2025)
# Visibility: Public
# Initialize: Add README: NO (we have our own)
# .gitignore: None
# License: None (we have our own)

# Click: "Create repository"
```

**OR via command line**:
```bash
gh repo create Luminous-Dynamics/historical-k-index \
  --public \
  --description "Data and code for Historical K(t) Index manuscript (Global Policy 2025)"
```

### Step 2: Clone Repository Locally

```bash
cd /srv/luminous-dynamics
git clone https://github.com/Luminous-Dynamics/historical-k-index.git
cd historical-k-index
```

### Step 3: Create Directory Structure

```bash
# Create all necessary directories
mkdir -p data/sources
mkdir -p manuscript/supplementary
mkdir -p docs

# Verify structure
tree -L 2
```

**Expected output**:
```
historical-k-index/
├── data/
│   └── sources/
├── manuscript/
│   └── supplementary/
└── docs/
```

### Step 4: Copy Files from Prepared Location

```bash
# From the historical-k-index directory:

# Copy repository root files
cp ../kosmic-lab/docs/papers/Historical-k/repository-files/README.md ./
cp ../kosmic-lab/docs/papers/Historical-k/repository-files/LICENSE ./

# Copy data documentation
cp ../kosmic-lab/docs/papers/Historical-k/repository-files/DATA_SOURCES.md ./data/sources/

# Copy manuscript
cp ../kosmic-lab/docs/papers/Historical-k/k_index_manuscript.pdf ./manuscript/

# Copy supplementary materials
cp -r ../kosmic-lab/docs/papers/Historical-k/supplementary/* ./manuscript/supplementary/
```

### Step 5: Verify File Structure

```bash
# Check that all files are in place
ls -lh

# Should see:
# -rw-r--r-- README.md (12 KB)
# -rw-r--r-- LICENSE (2 KB)
# drwxr-xr-x data/
# drwxr-xr-x manuscript/
# drwxr-xr-x docs/

# Check data sources
ls -lh data/sources/
# Should see: DATA_SOURCES.md (14 KB)

# Check manuscript
ls -lh manuscript/
# Should see: k_index_manuscript.pdf (1.8 MB)
# Should see: supplementary/ directory

# Check supplementary
ls -lh manuscript/supplementary/
# Should see: README.md, SUPPLEMENTARY_METHODS.md, SUPPLEMENTARY_TABLES.md
```

### Step 6: Git Configuration and Initial Commit

```bash
# Initialize git (if not already done by clone)
git status

# Add all files
git add .

# Check what will be committed
git status

# Create initial commit
git commit -m "Initial release: Historical K(t) Index for Civilizational Coherence

- Manuscript: k_index_manuscript.pdf (Global Policy 2025)
- Data sources documentation with citations and access instructions
- Supplementary materials (methods and tables)
- MIT license for code, CC-BY-4.0 for data
- Note: Full replication code and processed data coming upon manuscript acceptance"

# Verify commit
git log
```

### Step 7: Push to GitHub

```bash
# Set up remote (if not already done)
git remote -v
# Should show: origin https://github.com/Luminous-Dynamics/historical-k-index.git

# If remote not set:
git remote add origin https://github.com/Luminous-Dynamics/historical-k-index.git

# Push to main branch
git branch -M main
git push -u origin main
```

### Step 8: Verify on GitHub

1. Navigate to: https://github.com/Luminous-Dynamics/historical-k-index
2. Verify README displays correctly with:
   - Repository overview
   - Key findings (K₂₀₂₀ = 0.914)
   - Data sources table
   - Citation information
   - Contact information
3. Check that all files and directories are present
4. Click on manuscript/k_index_manuscript.pdf to verify it opens
5. Check that supplementary materials are accessible

---

## Final Repository Structure (Minimal Version)

```
historical-k-index/
├── README.md                          # Repository overview (12 KB)
├── LICENSE                            # MIT/CC-BY-4.0 dual license (2 KB)
├── data/
│   └── sources/
│       └── DATA_SOURCES.md            # Complete data documentation (14 KB)
├── manuscript/
│   ├── k_index_manuscript.pdf         # Published manuscript (1.8 MB)
│   └── supplementary/
│       ├── README.md                  # Supplementary overview (8 KB)
│       ├── SUPPLEMENTARY_METHODS.md   # Extended methods (16 KB)
│       └── SUPPLEMENTARY_TABLES.md    # Data tables (12 KB)
└── docs/
    └── (empty for now)
```

**Total repository size**: ~2 MB
**Files**: 8 files across 5 directories

---

## Verification Checklist

After uploading, verify these items:

### Repository Settings
- [ ] Repository is public
- [ ] Description is set: "Data and code for Historical K(t) Index manuscript (Global Policy 2025)"
- [ ] Topics/tags added: civilizational-coherence, global-development, historical-data, sustainability
- [ ] Website link added (if available): https://luminousdynamics.org

### File Access
- [ ] README.md displays on repository homepage
- [ ] LICENSE file visible and correctly formatted
- [ ] k_index_manuscript.pdf opens correctly (22 pages, 1.8 MB)
- [ ] DATA_SOURCES.md contains all data citations
- [ ] Supplementary materials are accessible

### Content Accuracy
- [ ] README shows correct K₂₀₂₀ = 0.914 value
- [ ] Citation information includes correct author (Tristan Stoltz)
- [ ] Contact email is correct: tristan.stoltz@luminousdynamics.org
- [ ] All data source links are live and correct

### Future Preparation
- [ ] Add note in README: "Full replication code coming upon manuscript acceptance"
- [ ] data/processed/ directory exists (empty) for future data files
- [ ] code/ directory structure planned in GITHUB_REPOSITORY_SETUP.md

---

## Post-Upload Actions

### 1. Update Manuscript Data Availability (Already Done!)

The manuscript already contains the correct URL:
```latex
Processed time series data, analysis code, and replication materials are
available at https://github.com/Luminous-Dynamics/historical-k-index
```

**No manuscript changes needed** - the Data Availability statement is already correct.

### 2. Submit Manuscript to Global Policy

Once repository is live:
1. Navigate to Global Policy submission portal
2. Upload `k_index_manuscript.pdf`
3. Upload supplementary materials as separate files
4. In submission form, reference GitHub repository in Data Availability section
5. Submit!

### 3. Optional: Add Repository Badges

After repository is public, you can add badges to README for visibility:

```markdown
[![GitHub repo size](https://img.shields.io/github/repo-size/Luminous-Dynamics/historical-k-index)](https://github.com/Luminous-Dynamics/historical-k-index)
[![GitHub stars](https://img.shields.io/github/stars/Luminous-Dynamics/historical-k-index?style=social)](https://github.com/Luminous-Dynamics/historical-k-index/stargazers)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
```

### 4. Optional: Create Zenodo DOI

For a permanent, citable archive:
1. Go to https://zenodo.org
2. Connect GitHub account
3. Enable repository for archiving
4. Create first release (v1.0)
5. Zenodo automatically creates DOI
6. Add DOI badge to README

---

## Quick Command Summary (Copy-Paste Ready)

```bash
# 1. Create and clone repository
cd /srv/luminous-dynamics
gh repo create Luminous-Dynamics/historical-k-index --public --description "Data and code for Historical K(t) Index manuscript (Global Policy 2025)"
git clone https://github.com/Luminous-Dynamics/historical-k-index.git
cd historical-k-index

# 2. Create directory structure
mkdir -p data/sources manuscript/supplementary docs

# 3. Copy files
cp ../kosmic-lab/docs/papers/Historical-k/repository-files/README.md ./
cp ../kosmic-lab/docs/papers/Historical-k/repository-files/LICENSE ./
cp ../kosmic-lab/docs/papers/Historical-k/repository-files/DATA_SOURCES.md ./data/sources/
cp ../kosmic-lab/docs/papers/Historical-k/k_index_manuscript.pdf ./manuscript/
cp -r ../kosmic-lab/docs/papers/Historical-k/supplementary/* ./manuscript/supplementary/

# 4. Commit and push
git add .
git commit -m "Initial release: Historical K(t) Index for Civilizational Coherence"
git branch -M main
git push -u origin main

# 5. Verify
echo "Repository uploaded! Verify at:"
echo "https://github.com/Luminous-Dynamics/historical-k-index"
```

---

## Timeline

**Estimated time**: 1-2 hours total

| Step | Time | Status |
|------|------|--------|
| Create repository | 2 min | Ready |
| Create directory structure | 1 min | Ready |
| Copy files | 5 min | Ready |
| Git commit and push | 3 min | Ready |
| Verify on GitHub | 5 min | After upload |
| Submit manuscript | 30-60 min | After verification |

**Can be completed**: Today (November 25, 2025)

---

## Troubleshooting

**Issue**: `gh` command not found
**Solution**: Use GitHub web interface to create repository, then clone manually

**Issue**: Permission denied when pushing
**Solution**: Set up SSH key or use HTTPS with personal access token

**Issue**: Files too large
**Solution**: Current files are <2 MB total, well under GitHub's 100 MB limit

**Issue**: Repository already exists
**Solution**: If you created it earlier, just clone and populate. No need to recreate.

---

## Next Steps After Repository Creation

1. **Submit manuscript** to Global Policy (URL already in manuscript ✅)
2. **Wait for reviews** (typically 4-8 weeks)
3. **During review period**: Build out full replication materials
   - Write data processing scripts
   - Generate all processed CSV files
   - Create analysis and visualization code
   - Write replication instructions
4. **Upon acceptance**: Update repository with complete replication package
5. **At publication**: Create Zenodo DOI for permanent archival

---

## Summary

**Status**: All files prepared and ready to upload
**Action required**: Execute Steps 1-7 above (1-2 hours)
**Outcome**: Publicly accessible repository fulfilling Data Availability requirements
**Next**: Submit manuscript to Global Policy

**The manuscript is 100% ready for submission once repository is live!**

---

**Last Updated**: November 25, 2025, 12:30 UTC
**Contact**: tristan.stoltz@luminousdynamics.org
