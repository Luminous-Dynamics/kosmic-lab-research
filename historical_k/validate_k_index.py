#!/usr/bin/env python3
"""
Validate K-Index Against Known Measures

Quick validation to check if K(t) correlates with:
1. Synthetic GDP trajectory (historically plausible)
2. Life expectancy (from H6 data)
3. Education (from H5 data)

Output: validation_report.txt + correlation figure
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy.stats import pearsonr

plt.style.use('seaborn-v0_8-paper')
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.size'] = 10

def load_k_index():
    """Load final K(t) index."""
    script_dir = Path(__file__).parent
    data_path = script_dir / 'data_sources/processed/k_index_final_1810_2020.csv'
    return pd.read_csv(data_path)

def create_synthetic_gdp(years):
    """
    Create historically plausible GDP per capita trajectory.

    Based on known patterns:
    - Slow growth 1810-1870 (pre-industrial)
    - Acceleration 1870-1914 (industrial revolution)
    - Stagnation 1914-1945 (world wars)
    - Fast growth 1945-1980 (post-war boom)
    - Moderate growth 1980-2020
    """

    gdp = []
    base = 1000  # 1810 baseline (arbitrary units)

    for year in years:
        if year < 1870:
            # Pre-industrial: 0.2% annual growth
            years_since = year - 1810
            gdp_val = base * (1.002 ** years_since)

        elif 1870 <= year < 1914:
            # Industrial revolution: 1.5% annual growth
            base_1870 = base * (1.002 ** 60)
            years_since = year - 1870
            gdp_val = base_1870 * (1.015 ** years_since)

        elif 1914 <= year < 1945:
            # World wars: 0.3% annual growth (stagnation)
            base_1914 = base * (1.002 ** 60) * (1.015 ** 44)
            years_since = year - 1914
            gdp_val = base_1914 * (1.003 ** years_since)

        elif 1945 <= year < 1980:
            # Post-war boom: 2.5% annual growth
            base_1945 = base * (1.002 ** 60) * (1.015 ** 44) * (1.003 ** 31)
            years_since = year - 1945
            gdp_val = base_1945 * (1.025 ** years_since)

        else:  # 1980-2020
            # Modern era: 1.8% annual growth
            base_1980 = base * (1.002 ** 60) * (1.015 ** 44) * (1.003 ** 31) * (1.025 ** 35)
            years_since = year - 1980
            gdp_val = base_1980 * (1.018 ** years_since)

        gdp.append(gdp_val)

    # Normalize to 0-1 for comparison
    gdp = np.array(gdp)
    gdp_norm = (gdp - gdp.min()) / (gdp.max() - gdp.min())

    return gdp_norm

def main():
    """Run validation analysis."""

    print("=" * 70)
    print("K-INDEX VALIDATION ANALYSIS")
    print("=" * 70)
    print()

    # Load data
    print("Loading K(t) data...")
    df = load_k_index()
    years = df['year'].values
    k_index = df['k_index'].values

    # Create synthetic GDP
    print("Creating synthetic GDP trajectory (historically plausible)...")
    gdp_synthetic = create_synthetic_gdp(years)

    # Extract H5 and H6 for real-data validation
    h5_education = df['h5'].values
    h6_wellbeing = df['h6'].values

    print()
    print("=" * 70)
    print("CORRELATION ANALYSIS")
    print("=" * 70)
    print()

    # Compute correlations
    r_gdp, p_gdp = pearsonr(k_index, gdp_synthetic)
    r_edu, p_edu = pearsonr(k_index, h5_education)
    r_well, p_well = pearsonr(k_index, h6_wellbeing)

    print(f"K(t) vs Synthetic GDP:    r = {r_gdp:.4f} (p < {p_gdp:.2e})")
    print(f"K(t) vs Education (H5):   r = {r_edu:.4f} (p < {p_edu:.2e})")
    print(f"K(t) vs Wellbeing (H6):   r = {r_well:.4f} (p < {p_well:.2e})")
    print()

    # Interpretation
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()

    if r_gdp > 0.95:
        print("✅ EXCELLENT: K(t) strongly correlates with synthetic GDP")
        print("   This suggests our index captures economic development")
    elif r_gdp > 0.90:
        print("✅ GOOD: K(t) correlates well with synthetic GDP")
        print("   Minor divergences may reflect non-economic factors")
    elif r_gdp > 0.80:
        print("⚠️  MODERATE: K(t) shows reasonable correlation")
        print("   Some divergences - investigate which harmonies differ")
    else:
        print("❌ WEAK: K(t) correlation is low")
        print("   Major divergences - check individual harmony data")

    print()
    print("Note: Synthetic GDP is historically plausible but not real data.")
    print("For publication, correlate with actual Maddison GDP dataset.")
    print()

    # Create validation figure
    script_dir = Path(__file__).parent
    output_dir = script_dir / 'figures'

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Plot 1: K(t) vs Synthetic GDP
    ax1 = axes[0, 0]
    ax1.plot(years, k_index, linewidth=2, label='K(t) Index', color='#2E86AB')
    ax1.plot(years, gdp_synthetic, linewidth=2, label='Synthetic GDP (normalized)',
            color='#FFA07A', linestyle='--', alpha=0.7)
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Index Value (normalized)')
    ax1.set_title(f'K(t) vs Synthetic GDP\n(r = {r_gdp:.3f})', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: Scatter K(t) vs GDP
    ax2 = axes[0, 1]
    ax2.scatter(gdp_synthetic, k_index, alpha=0.6, s=20, color='#2E86AB')

    # Add regression line
    z = np.polyfit(gdp_synthetic, k_index, 1)
    p = np.poly1d(z)
    ax2.plot(gdp_synthetic, p(gdp_synthetic), "r--", alpha=0.8, linewidth=2)

    ax2.set_xlabel('Synthetic GDP (normalized)')
    ax2.set_ylabel('K(t) Index')
    ax2.set_title(f'Correlation: r = {r_gdp:.3f}', fontweight='bold')
    ax2.grid(True, alpha=0.3)

    # Add correlation text
    ax2.text(0.05, 0.95, f'r = {r_gdp:.4f}\np < {p_gdp:.2e}',
            transform=ax2.transAxes, fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # Plot 3: K(t) vs Education
    ax3 = axes[1, 0]
    ax3.scatter(h5_education, k_index, alpha=0.6, s=20, color='#98D8C8')
    z = np.polyfit(h5_education, k_index, 1)
    p = np.poly1d(z)
    ax3.plot(h5_education, p(h5_education), "r--", alpha=0.8, linewidth=2)
    ax3.set_xlabel('Education (H5)')
    ax3.set_ylabel('K(t) Index')
    ax3.set_title(f'K(t) vs Education: r = {r_edu:.3f}', fontweight='bold')
    ax3.grid(True, alpha=0.3)

    # Plot 4: K(t) vs Wellbeing
    ax4 = axes[1, 1]
    ax4.scatter(h6_wellbeing, k_index, alpha=0.6, s=20, color='#F7DC6F')
    z = np.polyfit(h6_wellbeing, k_index, 1)
    p = np.poly1d(z)
    ax4.plot(h6_wellbeing, p(h6_wellbeing), "r--", alpha=0.8, linewidth=2)
    ax4.set_xlabel('Wellbeing (H6)')
    ax4.set_ylabel('K(t) Index')
    ax4.set_title(f'K(t) vs Wellbeing: r = {r_well:.3f}', fontweight='bold')
    ax4.grid(True, alpha=0.3)

    plt.suptitle('K-Index Validation Against Known Measures',
                fontsize=14, fontweight='bold', y=0.995)

    plt.tight_layout()

    output_path = output_dir / 'figure_validation_correlations.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Validation figure saved: {output_path}")

    plt.close()

    # Save validation report
    report_path = script_dir / 'validation_report.txt'

    with open(report_path, 'w') as f:
        f.write("K-INDEX VALIDATION REPORT\n")
        f.write("=" * 70 + "\n")
        f.write(f"Date: November 25, 2025\n")
        f.write(f"Coverage: {years.min()}-{years.max()} ({len(years)} years)\n")
        f.write("\n")

        f.write("CORRELATION RESULTS\n")
        f.write("-" * 70 + "\n")
        f.write(f"K(t) vs Synthetic GDP:    r = {r_gdp:.4f}, p < {p_gdp:.2e}\n")
        f.write(f"K(t) vs Education (H5):   r = {r_edu:.4f}, p < {p_edu:.2e}\n")
        f.write(f"K(t) vs Wellbeing (H6):   r = {r_well:.4f}, p < {p_well:.2e}\n")
        f.write("\n")

        f.write("INTERPRETATION\n")
        f.write("-" * 70 + "\n")

        if r_gdp > 0.95:
            f.write("✅ EXCELLENT correlation with synthetic GDP (r > 0.95)\n")
            f.write("   K(t) strongly tracks economic development patterns\n")
        elif r_gdp > 0.90:
            f.write("✅ GOOD correlation with synthetic GDP (0.90 < r < 0.95)\n")
            f.write("   K(t) tracks economic development with minor divergences\n")
        elif r_gdp > 0.80:
            f.write("⚠️  MODERATE correlation with synthetic GDP (0.80 < r < 0.90)\n")
            f.write("   Some divergences from pure economic development\n")
        else:
            f.write("❌ WEAK correlation with synthetic GDP (r < 0.80)\n")
            f.write("   Major divergences - investigate individual harmonies\n")

        f.write("\n")
        f.write("NOTES\n")
        f.write("-" * 70 + "\n")
        f.write("1. Synthetic GDP based on historically plausible growth rates\n")
        f.write("2. Real validation should use Maddison GDP dataset\n")
        f.write("3. High correlations expected given H5, H6 are components\n")
        f.write("4. K(t) designed to capture broader than just economic growth\n")
        f.write("\n")

        f.write("RECOMMENDATIONS\n")
        f.write("-" * 70 + "\n")

        if r_gdp > 0.90:
            f.write("✅ Data quality appears good - proceed with manuscript\n")
            f.write("✅ Add Maddison GDP correlation in final version\n")
            f.write("✅ Philosophical framing section to explain divergences\n")
        else:
            f.write("⚠️  Investigate which harmonies diverge from GDP\n")
            f.write("⚠️  Check if divergences are intentional (non-economic factors)\n")
            f.write("⚠️  Consider adjusting harmony weights if needed\n")

    print(f"✅ Validation report saved: {report_path}")
    print()

    print("=" * 70)
    print("✅ VALIDATION COMPLETE")
    print("=" * 70)
    print()
    print("Summary:")
    print(f"  K(t) vs GDP correlation: r = {r_gdp:.3f}")
    print(f"  Overall assessment: {'GOOD' if r_gdp > 0.90 else 'NEEDS REVIEW'}")
    print()
    print("Next steps:")
    print("  1. Review correlation figure")
    print("  2. If r > 0.90: Proceed with philosophical framing")
    print("  3. If r < 0.90: Investigate individual harmony divergences")
    print("  4. Add real Maddison GDP data for publication")
    print()

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
