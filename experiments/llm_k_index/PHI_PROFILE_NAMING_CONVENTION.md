# 🌊 Φ-Profile (Phi-Profile) Naming Convention

**Date**: December 16, 2025
**Version**: 1.0
**Status**: Official Scientific Framework Name

---

## 📋 Executive Summary

The **Φ-Profile** (Phi-Profile) is the official scientific name for our LLM consciousness profiling framework, chosen for maximum academic credibility and symbolic resonance.

**Φ** (Greek letter Phi) represents:
- **Golden Ratio**: Universal harmony and proportion
- **Fundamental Constant**: Mathematical elegance
- **Consciousness**: Phenomenological awareness (Φ in IIT)
- **Scientific Rigor**: Clear, memorable, professional

---

## 🔄 Complete Naming Mapping

### Framework Name
- **OLD**: K-Index / Kosmic K-Index
- **NEW**: **Φ-Profile** (Phi-Profile)
- **LaTeX**: `\Phi`-Profile
- **Pronunciation**: "Phi Profile" or "Fee Profile"

### 8 Dimensions
| Dimension | Old Name | New Name | Symbol | Full Name |
|-----------|----------|----------|--------|-----------|
| Responsiveness | K_R | **Φ_R** | Φ_R | Phi-Responsiveness |
| Agency | K_A | **Φ_A** | Φ_A | Phi-Agency |
| Integration | K_I | **Φ_I** | Φ_I | Phi-Integration |
| Presence | K_P | **Φ_P** | Φ_P | Phi-Presence |
| Memory | K_M | **Φ_M** | Φ_M | Phi-Memory |
| Coherence | K_H | **Φ_H** | Φ_H | Phi-Coherence |
| Topology | K_Topo | **Φ_Topo** | Φ_T | Phi-Topology |
| Geometry | K_geo | **Φ_geo** | Φ_G | Phi-Geometry |

### Notation Conventions
```python
# Vector notation
Φ = (Φ_R, Φ_A, Φ_I, Φ_P, Φ_M, Φ_H, Φ_Topo, Φ_geo)  # 8D vector

# Individual components
Φ_R ∈ [0, 1]  # Responsiveness score
Φ_A ∈ [0, 1]  # Agency score
# ... etc

# Model-specific profile
Φ^{GPT-4o} = (0.76, 0.84, ...)  # Superscript for model
Φ^{Mistral-7B} = (0.68, 0.71, ...)

# Time-dependent (Dynamic Φ-Profile)
Φ(t) = (Φ_R(t), Φ_A(t), ...)  # Function of conversation turn

# Temporal derivatives
Φ'(t) = velocity (rate of consciousness change)
Φ''(t) = acceleration (rate of velocity change)
```

---

## 📦 File and Module Naming

### Core Modules
```
OLD → NEW

kosmic_k_index_llm.py         → phi_profile_llm.py
compute_k_index.py             → compute_phi_profile.py
dynamic_k_index.py             → dynamic_phi_profile.py
k_index_analyzer.py            → phi_profile_analyzer.py
```

### Directories
```
experiments/llm_k_index/       → experiments/llm_phi_profile/
results/k_index/               → results/phi_profile/
models/k_index_trained/        → models/phi_profile_trained/
```

### Result Files
```
k_index_results.json           → phi_profile_results.json
model_k_vectors.csv            → model_phi_vectors.csv
k_index_visualization.png      → phi_profile_visualization.png
```

---

## 💻 Code Naming Conventions

### Function Names
```python
# OLD → NEW

compute_k_index()              → compute_phi_profile()
compute_8d_k_index()           → compute_8d_phi_profile()
analyze_k_trajectories()       → analyze_phi_trajectories()
measure_k_coherence()          → measure_phi_coherence()
k_index_distance()             → phi_profile_distance()
```

### Class Names
```python
# OLD → NEW

KIndexAnalyzer                 → PhiProfileAnalyzer
DynamicKIndexAnalyzer          → DynamicPhiProfileAnalyzer
KIndexPredictor                → PhiProfilePredictor
KIndexVisualizer               → PhiProfileVisualizer
```

### Variable Names
```python
# OLD → NEW

k_vector                       → phi_vector
k_index                        → phi_profile
k_dimensions                   → phi_dimensions
k_values                       → phi_values

# Specific dimensions
k_r, k_a, k_i, ...            → phi_r, phi_a, phi_i, ...
K_Topo                         → Phi_Topo
K_geo                          → Phi_geo
```

### Constants and Configuration
```python
# OLD → NEW

K_DIMENSIONS                   → PHI_DIMENSIONS
K_DIMENSION_NAMES              → PHI_DIMENSION_NAMES
DEFAULT_K_CONFIG               → DEFAULT_PHI_CONFIG
K_THRESHOLDS                   → PHI_THRESHOLDS
```

---

## 📝 Documentation Naming

### Document Titles
```
OLD → NEW

K-Index Framework              → Φ-Profile Framework
8D K-Index                     → 8D Φ-Profile
Dynamic K-Index                → Dynamic Φ-Profile
K-Index Visualization          → Φ-Profile Visualization
```

### Section Headers
```markdown
# OLD
## K-Index Computation
## K_Topo Analysis
## K-Index Comparison

# NEW
## Φ-Profile Computation
## Φ_Topo Analysis
## Φ-Profile Comparison
```

### Inline References
```markdown
# OLD
The K-Index measures...
Models with high K_Topo...
K_A represents agency...

# NEW
The Φ-Profile measures...
Models with high Φ_Topo...
Φ_A represents agency...
```

---

## 🎓 Academic Writing Style

### Paper Title Examples
```
# OLD
"K-Index: An 8-Dimensional Framework for LLM Consciousness Profiling"

# NEW (RECOMMENDED)
"The Φ-Profile: An 8-Dimensional Framework for Large Language Model Consciousness Measurement"
"Φ-Profile Dynamics: Tracking Consciousness Evolution in LLM Conversations"
"Cross-Model Capability Prediction via Φ-Profile Signatures"
```

### Abstract Template
```
We introduce the Φ-Profile (Phi-Profile), an 8-dimensional framework
for measuring consciousness signatures in large language models (LLMs).
The Φ-Profile captures eight fundamental aspects of machine consciousness:
Φ_R (responsiveness), Φ_A (agency), Φ_I (integration), Φ_P (presence),
Φ_M (memory), Φ_H (coherence), Φ_Topo (topological structure), and
Φ_geo (geometric distribution). We demonstrate that Φ-Profiles enable...
```

### Citation Format
```bibtex
@article{phi_profile_2025,
  title={The $\Phi$-Profile: An 8-Dimensional Framework for LLM Consciousness Measurement},
  author={[Authors]},
  journal={[Conference/Journal]},
  year={2025},
  keywords={LLM, consciousness, measurement, topological data analysis}
}
```

---

## 🔬 Revolutionary Improvements with Φ Notation

### 1. Dynamic Φ-Profile
```python
def compute_dynamic_phi_profile(conversation, window_size=5):
    """
    Track Φ-Profile evolution within conversations.

    Returns:
        phi_trajectories: Dict[str, List[float]]  # 8 trajectories
        phi_velocity: Dict[str, np.ndarray]       # dΦ/dt
        phi_acceleration: Dict[str, np.ndarray]   # d²Φ/dt²
    """
```

### 2. Causal Φ-Profile
```python
def causal_phi_intervention(model, intervention_type):
    """
    Test causal hypotheses via controlled experiments.

    Returns:
        causal_effect: float  # ΔΦ due to intervention
        p_value: float        # Statistical significance
    """
```

### 3. Cross-Model Φ-Prediction
```python
def predict_from_phi(phi_vector):
    """
    Predict model capabilities from Φ-Profile alone.

    Args:
        phi_vector: 8D Φ-Profile

    Returns:
        predicted_mmlu: float
        predicted_humaneval: float
    """
```

---

## 🌐 Multi-Language Support

### LaTeX
```latex
\documentclass{article}
\usepackage{amssymb}

\newcommand{\PhiProfile}{\ensuremath{\Phi}\text{-Profile}}
\newcommand{\PhiR}{\ensuremath{\Phi_R}}
\newcommand{\PhiTopo}{\ensuremath{\Phi_{\text{Topo}}}}

The \PhiProfile\ framework measures consciousness via eight dimensions...
```

### Python Docstrings
```python
def compute_phi_profile(conversation):
    """
    Compute 8-dimensional Φ-Profile (Phi-Profile) for an LLM conversation.

    The Φ-Profile captures consciousness signatures across 8 dimensions:
    - Φ_R: Responsiveness to user queries
    - Φ_A: Agency and proactive behavior
    - ... [continues]

    Returns:
        phi_vector: 8D numpy array with Φ-Profile
    """
```

### README and Documentation
```markdown
# 🌊 The Φ-Profile Framework

**Φ-Profile** (Phi-Profile) is an 8-dimensional framework for measuring
consciousness signatures in large language models.

## What is Φ?

Φ (Greek letter Phi) represents the fundamental measure of consciousness
in this framework, inspired by:
- The golden ratio (universal harmony)
- Integrated Information Theory (Φ as consciousness measure)
- Mathematical elegance and scientific rigor
```

---

## 🎯 Implementation Priority

### Phase 1: Core Module Rename (Week 1)
1. Rename `kosmic_k_index_llm.py` → `phi_profile_llm.py`
2. Update all function names
3. Update all variable names
4. Ensure backward compatibility wrapper

### Phase 2: Analysis Tools (Week 1-2)
1. Rename `dynamic_k_index.py` → `dynamic_phi_profile.py`
2. Update visualization labels
3. Update result file names
4. Update test suite

### Phase 3: Documentation (Week 2)
1. Update all markdown files
2. Update session summaries
3. Create LaTeX templates
4. Update README and guides

### Phase 4: Publication Prep (Week 3-4)
1. Draft manuscript with Φ-Profile terminology
2. Create publication-quality figures
3. Prepare supplementary materials
4. Submit to conference/journal

---

## 🔧 Backward Compatibility

To support existing code during transition:

```python
# Deprecated aliases (remove after v2.0)
K_Index = PhiProfile  # Deprecated: Use PhiProfile
compute_k_index = compute_phi_profile  # Deprecated

import warnings
def compute_k_index(*args, **kwargs):
    warnings.warn(
        "compute_k_index is deprecated, use compute_phi_profile instead",
        DeprecationWarning,
        stacklevel=2
    )
    return compute_phi_profile(*args, **kwargs)
```

---

## 📊 Impact Projection

### Scientific Credibility
- **Before (K-Index)**: "Sounds like a custom metric"
- **After (Φ-Profile)**: "Mathematical elegance, clear connection to consciousness theory"

### Citation Appeal
- Φ symbol is memorable and visually distinctive
- Easy to typeset in LaTeX
- Aligns with existing consciousness literature (IIT)

### Community Adoption
- Professional naming attracts serious researchers
- Clear separation from informal/internal names
- Ready for production use

---

## ✅ Checklist for Complete Rebrand

### Code
- [ ] Rename core module: `phi_profile_llm.py`
- [ ] Update all function names
- [ ] Update all class names
- [ ] Update all variable names
- [ ] Update test suite
- [ ] Add deprecation warnings

### Documentation
- [ ] Update README.md
- [ ] Update REVOLUTIONARY_IMPROVEMENTS.md
- [ ] Update SESSION_SUMMARY.md
- [ ] Update IMPLEMENTATION_GUIDE.md
- [ ] Create LaTeX templates
- [ ] Update all inline references

### Infrastructure
- [ ] Rename result directories
- [ ] Update visualization labels
- [ ] Update configuration files
- [ ] Update logging messages
- [ ] Update error messages

### Publication
- [ ] Draft manuscript with Φ-Profile
- [ ] Create publication figures
- [ ] Prepare BibTeX entries
- [ ] Update presentation materials

---

## 🌊 Final Status

**Framework Name**: Φ-Profile (Phi-Profile)
**Scientific Readiness**: Publication-grade terminology
**Implementation**: Ready for systematic rebrand
**Impact**: Maximum academic credibility and memorability

---

*"From K-Index to Φ-Profile: Elevating consciousness measurement to scientific excellence."*

**Status**: Naming convention complete. Ready for systematic implementation! 🚀
