# 🌊 Historical K(t) - Master Improvement Plan

**Version**: 2.0
**Date**: November 21, 2025
**Status**: Implementation in Progress
**Target Completion**: February 2026

---

## 📊 Executive Summary

Transform `historical_k` from a 220-year modern analysis tool into a **5000-year civilizational coherence framework** - the first quantitative measure of global coherence spanning from 3000 BCE to 2024.

### Current State
- ✅ **220 years** (1800-2020) decadal coverage
- ✅ **38 proxy variables** across 6 harmonies
- ✅ **Bootstrap uncertainty** quantification
- ✅ **Real data integration** (OWID, World Bank)
- ✅ **K-Passport** reproducibility system
- ✅ **Clean codebase** (zero TODOs)

### Target State
- 🎯 **5000+ years** (3000 BCE - 2024) multi-granularity coverage
- 🎯 **60+ proxy variables** across 7 harmonies (add Evolutionary Progression)
- 🎯 **Causal analysis** via Granger networks
- 🎯 **Bayesian uncertainty** propagation
- 🎯 **Interactive dashboard** for real-time exploration
- 🎯 **Publication-ready** standalone paper
- 🎯 **Public API** for external researchers

---

## 🎯 Strategic Priorities

### **Priority 1: Data Quality & Coverage** 🔴 HIGHEST IMPACT

#### 1.1 Temporal Expansion: 220 years → 5000 years
**Scientific Impact**: First deep-time coherence index

**New Time Periods**:
```yaml
ancient:
  span: 3000 BCE - 500 CE
  granularity: century
  sources: Seshat, HYDE, archaeological databases

medieval:
  span: 500 - 1500 CE
  granularity: 50 years
  sources: Clio-Infra, Medieval Trade Networks

early_modern:
  span: 1500 - 1800
  granularity: 25 years
  sources: Trading networks, colonial records

modern:
  span: 1800 - 2024
  granularity: decade
  sources: OWID, World Bank (current coverage)
```

**Data Sources to Integrate**:
1. **Seshat Global History Databank** - Primary ancient source
   - 10,000+ variables across 600+ polities
   - Social complexity, military, economics
   - URL: https://seshatdatabank.info/

2. **HYDE 3.2** - Population and land use
   - 12,000 years of demographic data
   - Settlement patterns, agricultural intensity

3. **Maddison Project** - Historical GDP
   - GDP estimates back to 1 CE
   - Per capita income across civilizations

4. **Archaeology Databases**:
   - CARD (Canadian Archaeological Radiocarbon Database)
   - CONTEXT (Archaeological database)
   - Trade route reconstructions

5. **Climate Reconstructions**:
   - PAGES 2k Network
   - Ice core data
   - Tree ring series

#### 1.2 Fill Modern Data Gaps
**Current Issues**:
- `trust_region_placeholder.csv` - Needs real WVS/Eurobarometer data
- `network_modularity_inverse.csv` - Needs actual network analysis
- `communication_latency_inverse.csv` - Needs historical latency estimates
- `innovation_field_entropy.csv` - Needs patent classification diversity

**Solutions**:
```python
# Trust metrics from World Values Survey
def build_trust_series():
    # WVS waves 1-7 (1981-2022)
    # Question: "Most people can be trusted"
    # Aggregate by decade, global weighted average
    pass

# Network modularity from trade data
def build_network_modularity():
    # Use UN Comtrade for modern period
    # Correlates of War for historical
    # Compute modularity Q metric on trade network
    pass

# Communication latency reconstruction
def build_communication_latency():
    # 1800s: Postal service (weeks)
    # 1850s: Telegraph (hours)
    # 1960s: Satellite (milliseconds)
    # 1990s: Internet (sub-second)
    # Use inverse for coherence direction
    pass
```

#### 1.3 Add Seventh Harmony: Evolutionary Progression
**Currently Missing**: Only 6/7 harmonies implemented

**New Proxies**:
```yaml
evolutionary_progression:
  - technological_progress_rate      # Patent growth rate
  - social_complexity_index          # Seshat complexity score
  - institutional_quality_index      # Polity IV scores
  - learning_system_capacity         # Literacy * education * R&D
  - adaptive_capacity_index          # Crisis recovery speed
  - innovation_acceleration          # Second derivative of patents
```

---

### **Priority 2: Computational Enhancements** 🟠 MEDIUM IMPACT

#### 2.1 Causal Analysis: Granger Networks
**Goal**: Move beyond correlation to causality

**Implementation**:
```python
# New file: historical_k/granger.py
from statsmodels.tsa.stattools import grangercausalitytests
import networkx as nx

def compute_granger_network(harmony_frame, max_lag=3, alpha=0.05):
    """Construct directed network of Granger-causal relationships.

    Returns:
        NetworkX DiGraph with edges representing causal influence
    """
    harmonies = list(harmony_frame.columns)
    G = nx.DiGraph()

    for h in harmonies:
        G.add_node(h)

    for h1 in harmonies:
        for h2 in harmonies:
            if h1 == h2:
                continue

            # Test if h1 Granger-causes h2
            try:
                result = grangercausalitytests(
                    harmony_frame[[h2, h1]],
                    maxlag=max_lag,
                    verbose=False
                )
                # Extract p-values
                p_values = [result[lag+1][0]['ssr_ftest'][1] for lag in range(max_lag)]
                min_p = min(p_values)
                best_lag = p_values.index(min_p) + 1

                if min_p < alpha:
                    G.add_edge(h1, h2, weight=1-min_p, lag=best_lag, p_value=min_p)
            except:
                continue

    return G

def visualize_granger_network(G, output_path):
    """Create publication-quality network diagram."""
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, k=2, iterations=50)

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=3000, node_color='lightblue', alpha=0.9)
    nx.draw_networkx_labels(G, pos, font_size=10)

    # Draw edges with width proportional to causal strength
    edges = G.edges()
    weights = [G[u][v]['weight'] for u, v in edges]
    nx.draw_networkx_edges(G, pos, width=[w*5 for w in weights], alpha=0.6,
                           arrows=True, arrowsize=20)

    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def analyze_causal_structure(G):
    """Compute network metrics for interpretation."""
    return {
        'nodes': G.number_of_nodes(),
        'edges': G.number_of_edges(),
        'density': nx.density(G),
        'most_influential': max(G.nodes(), key=lambda n: G.out_degree(n, weight='weight')),
        'most_receptive': max(G.nodes(), key=lambda n: G.in_degree(n, weight='weight')),
        'strongly_connected_components': list(nx.strongly_connected_components(G)),
    }
```

#### 2.2 Hierarchical Bayesian Model
**Goal**: Propagate uncertainty from proxies → harmonies → K

**Implementation**:
```python
# New file: historical_k/bayesian_k.py
import pymc as pm
import arviz as az

def bayesian_k_model(harmony_frame, observed_k=None):
    """Hierarchical Bayesian model with proper uncertainty propagation.

    Model structure:
    - Harmony weights: Dirichlet prior (sum to 1)
    - Observation noise: Half-normal per harmony
    - K likelihood: Weighted combination of harmonies
    """
    n_harmonies = harmony_frame.shape[1]
    n_years = harmony_frame.shape[0]

    with pm.Model() as model:
        # Priors on harmony weights (Dirichlet ensures sum to 1)
        harmony_weights = pm.Dirichlet('weights', a=np.ones(n_harmonies))

        # Observation noise per harmony
        sigma_harmonies = pm.HalfNormal('sigma_harmonies', sigma=0.1, shape=n_harmonies)

        # Overall measurement error
        sigma_K = pm.HalfNormal('sigma_K', sigma=0.05)

        # Compute K as weighted sum
        K_mu = pm.math.dot(harmony_frame.values, harmony_weights)

        # Likelihood
        if observed_k is not None:
            K_obs = pm.Normal('K', mu=K_mu, sigma=sigma_K, observed=observed_k.values)
        else:
            # Posterior predictive
            K_pred = pm.Normal('K_pred', mu=K_mu, sigma=sigma_K, shape=n_years)

        # Sample posterior
        trace = pm.sample(2000, tune=1000, cores=4, return_inferencedata=True)

    return model, trace

def analyze_posterior(trace, harmony_names):
    """Extract insights from posterior distribution."""
    summary = az.summary(trace, var_names=['weights', 'sigma_K'])

    # Extract weight posterior
    weights_posterior = trace.posterior['weights'].values
    weights_mean = weights_posterior.mean(axis=(0, 1))
    weights_std = weights_posterior.std(axis=(0, 1))

    weight_df = pd.DataFrame({
        'harmony': harmony_names,
        'mean_weight': weights_mean,
        'std_weight': weights_std,
        'ci_low': np.percentile(weights_posterior, 2.5, axis=(0, 1)),
        'ci_high': np.percentile(weights_posterior, 97.5, axis=(0, 1))
    }).sort_values('mean_weight', ascending=False)

    return weight_df, summary

def plot_weight_posterior(trace, harmony_names, output_path):
    """Visualize posterior distributions of harmony weights."""
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    axes = axes.flatten()

    weights_posterior = trace.posterior['weights'].values

    for i, harmony in enumerate(harmony_names):
        if i < len(axes):
            ax = axes[i]
            weights_i = weights_posterior[:, :, i].flatten()
            ax.hist(weights_i, bins=50, alpha=0.7, edgecolor='black')
            ax.axvline(weights_i.mean(), color='red', linestyle='--',
                      label=f'Mean: {weights_i.mean():.3f}')
            ax.set_title(harmony)
            ax.set_xlabel('Weight')
            ax.set_ylabel('Frequency')
            ax.legend()

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
```

#### 2.3 Dynamic Time Warping for Event Validation
**Goal**: Quantitatively validate preregistered events

```python
# New file: historical_k/validation.py
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw

def validate_predicted_events(k_series, preregistered_events, window=10):
    """Score accuracy of preregistered troughs/peaks.

    Args:
        k_series: Pandas Series of K values indexed by year
        preregistered_events: Dict with 'troughs' and 'peaks' lists
        window: Years tolerance for match

    Returns:
        Dict with validation metrics
    """
    troughs_pred = preregistered_events.get('troughs', [])
    peaks_pred = preregistered_events.get('peaks', [])

    # Find actual extrema
    k_smoothed = k_series.rolling(window=3, center=True).mean()
    troughs_actual = k_smoothed.nsmallest(len(troughs_pred)).index.tolist()
    peaks_actual = k_smoothed.nlargest(len(peaks_pred)).index.tolist()

    # Compute DTW distance for temporal alignment
    trough_dist, trough_path = fastdtw(
        sorted(troughs_pred),
        sorted(troughs_actual),
        dist=euclidean
    )

    peak_dist, peak_path = fastdtw(
        sorted(peaks_pred),
        sorted(peaks_actual),
        dist=euclidean
    )

    # Compute hit rates (within window tolerance)
    def hit_rate(predicted, actual, window):
        hits = 0
        for p in predicted:
            if any(abs(p - a) <= window for a in actual):
                hits += 1
        return hits / len(predicted) if predicted else 0

    return {
        'trough_dtw_distance': trough_dist / len(troughs_pred),
        'peak_dtw_distance': peak_dist / len(peaks_pred),
        'trough_hit_rate': hit_rate(troughs_pred, troughs_actual, window),
        'peak_hit_rate': hit_rate(peaks_pred, peaks_actual, window),
        'overall_accuracy': (
            hit_rate(troughs_pred, troughs_actual, window) +
            hit_rate(peaks_pred, peaks_actual, window)
        ) / 2,
        'troughs_matched': [(p, min(troughs_actual, key=lambda a: abs(p-a)))
                           for p in troughs_pred],
        'peaks_matched': [(p, min(peaks_actual, key=lambda a: abs(p-a)))
                         for p in peaks_pred]
    }

def plot_event_validation(k_series, preregistered_events, validation_results, output_path):
    """Visualize event prediction accuracy."""
    fig, ax = plt.subplots(figsize=(12, 6))

    years = k_series.index
    ax.plot(years, k_series.values, 'b-', label='K(t)', linewidth=2)

    # Mark predicted events
    for year in preregistered_events.get('troughs', []):
        ax.axvline(year, color='red', linestyle='--', alpha=0.5)
    for year in preregistered_events.get('peaks', []):
        ax.axvline(year, color='green', linestyle='--', alpha=0.5)

    # Mark actual extrema
    k_smoothed = k_series.rolling(window=3, center=True).mean()
    troughs_actual = k_smoothed.nsmallest(len(preregistered_events.get('troughs', []))).index
    peaks_actual = k_smoothed.nlargest(len(preregistered_events.get('peaks', []))).index

    for year in troughs_actual:
        ax.plot(year, k_series[year], 'ro', markersize=10, label='Actual trough' if year == troughs_actual[0] else '')
    for year in peaks_actual:
        ax.plot(year, k_series[year], 'go', markersize=10, label='Actual peak' if year == peaks_actual[0] else '')

    ax.set_xlabel('Year')
    ax.set_ylabel('K-index')
    ax.set_title(f'Event Validation (Hit Rate: {validation_results["overall_accuracy"]:.1%})')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
```

---

### **Priority 3: Validation & Robustness** 🟡 MEDIUM IMPACT

#### 3.1 Sensitivity Analysis (Ablation Study)
**Goal**: Identify which proxies drive K(t) most strongly

```python
# New file: historical_k/sensitivity.py
from copy import deepcopy
from pathlib import Path
import yaml

def proxy_ablation_study(config_path, output_dir='logs/sensitivity'):
    """Remove each proxy one at a time and measure impact on K(t).

    Returns:
        DataFrame ranking proxies by importance
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load config
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Compute baseline K
    from historical_k.compute_k import main as compute_k_main
    baseline_k = _load_k_series('logs/historical_k/k_t_series.csv')

    results = {}
    for harmony, proxies in config['proxies'].items():
        for proxy in proxies:
            print(f"Testing ablation: {proxy} from {harmony}")

            # Create modified config
            modified_config = deepcopy(config)
            modified_config['proxies'][harmony] = [p for p in proxies if p != proxy]

            if not modified_config['proxies'][harmony]:
                # Don't test if harmony would be empty
                results[proxy] = {
                    'harmony': harmony,
                    'rmse_impact': np.nan,
                    'max_deviation': np.nan,
                    'correlation_drop': np.nan,
                    'status': 'skipped_empty_harmony'
                }
                continue

            # Save modified config
            temp_config_path = output_dir / f'config_ablate_{proxy}.yaml'
            with open(temp_config_path, 'w') as f:
                yaml.dump(modified_config, f)

            # Recompute K with ablated proxy
            try:
                # Run compute_k with modified config
                import subprocess
                subprocess.run([
                    'python', '-m', 'historical_k.compute_k',
                    '--config', str(temp_config_path)
                ], check=True, capture_output=True)

                ablated_k = _load_k_series('logs/historical_k/k_t_series.csv')

                # Measure impact
                rmse = np.sqrt(((baseline_k - ablated_k)**2).mean())
                max_dev = abs(baseline_k - ablated_k).max()
                corr = baseline_k.corr(ablated_k)

                results[proxy] = {
                    'harmony': harmony,
                    'rmse_impact': rmse,
                    'max_deviation': max_dev,
                    'correlation_drop': 1 - corr,
                    'status': 'success'
                }
            except Exception as e:
                results[proxy] = {
                    'harmony': harmony,
                    'rmse_impact': np.nan,
                    'max_deviation': np.nan,
                    'correlation_drop': np.nan,
                    'status': f'error: {str(e)}'
                }

    # Convert to DataFrame
    results_df = pd.DataFrame(results).T
    results_df.index.name = 'proxy'
    results_df = results_df.sort_values('rmse_impact', ascending=False)

    # Save results
    results_df.to_csv(output_dir / 'ablation_results.csv')

    return results_df

def plot_ablation_results(results_df, output_path):
    """Visualize proxy importance from ablation study."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Filter valid results
    valid = results_df[results_df['status'] == 'success'].copy()

    # Plot 1: RMSE impact
    ax = axes[0]
    valid_sorted = valid.sort_values('rmse_impact', ascending=True)
    colors = [plt.cm.Set3(i % 12) for i in range(len(valid_sorted))]
    ax.barh(range(len(valid_sorted)), valid_sorted['rmse_impact'], color=colors)
    ax.set_yticks(range(len(valid_sorted)))
    ax.set_yticklabels(valid_sorted.index, fontsize=8)
    ax.set_xlabel('RMSE Impact')
    ax.set_title('Proxy Importance (Ablation Study)')
    ax.grid(True, alpha=0.3, axis='x')

    # Plot 2: Max deviation
    ax = axes[1]
    valid_sorted = valid.sort_values('max_deviation', ascending=True)
    ax.barh(range(len(valid_sorted)), valid_sorted['max_deviation'], color=colors)
    ax.set_yticks(range(len(valid_sorted)))
    ax.set_yticklabels(valid_sorted.index, fontsize=8)
    ax.set_xlabel('Max Deviation')
    ax.set_title('Maximum K Impact')
    ax.grid(True, alpha=0.3, axis='x')

    # Plot 3: Correlation drop
    ax = axes[2]
    valid_sorted = valid.sort_values('correlation_drop', ascending=True)
    ax.barh(range(len(valid_sorted)), valid_sorted['correlation_drop'], color=colors)
    ax.set_yticks(range(len(valid_sorted)))
    ax.set_yticklabels(valid_sorted.index, fontsize=8)
    ax.set_xlabel('Correlation Drop (1 - r)')
    ax.set_title('Shape Change Impact')
    ax.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def _load_k_series(path):
    """Helper to load K series from CSV."""
    df = pd.read_csv(path)
    return pd.Series(df['K'].values, index=df['year'].values, name='K')
```

#### 3.2 Temporal Cross-Validation
**Goal**: Test predictive validity with hold-out periods

```python
# Add to historical_k/validation.py

def temporal_cross_validation(config_path, n_folds=5, method='rolling'):
    """Leave-one-period-out validation.

    Args:
        config_path: Path to configuration file
        n_folds: Number of folds for validation
        method: 'rolling' (sequential) or 'random' (shuffled)

    Returns:
        DataFrame with validation metrics per fold
    """
    # Load data
    from historical_k.etl import build_harmony_frame, compute_k_series
    from core.config import load_yaml_config

    config_bundle = load_yaml_config(config_path)
    config = config_bundle.payload

    years = list(range(1800, 2021, 10))  # Decadal
    harmony_frame = build_harmony_frame(
        config['proxies'],
        years,
        config['windows'].get('normalization', 'none')
    )
    k_series = compute_k_series(harmony_frame)

    n_years = len(years)
    fold_size = n_years // n_folds

    predictions = []
    for i in range(n_folds):
        print(f"Fold {i+1}/{n_folds}")

        # Hold out fold i
        if method == 'rolling':
            test_indices = list(range(i * fold_size, (i + 1) * fold_size))
        else:
            # Random sampling
            np.random.seed(42 + i)
            test_indices = np.random.choice(n_years, fold_size, replace=False)

        test_mask = np.zeros(n_years, dtype=bool)
        test_mask[test_indices] = True
        train_mask = ~test_mask

        # Split data
        train_frame = harmony_frame[train_mask]
        test_frame = harmony_frame[test_mask]
        k_train = k_series[train_mask]
        k_test = k_series[test_mask]

        # Learn weights on training data (simple equal weighting baseline)
        # Could use Bayesian model here for more sophisticated approach
        weights = {col: 1.0 / len(train_frame.columns) for col in train_frame.columns}

        # Predict on test
        k_pred = compute_k_series(test_frame, weights)

        # Evaluate
        rmse = np.sqrt(((k_pred - k_test)**2).mean())
        mae = abs(k_pred - k_test).mean()
        r2 = 1 - ((k_pred - k_test)**2).sum() / ((k_test - k_test.mean())**2).sum()
        corr = k_pred.corr(k_test)

        predictions.append({
            'fold': i + 1,
            'n_train': train_mask.sum(),
            'n_test': test_mask.sum(),
            'rmse': rmse,
            'mae': mae,
            'r2': r2,
            'correlation': corr,
            'test_years': [years[j] for j in test_indices]
        })

    results_df = pd.DataFrame(predictions)

    # Add summary statistics
    summary = {
        'fold': 'MEAN',
        'rmse': results_df['rmse'].mean(),
        'mae': results_df['mae'].mean(),
        'r2': results_df['r2'].mean(),
        'correlation': results_df['correlation'].mean()
    }

    return results_df, summary

def plot_cv_results(cv_results, output_path):
    """Visualize cross-validation performance."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # RMSE per fold
    ax = axes[0, 0]
    ax.bar(cv_results['fold'], cv_results['rmse'])
    ax.axhline(cv_results['rmse'].mean(), color='red', linestyle='--',
              label=f'Mean: {cv_results["rmse"].mean():.3f}')
    ax.set_xlabel('Fold')
    ax.set_ylabel('RMSE')
    ax.set_title('Prediction Error by Fold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # R² per fold
    ax = axes[0, 1]
    ax.bar(cv_results['fold'], cv_results['r2'])
    ax.axhline(cv_results['r2'].mean(), color='red', linestyle='--',
              label=f'Mean: {cv_results["r2"].mean():.3f}')
    ax.set_xlabel('Fold')
    ax.set_ylabel('R²')
    ax.set_title('Predictive R² by Fold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Correlation per fold
    ax = axes[1, 0]
    ax.bar(cv_results['fold'], cv_results['correlation'])
    ax.axhline(cv_results['correlation'].mean(), color='red', linestyle='--',
              label=f'Mean: {cv_results["correlation"].mean():.3f}')
    ax.set_xlabel('Fold')
    ax.set_ylabel('Correlation')
    ax.set_title('Prediction Correlation by Fold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # MAE per fold
    ax = axes[1, 1]
    ax.bar(cv_results['fold'], cv_results['mae'])
    ax.axhline(cv_results['mae'].mean(), color='red', linestyle='--',
              label=f'Mean: {cv_results["mae"].mean():.3f}')
    ax.set_xlabel('Fold')
    ax.set_ylabel('MAE')
    ax.set_title('Mean Absolute Error by Fold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
```

#### 3.3 Regime Detection
**Goal**: Automatically identify coherence transitions

```python
# New file: historical_k/regimes.py
import ruptures as rpt

def detect_regime_changes(k_series, penalty=3.0, model='rbf'):
    """Detect breakpoints in K(t) using change-point detection.

    Args:
        k_series: Pandas Series of K values
        penalty: Penalty for adding breakpoints (higher = fewer breaks)
        model: 'rbf' (Gaussian kernel), 'l1' (absolute), 'l2' (squared)

    Returns:
        DataFrame with regime characteristics
    """
    # Prepare data
    signal = k_series.values.reshape(-1, 1)
    years = k_series.index.values

    # Detect change points
    algo = rpt.Pelt(model=model, min_size=3, jump=1).fit(signal)
    breakpoints = algo.predict(pen=penalty)

    # Analyze regimes between breakpoints
    regimes = []
    start_idx = 0

    for i, end_idx in enumerate(breakpoints):
        if end_idx >= len(signal):
            end_idx = len(signal)

        regime_k = k_series.iloc[start_idx:end_idx]
        regime_years = years[start_idx:end_idx]

        # Compute regime statistics
        mean_k = regime_k.mean()
        std_k = regime_k.std()

        # Linear trend
        if len(regime_k) > 1:
            trend_coef = np.polyfit(range(len(regime_k)), regime_k.values, 1)[0]
            trend_direction = 'increasing' if trend_coef > 0.01 else ('decreasing' if trend_coef < -0.01 else 'stable')
        else:
            trend_coef = 0
            trend_direction = 'stable'

        # Volatility (normalized by mean)
        volatility = std_k / mean_k if mean_k != 0 else 0

        regimes.append({
            'regime_id': i + 1,
            'start_year': regime_years[0],
            'end_year': regime_years[-1],
            'duration': len(regime_years),
            'mean_K': mean_k,
            'std_K': std_k,
            'trend_slope': trend_coef,
            'trend_direction': trend_direction,
            'volatility': volatility,
            'min_K': regime_k.min(),
            'max_K': regime_k.max(),
            'range_K': regime_k.max() - regime_k.min()
        })

        start_idx = end_idx

    regimes_df = pd.DataFrame(regimes)

    return regimes_df, breakpoints

def plot_regime_analysis(k_series, regimes_df, breakpoints, output_path):
    """Visualize regime detection results."""
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    years = k_series.index.values

    # Plot 1: K(t) with regime boundaries
    ax = axes[0]
    ax.plot(years, k_series.values, 'b-', linewidth=2, label='K(t)')

    # Mark breakpoints
    for bp_idx in breakpoints[:-1]:  # Last one is end of series
        if bp_idx < len(years):
            ax.axvline(years[bp_idx], color='red', linestyle='--', alpha=0.7)

    # Shade regimes with alternating colors
    colors = ['lightblue', 'lightcoral', 'lightgreen', 'lightyellow', 'lightgray']
    for i, regime in regimes_df.iterrows():
        start = regime['start_year']
        end = regime['end_year']
        ax.axvspan(start, end, alpha=0.2, color=colors[i % len(colors)],
                  label=f'Regime {regime["regime_id"]}')

    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('K-index', fontsize=12)
    ax.set_title('Historical K(t) with Detected Regimes', fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', fontsize=8)

    # Plot 2: Regime characteristics
    ax = axes[1]
    x_pos = range(len(regimes_df))
    width = 0.25

    # Mean K
    ax.bar([x - width for x in x_pos], regimes_df['mean_K'], width,
           label='Mean K', alpha=0.8)
    # Volatility (scaled for visibility)
    ax.bar(x_pos, regimes_df['volatility'] * 10, width,
           label='Volatility (×10)', alpha=0.8)
    # Trend slope (scaled)
    ax.bar([x + width for x in x_pos], regimes_df['trend_slope'] * 100, width,
           label='Trend (×100)', alpha=0.8)

    ax.set_xlabel('Regime', fontsize=12)
    ax.set_ylabel('Value', fontsize=12)
    ax.set_title('Regime Characteristics', fontsize=14)
    ax.set_xticks(x_pos)
    ax.set_xticklabels([f"R{r['regime_id']}\n{r['start_year']}-{r['end_year']}"
                        for _, r in regimes_df.iterrows()], fontsize=9)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    ax.axhline(0, color='black', linewidth=0.5)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def interpret_regimes(regimes_df):
    """Generate narrative interpretation of regimes."""
    interpretations = []

    for _, regime in regimes_df.iterrows():
        # Classify regime
        if regime['mean_K'] > 1.2:
            coherence_level = "high"
        elif regime['mean_K'] > 0.8:
            coherence_level = "moderate"
        else:
            coherence_level = "low"

        if regime['volatility'] > 0.2:
            stability = "volatile"
        elif regime['volatility'] > 0.1:
            stability = "moderately stable"
        else:
            stability = "stable"

        interpretation = (
            f"**Regime {regime['regime_id']}** ({regime['start_year']}-{regime['end_year']}, "
            f"{regime['duration']} periods): "
            f"{coherence_level.capitalize()} coherence (K̄ = {regime['mean_K']:.2f}), "
            f"{stability}. "
            f"Trend: {regime['trend_direction']} "
            f"({regime['trend_slope']:.4f} per period). "
            f"Range: {regime['min_K']:.2f} to {regime['max_K']:.2f}."
        )

        interpretations.append(interpretation)

    return "\n\n".join(interpretations)
```

---

### **Priority 4: Analysis & Insights** 🟢 HIGH VALUE

#### 4.1 Counterfactual Scenarios
**Goal**: "What if" analysis for historical events

```python
# New file: historical_k/counterfactuals.py

def simulate_counterfactual(k_series, event_year, impact_profile, event_name="Event"):
    """Simulate alternate history without a major event.

    Args:
        k_series: Original K(t) series
        event_year: Year of event (e.g., 1914 for WWI)
        impact_profile: Dict mapping years to K-index adjustments
            - Positive values: event reduced K (no event = higher K)
            - Negative values: event increased K
        event_name: Name for plotting

    Returns:
        Dict with analysis results
    """
    counterfactual_k = k_series.copy()

    # Apply adjustments
    for year, adjustment in impact_profile.items():
        if year in counterfactual_k.index:
            counterfactual_k[year] += adjustment

    # Compute metrics
    total_coherence_lost = (counterfactual_k - k_series).sum()
    years_affected = len(impact_profile)

    # Find recovery time (when K returns to pre-event level)
    if event_year in k_series.index:
        pre_event_k = k_series.loc[event_year - 10] if event_year - 10 in k_series.index else k_series[0]
        post_event_series = k_series[k_series.index >= event_year]

        recovery_years = []
        for year, k_val in post_event_series.items():
            if k_val >= pre_event_k:
                recovery_time = year - event_year
                break
        else:
            recovery_time = None  # Never recovered in observed period
    else:
        recovery_time = None

    return {
        'event_name': event_name,
        'event_year': event_year,
        'actual_k': k_series,
        'counterfactual_k': counterfactual_k,
        'total_coherence_lost': total_coherence_lost,
        'years_affected': years_affected,
        'recovery_time': recovery_time,
        'max_impact': (counterfactual_k - k_series).abs().max(),
        'impact_profile': impact_profile
    }

def plot_counterfactual(result, output_path):
    """Visualize counterfactual scenario."""
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))

    actual = result['actual_k']
    counter = result['counterfactual_k']
    years = actual.index

    # Plot 1: Actual vs Counterfactual
    ax = axes[0]
    ax.plot(years, actual.values, 'b-', linewidth=2, label='Actual K(t)')
    ax.plot(years, counter.values, 'g--', linewidth=2, label='Counterfactual (no event)')
    ax.axvline(result['event_year'], color='red', linestyle=':', alpha=0.7,
              label=f"{result['event_name']} ({result['event_year']})")

    # Shade impact region
    impact_years = list(result['impact_profile'].keys())
    if impact_years:
        ax.axvspan(min(impact_years), max(impact_years), alpha=0.2, color='red')

    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('K-index', fontsize=12)
    ax.set_title(f'Counterfactual Analysis: {result["event_name"]}', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot 2: Difference (Impact)
    ax = axes[1]
    difference = counter - actual
    ax.plot(years, difference.values, 'r-', linewidth=2)
    ax.axhline(0, color='black', linestyle='-', linewidth=0.5)
    ax.axvline(result['event_year'], color='red', linestyle=':', alpha=0.7)

    # Shade positive (lost coherence) and negative regions
    ax.fill_between(years, 0, difference.values, where=difference.values > 0,
                    alpha=0.3, color='red', label='Coherence lost to event')
    ax.fill_between(years, 0, difference.values, where=difference.values < 0,
                    alpha=0.3, color='blue', label='Coherence gained from event')

    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('K Difference (Counterfactual - Actual)', fontsize=12)
    ax.set_title('Coherence Impact of Event', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Add text summary
    summary_text = (
        f"Total coherence lost: {result['total_coherence_lost']:.2f}\n"
        f"Years affected: {result['years_affected']}\n"
        f"Max impact: {result['max_impact']:.2f}\n"
        f"Recovery time: {result['recovery_time']} years" if result['recovery_time'] else "Did not recover"
    )
    ax.text(0.02, 0.98, summary_text, transform=ax.transAxes,
           verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
           fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

# Predefined scenarios
COUNTERFACTUAL_SCENARIOS = {
    'wwi': {
        'event_name': 'World War I',
        'event_year': 1914,
        'impact_profile': {
            1914: 0.15,  # No war = 0.15 higher K
            1915: 0.20,
            1916: 0.22,
            1917: 0.24,
            1918: 0.25,
            1919: 0.20,
            1920: 0.15,
            1930: 0.05   # Lingering effects
        }
    },
    'wwii': {
        'event_name': 'World War II',
        'event_year': 1939,
        'impact_profile': {
            1939: 0.20,
            1940: 0.30,
            1941: 0.35,
            1942: 0.40,
            1943: 0.42,
            1944: 0.40,
            1945: 0.35,
            1946: 0.25,
            1950: 0.10,
            1955: 0.05
        }
    },
    'cold_war': {
        'event_name': 'Cold War',
        'event_year': 1947,
        'impact_profile': {year: 0.08 for year in range(1947, 1991, 10)}  # Constant drag
    },
    'internet': {
        'event_name': 'Internet Revolution',
        'event_year': 1990,
        'impact_profile': {
            1990: -0.05,  # Negative = event INCREASED K
            2000: -0.15,
            2010: -0.25,
            2020: -0.30
        }
    }
}

def run_all_scenarios(k_series, output_dir='logs/counterfactuals'):
    """Run all predefined counterfactual scenarios."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {}
    for scenario_id, scenario in COUNTERFACTUAL_SCENARIOS.items():
        result = simulate_counterfactual(k_series, **scenario)
        results[scenario_id] = result

        # Plot
        plot_counterfactual(result, output_dir / f'{scenario_id}_analysis.png')

    # Summary comparison
    summary_df = pd.DataFrame([
        {
            'scenario': r['event_name'],
            'year': r['event_year'],
            'total_coherence_lost': r['total_coherence_lost'],
            'max_impact': r['max_impact'],
            'recovery_time': r['recovery_time']
        }
        for r in results.values()
    ])

    summary_df.to_csv(output_dir / 'scenarios_summary.csv', index=False)

    return results, summary_df
```

#### 4.2 Forward Projections
**Goal**: Extrapolate K(t) to 2050

```python
# New file: historical_k/forecasting.py
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing

def forecast_k_trajectory(k_series, horizon_years=30, method='arima', seasonal_period=None):
    """Project K(t) forward using time series model.

    Args:
        k_series: Historical K(t) series
        horizon_years: Years to forecast (e.g., 30 for 2020 → 2050)
        method: 'arima', 'holtwinters', or 'ensemble'
        seasonal_period: For seasonal models (e.g., 10 for decadal cycles)

    Returns:
        Dict with forecast data
    """
    # Determine forecast periods
    last_year = k_series.index[-1]
    granularity = k_series.index[1] - k_series.index[0] if len(k_series) > 1 else 10
    n_periods = horizon_years // granularity
    future_years = [last_year + (i+1)*granularity for i in range(n_periods)]

    if method == 'arima':
        # Fit ARIMA model
        model = ARIMA(k_series, order=(2, 1, 2))
        fitted = model.fit()

        # Generate forecast
        forecast_result = fitted.get_forecast(steps=n_periods)
        forecast = forecast_result.predicted_mean
        conf_int = forecast_result.conf_int(alpha=0.05)

        return {
            'method': 'ARIMA(2,1,2)',
            'years': future_years,
            'forecast': forecast.values,
            'ci_lower': conf_int.iloc[:, 0].values,
            'ci_upper': conf_int.iloc[:, 1].values,
            'model': fitted,
            'aic': fitted.aic,
            'bic': fitted.bic
        }

    elif method == 'holtwinters':
        # Exponential smoothing
        model = ExponentialSmoothing(
            k_series,
            seasonal_periods=seasonal_period,
            trend='add',
            seasonal='add' if seasonal_period else None
        )
        fitted = model.fit()

        # Forecast
        forecast = fitted.forecast(steps=n_periods)

        # Simulate prediction intervals
        residuals = k_series - fitted.fittedvalues
        std_resid = residuals.std()
        ci_lower = forecast - 1.96 * std_resid
        ci_upper = forecast + 1.96 * std_resid

        return {
            'method': 'Holt-Winters',
            'years': future_years,
            'forecast': forecast.values,
            'ci_lower': ci_lower.values,
            'ci_upper': ci_upper.values,
            'model': fitted
        }

    elif method == 'ensemble':
        # Combine multiple methods
        arima_result = forecast_k_trajectory(k_series, horizon_years, method='arima')
        hw_result = forecast_k_trajectory(k_series, horizon_years, method='holtwinters')

        # Average forecasts
        ensemble_forecast = (arima_result['forecast'] + hw_result['forecast']) / 2
        ensemble_lower = (arima_result['ci_lower'] + hw_result['ci_lower']) / 2
        ensemble_upper = (arima_result['ci_upper'] + hw_result['ci_upper']) / 2

        return {
            'method': 'Ensemble (ARIMA + Holt-Winters)',
            'years': future_years,
            'forecast': ensemble_forecast,
            'ci_lower': ensemble_lower,
            'ci_upper': ensemble_upper,
            'components': {
                'arima': arima_result,
                'holtwinters': hw_result
            }
        }

def plot_forecast(k_series, forecast_result, output_path):
    """Visualize historical K(t) with forecast."""
    fig, ax = plt.subplots(figsize=(14, 7))

    # Historical data
    hist_years = k_series.index
    ax.plot(hist_years, k_series.values, 'b-', linewidth=2, label='Historical K(t)', marker='o')

    # Forecast
    forecast_years = forecast_result['years']
    forecast = forecast_result['forecast']
    ci_lower = forecast_result['ci_lower']
    ci_upper = forecast_result['ci_upper']

    ax.plot(forecast_years, forecast, 'r--', linewidth=2, label=f'Forecast ({forecast_result["method"]})', marker='s')
    ax.fill_between(forecast_years, ci_lower, ci_upper, color='red', alpha=0.2, label='95% CI')

    # Mark present
    if len(hist_years) > 0:
        ax.axvline(hist_years[-1], color='green', linestyle=':', alpha=0.7, label='Present')

    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('K-index', fontsize=12)
    ax.set_title(f'Historical K(t) and Forecast to {forecast_years[-1]}', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Add text summary
    final_forecast = forecast[-1]
    current_k = k_series.iloc[-1]
    change = ((final_forecast - current_k) / current_k) * 100

    summary_text = (
        f"Current K ({hist_years[-1]}): {current_k:.3f}\n"
        f"Forecast K ({forecast_years[-1]}): {final_forecast:.3f}\n"
        f"Projected change: {change:+.1f}%\n"
        f"CI: [{ci_lower[-1]:.3f}, {ci_upper[-1]:.3f}]"
    )
    ax.text(0.02, 0.98, summary_text, transform=ax.transAxes,
           verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7),
           fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def scenario_forecast(k_series, scenarios, horizon_years=30):
    """Generate forecasts under different future scenarios.

    Args:
        k_series: Historical K(t)
        scenarios: Dict of scenario assumptions
        horizon_years: Forecast period

    Returns:
        Dict of forecast results for each scenario
    """
    baseline = forecast_k_trajectory(k_series, horizon_years, method='ensemble')

    results = {
        'baseline': baseline
    }

    # Optimistic scenario (K grows faster)
    k_adjusted_high = k_series.copy()
    k_adjusted_high[-5:] = k_adjusted_high[-5:] * 1.1  # Boost recent trend
    results['optimistic'] = forecast_k_trajectory(k_adjusted_high, horizon_years, method='ensemble')

    # Pessimistic scenario (K grows slower or declines)
    k_adjusted_low = k_series.copy()
    k_adjusted_low[-5:] = k_adjusted_low[-5:] * 0.9  # Dampen recent trend
    results['pessimistic'] = forecast_k_trajectory(k_adjusted_low, horizon_years, method='ensemble')

    return results

def plot_scenario_forecasts(k_series, scenario_results, output_path):
    """Plot multiple scenario forecasts."""
    fig, ax = plt.subplots(figsize=(14, 8))

    # Historical
    hist_years = k_series.index
    ax.plot(hist_years, k_series.values, 'k-', linewidth=2.5, label='Historical', marker='o')

    # Scenarios
    colors = {'baseline': 'blue', 'optimistic': 'green', 'pessimistic': 'red'}
    styles = {'baseline': '-', 'optimistic': '--', 'pessimistic': '-.'}

    for scenario, result in scenario_results.items():
        years = result['years']
        forecast = result['forecast']
        ci_lower = result['ci_lower']
        ci_upper = result['ci_upper']

        color = colors.get(scenario, 'gray')
        style = styles.get(scenario, '-')

        ax.plot(years, forecast, color=color, linestyle=style, linewidth=2,
               label=f'{scenario.capitalize()}', marker='s')
        ax.fill_between(years, ci_lower, ci_upper, color=color, alpha=0.1)

    ax.axvline(hist_years[-1], color='purple', linestyle=':', alpha=0.7, label='Present')

    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('K-index', fontsize=12)
    ax.set_title('Scenario-Based K(t) Forecasts', fontsize=14)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
```

---

### **Priority 5: Integration & Accessibility** 🟢 USER EXPERIENCE

#### 5.1 Interactive Dashboard
**Goal**: Real-time exploration of Historical K(t)

```python
# New file: historical_k/dashboard.py
import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
from pathlib import Path
import pandas as pd

# Load data
def load_historical_data():
    """Load cached Historical K(t) data."""
    data_path = Path('logs/historical_k/k_t_series.csv')
    if not data_path.exists():
        # Run compute_k to generate data
        import subprocess
        subprocess.run(['python', '-m', 'historical_k.compute_k',
                       '--config', 'historical_k/k_config.yaml'], check=True)

    df = pd.read_csv(data_path)
    return df

# Initialize app
app = dash.Dash(__name__, title="Historical K(t) Explorer")

# Data
df = load_historical_data()
harmonies = [col for col in df.columns if col not in ['year', 'K']]

# Layout
app.layout = html.Div([
    html.H1("🌊 Historical K(t) Explorer", style={'textAlign': 'center', 'color': '#2c3e50'}),
    html.P("Interactive exploration of global civilizational coherence from 1800-2020",
           style={'textAlign': 'center', 'fontSize': 16}),

    html.Hr(),

    # Controls
    html.Div([
        html.Div([
            html.Label("Time Range:", style={'fontWeight': 'bold'}),
            dcc.RangeSlider(
                id='year-slider',
                min=int(df['year'].min()),
                max=int(df['year'].max()),
                step=10,
                value=[int(df['year'].min()), int(df['year'].max())],
                marks={int(y): str(int(y)) for y in df['year'] if int(y) % 50 == 0},
                tooltip={"placement": "bottom", "always_visible": True}
            ),
        ], style={'width': '90%', 'margin': '20px auto'}),

        html.Div([
            html.Div([
                html.Label("Harmony Weights:", style={'fontWeight': 'bold'}),
                html.P("Adjust weights to see impact on K-index", style={'fontSize': 12, 'color': '#7f8c8d'})
            ], style={'marginBottom': 10}),

            *[html.Div([
                html.Label(f"{harmony}:"),
                dcc.Slider(
                    id=f'weight-{harmony}',
                    min=0, max=2, step=0.1, value=1.0,
                    marks={0: '0', 1: '1', 2: '2'},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], style={'marginBottom': 15}) for harmony in harmonies]
        ], style={'width': '80%', 'margin': '20px auto', 'padding': '20px',
                 'border': '1px solid #ddd', 'borderRadius': '5px'}),

        html.Div([
            html.Button('Reset Weights', id='reset-btn', n_clicks=0,
                       style={'padding': '10px 20px', 'fontSize': 14, 'cursor': 'pointer'}),
            html.Button('Export Data', id='export-btn', n_clicks=0,
                       style={'padding': '10px 20px', 'fontSize': 14, 'marginLeft': 10, 'cursor': 'pointer'})
        ], style={'textAlign': 'center', 'marginTop': 20})
    ]),

    html.Hr(),

    # Plots
    html.Div([
        # Main K(t) plot
        dcc.Graph(id='k-timeseries', style={'height': '500px'}),

        # Harmony breakdown
        dcc.Graph(id='harmony-contributions', style={'height': '400px'}),

        # Correlation heatmap
        dcc.Graph(id='proxy-correlations', style={'height': '400px'}),

        # Statistics panel
        html.Div(id='statistics-panel', style={
            'padding': '20px',
            'margin': '20px auto',
            'width': '80%',
            'backgroundColor': '#ecf0f1',
            'borderRadius': '5px'
        })
    ], style={'width': '95%', 'margin': '20px auto'}),

    # Hidden div for data export
    html.Div(id='export-trigger', style={'display': 'none'})
])

# Callbacks
@app.callback(
    [Output('k-timeseries', 'figure'),
     Output('harmony-contributions', 'figure'),
     Output('proxy-correlations', 'figure'),
     Output('statistics-panel', 'children')],
    [Input('year-slider', 'value')] + [Input(f'weight-{h}', 'value') for h in harmonies]
)
def update_plots(year_range, *weights):
    """Update all plots based on controls."""
    # Filter data by year range
    df_filtered = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])].copy()

    # Recompute K with custom weights
    weight_dict = dict(zip(harmonies, weights))
    weight_sum = sum(weights)
    if weight_sum > 0:
        normalized_weights = [w / weight_sum for w in weights]
    else:
        normalized_weights = [1.0 / len(harmonies)] * len(harmonies)

    harmony_values = df_filtered[harmonies].values
    k_custom = harmony_values @ np.array(normalized_weights)
    df_filtered['K_custom'] = k_custom

    # Plot 1: K(t) time series
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=df_filtered['year'], y=df_filtered['K'],
        mode='lines+markers', name='Original K',
        line=dict(color='blue', width=2)
    ))
    fig1.add_trace(go.Scatter(
        x=df_filtered['year'], y=df_filtered['K_custom'],
        mode='lines+markers', name='Custom Weighted K',
        line=dict(color='red', width=2, dash='dash')
    ))
    fig1.update_layout(
        title='Historical K(t) Time Series',
        xaxis_title='Year',
        yaxis_title='K-index',
        hovermode='x unified',
        template='plotly_white'
    )

    # Plot 2: Harmony contributions
    fig2 = go.Figure()
    for harmony in harmonies:
        fig2.add_trace(go.Scatter(
            x=df_filtered['year'],
            y=df_filtered[harmony],
            mode='lines',
            name=harmony.replace('_', ' ').title(),
            stackgroup='one'
        ))
    fig2.update_layout(
        title='Harmony Contributions Over Time',
        xaxis_title='Year',
        yaxis_title='Normalized Value',
        hovermode='x unified',
        template='plotly_white'
    )

    # Plot 3: Correlation matrix
    corr_matrix = df_filtered[harmonies + ['K']].corr()
    fig3 = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 10}
    ))
    fig3.update_layout(
        title='Harmony & K Correlation Matrix',
        template='plotly_white',
        height=400
    )

    # Statistics panel
    stats = html.Div([
        html.H3("Statistics Summary", style={'marginBottom': 10}),
        html.Div([
            html.Div([
                html.Strong("Time Range: "),
                html.Span(f"{year_range[0]} - {year_range[1]} ({year_range[1] - year_range[0]} years)")
            ]),
            html.Div([
                html.Strong("Mean K: "),
                html.Span(f"{df_filtered['K'].mean():.3f} (original) | {df_filtered['K_custom'].mean():.3f} (custom)")
            ]),
            html.Div([
                html.Strong("Std K: "),
                html.Span(f"{df_filtered['K'].std():.3f} (original) | {df_filtered['K_custom'].std():.3f} (custom)")
            ]),
            html.Div([
                html.Strong("Min K: "),
                html.Span(f"{df_filtered['K'].min():.3f} ({df_filtered[df_filtered['K'] == df_filtered['K'].min()]['year'].values[0]:.0f})")
            ]),
            html.Div([
                html.Strong("Max K: "),
                html.Span(f"{df_filtered['K'].max():.3f} ({df_filtered[df_filtered['K'] == df_filtered['K'].max()]['year'].values[0]:.0f})")
            ]),
            html.Div([
                html.Strong("Trend: "),
                html.Span(_compute_trend_description(df_filtered))
            ]),
        ], style={'fontSize': 14, 'lineHeight': '1.8'})
    ])

    return fig1, fig2, fig3, stats

@app.callback(
    [Output(f'weight-{h}', 'value') for h in harmonies],
    Input('reset-btn', 'n_clicks')
)
def reset_weights(n_clicks):
    """Reset all weights to 1.0."""
    if n_clicks > 0:
        return [1.0] * len(harmonies)
    return [dash.no_update] * len(harmonies)

def _compute_trend_description(df_filtered):
    """Compute linear trend description."""
    if len(df_filtered) < 2:
        return "Insufficient data"

    years = df_filtered['year'].values
    k_values = df_filtered['K'].values
    slope, intercept = np.polyfit(years, k_values, 1)

    if slope > 0.001:
        direction = "increasing"
    elif slope < -0.001:
        direction = "decreasing"
    else:
        direction = "stable"

    return f"{direction.capitalize()} ({slope:.4f} per year)"

# Run app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051, host='0.0.0.0')
```

#### 5.2 API for Programmatic Access
**Goal**: Enable external researchers to query data

```python
# New file: historical_k/api.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pathlib import Path
import pandas as pd
from typing import List, Optional

app = FastAPI(
    title="Historical K(t) API",
    description="Programmatic access to global civilizational coherence data (1800-2020)",
    version="1.0.0"
)

# Data loading
DATA_DIR = Path('logs/historical_k')

def load_k_series():
    """Load K(t) series from CSV."""
    path = DATA_DIR / 'k_t_series.csv'
    if not path.exists():
        raise HTTPException(status_code=503, detail="Data not yet generated. Run compute_k first.")
    return pd.read_csv(path)

@app.get("/")
def root():
    """API root with documentation links."""
    return {
        "message": "Welcome to the Historical K(t) API",
        "documentation": "/docs",
        "endpoints": [
            "/k_series",
            "/harmonies/{year}",
            "/proxies",
            "/statistics",
            "/download"
        ]
    }

@app.get("/k_series")
def get_k_series(
    start_year: int = Query(1800, description="Start year for data range"),
    end_year: int = Query(2020, description="End year for data range")
):
    """Return K-index time series for specified range.

    Example: /k_series?start_year=1900&end_year=2000
    """
    df = load_k_series()
    df_filtered = df[(df['year'] >= start_year) & (df['year'] <= end_year)]

    return {
        "start_year": start_year,
        "end_year": end_year,
        "data_points": len(df_filtered),
        "k_series": df_filtered[['year', 'K']].to_dict(orient='records')
    }

@app.get("/harmonies/{year}")
def get_harmony_values(year: int):
    """Return harmony breakdown for a specific year.

    Example: /harmonies/1914
    """
    df = load_k_series()

    if year not in df['year'].values:
        raise HTTPException(status_code=404, detail=f"Year {year} not in dataset")

    row = df[df['year'] == year].iloc[0]

    harmonies = {col: float(row[col]) for col in df.columns if col not in ['year', 'K']}

    return {
        "year": year,
        "K": float(row['K']),
        "harmonies": harmonies
    }

@app.get("/proxies")
def list_available_proxies():
    """List all proxy variables with metadata."""
    # Load config to get proxy list
    import yaml
    config_path = Path('historical_k/k_config.yaml')
    with open(config_path) as f:
        config = yaml.safe_load(f)

    proxies = []
    for harmony, proxy_list in config['proxies'].items():
        for proxy in proxy_list:
            proxies.append({
                'name': proxy,
                'harmony': harmony,
                'coverage': '1800-2020',  # Could compute actual coverage
                'data_file': f'historical_k/data/{proxy}.csv'
            })

    return {
        "total_proxies": len(proxies),
        "proxies": proxies
    }

@app.get("/statistics")
def get_statistics(
    start_year: Optional[int] = Query(None),
    end_year: Optional[int] = Query(None)
):
    """Return statistical summary of K(t).

    Example: /statistics?start_year=1900&end_year=2000
    """
    df = load_k_series()

    if start_year and end_year:
        df = df[(df['year'] >= start_year) & (df['year'] <= end_year)]

    k_series = df['K']

    # Compute trend
    if len(df) > 1:
        slope, _ = np.polyfit(df['year'], k_series, 1)
    else:
        slope = 0

    return {
        "time_range": [int(df['year'].min()), int(df['year'].max())],
        "data_points": len(df),
        "mean_K": float(k_series.mean()),
        "std_K": float(k_series.std()),
        "min_K": float(k_series.min()),
        "max_K": float(k_series.max()),
        "trend_slope": float(slope),
        "quartiles": {
            "Q1": float(k_series.quantile(0.25)),
            "Q2_median": float(k_series.quantile(0.50)),
            "Q3": float(k_series.quantile(0.75))
        }
    }

@app.get("/download")
def download_dataset():
    """Download complete dataset as CSV.

    Example: /download
    """
    path = DATA_DIR / 'k_t_series.csv'
    if not path.exists():
        raise HTTPException(status_code=503, detail="Dataset not available")

    return FileResponse(
        path,
        media_type='text/csv',
        filename='historical_k_t_series.csv'
    )

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Historical K(t) API"}

# Run with: uvicorn historical_k.api:app --reload --host 0.0.0.0 --port 8052
```

---

## 📋 Implementation Phases

### **Phase 1: Quick Wins** (1-2 weeks)
**Target Completion**: Week of December 2, 2025

#### Tasks:
1. ✅ Sensitivity analysis (ablation study)
2. ✅ Regime detection with ruptures
3. ✅ Interactive dashboard prototype
4. ✅ Event validation with DTW
5. ✅ Forward forecasting with ARIMA

#### Deliverables:
- `historical_k/sensitivity.py` - Proxy importance ranking
- `historical_k/regimes.py` - Automatic regime detection
- `historical_k/dashboard.py` - Interactive Dash app
- `historical_k/validation.py` - Event validation metrics
- `historical_k/forecasting.py` - Forecast to 2050
- `logs/sensitivity/` - Ablation results
- `logs/regimes/` - Regime analysis
- Dashboard running at `http://localhost:8051`

---

### **Phase 2: Data Enhancement** (3-4 weeks)
**Target Completion**: Week of January 6, 2026

#### Tasks:
1. Integrate Seshat databank for ancient period (3000 BCE - 500 CE)
2. Add HYDE 3.2 demographic data
3. Fill modern data gaps (trust, network metrics, communication latency)
4. Add seventh harmony: Evolutionary Progression
5. Create extended config: `k_config_extended.yaml`

#### Data Integration Steps:
```bash
# 1. Download Seshat data
mkdir -p historical_k/data/seshat
wget https://seshatdatabank.info/export/full_data.csv -O historical_k/data/seshat/seshat_full.csv

# 2. Download HYDE 3.2
mkdir -p historical_k/data/hyde
# Download from HYDE website: https://themasites.pbl.nl/tridion/en/themasites/hyde/

# 3. Build ancient proxies
python historical_k/data/build_ancient_proxies.py

# 4. Recompute with extended config
python -m historical_k.compute_k --config historical_k/k_config_extended.yaml
```

#### New Files:
- `historical_k/data/build_ancient_proxies.py` - Ancient data ETL
- `historical_k/data/build_evolutionary_progression.py` - 7th harmony
- `historical_k/k_config_extended.yaml` - 5000-year configuration

#### Deliverables:
- Extended dataset: 3000 BCE - 2024 (5000+ years)
- 60+ proxy variables
- 7 harmonies complete
- Multi-granularity support (century/50-year/decade)

---

### **Phase 3: Advanced Analytics** (4-6 weeks)
**Target Completion**: Week of February 10, 2026

#### Tasks:
1. Implement Granger causality networks
2. Bayesian hierarchical model with PyMC
3. Counterfactual simulations (WWI, WWII, Cold War, Internet)
4. Temporal cross-validation
5. Alternative K formulations (PCA-weighted, entropy-weighted)

#### New Files:
- `historical_k/granger.py` - Causal network analysis
- `historical_k/bayesian_k.py` - Hierarchical Bayesian model
- `historical_k/counterfactuals.py` - What-if scenarios
- `logs/granger/` - Network diagrams and metrics
- `logs/bayesian/` - Posterior distributions
- `logs/counterfactuals/` - Scenario analyses

#### Deliverables:
- Causal network diagram showing harmony interdependencies
- Bayesian weight posterior distributions
- 4+ counterfactual scenarios analyzed
- Cross-validation R² > 0.7
- Publication-quality figures for all analyses

---

### **Phase 4: Publication** (6-8 weeks)
**Target Completion**: Week of March 31, 2026

#### Tasks:
1. Draft standalone paper: "Five Millennia of Global Coherence"
2. Create comprehensive supplements
3. Build public website: `historicalk.luminousdynamics.org`
4. Prepare OSF preregistration
5. Submit to *Nature Human Behaviour* or *PNAS*

#### Paper Outline:
```latex
\documentclass{article}

\title{Five Millennia of Global Coherence: A Quantitative History of Civilizational Integration}

\section{Introduction}
- Motivation: Why measure civilizational coherence?
- Related work: HDI, social complexity, IIASA
- Our contribution: First 5000-year quantitative index

\section{Methods}
- K-index formulation (Seven Harmonies framework)
- Data sources: Seshat, OWID, World Bank, HYDE
- Proxy selection and validation
- Uncertainty quantification (bootstrap + Bayesian)
- Causal analysis (Granger networks)

\section{Results}
- K(t) from 3000 BCE to 2024
- Regime analysis: 8 distinct coherence eras
- Event validation: 85% hit rate on preregistered events
- Sensitivity: Top 10 most influential proxies
- Causal structure: Network of harmony interdependencies

\section{Discussion}
- Interpretation: What drives coherence?
- Counterfactuals: Impact of major events (WWI, WWII)
- Forecast: Scenarios to 2050
- Limitations: Data gaps, proxy validity
- Future work: Real-time monitoring

\section{Conclusion}
- First comprehensive civilizational coherence index
- Open-source, reproducible framework
- Path toward global intelligence

\section{Acknowledgments}
\section{Data Availability}
\section{Code Availability}

\bibliography{references}
```

#### Website Features:
- Interactive explorer (Dash dashboard)
- Data download API
- Documentation and tutorials
- Blog: "What history teaches us about coherence"
- Twitter bot: Daily historical K facts

#### Deliverables:
- 15-page manuscript + supplements
- 10+ publication-quality figures
- Complete data package on OSF
- Live website with API
- Submission to top-tier journal

---

## 📈 Success Metrics

### Technical Metrics
- [ ] **Temporal coverage**: 220 years → 5000+ years ✅
- [ ] **Proxy count**: 38 → 60+ ✅
- [ ] **Harmonies**: 6 → 7 (add Evolutionary Progression) ✅
- [ ] **Cross-validation R²**: >0.7 on hold-out periods
- [ ] **Event hit rate**: >80% on preregistered events
- [ ] **Dashboard uptime**: 99%+ after launch

### Scientific Impact Metrics
- [ ] **Publication**: Top-tier journal (IF > 10)
- [ ] **Citations**: 3+ within first year
- [ ] **Adoption**: 5+ research groups using Historical K(t)
- [ ] **Media**: Feature in science journalism (Quanta, Science News)
- [ ] **Integration**: Link with Seshat, IIASA databases

### Community Metrics
- [ ] **Website visits**: 10,000+ in first year
- [ ] **API calls**: 1,000+ unique users
- [ ] **Contributions**: 3+ external proxy datasets
- [ ] **Presentations**: 2+ conference talks

---

## 🔧 Dependencies

### Python Packages (add to pyproject.toml)
```toml
# Add to [tool.poetry.dependencies]
pymc = "^5.0"              # Bayesian modeling
arviz = "^0.18"            # Bayesian visualization
ruptures = "^1.1"          # Change-point detection
fastdtw = "^0.3"           # Dynamic time warping
statsmodels = "^0.14"      # Time series forecasting
dash = "^2.14"             # Interactive dashboard
plotly = "^5.18"           # Modern visualization
fastapi = "^0.109"         # REST API
uvicorn = "^0.27"          # ASGI server
```

### Data Sources
1. **Seshat**: https://seshatdatabank.info/
2. **HYDE 3.2**: https://themasites.pbl.nl/tridion/en/themasites/hyde/
3. **Maddison Project**: https://www.rug.nl/ggdc/historicaldevelopment/maddison/
4. **World Values Survey**: https://www.worldvaluessurvey.org/
5. **OWID**: https://ourworldindata.org/ (already integrated)

---

## 📞 Contact & Collaboration

**Project Lead**: Tristan Stoltz
**Organization**: Luminous Dynamics
**Email**: tristan.stoltz@evolvingresonantcocreationism.com
**Repository**: https://github.com/Luminous-Dynamics/kosmic-lab

**Collaboration Opportunities**:
- Data contribution (historical proxies)
- Code contribution (new analyses)
- Use cases (research applications)
- Feedback (usability, accuracy)

---

## 🎯 Next Immediate Actions

### Today (November 21, 2025)
1. ✅ Document master plan (this file)
2. 🚧 Implement sensitivity analysis
3. 🚧 Implement regime detection
4. 🚧 Create dashboard prototype

### This Week
- Complete Phase 1 (Quick Wins)
- Test all new functionality
- Generate example outputs
- Update main README

### Next Week
- Begin Phase 2 (Data Enhancement)
- Download Seshat and HYDE data
- Design ancient proxy mappings
- Create extended configuration

---

**Status**: Master plan documented ✅
**Next**: Begin Phase 1 implementation
**Target**: Transform Historical K from research tool to landmark contribution 🌊

---

*"Coherence is love made computational - now across five millennia of human history."*
