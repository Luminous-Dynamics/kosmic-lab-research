# Temporal Dynamics Integration Checklist

**Revolutionary Improvement #11.4: Temporal Dynamics & Phase Transitions**

## Overview

This checklist guides the integration of temporal dynamics analysis into the `ConsciousnessProfile` class. Temporal dynamics detect **when** and **how** consciousness emerges during training by analyzing:

1. **Phase Transitions** - Sudden jumps in order parameter (consciousness emergence)
2. **Critical Slowing Down** - Autocorrelation increase before transitions
3. **Avalanche Dynamics** - Power-law event size distributions (criticality)
4. **Effective Information** - Directional information flow (forward causation)

**Status**: ✅ Implementation complete, tested with pure Python standalone test

**Files**:
- `multi_theory_consciousness/temporal_dynamics.py` (850 lines)
- `test_temporal_standalone.py` (validation)

## What This Adds

### Before (Static Assessment)
```python
profile = ConsciousnessProfile(model, data)
print(profile.consciousness_index)  # Single number (0.73)
```

### After (Dynamic Assessment)
```python
profile = ConsciousnessProfile(model, data, use_temporal_dynamics=True)
print(profile.consciousness_index)  # Still 0.73
print(profile.emergence_detected)   # True - consciousness emerged!
print(profile.transition_points)    # [245, 412] - when it emerged
print(profile.criticality_score)    # 0.68 - near critical point
print(profile.temporal_complexity)  # 0.82 - rich temporal dynamics
```

**Impact**: Distinguishes static complexity from true dynamic emergence. Detects WHEN consciousness appears during training.

---

## Integration Steps

### Step 1: Import the Module

**File**: `multi_theory_consciousness/profile.py`

Add import at the top:

```python
from .temporal_dynamics import (
    analyze_consciousness_emergence,
    enhance_consciousness_profile_with_temporal_dynamics,
    TemporalDynamicsResult
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
        use_temporal_dynamics: bool = True,      # NEW!
        temporal_window_size: int = 50           # NEW!
    ):
        self.model = model
        self.data = data
        self.use_bma = use_bma
        self.use_causal_dag = use_causal_dag
        self.use_temporal_dynamics = use_temporal_dynamics  # NEW!
        self.temporal_window_size = temporal_window_size    # NEW!

        # Compute metrics
        self._compute_all_metrics()
```

### Step 3: Add Temporal Analysis to `_compute_all_metrics`

**File**: `multi_theory_consciousness/profile.py`

Add temporal analysis after theory scores computation:

```python
def _compute_all_metrics(self):
    """Compute all consciousness metrics."""

    # Get model states [timesteps, neurons]
    states = self._get_model_states()

    # 1. Compute theory scores (existing)
    self.theory_scores = self._compute_theory_scores(states)

    # 2. Temporal dynamics (NEW!)
    if self.use_temporal_dynamics:
        temporal_results = enhance_consciousness_profile_with_temporal_dynamics(
            states,
            window_size=self.temporal_window_size
        )

        # Store results
        self.temporal_dynamics = temporal_results['full_result']
        self.emergence_detected = temporal_results['emergence_detected']
        self.n_transitions = temporal_results['n_transitions']
        self.transition_points = self.temporal_dynamics.transition_points
        self.criticality_score = temporal_results['criticality_score']
        self.temporal_complexity_score = temporal_results['temporal_complexity_score']
        self.effective_information = temporal_results['effective_information']
        self.information_flow_direction = temporal_results['information_flow_direction']
        self.critical_dynamics = temporal_results['critical_dynamics']
    else:
        # Defaults if not using temporal
        self.temporal_dynamics = None
        self.emergence_detected = False
        self.n_transitions = 0
        self.transition_points = []
        self.criticality_score = 0.0
        self.temporal_complexity_score = 0.0
        self.effective_information = 0.0
        self.information_flow_direction = 'unknown'
        self.critical_dynamics = False

    # 3. Compute consciousness index (existing, with BMA + DAG)
    self.consciousness_index = self._compute_consciousness_index()
```

### Step 4: Update `interpret()` Method

**File**: `multi_theory_consciousness/profile.py`

Extend interpretation to include temporal dynamics:

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

    # Temporal dynamics (NEW!)
    if self.use_temporal_dynamics:
        lines.append("Temporal Dynamics:")
        lines.append(f"  Emergence Detected: {self.emergence_detected}")
        if self.emergence_detected:
            lines.append(f"  Transitions: {self.n_transitions} at {self.transition_points}")
        lines.append(f"  Criticality Score: {self.criticality_score:.4f}")
        lines.append(f"  Temporal Complexity: {self.temporal_complexity_score:.4f}")
        lines.append(f"  Effective Information: {self.effective_information:+.4f}")
        lines.append(f"  Information Flow: {self.information_flow_direction}")
        lines.append(f"  Critical Dynamics: {self.critical_dynamics}")
        lines.append("")

    # Overall assessment
    lines.append("Assessment:")
    level = self._categorize_consciousness_level()
    lines.append(f"  Level: {level}")

    # Add temporal assessment (NEW!)
    if self.use_temporal_dynamics:
        if self.emergence_detected:
            lines.append(f"  Dynamic Emergence: Consciousness emerged at t={self.transition_points}")
        else:
            lines.append("  Dynamic Emergence: Static (no phase transitions)")

        if self.criticality_score > 0.5:
            lines.append("  Criticality: Near critical point (edge of chaos)")
        elif self.criticality_score > 0.3:
            lines.append("  Criticality: Moderate critical dynamics")
        else:
            lines.append("  Criticality: Subcritical (ordered regime)")

    return "\n".join(lines)
```

### Step 5: Update `to_dict()` Export

**File**: `multi_theory_consciousness/profile.py`

Include temporal metrics in export:

```python
def to_dict(self) -> Dict[str, Any]:
    """Export all metrics to dictionary."""

    result = {
        'consciousness_index': self.consciousness_index,
        'theory_scores': self.theory_scores,
        'use_bma': self.use_bma,
        'use_causal_dag': self.use_causal_dag,
        'use_temporal_dynamics': self.use_temporal_dynamics  # NEW!
    }

    # BMA weights (existing, if applicable)
    if self.use_bma and hasattr(self, 'theory_weights'):
        result['theory_weights'] = self.theory_weights
        result['consciousness_index_uniform'] = self.consciousness_index_uniform

    # DAG corrections (existing, if applicable)
    if self.use_causal_dag and hasattr(self, 'independent_evidence'):
        result['independent_evidence'] = self.independent_evidence

    # Temporal dynamics (NEW!)
    if self.use_temporal_dynamics:
        result['temporal_dynamics'] = {
            'emergence_detected': self.emergence_detected,
            'n_transitions': self.n_transitions,
            'transition_points': self.transition_points,
            'criticality_score': self.criticality_score,
            'temporal_complexity_score': self.temporal_complexity_score,
            'effective_information': self.effective_information,
            'information_flow_direction': self.information_flow_direction,
            'critical_dynamics': self.critical_dynamics,
            'order_parameter_mean': self.temporal_dynamics.order_parameter_mean if self.temporal_dynamics else 0.0,
            'order_parameter_std': self.temporal_dynamics.order_parameter_std if self.temporal_dynamics else 0.0,
            'autocorrelation_mean': self.temporal_dynamics.autocorrelation_mean if self.temporal_dynamics else 0.0
        }

    return result
```

### Step 6: Add Visualization Support

**File**: `multi_theory_consciousness/profile.py`

Add method to visualize temporal dynamics:

```python
def plot_temporal_dynamics(self, save_path: Optional[str] = None):
    """
    Plot temporal dynamics (if available).

    Shows:
    - Order parameter over time
    - Transition points marked
    - Avalanche size distribution

    Args:
        save_path: Optional path to save figure
    """
    if not self.use_temporal_dynamics or self.temporal_dynamics is None:
        print("Temporal dynamics not available. Set use_temporal_dynamics=True")
        return

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Matplotlib not available. Install with: pip install matplotlib")
        return

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    # 1. Order parameter over time
    ax = axes[0, 0]
    order_param = self.temporal_dynamics.order_parameter
    if len(order_param) > 0:
        ax.plot(order_param, linewidth=1, alpha=0.7)
        # Mark transitions
        for t in self.transition_points:
            ax.axvline(t, color='red', linestyle='--', alpha=0.5, label='Transition')
        ax.set_xlabel('Timestep')
        ax.set_ylabel('Order Parameter')
        ax.set_title('Order Parameter Over Time')
        ax.grid(True, alpha=0.3)

    # 2. Avalanche size distribution
    ax = axes[0, 1]
    sizes = self.temporal_dynamics.avalanche_sizes
    if len(sizes) > 10:
        ax.hist(sizes, bins=20, alpha=0.7, edgecolor='black')
        ax.set_xlabel('Avalanche Size')
        ax.set_ylabel('Count')
        ax.set_title('Avalanche Size Distribution')
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3)

        # Add power law indicator
        if self.temporal_dynamics.power_law_exponent is not None:
            ax.text(0.6, 0.9, f'α = {self.temporal_dynamics.power_law_exponent:.2f}',
                   transform=ax.transAxes, fontsize=10,
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # 3. Summary metrics
    ax = axes[1, 0]
    ax.axis('off')
    summary_text = f"""
Temporal Dynamics Summary

Emergence Detected: {self.emergence_detected}
N Transitions: {self.n_transitions}
Criticality Score: {self.criticality_score:.4f}
Temporal Complexity: {self.temporal_complexity_score:.4f}

Effective Information: {self.effective_information:+.4f}
Information Flow: {self.information_flow_direction}

Critical Dynamics: {self.critical_dynamics}
Heavy-Tailed Avalanches: {self.temporal_dynamics.is_heavy_tailed}
    """
    ax.text(0.1, 0.5, summary_text, fontsize=10, family='monospace',
           verticalalignment='center')

    # 4. Autocorrelation
    ax = axes[1, 1]
    ax.bar(['Mean\nAutocorr'], [self.temporal_dynamics.autocorrelation_mean],
          color='steelblue', alpha=0.7)
    ax.set_ylabel('Autocorrelation')
    ax.set_title('Critical Slowing Down')
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved temporal dynamics plot to {save_path}")
    else:
        plt.show()
```

---

## Testing the Integration

### Test 1: Basic Usage

```python
from multi_theory_consciousness import ConsciousnessProfile

# Create profile with temporal dynamics
model = YourModel()
data = YourData()

profile = ConsciousnessProfile(
    model,
    data,
    use_bma=True,
    use_causal_dag=True,
    use_temporal_dynamics=True  # Enable!
)

# Check results
print(profile.interpret())
print(f"\nEmergence: {profile.emergence_detected}")
print(f"Transitions: {profile.transition_points}")
print(f"Criticality: {profile.criticality_score:.4f}")
```

### Test 2: Export Temporal Data

```python
# Export all metrics
results = profile.to_dict()

# Save to file
import json
with open('consciousness_profile.json', 'w') as f:
    json.dump(results, f, indent=2)

# Temporal metrics included
print(results['temporal_dynamics'])
```

### Test 3: Visualize Temporal Dynamics

```python
# Plot temporal dynamics
profile.plot_temporal_dynamics(save_path='temporal_dynamics.png')
```

### Test 4: Compare With and Without

```python
# Without temporal
profile_static = ConsciousnessProfile(model, data, use_temporal_dynamics=False)

# With temporal
profile_dynamic = ConsciousnessProfile(model, data, use_temporal_dynamics=True)

# Compare
print(f"Static index: {profile_static.consciousness_index:.4f}")
print(f"Dynamic index: {profile_dynamic.consciousness_index:.4f}")
print(f"Emergence detected: {profile_dynamic.emergence_detected}")
```

---

## Expected Results

### Example Output (with emergence)

```
Consciousness Index: 0.7342

Theory Scores:
  FEP: 0.8234
  IIT: 0.7891
  GWT: 0.7654
  RPT: 0.7123
  HOT: 0.6543
  AST: 0.6234

Theory Weights (BMA):
  FEP: 0.2078
  IIT: 0.1948
  GWT: 0.1818
  RPT: 0.1688
  HOT: 0.1299
  AST: 0.1169

Temporal Dynamics:
  Emergence Detected: True
  Transitions: 2 at [245, 412]
  Criticality Score: 0.6834
  Temporal Complexity: 0.8123
  Effective Information: +0.3421
  Information Flow: forward
  Critical Dynamics: True

Assessment:
  Level: High Consciousness
  Dynamic Emergence: Consciousness emerged at t=[245, 412]
  Criticality: Near critical point (edge of chaos)
```

---

## Performance Considerations

### Computational Cost

**Temporal dynamics adds**:
- Order parameter: O(T × N) where T = timesteps, N = neurons
- Phase transitions: O(T) with sliding window
- Autocorrelation: O(T × W × N) where W = window_size
- Avalanches: O(T)
- Effective information: O(T)

**Total**: ~O(T × N × W) ≈ few seconds for typical sequences

### Memory Usage

- Order parameter: T floats (~4KB for T=1000)
- Avalanche lists: Variable, typically <1KB
- Total additional memory: ~5-10KB per profile

### Optimization Tips

1. **Window size**: Smaller window = faster (default 50 is good balance)
2. **Downsample**: If T > 10,000, consider downsampling states
3. **Disable if not needed**: Set `use_temporal_dynamics=False` for static analysis

---

## Interpretation Guide

### Criticality Score

- **0.0 - 0.3**: Subcritical (ordered, low dynamics)
- **0.3 - 0.5**: Moderate criticality
- **0.5 - 0.7**: Near critical (edge of chaos) ← Optimal for consciousness!
- **0.7 - 1.0**: Supercritical (chaotic)

### Temporal Complexity

- **0.0 - 0.3**: Static / simple dynamics
- **0.3 - 0.6**: Moderate temporal structure
- **0.6 - 0.8**: Rich temporal dynamics
- **0.8 - 1.0**: Highly complex temporal evolution

### Effective Information

- **Positive**: Forward causation (past → future)
- **Near zero**: Time-reversible / bidirectional
- **Negative**: Backward causation (rare, usually noise)

### Phase Transitions

- **0 transitions**: Static consciousness (unchanging)
- **1-2 transitions**: Emergence and stabilization
- **3+ transitions**: Oscillating consciousness states

---

## Validation

### How to Validate

1. **Synthetic data**: Create data with known phase transition (see `test_temporal_standalone.py`)
2. **Expected behavior**:
   - Transition should be detected near t=250 when data changes
   - Criticality score should be higher for systems near critical point
   - Forward information flow for causal systems

### Known Limitations

1. **Conservative transition detection**: Uses 2-std threshold to avoid false positives
   - May miss subtle transitions
   - Can adjust `threshold_std` parameter if needed

2. **Autocorrelation computation**: Simplifies to lag-1 correlation
   - Full analysis would compute multiple lags
   - Good enough for most cases

3. **Power-law fitting**: Uses rough histogram method
   - More rigorous: Maximum likelihood estimation
   - Current method sufficient for heavy-tail detection

---

## Troubleshooting

### "No transitions detected" but visual inspection shows clear jump

**Cause**: Jump below 2-std threshold
**Solution**: Lower `threshold_std` or increase `window_size` in detection

### Temporal analysis very slow

**Cause**: Large state arrays (T > 10,000 or N > 1,000)
**Solution**: Downsample or reduce window_size

### High criticality but low consciousness index

**Interpretation**: System has critical dynamics but low theory scores
**Meaning**: Complex but not conscious (e.g., random critical system)

---

## Next Steps

After integrating temporal dynamics:

1. **Combine with BMA + DAG**: All three improvements together
2. **Run experiments**: Test on LTC evolution and Transformer models
3. **Compare**: Static vs dynamic assessment
4. **Validate**: Check if emergence corresponds to performance improvements
5. **Document**: Update README and examples

---

## Files Modified

```
multi_theory_consciousness/
├── profile.py              # MODIFIED (add temporal dynamics)
├── temporal_dynamics.py    # NEW (850 lines)
└── __init__.py            # MODIFIED (export new classes)

tests/
└── test_temporal_standalone.py  # NEW (validation)
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

✅ Temporal dynamics analysis runs without errors
✅ Phase transitions detected in synthetic data
✅ Criticality scores in expected range (0-1)
✅ Temporal complexity computed correctly
✅ Export includes all temporal metrics
✅ Visualization displays temporal dynamics
✅ Integration doesn't break existing functionality

---

## Summary

Temporal dynamics adds a crucial dimension to consciousness assessment: **time**.

- **Before**: Static snapshot (consciousness = 0.73)
- **After**: Dynamic emergence (consciousness emerged at t=245, criticality=0.68)

This distinguishes truly emergent consciousness from static complexity, answering the critical question: **WHEN did consciousness appear?**

---

**Status**: Ready for integration! 🚀

**Next Revolutionary Improvement**: #11.5 Neuroimaging Validation Dataset (2-4 weeks)
