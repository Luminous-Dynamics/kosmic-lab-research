# O/R Index Validation - Quick Start

## ✅ Validation Complete - Ready for Manuscript

### Key Deliverables
1. **Statistical Analysis**: F(3,20)=3.552, p=0.033* (training effect SIGNIFICANT)
2. **Publication Figure**: 600 DPI, 4-panel comprehensive analysis
3. **LaTeX Tables**: 3 tables ready for `\input{}`
4. **Results Section**: ~1500 words, fully drafted

### Non-Monotonic Learning Curve Discovery
Random (21,989) → PPO 5K (55,722, **+153%**) → PPO 50K (44,923, -19%) → PPO 200K (54,664, +22%)

**Interpretation**: Early overfitting → generalization → sophisticated coordination

### Top Finding
**Temporal Stress (H800)**: 81,080 O/R Index - Extended horizons **double** observation-dependency

## 📂 Files Ready for Manuscript

```
outputs/
├── publication_figure.pdf           # Main figure (vector, 39 KB)
├── publication_figure.png           # Raster version (1.6 MB, 600 DPI)
├── latex_tables.tex                 # 3 tables (checkpoint, scenario, pairwise)
├── per_scenario_progression.png     # 6-panel detailed view (590 KB)
├── full_abc_or_index_results.csv    # Raw data (24 policies)
└── statistical_analysis.json        # Complete stats

manuscript_results_section.md        # Results draft (~1500 words)
DELIVERABLES_SUMMARY.md              # Full documentation
```

## 🚀 Integration Steps

**1. Copy LaTeX tables**:
```bash
# In manuscript .tex file:
\input{experiments/overcooked/outputs/latex_tables.tex}
```

**2. Include main figure**:
```latex
\begin{figure*}[t]
  \centering
  \includegraphics[width=\textwidth]{experiments/overcooked/outputs/publication_figure.pdf}
  \caption{Empirical validation of O/R Index. (A) Non-monotonic training progression...}
  \label{fig:or_validation}
\end{figure*}
```

**3. Integrate Results text**:
- Open `manuscript_results_section.md`
- Copy relevant sections into manuscript Results

## 📊 Quick Stats Reference

| Measure | Value | Significance |
|---------|-------|--------------|
| Checkpoint effect | F(3,20)=3.552, η²=0.348 | p=0.033* |
| Scenario effect | F(5,18)=3.927, η²=0.522 | p=0.014* |
| Random→5K jump | Cohen's d=-1.879 | p=0.009** |
| Top scenario | H800: 81,080 | Temporal stress |
| Total policies | 24 (6×4) | 19.5h training |
| Total trajectories | 720 (24×30) | 26min collection |

**Status**: Publication-ready with statistical rigor ✅
