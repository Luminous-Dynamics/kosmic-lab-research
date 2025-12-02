#!/usr/bin/env python3
"""
Structural break detection for K(t) time series using Bai-Perron test.
Identifies discrete regime changes aligned with historical events.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def bai_perron_breaks(k_series, years, n_breaks=4):
    """
    Detect structural breaks using Bai-Perron sequential test.

    Args:
        k_series: K(t) values
        years: Corresponding years
        n_breaks: Number of breaks to detect

    Returns:
        break_years: Years where breaks occur
        break_indices: Indices in the series
    """
    try:
        from ruptures import Binseg

        # Use Binary Segmentation (Bai-Perron approximation)
        model = "l2"  # L2 norm for mean shift
        algo = Binseg(model=model).fit(k_series)
        break_indices = algo.predict(n_bkps=n_breaks)

        # Remove final index (end of series)
        break_indices = [b for b in break_indices if b < len(years)]
        break_years = [years[idx] for idx in break_indices]

        return break_years, break_indices
    except ImportError:
        print("Warning: ruptures not installed. Using simple threshold method.")
        # Fallback: detect large changes
        diffs = np.diff(k_series)
        threshold = np.std(diffs) * 2  # 2 sigma threshold
        break_indices = np.where(np.abs(diffs) > threshold)[0]
        break_years = [years[idx] for idx in break_indices[:n_breaks]]
        return break_years, break_indices[:n_breaks]


def align_with_historical_events(break_years):
    """
    Compare detected breaks with known historical events.
    """
    historical_events = {
        "WWI": (1914, 1918),
        "Great Depression": (1929, 1933),
        "WWII": (1939, 1945),
        "1970s Stagflation": (1973, 1979),
        "Cold War End": (1989, 1991),
        "2008 Financial Crisis": (2007, 2009)
    }

    alignments = []
    for break_year in break_years:
        for event_name, (start, end) in historical_events.items():
            if start <= break_year <= end:
                alignments.append({
                    "break_year": break_year,
                    "event": event_name,
                    "event_period": f"{start}-{end}",
                    "aligned": True
                })
                break
        else:
            alignments.append({
                "break_year": break_year,
                "event": "Unknown",
                "event_period": "N/A",
                "aligned": False
            })

    return pd.DataFrame(alignments)


def plot_structural_breaks(years, k_series, break_years, output_path):
    """
    Create publication-quality figure showing K(t) with structural breaks.
    """
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

    # Plot K(t) time series
    ax.plot(years, k_series, 'k-', linewidth=1.5, label='K(t)')

    # Mark structural breaks
    for break_year in break_years:
        ax.axvline(break_year, color='red', linestyle='--', alpha=0.7,
                   linewidth=1, label='Structural Break' if break_year == break_years[0] else '')

    # Annotate major events
    event_annotations = {
        1914: "WWI",
        1939: "WWII",
        1989: "Cold War End",
        2008: "Financial Crisis"
    }

    for year, label in event_annotations.items():
        if min(years) <= year <= max(years):
            idx = list(years).index(year)
            ax.annotate(label, xy=(year, k_series[idx]),
                       xytext=(year, k_series[idx] + 0.05),
                       fontsize=8, ha='center',
                       arrowprops=dict(arrowstyle='->', lw=0.5))

    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('K(t)', fontsize=12)
    ax.set_title('Structural Breaks in Civilizational Coherence (1810-2020)', fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✅ Figure saved to {output_path}")


def main():
    """
    Main execution: Load K(t) data, detect breaks, generate outputs.
    """
    # Load K(t) time series
    data_path = Path("logs/historical_k/k_t_series.csv")
    if not data_path.exists():
        print(f"❌ Error: {data_path} not found. Run compute_k.py first.")
        return

    df = pd.read_csv(data_path)
    years = df['year'].values
    k_series = df['K'].values

    # Detect structural breaks
    print("Detecting structural breaks...")
    break_years, break_indices = bai_perron_breaks(k_series, years, n_breaks=4)

    print(f"\n📊 Detected {len(break_years)} structural breaks:")
    for i, year in enumerate(break_years):
        idx = break_indices[i] if i < len(break_indices) else -1
        k_before = k_series[idx-1] if idx > 0 else k_series[0]
        k_after = k_series[idx] if idx < len(k_series) else k_series[-1]
        change = ((k_after - k_before) / k_before) * 100
        print(f"  {year}: K(t) change = {change:+.1f}%")

    # Align with historical events
    print("\n🔍 Aligning with historical events...")
    alignment_df = align_with_historical_events(break_years)
    print(alignment_df.to_string(index=False))

    # Save results
    output_dir = Path("logs/structural_breaks")
    output_dir.mkdir(parents=True, exist_ok=True)

    alignment_df.to_csv(output_dir / "break_alignment.csv", index=False)

    # Generate figure
    plot_structural_breaks(years, k_series, break_years,
                          output_dir / "structural_breaks_figure.png")

    print(f"\n✅ Analysis complete. Results in {output_dir}/")


if __name__ == "__main__":
    main()
