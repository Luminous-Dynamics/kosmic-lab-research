# MPE Validation Setup

## Overview
This document describes how to run the MPE (Multi-Agent Particle Environment) validation experiments for Paper 6's O/R Index.

## Prerequisites

### 1. Enter the Nix Development Shell
```bash
cd /srv/luminous-dynamics/kosmic-lab
nix develop
```

This provides:
- Python 3.11 with scientific packages
- SDL2 libraries for pygame (pettingzoo dependency)
- Poetry for Python package management
- LaTeX for paper compilation

### 2. Install Python Dependencies
```bash
poetry install
```

This installs pettingzoo[mpe] and all required packages.

## Running Validation

### Quick Test (5 minutes)
```bash
poetry run python experiments/mpe_validation.py --n-teams 10 --n-episodes 3
```

### Standard Validation (15-30 minutes)
```bash
poetry run python experiments/mpe_validation.py --n-teams 50 --n-episodes 5
```

### Full Validation (1-2 hours)
```bash
poetry run python experiments/mpe_validation.py --n-teams 100 --n-episodes 10
```

## Expected Results

### Primary Metric
- **Pearson r**: Expected +0.50 to +0.75 (positive correlation)
- **p-value**: < 0.001 (highly significant)

### Policy Comparison
| Policy Type | Expected O/R | Expected Success |
|-------------|--------------|------------------|
| random | Low | Low |
| greedy | Low-Medium | Medium |
| coordinated | High | High |
| mixed | Medium | Medium |

### Output Files
Results are saved to `results/mpe_validation/`:
- `mpe_validation_results.csv` - Raw data
- `mpe_validation_figure.png` - Visualization
- `mpe_validation_summary.txt` - Summary statistics

## Troubleshooting

### pygame/SDL2 Errors
If you see SDL2 errors, ensure you're in the nix develop shell:
```bash
nix develop
```

The shell provides SDL2 libraries and sets LD_LIBRARY_PATH.

### Import Errors
Ensure core/or_index.py exists and compute_or_index is exported.

### Permission Errors
Some directories may be owned by root. Use sudo if needed:
```bash
sudo chown -R $USER:users /srv/luminous-dynamics/kosmic-lab/results
```

## Integration with Paper

Add results to supplementary materials:
1. Copy figure to `paper-6-or-index/figures/`
2. Add table to LaTeX appendix
3. Reference in main text under "Real MARL Environments"

## Next Steps

1. **SMAC Validation** - Test on StarCraft Multi-Agent Challenge
2. **GRF Validation** - Test on Google Research Football
3. **arXiv Preprint** - Submit with validation results
