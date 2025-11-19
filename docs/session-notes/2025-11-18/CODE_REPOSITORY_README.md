# K-Index: Code Repository

Reproducible experiments for "Behavioral Flexibility Predicts Multi-Agent Coordination"

## Quick Start

```bash
# Option 1: Nix (recommended)
nix-shell -p python3 python3Packages.numpy python3Packages.scipy python3Packages.matplotlib

# Option 2: pip
pip install -r requirements.txt

# Run main experiment
python3 original_conditions_replication.py

# Generate all figures
python3 generate_figures.py
python3 generate_supplementary_figures.py
```

## Experiments (30 total)

### Core Validation (5)
- `original_conditions_replication.py` - r = +0.70, n=1200
- `mechanism_validation.py` - A/B test
- `episode_length_gradient.py` - Dose-response r = +0.97
- `proper_rl_training.py` - Trained policies

### Paper 4 Main (15)
- `track_f1_flexibility_regularization.py` - Causal: λ=0.2 → +6.9%
- `track_g3_quick.py` - Robustness: r > 0.93
- `track_c_varied_abstract.py` - Generalization: 5 conditions
- `track_a_metric_comparison_v2.py` - vs entropy/MI
- `track_b_zeroshot_coordination.py` - r = -0.50

### MPE Boundary (7)
- `track_j1_trained_teams.py` - Spatial: variance → 0
- `track_j2_predator_prey.py` - Predator-prey

### Supplementary (5)
- `supplementary_large_n.py` - n=50, tighter CI
- `supplementary_algorithms.py` - A2C/REINFORCE/PPO
- `supplementary_ablations.py` - Hyperparameter robustness
- `supplementary_temporal.py` - Early prediction
- `supplementary_power.py` - Statistical power

## Figures

### Main (7)
```bash
python3 generate_figures.py
```
Creates: `figure_1_metric_comparison.png` through `figure_7_theoretical_framework.png`

### Supplementary (5)
```bash
python3 generate_supplementary_figures.py
```
Creates: `figure_s1_algorithms.png` through `figure_s5_summary.png`

## Key Results

| Finding | Value | Script |
|---------|-------|--------|
| Main effect | r = +0.70*** | `original_conditions_replication.py` |
| Causal | +6.9% | `track_f1_flexibility_regularization.py` |
| Robust | r > 0.93 | `track_g3_quick.py` |
| Algorithms | A2C: 0.88 | `supplementary_algorithms.py` |
| Power | 99.2% | `supplementary_power.py` |

## License

MIT
