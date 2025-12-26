# Hierarchical Consciousness Integration Checklist

**Revolutionary Improvement #11.6: Hierarchical/Compositional Consciousness Assessment**

## Overview

This checklist guides the integration of hierarchical consciousness analysis into the `ConsciousnessProfile` class. Hierarchical analysis answers critical questions:

1. **WHERE does consciousness live?** (localization across network regions)
2. **Is consciousness distributed or localized?** (consciousness distribution)
3. **Does emergence occur?** (whole > sum of parts)
4. **How do levels integrate?** (cross-level coherence)

**Status**: ✅ Implementation complete, tested with pure Python standalone test

**Files**:
- `multi_theory_consciousness/hierarchical_consciousness.py` (700 lines)
- `test_hierarchical_standalone.py` (validation)

## What This Adds

### Before (Monolithic Assessment)
```python
profile = ConsciousnessProfile(model, data)
print(profile.consciousness_index)  # 0.73
# Where in the network? No idea!
```

### After (Hierarchical Assessment)
```python
profile = ConsciousnessProfile(model, data, use_hierarchy=True, n_levels=4)
print(profile.consciousness_index)  # Still 0.73
print(profile.dominant_level)       # Level 3 (upper layers!)
print(profile.consciousness_distribution)  # {0: 12%, 1: 23%, 2: 28%, 3: 37%}
print(profile.emergence_score)      # +0.15 (emergence detected!)
print(profile.is_emergent)          # True - whole > sum of parts
```

**Impact**: Distinguishes localized from distributed consciousness. Detects WHERE consciousness lives and tests for emergence.

---

## Integration Steps

### Step 1: Import the Module

**File**: `multi_theory_consciousness/profile.py`

Add import at the top:

```python
from .hierarchical_consciousness import (
    compute_hierarchical_consciousness,
    enhance_consciousness_profile_with_hierarchy,
    HierarchicalConsciousnessResult,
    HierarchicalLevel
)
```

### Step 2: Add Parameters to `__init__`

**File**: `multi_theory_consciousness/profile.py`

Modify `ConsciousnessProfile.__init__`:

```python
class ConsciousnessProfile:
    def __init__(
        self,
        model: Any,
        data: Any,
        use_bma: bool = True,                    # Existing
        use_causal_dag: bool = True,             # Existing
        use_temporal_dynamics: bool = True,      # Existing
        use_hierarchy: bool = True,              # NEW!
        hierarchy_type: str = 'modular',         # NEW! 'spatial' or 'modular'
        n_levels: int = 4                        # NEW!
    ):
        self.model = model
        self.data = data
        self.use_bma = use_bma
        self.use_causal_dag = use_causal_dag
        self.use_temporal_dynamics = use_temporal_dynamics
        self.use_hierarchy = use_hierarchy              # NEW!
        self.hierarchy_type = hierarchy_type            # NEW!
        self.n_levels = n_levels                        # NEW!

        # Compute metrics
        self._compute_all_metrics()
```

### Step 3: Add Hierarchical Analysis to `_compute_all_metrics`

**File**: `multi_theory_consciousness/profile.py`

Add hierarchical analysis after theory scores computation:

```python
def _compute_all_metrics(self):
    """Compute all consciousness metrics."""

    # Get model states [timesteps, neurons]
    states = self._get_model_states()

    # 1. Compute theory scores (existing)
    self.theory_scores = self._compute_theory_scores(states)

    # 2. Temporal dynamics (existing, if enabled)
    if self.use_temporal_dynamics:
        # ... temporal analysis ...

    # 3. Hierarchical analysis (NEW!)
    if self.use_hierarchy:
        hierarchical_results = enhance_consciousness_profile_with_hierarchy(
            states,
            hierarchy_type=self.hierarchy_type,
            n_levels=self.n_levels
        )

        # Store results
        self.hierarchical = hierarchical_results['full_result']
        self.n_hierarchy_levels = hierarchical_results['n_levels']
        self.whole_system_consciousness = hierarchical_results['whole_system_consciousness']
        self.sum_of_parts = hierarchical_results['sum_of_parts']
        self.emergence_score = hierarchical_results['emergence_score']
        self.is_emergent = hierarchical_results['is_emergent']
        self.emergence_type = hierarchical_results['emergence_type']
        self.mean_integration = hierarchical_results['mean_integration']
        self.dominant_level = hierarchical_results['dominant_level']
        self.consciousness_distribution = hierarchical_results['consciousness_distribution']
    else:
        # Defaults if not using hierarchy
        self.hierarchical = None
        self.n_hierarchy_levels = 1
        self.whole_system_consciousness = 0.0
        self.sum_of_parts = 0.0
        self.emergence_score = 0.0
        self.is_emergent = False
        self.emergence_type = 'none'
        self.mean_integration = 0.0
        self.dominant_level = 0
        self.consciousness_distribution = {'level_0': 1.0}

    # 4. Compute consciousness index (existing, with BMA + DAG)
    self.consciousness_index = self._compute_consciousness_index()
```

### Step 4: Update `interpret()` Method

**File**: `multi_theory_consciousness/profile.py`

Extend interpretation to include hierarchical analysis:

```python
def interpret(self) -> str:
    """Generate human-readable interpretation."""

    lines = []
    lines.append(f"Consciousness Index: {self.consciousness_index:.4f}")
    lines.append("")

    # Theory scores (existing)
    lines.append("Theory Scores:")
    for theory, score in sorted(self.theory_scores.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"  {theory}: {score:.4f}")
    lines.append("")

    # BMA weights (existing, if using)
    if self.use_bma and hasattr(self, 'theory_weights'):
        lines.append("Theory Weights (BMA):")
        for theory, weight in sorted(self.theory_weights.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  {theory}: {weight:.4f}")
        lines.append("")

    # Temporal dynamics (existing, if using)
    if self.use_temporal_dynamics:
        # ... temporal interpretation ...

    # Hierarchical analysis (NEW!)
    if self.use_hierarchy:
        lines.append("Hierarchical Analysis:")
        lines.append(f"  Hierarchy Type: {self.hierarchy_type}")
        lines.append(f"  Levels: {self.n_hierarchy_levels}")
        lines.append(f"  Dominant Level: Level {self.dominant_level}")
        lines.append("")

        lines.append("Consciousness Distribution:")
        for level_name, fraction in sorted(self.consciousness_distribution.items()):
            level_num = int(level_name.split('_')[1])
            bar_length = int(fraction * 40)
            bar = '█' * bar_length + '░' * (40 - bar_length)
            lines.append(f"  {level_name}: {bar} {fraction:.1%}")
        lines.append("")

        lines.append(f"  Whole System:      {self.whole_system_consciousness:.4f}")
        lines.append(f"  Sum of Parts:      {self.sum_of_parts:.4f}")
        lines.append(f"  Emergence Score:   {self.emergence_score:+.4f}")
        lines.append(f"  Is Emergent:       {self.is_emergent} ({self.emergence_type})")
        lines.append(f"  Mean Integration:  {self.mean_integration:.4f}")
        lines.append("")

    # Overall assessment
    lines.append("Assessment:")
    level = self._categorize_consciousness_level()
    lines.append(f"  Level: {level}")

    # Add hierarchical assessment (NEW!)
    if self.use_hierarchy:
        # Localization
        total_levels = self.n_hierarchy_levels
        dominant_fraction = self.consciousness_distribution[f'level_{self.dominant_level}']

        if dominant_fraction > 0.6:
            lines.append(f"  Localization: Highly localized (Level {self.dominant_level}: {dominant_fraction:.0%})")
        elif dominant_fraction > 0.4:
            lines.append(f"  Localization: Moderately localized (Level {self.dominant_level}: {dominant_fraction:.0%})")
        else:
            lines.append("  Localization: Distributed across levels")

        # Emergence
        if self.is_emergent:
            if self.emergence_type == 'strong':
                lines.append(f"  Emergence: Strong emergence detected (+{self.emergence_score:.3f})")
            else:
                lines.append(f"  Emergence: Weak emergence detected (+{self.emergence_score:.3f})")
        else:
            lines.append("  Emergence: No emergence (whole ≈ sum of parts)")

        # Integration
        if self.mean_integration > 0.7:
            lines.append("  Integration: High cross-level integration")
        elif self.mean_integration > 0.4:
            lines.append("  Integration: Moderate cross-level integration")
        else:
            lines.append("  Integration: Low cross-level integration")

    return "\n".join(lines)
```

### Step 5: Update `to_dict()` Export

**File**: `multi_theory_consciousness/profile.py`

Include hierarchical metrics in export:

```python
def to_dict(self) -> Dict[str, Any]:
    """Export all metrics to dictionary."""

    result = {
        'consciousness_index': self.consciousness_index,
        'theory_scores': self.theory_scores,
        'use_bma': self.use_bma,
        'use_causal_dag': self.use_causal_dag,
        'use_temporal_dynamics': self.use_temporal_dynamics,
        'use_hierarchy': self.use_hierarchy  # NEW!
    }

    # BMA weights (existing, if applicable)
    if self.use_bma and hasattr(self, 'theory_weights'):
        result['theory_weights'] = self.theory_weights

    # DAG corrections (existing, if applicable)
    if self.use_causal_dag and hasattr(self, 'independent_evidence'):
        result['independent_evidence'] = self.independent_evidence

    # Temporal dynamics (existing, if applicable)
    if self.use_temporal_dynamics:
        result['temporal_dynamics'] = {
            # ... temporal metrics ...
        }

    # Hierarchical analysis (NEW!)
    if self.use_hierarchy:
        result['hierarchical_analysis'] = {
            'hierarchy_type': self.hierarchy_type,
            'n_levels': self.n_hierarchy_levels,
            'dominant_level': self.dominant_level,
            'consciousness_distribution': self.consciousness_distribution,
            'whole_system_consciousness': self.whole_system_consciousness,
            'sum_of_parts': self.sum_of_parts,
            'emergence_score': self.emergence_score,
            'is_emergent': self.is_emergent,
            'emergence_type': self.emergence_type,
            'mean_integration': self.mean_integration
        }

    return result
```

### Step 6: Add Visualization Support

**File**: `multi_theory_consciousness/profile.py`

Add method to visualize hierarchical structure:

```python
def plot_hierarchical_structure(self, save_path: Optional[str] = None):
    """
    Plot hierarchical consciousness structure.

    Shows:
    - Consciousness distribution across levels
    - Integration between levels
    - Emergence visualization

    Args:
        save_path: Optional path to save figure
    """
    if not self.use_hierarchy or self.hierarchical is None:
        print("Hierarchical analysis not available. Set use_hierarchy=True")
        return

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Matplotlib not available. Install with: pip install matplotlib")
        return

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    # 1. Consciousness distribution
    ax = axes[0, 0]
    levels = [f"L{i}" for i in range(self.n_hierarchy_levels)]
    consciousness = [
        self.consciousness_distribution[f'level_{i}']
        for i in range(self.n_hierarchy_levels)
    ]
    colors = ['steelblue' if i != self.dominant_level else 'crimson'
             for i in range(self.n_hierarchy_levels)]

    ax.bar(levels, consciousness, color=colors, alpha=0.7, edgecolor='black')
    ax.set_ylabel('Consciousness Fraction')
    ax.set_title('Consciousness Distribution by Level')
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3, axis='y')
    ax.axhline(1.0 / self.n_hierarchy_levels, color='gray', linestyle='--',
              alpha=0.5, label='Uniform')
    ax.legend()

    # 2. Integration between levels
    ax = axes[0, 1]
    if self.hierarchical.integration_between_levels:
        level_pairs = [f"L{i}↔L{i+1}" for i in range(len(self.hierarchical.integration_between_levels))]
        integrations = self.hierarchical.integration_between_levels

        ax.bar(level_pairs, integrations, color='seagreen', alpha=0.7, edgecolor='black')
        ax.axhline(self.mean_integration, color='red', linestyle='--',
                  label=f'Mean: {self.mean_integration:.3f}')
        ax.set_ylabel('Integration')
        ax.set_title('Integration Between Levels')
        ax.set_ylim(0, 1)
        ax.grid(True, alpha=0.3, axis='y')
        ax.legend()
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

    # 3. Emergence visualization
    ax = axes[1, 0]
    ax.axis('off')
    emergence_text = f"""
Emergence Analysis

Whole System:     {self.whole_system_consciousness:.4f}
Sum of Parts:     {self.sum_of_parts:.4f}
Emergence Score:  {self.emergence_score:+.4f}

Is Emergent:      {self.is_emergent}
Type:             {self.emergence_type}

Mean Integration: {self.mean_integration:.4f}
    """
    ax.text(0.1, 0.5, emergence_text, fontsize=11, family='monospace',
           verticalalignment='center')

    # Add visual indicator
    if self.is_emergent:
        indicator_color = 'green' if self.emergence_type == 'strong' else 'orange'
        indicator_text = '✓ EMERGENCE\nDETECTED' if self.is_emergent else '✗ No Emergence'
        ax.text(0.7, 0.5, indicator_text, fontsize=14, weight='bold',
               color=indicator_color, ha='center', va='center',
               bbox=dict(boxstyle='round', facecolor=indicator_color, alpha=0.2))

    # 4. Detailed level breakdown
    ax = axes[1, 1]
    if self.hierarchical.levels:
        level_ids = [level.level_id for level in self.hierarchical.levels]
        level_k = [level.consciousness_index for level in self.hierarchical.levels]

        ax.plot(level_ids, level_k, marker='o', markersize=10,
               linewidth=2, color='steelblue', label='K-index')
        ax.scatter([self.dominant_level], [self.hierarchical.levels[self.dominant_level].consciousness_index],
                  s=200, color='crimson', marker='*', zorder=10, label='Dominant')
        ax.set_xlabel('Level')
        ax.set_ylabel('Consciousness Index')
        ax.set_title('Consciousness Index by Level')
        ax.grid(True, alpha=0.3)
        ax.legend()

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved hierarchical structure plot to {save_path}")
    else:
        plt.show()
```

---

## Testing the Integration

### Test 1: Basic Usage

```python
from multi_theory_consciousness import ConsciousnessProfile

# Create profile with hierarchical analysis
model = YourModel()
data = YourData()

profile = ConsciousnessProfile(
    model,
    data,
    use_bma=True,
    use_causal_dag=True,
    use_temporal_dynamics=True,
    use_hierarchy=True,          # Enable!
    hierarchy_type='modular',    # or 'spatial'
    n_levels=4
)

# Check results
print(profile.interpret())
print(f"\nDominant level: {profile.dominant_level}")
print(f"Emergence: {profile.emergence_score:+.3f}")
print(f"Is emergent: {profile.is_emergent}")
```

### Test 2: Compare Hierarchy Types

```python
# Spatial hierarchy
profile_spatial = ConsciousnessProfile(
    model, data, use_hierarchy=True, hierarchy_type='spatial', n_levels=4
)

# Modular hierarchy
profile_modular = ConsciousnessProfile(
    model, data, use_hierarchy=True, hierarchy_type='modular', n_levels=4
)

# Compare
print("Spatial:", profile_spatial.dominant_level, profile_spatial.emergence_score)
print("Modular:", profile_modular.dominant_level, profile_modular.emergence_score)
```

### Test 3: Find Optimal Number of Levels

```python
from multi_theory_consciousness.hierarchical_consciousness import find_optimal_hierarchy

states = model.get_hidden_states(data)
optimal_n, result = find_optimal_hierarchy(states, min_levels=2, max_levels=10)

print(f"Optimal number of levels: {optimal_n}")
print(f"Emergence score: {result.emergence_score:+.3f}")
```

### Test 4: Visualize

```python
# Plot hierarchical structure
profile.plot_hierarchical_structure(save_path='hierarchical_structure.png')
```

---

## Expected Results

### Example Output (Localized Consciousness)

```
Consciousness Index: 0.7342

Theory Scores:
  FEP: 0.8234
  IIT: 0.7891
  ...

Hierarchical Analysis:
  Hierarchy Type: modular
  Levels: 4
  Dominant Level: Level 3

Consciousness Distribution:
  level_0: ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 12.3%
  level_1: ██████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 23.4%
  level_2: ████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 27.8%
  level_3: ███████████████░░░░░░░░░░░░░░░░░░░░░░░░░ 36.5%

  Whole System:      0.7342
  Sum of Parts:      0.6891
  Emergence Score:   +0.1234
  Is Emergent:       True (weak)
  Mean Integration:  0.5678

Assessment:
  Level: High Consciousness
  Localization: Moderately localized (Level 3: 37%)
  Emergence: Weak emergence detected (+0.123)
  Integration: Moderate cross-level integration
```

### Example Output (Distributed Consciousness)

```
Hierarchical Analysis:
  Hierarchy Type: spatial
  Levels: 5
  Dominant Level: Level 2

Consciousness Distribution:
  level_0: ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 18%
  level_1: ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 19%
  level_2: █████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 22%
  level_3: ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 21%
  level_4: ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 20%

Assessment:
  Localization: Distributed across levels
  Emergence: No emergence (whole ≈ sum of parts)
  Integration: High cross-level integration
```

---

## Performance Considerations

### Computational Cost

**Hierarchical analysis adds**:
- Level extraction: O(N × L) where N = neurons, L = levels
- Per-level consciousness: O(T × N/L) per level → O(T × N) total
- Integration: O(T × (N/L)² × L) ≈ O(T × N²/L) with sampling
- Total: ~O(T × N) with careful sampling

**Typical cost**: ~1-2 seconds for T=1000, N=512, L=4

### Memory Usage

- Level states: N × L indices (~4KB for 512 neurons, 4 levels)
- Consciousness per level: L floats (~32 bytes for 4 levels)
- Integration scores: (L-1) floats
- **Total**: <10KB additional per profile

### Optimization Tips

1. **Sample neurons for integration**: Don't compute all N² pairs
2. **Cache level states**: Reuse extractions if analyzing multiple times
3. **Spatial over modular**: Spatial is faster (no clustering)
4. **Fewer levels**: L=3-4 is usually sufficient

---

## Interpretation Guide

### Localization

**Highly Localized** (dominant level > 60%):
- Consciousness concentrated in specific layers/modules
- Example: Upper layers in transformer (semantic processing)

**Moderately Localized** (dominant level 40-60%):
- Primary locus but with significant distribution
- Example: Distributed across middle and upper layers

**Distributed** (dominant level < 40%):
- Consciousness spread across network
- Example: Fully connected networks

### Emergence

**Strong Emergence** (score > 0.2):
- Whole system significantly exceeds parts
- High integration enables emergent properties
- Global consciousness from local components

**Weak Emergence** (score 0.05-0.2):
- Modest emergence
- Some integration-enabled properties

**No Emergence** (score < 0.05):
- Whole ≈ sum of parts
- Additive consciousness (no synergy)

### Integration

**High Integration** (> 0.7):
- Levels strongly coupled
- Information flows freely
- Enables emergence

**Moderate Integration** (0.4-0.7):
- Some cross-level coherence
- Partial information flow

**Low Integration** (< 0.4):
- Levels relatively independent
- Limited cross-level communication
- Blocks emergence

---

## Troubleshooting

### "All levels have same consciousness"

**Cause**: Network not hierarchically structured
**Solution**: Try modular clustering instead of spatial, or increase n_levels

### "No emergence detected" but visual inspection shows integration

**Cause**: Conservative emergence threshold
**Solution**: Emergence score is relative - check if > 0 indicates some emergence

### Hierarchical analysis very slow

**Cause**: Too many levels or neurons
**Solution**: Reduce n_levels or use sampling in integration computation

---

## Next Steps

After integrating hierarchical analysis:

1. **Combine with all improvements**: FEP + BMA + DAG + Temporal + Hierarchy
2. **Analyze layer-wise consciousness** in transformers
3. **Test emergence hypothesis**: Do large models show emergence?
4. **Identify conscious modules**: Where does consciousness live?
5. **Validate**: Does localization correspond to known network architecture?

---

## Files Modified

```
multi_theory_consciousness/
├── profile.py                           # MODIFIED (add hierarchical analysis)
├── hierarchical_consciousness.py        # NEW (700 lines)
└── __init__.py                         # MODIFIED (export new classes)

tests/
└── test_hierarchical_standalone.py     # NEW (validation)
```

---

## Estimated Integration Time

- Step 1-3: **30 minutes** (imports, parameters, metric computation)
- Step 4-5: **30 minutes** (interpret, export)
- Step 6: **30 minutes** (visualization)
- Testing: **30 minutes** (run tests, validate)

**Total**: ~2 hours for complete integration

---

## Success Criteria

✅ Hierarchical analysis runs without errors
✅ Levels detected with different consciousness values
✅ Dominant level identified correctly
✅ Emergence score computed
✅ Integration between levels measured
✅ Export includes all hierarchical metrics
✅ Visualization displays hierarchical structure
✅ Integration doesn't break existing functionality

---

## Summary

Hierarchical consciousness analysis adds a spatial dimension to consciousness assessment: **WHERE**.

- **Before**: "This system has consciousness index 0.73" (where? no idea!)
- **After**: "Consciousness localized in upper layers (Level 3: 37%), with weak emergence (+0.12) from cross-level integration (0.57)"

This answers fundamental questions about consciousness localization, distribution, and emergence in neural networks.

---

**Status**: Ready for integration! 🚀

**Next Revolutionary Improvement**: #11.7 Active Learning & Optimal Experiment Design (1 week)
