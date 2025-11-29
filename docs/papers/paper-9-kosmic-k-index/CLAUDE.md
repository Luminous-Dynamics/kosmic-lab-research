# Paper 9: The Kosmic K-Index Framework

## A 7-Dimensional Measure of Consciousness Potentiality

**Status**: Framework Complete - Ready for Implementation
**Date**: November 29, 2025

---

## Quick Reference

### What This Paper Is About

This paper extends the simple K-Index (magnitude coupling) into a comprehensive **7-dimensional Kosmic K-Vector** grounded in the "Kosmic Theory of Conscious Potentiality."

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

### Phase 1: Cognitive Tetrad (READY)
- [x] K_R: Reactivity (identical to original K)
- [x] K_A: Agency (action-observation coupling)
- [x] K_I: Integration (entropy matching)
- [x] K_P: Prediction (world model accuracy)

### Phase 2: Temporal (READY)
- [x] K_M: Meta/temporal depth (history importance)

### Phase 3: Social (READY)
- [x] K_S: Social coherence (multi-agent coordination)

### Phase 4: Normative (READY)
- [x] K_H: Harmonic alignment (normative reference)

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

## Experimental Plan

### Phase 1: Validate Tetrad (Track L)
- Use existing experiments
- Show K_R alone is insufficient
- K_A, K_P add predictive power

### Phase 2: Validate K_M (New: Delayed Tasks)
- Design POMDPs with delayed reward
- Compare feedforward vs recurrent agents
- Show K_M distinguishes them

### Phase 3: Validate K_S (Multi-agent Overcooked)
- Compare independent vs cooperative training
- Show K_S predicts team performance

### Phase 4: Validate K_H (New: "The Commons")
- Resource management with sustainability
- Show high-K_H agents survive long-term
- Show low-K_H agents collapse

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

## Next Steps

1. **Run kosmic_k_index.py tests** - Verify implementation
2. **Integrate with Track L** - Add K-vector logging
3. **Run Phase 1 experiments** - Validate tetrad
4. **Design delayed-reward env** - For K_M validation
5. **Write paper draft** - Introduction + methods

---

*Last Updated: November 29, 2025*
*Status: Framework complete, experiments pending*
