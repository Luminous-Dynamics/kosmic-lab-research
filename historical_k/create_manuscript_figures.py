#!/usr/bin/env python3
"""
Create Manuscript Figures for Historical K-Index

Generates publication-quality figures:
1. K(t) trajectory (1810-2020)
2. All 7 harmonies comparison
3. Historical period analysis
4. Growth rates by period
5. Harmony contributions

Output: historical_k/figures/
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set publication style
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")

# Configure matplotlib for publication quality
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'serif'
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 14

def load_k_index_data():
    """Load final K(t) index dataset."""

    script_dir = Path(__file__).parent
    data_path = script_dir / 'data_sources/processed/k_index_final_1810_2020.csv'

    print(f"Loading K(t) data from {data_path}...")
    df = pd.read_csv(data_path)

    print(f"  ✅ Loaded: {len(df)} years × {len(df.columns)} columns")
    return df

def create_figure_1_k_trajectory(df, output_dir):
    """
    Figure 1: K(t) Trajectory 1810-2020
    Main result showing collective human capital evolution.
    """

    print("\nCreating Figure 1: K(t) Trajectory...")

    fig, ax = plt.subplots(figsize=(10, 6))

    # Main K(t) line
    ax.plot(df['year'], df['k_index'],
            linewidth=2.5, color='#2E86AB', label='K(t) Index')

    # Historical period shading
    periods = [
        (1810, 1870, "Pre-industrial", '#FFE5B4', 0.2),
        (1870, 1914, "First globalization", '#E6F3FF', 0.2),
        (1914, 1945, "World wars", '#FFE6E6', 0.3),
        (1945, 1980, "Post-war golden age", '#E6FFE6', 0.2),
        (1980, 2000, "Late 20th century", '#F0E6FF', 0.2),
        (2000, 2020, "21st century", '#FFF4E6', 0.2),
    ]

    for start, end, label, color, alpha in periods:
        ax.axvspan(start, end, alpha=alpha, color=color, zorder=0)

    # Key historical events
    events = [
        (1840, 0.08, "Telegraph", 'top'),
        (1914, 0.27, "WWI", 'bottom'),
        (1945, 0.28, "UN Founded", 'top'),
        (1969, 0.40, "Moon Landing", 'bottom'),
        (1990, 0.55, "Internet Era", 'top'),
    ]

    for year, y_pos, label, va in events:
        ax.annotate(label, xy=(year, y_pos),
                   xytext=(year, y_pos + (0.05 if va == 'top' else -0.05)),
                   fontsize=8, ha='center', va=va,
                   arrowprops=dict(arrowstyle='->', lw=0.8, color='gray'))

    # Formatting
    ax.set_xlabel('Year', fontweight='bold')
    ax.set_ylabel('K(t) Index (normalized)', fontweight='bold')
    ax.set_title('Collective Human Capital Index (K) Evolution: 1810-2020',
                fontweight='bold', pad=20)

    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(1810, 2020)
    ax.set_ylim(0, 1)

    # Add growth statistics
    k_1810 = df[df['year'] == 1810]['k_index'].values[0]
    k_2020 = df[df['year'] == 2020]['k_index'].values[0]
    growth = k_2020 / k_1810

    textstr = f'Growth: {growth:.2f}x\n1810: {k_1810:.3f}\n2020: {k_2020:.3f}'
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes,
           fontsize=9, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()

    output_path = output_dir / 'figure_1_k_trajectory.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  ✅ Saved: {output_path}")

    plt.close()

def create_figure_2_all_harmonies(df, output_dir):
    """
    Figure 2: All Seven Harmonies Comparison
    Shows individual harmony trajectories.
    """

    print("\nCreating Figure 2: All Seven Harmonies...")

    fig, ax = plt.subplots(figsize=(12, 7))

    # Harmony metadata
    harmonies = {
        'h1': ('Resonant Coherence', '#FF6B6B'),
        'h2': ('Universal Interconnectedness', '#4ECDC4'),
        'h3': ('Sacred Reciprocity', '#45B7D1'),
        'h4': ('Infinite Play', '#FFA07A'),
        'h5': ('Integral Wisdom', '#98D8C8'),
        'h6': ('Pan-Sentient Flourishing', '#F7DC6F'),
        'h7': ('Evolutionary Progression', '#BB8FCE'),
    }

    # Plot each harmony
    for h_code, (h_name, color) in harmonies.items():
        ax.plot(df['year'], df[h_code],
               linewidth=2, label=h_name, color=color, alpha=0.8)

    # Formatting
    ax.set_xlabel('Year', fontweight='bold')
    ax.set_ylabel('Harmony Component (normalized)', fontweight='bold')
    ax.set_title('Seven Harmonies of Collective Human Capital: 1810-2020',
                fontweight='bold', pad=20)

    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(1810, 2020)
    ax.set_ylim(0, 1)

    ax.legend(loc='upper left', framealpha=0.9, ncol=1)

    plt.tight_layout()

    output_path = output_dir / 'figure_2_all_harmonies.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  ✅ Saved: {output_path}")

    plt.close()

def create_figure_3_growth_rates(df, output_dir):
    """
    Figure 3: Growth Rates by Historical Period
    Compares K(t) growth across eras.
    """

    print("\nCreating Figure 3: Growth Rates by Period...")

    # Define periods
    periods = [
        (1810, 1870, "Pre-industrial\n(1810-1870)"),
        (1870, 1914, "First globalization\n(1870-1914)"),
        (1914, 1945, "World wars\n(1914-1945)"),
        (1945, 1980, "Post-war golden age\n(1945-1980)"),
        (1980, 2000, "Late 20th century\n(1980-2000)"),
        (2000, 2020, "21st century\n(2000-2020)"),
    ]

    # Calculate growth rates
    period_labels = []
    growth_rates = []

    for start, end, label in periods:
        k_start = df[df['year'] == start]['k_index'].values[0]
        k_end = df[df['year'] == end]['k_index'].values[0]
        years = end - start
        annual_growth = ((k_end - k_start) / k_start) / years * 100

        period_labels.append(label)
        growth_rates.append(annual_growth)

    # Create bar chart
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = ['#FFE5B4', '#E6F3FF', '#FFE6E6', '#E6FFE6', '#F0E6FF', '#FFF4E6']
    bars = ax.bar(range(len(period_labels)), growth_rates, color=colors,
                  edgecolor='black', linewidth=1.2)

    # Add value labels on bars
    for i, (bar, rate) in enumerate(zip(bars, growth_rates)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{rate:.3f}%',
               ha='center', va='bottom', fontsize=9, fontweight='bold')

    # Formatting
    ax.set_xlabel('Historical Period', fontweight='bold')
    ax.set_ylabel('Annual Growth Rate (%)', fontweight='bold')
    ax.set_title('K(t) Annual Growth Rates by Historical Period',
                fontweight='bold', pad=20)

    ax.set_xticks(range(len(period_labels)))
    ax.set_xticklabels(period_labels, rotation=15, ha='right')

    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax.axhline(y=0, color='black', linewidth=0.8)

    plt.tight_layout()

    output_path = output_dir / 'figure_3_growth_rates.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  ✅ Saved: {output_path}")

    plt.close()

def create_figure_4_harmony_contributions(df, output_dir):
    """
    Figure 4: Harmony Contributions to K(t)
    Stacked area chart showing relative contributions.
    """

    print("\nCreating Figure 4: Harmony Contributions...")

    fig, ax = plt.subplots(figsize=(12, 7))

    # Extract harmonies
    harmonies = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7']
    harmony_names = [
        'H1: Resonant Coherence',
        'H2: Universal Interconnectedness',
        'H3: Sacred Reciprocity',
        'H4: Infinite Play',
        'H5: Integral Wisdom',
        'H6: Pan-Sentient Flourishing',
        'H7: Evolutionary Progression',
    ]

    # Create stacked area
    harmony_data = df[harmonies].values.T / 7  # Normalize by equal weights

    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE']

    ax.stackplot(df['year'], *harmony_data, labels=harmony_names,
                colors=colors, alpha=0.7)

    # Formatting
    ax.set_xlabel('Year', fontweight='bold')
    ax.set_ylabel('Contribution to K(t)', fontweight='bold')
    ax.set_title('Harmony Contributions to Collective Human Capital',
                fontweight='bold', pad=20)

    ax.set_xlim(1810, 2020)
    ax.legend(loc='upper left', framealpha=0.9, ncol=1, fontsize=8)
    ax.grid(True, alpha=0.3, linestyle='--')

    plt.tight_layout()

    output_path = output_dir / 'figure_4_harmony_contributions.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  ✅ Saved: {output_path}")

    plt.close()

def create_figure_5_harmony_growth_comparison(df, output_dir):
    """
    Figure 5: Harmony Growth Factor Comparison
    Bar chart comparing total growth (1810-2020).
    """

    print("\nCreating Figure 5: Harmony Growth Comparison...")

    harmonies = {
        'H1': 'h1',
        'H2': 'h2',
        'H3': 'h3',
        'H4': 'h4',
        'H5': 'h5',
        'H6': 'h6',
        'H7': 'h7',
    }

    harmony_full_names = {
        'H1': 'Resonant Coherence',
        'H2': 'Universal Interconnectedness',
        'H3': 'Sacred Reciprocity',
        'H4': 'Infinite Play',
        'H5': 'Integral Wisdom',
        'H6': 'Pan-Sentient Flourishing',
        'H7': 'Evolutionary Progression',
    }

    # Calculate growth factors
    growth_data = []

    for h_name, h_code in harmonies.items():
        val_1810 = df[df['year'] == 1810][h_code].values[0]
        val_2020 = df[df['year'] == 2020][h_code].values[0]
        growth = val_2020 / val_1810

        growth_data.append({
            'harmony': h_name,
            'full_name': harmony_full_names[h_name],
            'growth': growth
        })

    growth_df = pd.DataFrame(growth_data).sort_values('growth', ascending=False)

    # Create bar chart
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = ['#FF6B6B', '#BB8FCE', '#98D8C8', '#FFA07A', '#4ECDC4', '#45B7D1', '#F7DC6F']
    bars = ax.barh(range(len(growth_df)), growth_df['growth'],
                   color=colors, edgecolor='black', linewidth=1.2)

    # Add value labels
    for i, (bar, row) in enumerate(zip(bars, growth_df.itertuples())):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2.,
               f'{row.growth:.2f}x',
               ha='left', va='center', fontsize=9, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))

    # Formatting
    ax.set_xlabel('Growth Factor (2020 / 1810)', fontweight='bold')
    ax.set_title('Harmony Growth Factors: 1810-2020',
                fontweight='bold', pad=20)

    ax.set_yticks(range(len(growth_df)))
    ax.set_yticklabels([f"{row.harmony}: {row.full_name}"
                        for row in growth_df.itertuples()])

    ax.grid(True, alpha=0.3, linestyle='--', axis='x')

    plt.tight_layout()

    output_path = output_dir / 'figure_5_harmony_growth_comparison.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  ✅ Saved: {output_path}")

    plt.close()

def main():
    """Generate all manuscript figures."""

    print("=" * 70)
    print("MANUSCRIPT FIGURE GENERATION")
    print("Historical K-Index (1810-2020)")
    print("=" * 70)
    print()

    # Create output directory
    script_dir = Path(__file__).parent
    output_dir = script_dir / 'figures'
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Output directory: {output_dir}")
    print()

    # Load data
    df = load_k_index_data()

    # Generate figures
    create_figure_1_k_trajectory(df, output_dir)
    create_figure_2_all_harmonies(df, output_dir)
    create_figure_3_growth_rates(df, output_dir)
    create_figure_4_harmony_contributions(df, output_dir)
    create_figure_5_harmony_growth_comparison(df, output_dir)

    print()
    print("=" * 70)
    print("✅ ALL FIGURES GENERATED SUCCESSFULLY!")
    print("=" * 70)
    print()
    print(f"📊 Output location: {output_dir}")
    print(f"📈 Total figures: 5")
    print()
    print("Figures created:")
    print("  1. K(t) trajectory (1810-2020)")
    print("  2. All seven harmonies comparison")
    print("  3. Growth rates by historical period")
    print("  4. Harmony contributions (stacked area)")
    print("  5. Harmony growth factor comparison")
    print()
    print("Next steps:")
    print("  - Review figures for quality and accuracy")
    print("  - Add validation analysis (K vs GDP correlation)")
    print("  - Integrate figures into manuscript")
    print("  - Add philosophical framing section")
    print()
    print("=" * 70)

if __name__ == '__main__':
    try:
        main()
        import sys
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)
