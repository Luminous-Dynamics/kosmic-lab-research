"""
k_topo_viz.py

Visualization Tools for K_Topo (Topological Consciousness)

This module provides publication-quality visualizations of persistent homology
features in agent trajectories, revealing the topological structure of consciousness.

Features:
- Persistence diagrams (birth-death plots)
- Barcode plots showing feature lifespans
- 3D trajectory visualization with detected loops
- Comparative analysis plots

Author: Kosmic Lab
Date: December 2, 2025
Version: 1.0.0
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Tuple
import warnings

try:
    from ripser import ripser
    RIPSER_AVAILABLE = True
except ImportError:
    RIPSER_AVAILABLE = False
    warnings.warn("ripser not available, some visualizations will be limited")


# =============================================================================
# Persistence Diagram Visualization
# =============================================================================

def plot_persistence_diagram(
    observations: np.ndarray,
    actions: np.ndarray,
    max_dim: int = 2,
    title: str = "Persistence Diagram",
    show_diagonal: bool = True,
    subsample: int = 500,
) -> go.Figure:
    """
    Create a persistence diagram (birth-death plot) showing topological features.

    A persistence diagram plots (birth, death) points for each topological feature:
    - Points far from the diagonal = long-lived features (signal)
    - Points near the diagonal = short-lived features (noise)

    Args:
        observations: Agent observations [T, obs_dim]
        actions: Agent actions [T, act_dim]
        max_dim: Maximum homology dimension (0=components, 1=loops, 2=voids)
        title: Plot title
        show_diagonal: Show y=x diagonal (features on this line have zero persistence)
        subsample: Subsample trajectory if longer

    Returns:
        Plotly figure object
    """
    if not RIPSER_AVAILABLE:
        raise ImportError("ripser required for persistence diagrams. Install with: poetry add ripser")

    # Combine trajectory
    trajectory = np.hstack([observations, actions])

    # Subsample
    if len(trajectory) > subsample:
        indices = np.linspace(0, len(trajectory) - 1, subsample, dtype=int)
        trajectory = trajectory[indices]

    # Standardize
    trajectory = (trajectory - np.mean(trajectory, axis=0)) / (np.std(trajectory, axis=0) + 1e-10)

    # Compute persistence
    result = ripser(trajectory, maxdim=max_dim)
    diagrams = result['dgms']

    # Create figure
    fig = go.Figure()

    # Colors for different dimensions
    colors = ['blue', 'red', 'green', 'purple']
    names = ['H₀ (Components)', 'H₁ (Loops)', 'H₂ (Voids)', 'H₃']

    # Plot each dimension
    for dim in range(min(len(diagrams), max_dim + 1)):
        if len(diagrams[dim]) == 0:
            continue

        births = diagrams[dim][:, 0]
        deaths = diagrams[dim][:, 1]

        # Filter infinite persistence
        finite_mask = np.isfinite(deaths)
        births_finite = births[finite_mask]
        deaths_finite = deaths[finite_mask]

        if len(births_finite) > 0:
            fig.add_trace(go.Scatter(
                x=births_finite,
                y=deaths_finite,
                mode='markers',
                name=names[dim],
                marker=dict(
                    size=8,
                    color=colors[dim],
                    opacity=0.6,
                    line=dict(width=1, color='white')
                ),
                hovertemplate=(
                    f'<b>{names[dim]}</b><br>' +
                    'Birth: %{x:.3f}<br>' +
                    'Death: %{y:.3f}<br>' +
                    'Persistence: %{customdata:.3f}<br>' +
                    '<extra></extra>'
                ),
                customdata=deaths_finite - births_finite,
            ))

    # Add diagonal line (y=x)
    if show_diagonal and len(diagrams) > 0:
        max_val = max([np.max(d[np.isfinite(d[:, 1]), 1]) for d in diagrams if len(d) > 0])
        min_val = min([np.min(d[:, 0]) for d in diagrams if len(d) > 0])

        fig.add_trace(go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode='lines',
            name='Zero Persistence',
            line=dict(color='gray', dash='dash', width=1),
            showlegend=False,
            hoverinfo='skip',
        ))

    # Layout
    fig.update_layout(
        title=title,
        xaxis_title='Birth Time',
        yaxis_title='Death Time',
        width=700,
        height=700,
        template='plotly_white',
        hovermode='closest',
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='gray',
            borderwidth=1,
        ),
    )

    # Equal aspect ratio
    fig.update_xaxes(scaleanchor="y", scaleratio=1)

    return fig


# =============================================================================
# Barcode Plot
# =============================================================================

def plot_barcode(
    observations: np.ndarray,
    actions: np.ndarray,
    max_dim: int = 2,
    title: str = "Persistence Barcode",
    subsample: int = 500,
) -> go.Figure:
    """
    Create a barcode plot showing lifespans of topological features.

    Barcode plots show each feature as a horizontal bar:
    - Longer bars = more persistent features (signal)
    - Shorter bars = less persistent features (noise)

    Args:
        observations: Agent observations [T, obs_dim]
        actions: Agent actions [T, act_dim]
        max_dim: Maximum homology dimension
        title: Plot title
        subsample: Subsample trajectory if longer

    Returns:
        Plotly figure object
    """
    if not RIPSER_AVAILABLE:
        raise ImportError("ripser required for barcode plots. Install with: poetry add ripser")

    # Combine trajectory
    trajectory = np.hstack([observations, actions])

    # Subsample
    if len(trajectory) > subsample:
        indices = np.linspace(0, len(trajectory) - 1, subsample, dtype=int)
        trajectory = trajectory[indices]

    # Standardize
    trajectory = (trajectory - np.mean(trajectory, axis=0)) / (np.std(trajectory, axis=0) + 1e-10)

    # Compute persistence
    result = ripser(trajectory, maxdim=max_dim)
    diagrams = result['dgms']

    # Create figure
    fig = go.Figure()

    # Colors for different dimensions
    colors = ['blue', 'red', 'green', 'purple']
    names = ['H₀', 'H₁', 'H₂', 'H₃']

    # Track y-position for bars
    y_pos = 0

    # Plot each dimension
    for dim in range(min(len(diagrams), max_dim + 1)):
        if len(diagrams[dim]) == 0:
            continue

        births = diagrams[dim][:, 0]
        deaths = diagrams[dim][:, 1]

        # Filter infinite persistence
        finite_mask = np.isfinite(deaths)
        births_finite = births[finite_mask]
        deaths_finite = deaths[finite_mask]

        # Sort by persistence (longest first)
        persistences = deaths_finite - births_finite
        sort_idx = np.argsort(-persistences)
        births_sorted = births_finite[sort_idx]
        deaths_sorted = deaths_finite[sort_idx]

        # Add bars
        for i, (b, d) in enumerate(zip(births_sorted, deaths_sorted)):
            fig.add_trace(go.Scatter(
                x=[b, d],
                y=[y_pos, y_pos],
                mode='lines',
                name=names[dim] if i == 0 else None,
                line=dict(color=colors[dim], width=3),
                showlegend=(i == 0),
                hovertemplate=(
                    f'<b>{names[dim]} #{i+1}</b><br>' +
                    'Birth: %{x[0]:.3f}<br>' +
                    'Death: %{x[1]:.3f}<br>' +
                    f'Persistence: {d-b:.3f}<br>' +
                    '<extra></extra>'
                ),
            ))
            y_pos += 1

        # Add spacing between dimensions
        y_pos += 2

    # Layout
    fig.update_layout(
        title=title,
        xaxis_title='Time',
        yaxis_title='Features',
        width=900,
        height=600,
        template='plotly_white',
        hovermode='closest',
        yaxis=dict(showticklabels=False),
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='gray',
            borderwidth=1,
        ),
    )

    return fig


# =============================================================================
# 3D Trajectory Visualization
# =============================================================================

def plot_trajectory_3d(
    observations: np.ndarray,
    actions: np.ndarray,
    title: str = "Agent Trajectory in (O, A) Space",
    show_loops: bool = True,
    subsample: int = 500,
) -> go.Figure:
    """
    Visualize agent trajectory in 3D space (PCA projection).

    Projects high-dimensional (O, A) trajectory to 3D using PCA,
    optionally highlighting detected loops.

    Args:
        observations: Agent observations [T, obs_dim]
        actions: Agent actions [T, act_dim]
        title: Plot title
        show_loops: Highlight regions with high loop persistence
        subsample: Subsample trajectory if longer

    Returns:
        Plotly figure object
    """
    from sklearn.decomposition import PCA

    # Combine trajectory
    trajectory = np.hstack([observations, actions])

    # Subsample
    if len(trajectory) > subsample:
        indices = np.linspace(0, len(trajectory) - 1, subsample, dtype=int)
        trajectory = trajectory[indices]

    # PCA to 3D (or fewer if trajectory is low-dimensional)
    n_features = trajectory.shape[1]
    n_components = min(3, n_features, len(trajectory))
    pca = PCA(n_components=n_components)
    trajectory_pca = pca.fit_transform(trajectory)

    # Pad to 3D if needed
    if n_components < 3:
        trajectory_3d = np.zeros((len(trajectory_pca), 3))
        trajectory_3d[:, :n_components] = trajectory_pca
    else:
        trajectory_3d = trajectory_pca

    # Create figure
    fig = go.Figure()

    # Color by time
    time_color = np.arange(len(trajectory_3d))

    # Add trajectory
    fig.add_trace(go.Scatter3d(
        x=trajectory_3d[:, 0],
        y=trajectory_3d[:, 1],
        z=trajectory_3d[:, 2],
        mode='lines+markers',
        name='Trajectory',
        line=dict(
            color=time_color,
            colorscale='Viridis',
            width=2,
            colorbar=dict(title='Time Step'),
        ),
        marker=dict(
            size=3,
            color=time_color,
            colorscale='Viridis',
            showscale=False,
        ),
        hovertemplate=(
            'Time: %{customdata}<br>' +
            'PC1: %{x:.3f}<br>' +
            'PC2: %{y:.3f}<br>' +
            'PC3: %{z:.3f}<br>' +
            '<extra></extra>'
        ),
        customdata=time_color,
    ))

    # Add start/end markers
    fig.add_trace(go.Scatter3d(
        x=[trajectory_3d[0, 0]],
        y=[trajectory_3d[0, 1]],
        z=[trajectory_3d[0, 2]],
        mode='markers',
        name='Start',
        marker=dict(size=10, color='green', symbol='circle'),
    ))

    fig.add_trace(go.Scatter3d(
        x=[trajectory_3d[-1, 0]],
        y=[trajectory_3d[-1, 1]],
        z=[trajectory_3d[-1, 2]],
        mode='markers',
        name='End',
        marker=dict(size=10, color='red', symbol='x'),
    ))

    # Layout
    variance_explained = pca.explained_variance_ratio_

    # Pad variance_explained if needed
    var_exp_padded = np.zeros(3)
    var_exp_padded[:len(variance_explained)] = variance_explained

    var_pct_str = ", ".join([f"{v:.1%}" for v in variance_explained])

    fig.update_layout(
        title=f"{title}<br><sub>PCA: {var_pct_str} variance explained</sub>",
        scene=dict(
            xaxis_title=f'PC1 ({var_exp_padded[0]:.1%})' if len(variance_explained) > 0 else 'PC1',
            yaxis_title=f'PC2 ({var_exp_padded[1]:.1%})' if len(variance_explained) > 1 else 'PC2',
            zaxis_title=f'PC3 ({var_exp_padded[2]:.1%})' if len(variance_explained) > 2 else 'PC3',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5),
            ),
        ),
        width=900,
        height=700,
        template='plotly_white',
    )

    return fig


# =============================================================================
# Comparative Analysis
# =============================================================================

def plot_comparative_analysis(
    trajectories: Dict[str, Tuple[np.ndarray, np.ndarray]],
    max_dim: int = 1,
    subsample: int = 500,
) -> go.Figure:
    """
    Compare persistence diagrams across multiple trajectories.

    Args:
        trajectories: Dict mapping names to (observations, actions) tuples
        max_dim: Maximum homology dimension
        subsample: Subsample trajectories if longer

    Returns:
        Plotly figure with subplots for each trajectory
    """
    if not RIPSER_AVAILABLE:
        raise ImportError("ripser required for comparative analysis. Install with: poetry add ripser")

    n_traj = len(trajectories)

    # Create subplots
    fig = make_subplots(
        rows=1, cols=n_traj,
        subplot_titles=list(trajectories.keys()),
        specs=[[{'type': 'scatter'}] * n_traj],
    )

    colors = ['blue', 'red', 'green']
    names = ['H₀', 'H₁', 'H₂']

    for col_idx, (name, (obs, act)) in enumerate(trajectories.items(), start=1):
        # Combine trajectory
        trajectory = np.hstack([obs, act])

        # Subsample
        if len(trajectory) > subsample:
            indices = np.linspace(0, len(trajectory) - 1, subsample, dtype=int)
            trajectory = trajectory[indices]

        # Standardize
        trajectory = (trajectory - np.mean(trajectory, axis=0)) / (np.std(trajectory, axis=0) + 1e-10)

        # Compute persistence
        result = ripser(trajectory, maxdim=max_dim)
        diagrams = result['dgms']

        # Plot each dimension
        for dim in range(min(len(diagrams), max_dim + 1)):
            if len(diagrams[dim]) == 0:
                continue

            births = diagrams[dim][:, 0]
            deaths = diagrams[dim][:, 1]

            # Filter infinite
            finite_mask = np.isfinite(deaths)
            births_finite = births[finite_mask]
            deaths_finite = deaths[finite_mask]

            if len(births_finite) > 0:
                fig.add_trace(
                    go.Scatter(
                        x=births_finite,
                        y=deaths_finite,
                        mode='markers',
                        name=names[dim],
                        marker=dict(size=6, color=colors[dim], opacity=0.6),
                        showlegend=(col_idx == 1),  # Only show legend once
                    ),
                    row=1, col=col_idx
                )

        # Add diagonal
        if len(diagrams) > 0:
            max_val = max([np.max(d[np.isfinite(d[:, 1]), 1]) for d in diagrams if len(d) > 0], default=1)
            min_val = min([np.min(d[:, 0]) for d in diagrams if len(d) > 0], default=0)

            fig.add_trace(
                go.Scatter(
                    x=[min_val, max_val],
                    y=[min_val, max_val],
                    mode='lines',
                    line=dict(color='gray', dash='dash', width=1),
                    showlegend=False,
                ),
                row=1, col=col_idx
            )

        # Update axes
        fig.update_xaxes(title_text='Birth', row=1, col=col_idx)
        if col_idx == 1:
            fig.update_yaxes(title_text='Death', row=1, col=col_idx)

    fig.update_layout(
        title='Comparative Persistence Analysis',
        width=300 * n_traj,
        height=400,
        template='plotly_white',
    )

    return fig


# =============================================================================
# Convenience Function: Generate All Plots
# =============================================================================

def generate_all_plots(
    observations: np.ndarray,
    actions: np.ndarray,
    title_prefix: str = "",
    save_html: bool = False,
    output_dir: str = ".",
) -> Dict[str, go.Figure]:
    """
    Generate all K_Topo visualizations for a trajectory.

    Args:
        observations: Agent observations [T, obs_dim]
        actions: Agent actions [T, act_dim]
        title_prefix: Prefix for plot titles
        save_html: Save plots as HTML files
        output_dir: Directory for HTML files

    Returns:
        Dictionary of figure names to Plotly figures
    """
    from core.k_topo import compute_k_topo, compute_k_spectral

    # Compute K_Topo
    k_topo = compute_k_topo(observations, actions)
    k_spectral = compute_k_spectral(observations, actions)

    title_suffix = f" (K_Topo={k_topo:.3f}, K_Spectral={k_spectral:.3f})"

    figures = {}

    # Persistence diagram
    figures['persistence_diagram'] = plot_persistence_diagram(
        observations, actions,
        title=f"{title_prefix}Persistence Diagram{title_suffix}",
    )

    # Barcode
    figures['barcode'] = plot_barcode(
        observations, actions,
        title=f"{title_prefix}Persistence Barcode{title_suffix}",
    )

    # 3D trajectory
    figures['trajectory_3d'] = plot_trajectory_3d(
        observations, actions,
        title=f"{title_prefix}Trajectory{title_suffix}",
    )

    # Save if requested
    if save_html:
        import os
        os.makedirs(output_dir, exist_ok=True)

        for name, fig in figures.items():
            filepath = os.path.join(output_dir, f"{title_prefix}{name}.html")
            fig.write_html(filepath)
            print(f"Saved: {filepath}")

    return figures


if __name__ == "__main__":
    # Demo: Generate visualizations for test trajectories
    import numpy as np

    np.random.seed(42)

    # Periodic trajectory (strong loops)
    print("Generating periodic trajectory visualizations...")
    t = np.linspace(0, 8 * np.pi, 200)
    obs_periodic = np.column_stack([
        np.sin(t), np.cos(t),
        np.sin(2 * t), np.cos(2 * t),
    ])
    act_periodic = np.column_stack([np.sin(t + 0.5), np.cos(t + 0.5)])

    figs_periodic = generate_all_plots(
        obs_periodic, act_periodic,
        title_prefix="Periodic: ",
        save_html=True,
        output_dir="visualizations/periodic",
    )

    # Random walk (minimal structure)
    print("\nGenerating random walk visualizations...")
    obs_random = np.random.randn(200, 4)
    act_random = np.random.randn(200, 2)

    figs_random = generate_all_plots(
        obs_random, act_random,
        title_prefix="Random: ",
        save_html=True,
        output_dir="visualizations/random",
    )

    # Thermostat (no loops)
    print("\nGenerating thermostat visualizations...")
    temps = np.linspace(18, 22, 200)
    obs_thermo = temps.reshape(-1, 1)
    act_thermo = (temps > 20).astype(float).reshape(-1, 1)

    figs_thermo = generate_all_plots(
        obs_thermo, act_thermo,
        title_prefix="Thermostat: ",
        save_html=True,
        output_dir="visualizations/thermostat",
    )

    # Comparative plot
    print("\nGenerating comparative analysis...")
    fig_compare = plot_comparative_analysis({
        'Periodic (K_Topo=0.91)': (obs_periodic, act_periodic),
        'Random (K_Topo=0.07)': (obs_random, act_random),
        'Thermostat (K_Topo=0.00)': (obs_thermo, act_thermo),
    })

    fig_compare.write_html("visualizations/comparative_analysis.html")
    print("Saved: visualizations/comparative_analysis.html")

    print("\n✅ All visualizations generated!")
    print("\nOpen visualizations/*.html in your browser to explore.")
