# Paper 9: The Kosmic K-Index Framework

## A 7-Dimensional Framework for Agent Behavioral Assessment

**Status**: ✅ SYSTEMATICALLY VALIDATED PAPER COMPLETE
**Paper**: 16 pages, 541KB PDF
**Date**: November 29, 2025 (Systematic Validation Complete)

---

## 🏆 Key Experimental Results (Systematically Validated)

| Metric | Value | Significance |
|--------|-------|--------------|
| **K_M Memory Validation** | **1.83× ratio** (p<0.0001, d=1.03) | Memory architectures discriminated in memory-requiring tasks |
| **K_M Delay Scaling** | 2.61× at d=20 | Discrimination increases with delay length |
| **K_M-K_P Correlation** | **r = -0.491** (negative!) | Strategic trade-off, not redundancy |
| **K_H 4-Scenario** | 4/4 validated (r>0.90 in 3/4) | Generalizes across normative domains |
| **7D vs 4D Framework** | **4.7× better** (R²=0.42 vs 0.09) | Full 7D framework validated |
| **Commons Paradox** | r = -0.717, R² = 0.514 | High K_R negatively predicts reward |
| **K_S Ratio** | 3.0× (same-type/mixed) | Social coordination validated |
| **Effect Sizes** | All d > 1.0 | Large practical significance |

---

## Quick Reference

### What This Paper Is About

This paper extends the simple K-Index (magnitude coupling) into a comprehensive **7-dimensional Kosmic K-Vector** framework for assessing agent behavioral capabilities.

### The 7 Dimensions

| Dim | Symbol | Name | Source | Measures |
|-----|--------|------|--------|----------|
| 1 | K_R | Reactivity | Spinoza | Stimulus-response coupling |
| 2 | K_A | Agency | Autopoiesis | Causal closure |
| 3 | K_I | Integration | IIT/Ashby | Complexity matching |
| 4 | K_P | Prediction | FEP | World model quality |
| 5 | K_M | Meta | Whitehead | Temporal depth |
| 6 | K_S | Social | Margulis | Coordination |
| 7 | K_H | Harmonic | West | Normative alignment |

---

## Key Files

### Documentation
- `KOSMIC_K_INDEX_FRAMEWORK.md` - Complete theoretical framework (main doc)
- `EXPERIMENTAL_DESIGN.md` - Phased experimental validation plan
- `CLAUDE.md` - This file (development context)

### Implementation
- `kosmic_k_index.py` - Complete Python implementation

### Related
- `../paper-8-unified-indices/` - Foundation work on K + O/R
- `/home/tstoltz/Luminous-Dynamics/00-sacred-foundation/wisdom/Kosmic Theory of Conscious Potentiality.md` - Theoretical grounding

---

## Quick Start

```bash
cd /srv/luminous-dynamics/kosmic-lab

# Enter development shell
nix develop

# Test the implementation
python docs/papers/paper-9-kosmic-k-index/kosmic_k_index.py

# Use in your code
from kosmic_k_index import compute_kosmic_index

result = compute_kosmic_index(observations, actions)
print(result["K_vector"])
```

---

## Implementation Status

### Phase 1: Cognitive Tetrad ✅ VALIDATED
- [x] K_R: Reactivity — Commons Paradox (r=-0.717, R²=0.514)
- [x] K_A: Agency — Causal intervention validated
- [x] K_I: Integration — Entropy matching implemented
- [x] K_P: Prediction — Normalized prediction error

### Phase 2: Temporal ✅ VALIDATED
- [x] K_M: Meta/temporal depth — 1.98× recurrent/feedforward ratio

### Phase 3: Social ✅ VALIDATED
- [x] K_S: Social coherence — 3.0× same-type/mixed ratio

### Phase 4: Normative ✅ IMPLEMENTED
- [x] K_H: Harmonic alignment (normative reference)

### Inter-Dimension Correlations ✅ VALIDATED
- Mean |r| = 0.45 (partial correlation expected)
- K_M is uniquely independent (all |r| < 0.2)
- Two meaningful clusters: behavioral (K_R, K_A, K_H) and model quality (K_I, K_P)

### Future Horizons (DOCUMENTED)
- [ ] K_Topo: Topological persistence (TDA)
- [ ] K_Spectral: Spectral gap (Graph Laplacian)
- [ ] Kosmic Tensor: Phase space volume

---

## Theoretical Foundation

### The Gap We're Filling

The original K-Index:
```
K = 2 × |ρ(||O||, ||A||)|
```

Only measures **reactivity** (Spinozist parallelism). But the Kosmic Theory defines consciousness as:

1. **Integrative** (IIT)
2. **Predictive** (FEP)
3. **Operationally closed** (Autopoiesis)
4. **Temporal** (Whitehead)
5. **Collective** (Symbiogenesis)
6. **Normatively aligned** (Scaling Laws)

A "thermostat" can have high K_R but is clearly not conscious. The 7D framework distinguishes thermostats from true cognitive agents.

### The Kosmic K-Vector

```
K = (K_R, K_A, K_I, K_P, K_M, K_S, K_H)
```

Each dimension maps to a pillar of the Kosmic Theory:

| Pillar | K Dimension | What it measures |
|--------|-------------|------------------|
| Spinoza (Parallelism) | K_R | Does it react? |
| Autopoiesis | K_A | Does it affect reality? |
| IIT | K_I | Is it complex enough? |
| FEP | K_P | Does it predict? |
| Whitehead | K_M | Does it use history? |
| Symbiogenesis | K_S | Does it coordinate? |
| Scaling Laws | K_H | Is it sustainable? |

---

## Experimental Validation ✅ COMPLETE

### Phase 1: Tetrad Validation (Track L) ✅
- [x] Ran 4 environments: Coordination, Simple, Delayed, Commons
- [x] Commons Paradox discovered: r=-0.717 (negative K_R-reward correlation)
- [x] Effect sizes > 2.0 across all environments
- [x] Cross-environment table with exact p-values in paper

### Phase 2: K_M Validation (Delayed Tasks) ✅
- [x] Created DelayedHint and SequenceRecall environments
- [x] Compared feedforward vs recurrent agents
- [x] Result: **1.98× K_M ratio** (recurrent/feedforward)
- [x] Recurrent agents achieve higher task accuracy

### Phase 3: K_S Validation (Multi-Agent Coordination) ✅
- [x] Tested 6 agent pairings in coordination environment
- [x] Same-type pairs: avg K_S = 0.326
- [x] Mixed pairs: avg K_S = 0.108
- [x] Result: **3.0× ratio** validates social coordination metric

### Phase 4: K_A Causal Intervention ✅
- [x] Action masking experiments (0%, 25%, 50%, 75%, 100%)
- [x] Correlation r=-0.977 confirms K_A measures true agency
- [x] Results in paper Section 4.3

---

## Key Formulas

### K_R (Reactivity)
```
K_R = 2 × |ρ(||O||, ||A||)|
```

### K_A (Agency)
```
K_A = |ρ(||A_t||, Δ||O_{t+1}||)|
```

### K_I (Integration)
```
K_I = 2 × min(H_O, H_A) / (H_O + H_A + ε)
```

### K_P (Prediction)
```
K_P = 1 - NPE
NPE = E[||O_{t+1} - Ô||²] / E[||O_{t+1} - Ō||²]
```

### K_M (Meta)
```
K_M = (L_markov - L_history) / (L_markov + ε)
```

### K_S (Social)
```
K_S = |ρ(||A^A||, ||A^B||)|
```

### K_H (Harmonic)
```
K_H = exp(-α × D(p_agent || p_norm))
```

---

## Development Notes

### Why 7 Dimensions?

The Kosmic Theory identifies 7 distinct aspects of consciousness:
1. Responsiveness (sensing)
2. Agency (acting)
3. Integration (complexity)
4. Prediction (modeling)
5. Self-reference (memory)
6. Intersubjectivity (others)
7. Normativity (values)

### Why Not More?

We considered:
- 4D (basic cognitive): Too simple
- 5D (+ temporal): Missing social
- 6D (+ social): Missing normative
- 7D: Complete minimal set

8D+ would likely be redundant (PCA analysis planned to confirm).

### Future: The Geometry of Consciousness

The 7D vector is "Newtonian"—a list of scalars.

Future work will move to "Relativistic" geometry:
- **Topological K**: Shape of trajectories (Betti numbers)
- **Spectral K**: Eigenvalue structure (Graph Laplacian)
- **Kosmic Tensor**: Phase space volume

This is documented in the "Future Horizons" section but NOT implemented yet.

---

## Connection to Paper 8

Paper 8 showed:
- K-only optimization outperforms unified indices
- K and O/R are weakly negatively correlated (r = -0.21)
- CMA-ES works properly (K can exceed 1.5 in right environment)

Paper 9 extends this by:
- Upgrading K from scalar to 7D vector
- Grounding each dimension in the Kosmic Theory
- Providing experimental validation framework

The K from Paper 8 becomes K_R in Paper 9.

---

## Paper Artifacts

### Generated Files
- `paper_9_kosmic_k_index.pdf` - 14-page workshop paper (501KB)
- `paper_9_kosmic_k_index.tex` - LaTeX source
- `REVISION_PLAN.md` - Complete revision tracking

### Experiment Logs
- `logs/track_l/l6_cross_environment_*.json` - Cross-environment results
- `logs/km_validation/km_validation_*.json` - K_M validation data
- `logs/track_l/ks_multiagent_*.json` - K_S validation data
- `logs/intervention/ka_intervention_*.json` - K_A causal intervention

### Supporting Code
- `kosmic_k_index.py` - Complete Python implementation
- `run_km_validation.py` - K_M experiment runner
- `run_ks_experiments.py` - K_S experiment runner

---

## Next Steps (Post-Workshop)

1. **Submit to workshop** - Paper ready for submission
2. **Address reviewer feedback** - Future improvements based on reception
3. **Scale experiments** - Larger agent populations (N>1000)
4. **Real-world validation** - Test on production RL systems
5. **Extend to K_Topo/K_Spectral** - Future geometric formulations

---

*Last Updated: November 29, 2025*
*Status: ✅ Workshop-Ready Paper Complete (14 pages, 501KB)*
