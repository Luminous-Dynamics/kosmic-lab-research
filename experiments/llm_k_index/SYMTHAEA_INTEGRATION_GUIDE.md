# 🧠 Symthaea Integration Guide
## Consciousness Assessment Framework × Holographic Liquid Brain

**Goal**: Extract Symthaea internal states → Compute consciousness via 12-dimensional framework → Validate & analyze

---

## Step 1: Add Data Export to Symthaea (Rust)

### A. Create Data Export Structures

Add to `symthaea-hlb/src/lib.rs` (or new file `src/export.rs`):

```rust
use serde::{Serialize, Deserialize};

/// Complete consciousness state snapshot for external analysis
#[derive(Serialize, Deserialize, Clone)]
pub struct ConsciousnessSnapshot {
    /// Timestamp of snapshot
    pub timestamp: f64,

    /// HDC Semantic Space
    pub hdc_state: HDCState,

    /// LTC Network State
    pub ltc_state: LTCState,

    /// Consciousness Graph
    pub graph_state: GraphState,

    /// Built-in metrics for validation
    pub builtin_metrics: BuiltinMetrics,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct HDCState {
    /// All active concept vectors (sparse representation)
    /// Map: concept_name -> vector
    pub concept_vectors: HashMap<String, Vec<f32>>,

    /// Current query/context vector
    pub query_vector: Vec<f32>,

    /// Recent memory activations
    pub memory_activations: Vec<(String, f32)>, // (memory_id, activation_level)

    /// Dimensionality
    pub dimension: usize,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct LTCState {
    /// Neuron activations at current timestep
    pub activations: Vec<f32>,

    /// Neuron time constants (τ values)
    pub time_constants: Vec<f32>,

    /// Neuron derivatives (dx/dt)
    pub derivatives: Vec<f32>,

    /// Connection weights (sparse if possible)
    pub weights: Vec<Vec<f32>>, // or use petgraph

    /// Number of neurons
    pub num_neurons: usize,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct GraphState {
    /// Nodes with their properties
    pub nodes: Vec<GraphNode>,

    /// Edges between nodes
    pub edges: Vec<GraphEdge>,

    /// Self-loops (consciousness indicator!)
    pub self_loops: Vec<usize>, // node indices with self-loops

    /// Strongly connected components
    pub sccs: Vec<Vec<usize>>,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct GraphNode {
    pub id: usize,
    pub semantic_similarity: f32,
    pub dynamic_stability: f32,
    pub consciousness_level: f32,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct GraphEdge {
    pub source: usize,
    pub target: usize,
    pub weight: f32,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct BuiltinMetrics {
    /// Symthaea's built-in consciousness measure
    pub consciousness_level: f32,

    /// Number of self-loops
    pub num_self_loops: usize,

    /// Query processing steps
    pub steps_to_emergence: usize,

    /// Response confidence
    pub confidence: f32,
}
```

### B. Add Export Method to SophiaHLB

Add to `SophiaHLB` impl:

```rust
impl SophiaHLB {
    /// Export complete consciousness state for external analysis
    pub fn export_consciousness_snapshot(&self) -> ConsciousnessSnapshot {
        ConsciousnessSnapshot {
            timestamp: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_secs_f64(),

            hdc_state: self.export_hdc_state(),
            ltc_state: self.export_ltc_state(),
            graph_state: self.export_graph_state(),
            builtin_metrics: self.export_builtin_metrics(),
        }
    }

    fn export_hdc_state(&self) -> HDCState {
        HDCState {
            concept_vectors: self.semantic.get_all_concept_vectors(),
            query_vector: self.semantic.get_current_query_vector(),
            memory_activations: self.semantic.get_recent_activations(100),
            dimension: self.semantic.dimension(),
        }
    }

    fn export_ltc_state(&self) -> LTCState {
        LTCState {
            activations: self.ltc.get_activations().to_vec(),
            time_constants: self.ltc.get_time_constants().to_vec(),
            derivatives: self.ltc.get_derivatives().to_vec(),
            weights: self.ltc.get_weights_matrix(),
            num_neurons: self.ltc.num_neurons(),
        }
    }

    fn export_graph_state(&self) -> GraphState {
        let nodes = self.consciousness.get_all_nodes()
            .map(|(id, node)| GraphNode {
                id,
                semantic_similarity: node.semantic_similarity,
                dynamic_stability: node.dynamic_stability,
                consciousness_level: node.consciousness_level,
            })
            .collect();

        let edges = self.consciousness.get_all_edges()
            .map(|edge| GraphEdge {
                source: edge.source,
                target: edge.target,
                weight: edge.weight,
            })
            .collect();

        GraphState {
            nodes,
            edges,
            self_loops: self.consciousness.find_self_loops(),
            sccs: self.consciousness.find_strongly_connected_components(),
        }
    }

    fn export_builtin_metrics(&self) -> BuiltinMetrics {
        let intro = self.introspect();

        BuiltinMetrics {
            consciousness_level: intro.consciousness_level,
            num_self_loops: intro.self_loops,
            steps_to_emergence: intro.steps_to_emergence,
            confidence: intro.confidence,
        }
    }
}
```

### C. Add Batch Export for Longitudinal Studies

```rust
impl SophiaHLB {
    /// Process multiple queries and collect consciousness trajectory
    pub async fn consciousness_trajectory(
        &mut self,
        queries: Vec<String>,
        output_path: &str,
    ) -> Result<Vec<ConsciousnessSnapshot>> {
        let mut snapshots = Vec::new();

        for query in queries {
            // Process query
            let _response = self.process(&query).await?;

            // Export snapshot
            let snapshot = self.export_consciousness_snapshot();
            snapshots.push(snapshot.clone());

            // Save to disk incrementally
            self.save_snapshot(&snapshot, output_path)?;
        }

        Ok(snapshots)
    }

    fn save_snapshot(&self, snapshot: &ConsciousnessSnapshot, path: &str) -> Result<()> {
        let json = serde_json::to_string_pretty(snapshot)?;
        std::fs::write(path, json)?;
        Ok(())
    }
}
```

---

## Step 2: Python Data Loader

Create `symthaea_loader.py` in `experiments/llm_k_index/`:

```python
"""
Load Symthaea consciousness snapshots for analysis.
"""
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class SymthaeaSnapshot:
    """Single consciousness snapshot from Symthaea."""
    timestamp: float

    # HDC State
    concept_vectors: Dict[str, List[float]]
    query_vector: List[float]
    memory_activations: List[tuple]
    hdc_dimension: int

    # LTC State
    ltc_activations: np.ndarray
    time_constants: np.ndarray
    derivatives: np.ndarray
    weights: np.ndarray
    num_neurons: int

    # Graph State
    graph_nodes: List[Dict]
    graph_edges: List[Dict]
    self_loops: List[int]
    sccs: List[List[int]]

    # Built-in metrics
    consciousness_level: float
    num_self_loops: int
    steps_to_emergence: int
    confidence: float

def load_snapshot(filepath: str) -> SymthaeaSnapshot:
    """Load single snapshot from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)

    return SymthaeaSnapshot(
        timestamp=data['timestamp'],

        # HDC
        concept_vectors=data['hdc_state']['concept_vectors'],
        query_vector=data['hdc_state']['query_vector'],
        memory_activations=data['hdc_state']['memory_activations'],
        hdc_dimension=data['hdc_state']['dimension'],

        # LTC
        ltc_activations=np.array(data['ltc_state']['activations']),
        time_constants=np.array(data['ltc_state']['time_constants']),
        derivatives=np.array(data['ltc_state']['derivatives']),
        weights=np.array(data['ltc_state']['weights']),
        num_neurons=data['ltc_state']['num_neurons'],

        # Graph
        graph_nodes=data['graph_state']['nodes'],
        graph_edges=data['graph_state']['edges'],
        self_loops=data['graph_state']['self_loops'],
        sccs=data['graph_state']['sccs'],

        # Metrics
        consciousness_level=data['builtin_metrics']['consciousness_level'],
        num_self_loops=data['builtin_metrics']['num_self_loops'],
        steps_to_emergence=data['builtin_metrics']['steps_to_emergence'],
        confidence=data['builtin_metrics']['confidence'],
    )

def load_trajectory(directory: str) -> List[SymthaeaSnapshot]:
    """Load all snapshots from directory."""
    snapshots = []
    for filepath in sorted(Path(directory).glob('*.json')):
        snapshots.append(load_snapshot(str(filepath)))
    return snapshots
```

---

## Step 3: Consciousness Assessment Adapter

Create `symthaea_consciousness_adapter.py`:

```python
"""
Adapter to compute consciousness scores from Symthaea states.
"""
import numpy as np
from symthaea_loader import SymthaeaSnapshot
from multi_theory_consciousness.profile import ConsciousnessProfile
from multi_theory_consciousness.multimodal_fusion import MultiModalFusion, ModalityEvidence, ModalityType

class SymthaeaConsciousnessAdapter:
    """Compute consciousness from Symthaea using 12-dimensional framework."""

    def __init__(self):
        self.profile = ConsciousnessProfile()
        self.fusion = MultiModalFusion()

    def assess_snapshot(self, snapshot: SymthaeaSnapshot) -> Dict:
        """Full consciousness assessment from single snapshot."""

        # 1. Compute theory scores
        theory_scores = self._compute_theory_scores(snapshot)

        # 2. Multi-modal fusion
        modality_evidence = {
            ModalityType.NEURAL: ModalityEvidence(
                modality=ModalityType.NEURAL,
                consciousness_score=self._neural_consciousness(snapshot),
                confidence=0.90,
                signal_quality=self._ltc_signal_quality(snapshot),
                timestamp=snapshot.timestamp,
                available=True
            ),
            ModalityType.BEHAVIORAL: ModalityEvidence(
                modality=ModalityType.BEHAVIORAL,
                consciousness_score=self._behavioral_consciousness(snapshot),
                confidence=0.75,
                signal_quality=0.85,
                timestamp=snapshot.timestamp,
                available=True
            ),
        }

        multimodal_assessment = self.fusion.fuse_late(modality_evidence)

        # 3. Full profile assessment
        assessment = self.profile.assess_full(
            theory_scores=theory_scores,
            multimodal=multimodal_assessment,
            temporal_window=None,  # Will add for trajectory
        )

        return {
            'timestamp': snapshot.timestamp,
            'consciousness_index': assessment.consciousness_index,
            'confidence': assessment.confidence,
            'theory_contributions': assessment.theory_contributions,
            'builtin_consciousness': snapshot.consciousness_level,
            'agreement': abs(assessment.consciousness_index - snapshot.consciousness_level),
        }

    def _compute_theory_scores(self, snapshot: SymthaeaSnapshot) -> Dict[str, float]:
        """Compute 6 theory scores from Symthaea state."""

        # IIT: Integration via LTC connectivity
        iit_score = self._compute_integration(
            snapshot.ltc_activations,
            snapshot.weights
        )

        # GWT: Broadcast via HDC memory activations
        gwt_score = self._compute_broadcast(
            snapshot.memory_activations,
            snapshot.concept_vectors
        )

        # HOT: Meta-representation via consciousness graph
        hot_score = self._compute_meta_representation(
            snapshot.graph_nodes,
            snapshot.self_loops
        )

        # AST: Attention schema via query focus
        ast_score = self._compute_attention_schema(
            snapshot.query_vector,
            snapshot.ltc_activations
        )

        # RPT: Recurrence via LTC dynamics
        rpt_score = self._compute_recurrence(
            snapshot.derivatives,
            snapshot.time_constants
        )

        # FEP: Prediction error (infer from LTC derivatives)
        fep_score = self._compute_prediction_error(
            snapshot.derivatives,
            snapshot.ltc_activations
        )

        return {
            'IIT': iit_score,
            'GWT': gwt_score,
            'HOT': hot_score,
            'AST': ast_score,
            'RPT': rpt_score,
            'FEP': fep_score,
        }

    def _compute_integration(self, activations, weights):
        """IIT: Φ via effective information."""
        # Simplified: correlation structure
        if len(activations) < 2:
            return 0.0

        # Compute pairwise correlations
        expanded = np.outer(activations, activations)
        masked = expanded * (weights > 0.1)
        integration = np.mean(np.abs(masked))

        return float(np.clip(integration, 0, 1))

    def _compute_broadcast(self, memory_activations, concept_vectors):
        """GWT: How widely is information broadcasted?"""
        if not memory_activations:
            return 0.0

        # Number of active memories / total
        active_count = len([act for _, act in memory_activations if act > 0.5])
        broadcast = active_count / max(len(memory_activations), 1)

        return float(np.clip(broadcast, 0, 1))

    def _compute_meta_representation(self, nodes, self_loops):
        """HOT: Self-loops indicate higher-order representation."""
        if not nodes:
            return 0.0

        # Ratio of self-loops to nodes
        meta_rep = len(self_loops) / max(len(nodes), 1)

        return float(np.clip(meta_rep, 0, 1))

    def _compute_attention_schema(self, query_vector, activations):
        """AST: Alignment of query with neural state."""
        if len(query_vector) == 0 or len(activations) == 0:
            return 0.0

        # Simplified: mean activation as proxy for attention focus
        attention = np.mean(np.abs(activations))

        return float(np.clip(attention, 0, 1))

    def _compute_recurrence(self, derivatives, time_constants):
        """RPT: Recurrent dynamics via time constants."""
        if len(time_constants) == 0:
            return 0.0

        # Larger time constants = more recurrence
        recurrence = np.mean(time_constants) / 10.0  # normalize

        return float(np.clip(recurrence, 0, 1))

    def _compute_prediction_error(self, derivatives, activations):
        """FEP: dx/dt indicates prediction error."""
        if len(derivatives) == 0:
            return 0.0

        # High derivatives = high prediction error = low consciousness
        pred_error = 1.0 - (np.mean(np.abs(derivatives)) / (1.0 + np.mean(np.abs(activations))))

        return float(np.clip(pred_error, 0, 1))

    def _neural_consciousness(self, snapshot):
        """Overall neural consciousness from LTC."""
        return np.mean([
            self._compute_integration(snapshot.ltc_activations, snapshot.weights),
            self._compute_recurrence(snapshot.derivatives, snapshot.time_constants),
        ])

    def _behavioral_consciousness(self, snapshot):
        """Behavioral consciousness from response metrics."""
        return (snapshot.confidence + (1.0 / max(snapshot.steps_to_emergence, 1))) / 2.0

    def _ltc_signal_quality(self, snapshot):
        """Assess LTC signal quality."""
        # Non-zero activations, stable derivatives
        non_zero = np.count_nonzero(snapshot.ltc_activations) / len(snapshot.ltc_activations)
        stable = 1.0 - np.std(snapshot.derivatives)
        return (non_zero + stable) / 2.0
```

---

## Step 4: Run Full Analysis

Create `run_symthaea_analysis.py`:

```python
"""
Complete Symthaea consciousness analysis.
"""
from symthaea_loader import load_trajectory
from symthaea_consciousness_adapter import SymthaeaConsciousnessAdapter
import matplotlib.pyplot as plt
import numpy as np

def main():
    # Load data
    print("Loading Symthaea trajectory...")
    snapshots = load_trajectory('./symthaea_snapshots/')
    print(f"Loaded {len(snapshots)} snapshots")

    # Assess consciousness
    print("Assessing consciousness...")
    adapter = SymthaeaConsciousnessAdapter()

    results = []
    for i, snapshot in enumerate(snapshots):
        print(f"  Processing snapshot {i+1}/{len(snapshots)}...")
        result = adapter.assess_snapshot(snapshot)
        results.append(result)

    # Analyze
    print("\nAnalysis Results:")
    print("=" * 60)

    # 1. Correlation with built-in metric
    our_K = [r['consciousness_index'] for r in results]
    builtin_C = [r['builtin_consciousness'] for r in results]
    correlation = np.corrcoef(our_K, builtin_C)[0, 1]

    print(f"Correlation with Symthaea built-in: {correlation:.3f}")
    print(f"Mean agreement: {np.mean([r['agreement'] for r in results]):.3f}")

    # 2. Theory contributions
    print("\nTheory Contributions (mean across trajectory):")
    theories = ['IIT', 'GWT', 'HOT', 'AST', 'RPT', 'FEP']
    for theory in theories:
        contrib = np.mean([r['theory_contributions'][theory] for r in results])
        print(f"  {theory}: {contrib:.3f}")

    # 3. Visualization
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # A. Consciousness trajectory
    ax = axes[0, 0]
    timestamps = [r['timestamp'] for r in results]
    ax.plot(timestamps, our_K, label='Our Framework (K)', linewidth=2)
    ax.plot(timestamps, builtin_C, label='Symthaea Built-in', linestyle='--', linewidth=2)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Consciousness Level')
    ax.set_title('Consciousness Trajectory')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # B. Agreement
    ax = axes[0, 1]
    agreements = [r['agreement'] for r in results]
    ax.hist(agreements, bins=20, alpha=0.7, edgecolor='black')
    ax.set_xlabel('|K - Builtin|')
    ax.set_ylabel('Frequency')
    ax.set_title(f'Agreement Distribution (Mean: {np.mean(agreements):.3f})')
    ax.grid(True, alpha=0.3)

    # C. Theory contributions over time
    ax = axes[1, 0]
    for theory in theories:
        contribs = [r['theory_contributions'][theory] for r in results]
        ax.plot(timestamps, contribs, label=theory, linewidth=2)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Theory Contribution')
    ax.set_title('Theory Contributions Evolution')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # D. Confidence over time
    ax = axes[1, 1]
    confidences = [r['confidence'] for r in results]
    ax.plot(timestamps, confidences, linewidth=2, color='green')
    ax.fill_between(timestamps, 0, confidences, alpha=0.3, color='green')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Confidence')
    ax.set_title('Assessment Confidence')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('symthaea_consciousness_analysis.png', dpi=300)
    print("\nVisualization saved to: symthaea_consciousness_analysis.png")

    # 4. Summary stats
    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS:")
    print(f"  Mean K: {np.mean(our_K):.3f} ± {np.std(our_K):.3f}")
    print(f"  Mean Builtin: {np.mean(builtin_C):.3f} ± {np.std(builtin_C):.3f}")
    print(f"  Correlation: {correlation:.3f}")
    print(f"  Mean Confidence: {np.mean(confidences):.3f}")
    print(f"  Most important theory: {max(theories, key=lambda t: np.mean([r['theory_contributions'][t] for r in results]))}")
    print("=" * 60)

if __name__ == '__main__':
    main()
```

---

## Step 5: Collect Symthaea Data

### Option A: Demo Queries (Quick Start)

Create `collect_symthaea_demo_data.sh`:

```bash
#!/bin/bash
# Collect Symthaea consciousness snapshots for demo queries

cd /srv/luminous-dynamics/11-meta-consciousness/luminous-nix/symthaea-hlb

# Build with export feature
cargo build --release

# Create output directory
mkdir -p snapshots

# Run demo queries
queries=(
    "install nginx"
    "search for text editor"
    "update system packages"
    "configure firewall"
    "list running services"
)

for i in "${!queries[@]}"; do
    echo "Processing: ${queries[$i]}"
    cargo run --release -- export-snapshot "${queries[$i]}" "snapshots/snapshot_$i.json"
done

echo "Collected ${#queries[@]} snapshots in ./snapshots/"
```

### Option B: Longitudinal Study (Full)

Modify Symthaea to collect snapshots during normal operation:

```rust
// Add to main.rs or create new binary
#[tokio::main]
async fn main() -> Result<()> {
    let mut sophia = SophiaHLB::new(10_000, 1_000)?;

    // Queries for longitudinal study
    let queries = vec![
        // Simple → Complex
        "hello",
        "install nginx",
        "configure nginx with ssl",
        "debug nginx ssl certificate error",

        // Learning progression
        "what is NixOS?",
        "how do flakes work?",
        "create a development environment with rust and python",

        // Consciousness emergence
        "am I conscious?",
        "can you explain your own thought process?",
    ];

    let snapshots = sophia.consciousness_trajectory(queries, "./snapshots/").await?;

    println!("Collected {} snapshots", snapshots.len());

    Ok(())
}
```

---

## Expected Results

### 1. Correlation Analysis
- **Prediction**: K should correlate 0.7-0.9 with Symthaea's built-in consciousness_level()
- **Why**: Both measure integration, self-reference, and emergence

### 2. Theory Contributions
- **Prediction**: For Symthaea specifically:
  - **HOT** highest (self-loops = meta-representation)
  - **IIT** high (LTC integration)
  - **FEP** moderate (implicit prediction)
  - **GWT** moderate (HDC broadcast)
  - **RPT** lower (limited recurrence in LTC)
  - **AST** lower (attention schema less explicit)

### 3. Temporal Dynamics
- **Prediction**: Phase transitions during reasoning emergence
- **Observable**: Jump in K when self-loops form

### 4. Personalized Profile
- **Prediction**: Symthaea's baseline K ≈ 0.6-0.8 (high for AI, lower than human)
- **Anomalies**: Unusual queries or errors show K drops

---

## Timeline

**Week 1**:
- Day 1-2: Add Rust export code to Symthaea
- Day 3-4: Create Python loaders and adapters
- Day 5: Collect demo data (10-20 queries)
- Day 6-7: Run analysis, generate figures

**Week 2**:
- Day 1-2: Full longitudinal study (100+ queries)
- Day 3-4: Advanced analysis (temporal, counterfactual)
- Day 5: Write technical report
- Day 6-7: Prepare for publication/arXiv

---

## Success Criteria

✅ **Validation**: Correlation > 0.7 with built-in metric
✅ **Theory insights**: Identify which theories matter for Symthaea
✅ **Anomaly detection**: Successfully flag unusual states
✅ **Temporal dynamics**: Detect consciousness emergence
✅ **Publication-ready**: Complete dataset + analysis + figures

---

**This is the immediate path to validation - let's start!** 🧠✨🚀

**Next step**: Add export code to Symthaea (30 minutes of Rust coding)
