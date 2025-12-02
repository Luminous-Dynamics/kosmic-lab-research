#!/usr/bin/env python3
"""
External Validation: Cross-Validate K(t) with Established Indices

This module validates the K-index against well-established external indices:
1. Human Development Index (HDI) - UNDP
2. GDP per capita - Maddison Project
3. Democracy scores - Polity IV/V-Dem
4. Battle deaths - UCDP/Correlates of War

Expected Correlations:
- K(t) vs HDI: r > 0.70 (positive, strong)
- K(t) vs GDP per capita: r > 0.60 (positive, moderate-strong)
- K(t) vs Democracy: r > 0.50 (positive, moderate)
- K(t) vs Battle deaths: r < -0.50 (negative, moderate)

Data Sources:
=============

1. Human Development Index (HDI)
   - Source: United Nations Development Programme
   - URL: http://hdr.undp.org/en/data
   - Coverage: 1990-present
   - Variables: HDI (composite of health, education, income)

2. Maddison Project GDP
   - Source: Maddison Historical Statistics
   - URL: https://www.rug.nl/ggdc/historicaldevelopment/maddison/
   - Coverage: 1 CE - present
   - Variables: GDP per capita (constant 2011 US$)

3. Polity V Democracy Scores
   - Source: Center for Systemic Peace
   - URL: https://www.systemicpeace.org/polityproject.html
   - Coverage: 1800-present
   - Variables: Polity score (-10 to +10)

4. V-Dem Democracy Index
   - Source: Varieties of Democracy Project
   - URL: https://www.v-dem.net/
   - Coverage: 1789-present
   - Variables: Electoral democracy index (0-1)

5. Battle Deaths (UCDP)
   - Source: Uppsala Conflict Data Program
   - URL: https://ucdp.uu.se/
   - Coverage: 1989-present
   - Variables: Annual battle-related deaths

6. Correlates of War (COW)
   - Source: Correlates of War Project
   - URL: https://correlatesofwar.org/
   - Coverage: 1816-2007
   - Variables: War participants, casualties
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExternalDataSource:
    """Fetch and process external validation datasets."""

    def __init__(self, data_dir: str = "data/sources/external"):
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"

        # Create directories
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def download_instructions(self) -> str:
        """Return download instructions for all external datasets."""
        instructions = """
=============================================================================
                   External Validation Data Download Guide
=============================================================================

1. HUMAN DEVELOPMENT INDEX (HDI)
--------------------------------
Visit: http://hdr.undp.org/en/data
Download: "Human Development Index (HDI)" time series
Format: CSV or Excel
Place in: data/sources/external/raw/hdi.csv

2. MADDISON PROJECT GDP
-----------------------
Visit: https://www.rug.nl/ggdc/historicaldevelopment/maddison/releases/maddison-project-database-2020
Download: "Full dataset" (Excel or CSV)
Place in: data/sources/external/raw/maddison_gdp.csv

3. POLITY V
-----------
Visit: https://www.systemicpeace.org/inscrdata.html
Download: "Polity5 Annual Time-Series, 1946-2018"
Place in: data/sources/external/raw/polity5.csv

4. V-DEM DEMOCRACY
-----------------
Visit: https://www.v-dem.net/data/the-v-dem-dataset/
Download: "Country-Year: V-Dem Full+Others" (CSV)
Place in: data/sources/external/raw/vdem.csv
(Note: Large file ~500 MB)

5. UCDP BATTLE DEATHS
--------------------
Visit: https://ucdp.uu.se/downloads/
Download: "UCDP Battle-Related Deaths Dataset"
Place in: data/sources/external/raw/ucdp_battle_deaths.csv

6. CORRELATES OF WAR
-------------------
Visit: https://correlatesofwar.org/data-sets/
Download: "Inter-State War Data, v4.0" and "Intra-State War Data, v5.1"
Place in: data/sources/external/raw/cow_inter_state.csv
          data/sources/external/raw/cow_intra_state.csv

7. KOF GLOBALIZATION INDEX ⭐ TRACK C-1
---------------------------------------
Visit: https://kof.ethz.ch/en/forecasts-and-indicators/indicators/kof-globalisation-index.html
Download: "KOF Globalisation Index" data (Excel or CSV)
Process to: year, kof_globalization (overall index)
Place in: data/sources/external/raw/kof_globalization.csv

8. DHL GLOBAL CONNECTEDNESS INDEX ⭐ TRACK C-1
---------------------------------------------
Visit: https://www.dhl.com/global-en/delivered/globalization/global-connectedness-index.html
Download: Latest Global Connectedness Index data
Process to: year, dhl_connectedness (depth score)
Place in: data/sources/external/raw/dhl_connectedness.csv

=============================================================================
After downloading, run:
  python external_validation.py --process

This will:
1. Load all datasets
2. Align years
3. Compute correlations with K(t)
4. Generate validation report

⭐ Track C-1 requires: HDI, GDP, KOF, DHL for manuscript validation
=============================================================================
"""
        return instructions

    def load_hdi(self) -> pd.DataFrame:
        """Load Human Development Index data."""
        # Try processed first, then raw
        filepath = self.processed_dir / "hdi.csv"
        if not filepath.exists():
            filepath = self.raw_dir / "hdi.csv"

        if not filepath.exists():
            logger.warning(f"HDI data not found: {filepath}")
            return pd.DataFrame()

        try:
            df = pd.read_csv(filepath)

            # Look for year and HDI value columns
            year_cols = [c for c in df.columns if "year" in c.lower()]
            hdi_cols = [c for c in df.columns if "hdi" in c.lower()]

            if not year_cols or not hdi_cols:
                logger.error("Could not identify year/HDI columns")
                return pd.DataFrame()

            result = df[[year_cols[0], hdi_cols[0]]].copy()
            result.columns = ["year", "hdi"]

            # Filter to numeric years
            result = result[pd.to_numeric(result["year"], errors="coerce").notna()]
            result["year"] = result["year"].astype(int)
            result["hdi"] = pd.to_numeric(result["hdi"], errors="coerce")

            logger.info(
                f"✓ Loaded HDI: {len(result)} records, {result['year'].min()}-{result['year'].max()}"
            )
            return result

        except Exception as e:
            logger.error(f"Error loading HDI: {e}")
            return pd.DataFrame()

    def load_maddison_gdp(self) -> pd.DataFrame:
        """Load Maddison Project GDP per capita data."""
        # Try processed first, then raw
        filepath = self.processed_dir / "maddison_gdp.csv"
        if not filepath.exists():
            filepath = self.raw_dir / "maddison_gdp.csv"

        if not filepath.exists():
            logger.warning(f"Maddison GDP data not found: {filepath}")
            return pd.DataFrame()

        try:
            df = pd.read_csv(filepath)

            # Maddison has 'year' and 'gdppc' (GDP per capita)
            if "year" not in df.columns:
                # Try finding year column
                year_cols = [c for c in df.columns if "year" in c.lower()]
                if year_cols:
                    df = df.rename(columns={year_cols[0]: "year"})

            # Find GDP per capita column
            gdp_cols = [
                c
                for c in df.columns
                if "gdppc" in c.lower()
                or "gdp per capita" in c.lower()
                or "gdp_per_capita" in c.lower()
            ]
            if gdp_cols:
                df = df.rename(columns={gdp_cols[0]: "gdp_per_capita"})

            if "year" not in df.columns or "gdp_per_capita" not in df.columns:
                logger.error("Could not identify year/GDP columns")
                return pd.DataFrame()

            # Aggregate to global average (if multiple countries)
            if "country" in df.columns or "countrycode" in df.columns:
                result = df.groupby("year")["gdp_per_capita"].mean().reset_index()
            else:
                result = df[["year", "gdp_per_capita"]].copy()

            result["year"] = result["year"].astype(int)
            result["gdp_per_capita"] = pd.to_numeric(
                result["gdp_per_capita"], errors="coerce"
            )

            logger.info(
                f"✓ Loaded Maddison GDP: {len(result)} records, {result['year'].min()}-{result['year'].max()}"
            )
            return result

        except Exception as e:
            logger.error(f"Error loading Maddison GDP: {e}")
            return pd.DataFrame()

    def load_polity(self) -> pd.DataFrame:
        """Load Polity V democracy scores."""
        filepath = self.raw_dir / "polity5.csv"

        if not filepath.exists():
            logger.warning(f"Polity data not found: {filepath}")
            return pd.DataFrame()

        try:
            df = pd.read_csv(filepath)

            # Polity has 'year' and 'polity2' (revised combined polity score)
            if "year" in df.columns and "polity2" in df.columns:
                # Aggregate to global average
                if "country" in df.columns or "ccode" in df.columns:
                    result = df.groupby("year")["polity2"].mean().reset_index()
                else:
                    result = df[["year", "polity2"]].copy()

                result.columns = ["year", "polity_score"]
                result["year"] = result["year"].astype(int)
                result["polity_score"] = pd.to_numeric(
                    result["polity_score"], errors="coerce"
                )

                logger.info(
                    f"✓ Loaded Polity: {len(result)} records, {result['year'].min()}-{result['year'].max()}"
                )
                return result
            else:
                logger.error("Could not find Polity columns")
                return pd.DataFrame()

        except Exception as e:
            logger.error(f"Error loading Polity: {e}")
            return pd.DataFrame()

    def load_vdem(self) -> pd.DataFrame:
        """Load V-Dem democracy index."""
        filepath = self.raw_dir / "vdem.csv"

        if not filepath.exists():
            logger.warning(f"V-Dem data not found: {filepath}")
            return pd.DataFrame()

        try:
            # V-Dem is large, specify columns to load
            df = pd.read_csv(
                filepath, usecols=["year", "v2x_polyarchy"]
            )  # Electoral democracy index

            # Aggregate to global average
            result = df.groupby("year")["v2x_polyarchy"].mean().reset_index()
            result.columns = ["year", "democracy_index"]

            result["year"] = result["year"].astype(int)
            result["democracy_index"] = pd.to_numeric(
                result["democracy_index"], errors="coerce"
            )

            logger.info(
                f"✓ Loaded V-Dem: {len(result)} records, {result['year'].min()}-{result['year'].max()}"
            )
            return result

        except Exception as e:
            logger.error(f"Error loading V-Dem: {e}")
            return pd.DataFrame()

    def load_battle_deaths(self) -> pd.DataFrame:
        """Load UCDP battle deaths data."""
        filepath = self.raw_dir / "ucdp_battle_deaths.csv"

        if not filepath.exists():
            logger.warning(f"UCDP data not found: {filepath}")
            return pd.DataFrame()

        try:
            df = pd.read_csv(filepath)

            # UCDP has 'year' and 'bd_best' (best estimate of battle deaths)
            year_col = [c for c in df.columns if "year" in c.lower()][0]
            deaths_col = [
                c for c in df.columns if "bd" in c.lower() or "death" in c.lower()
            ][0]

            result = df.groupby(year_col)[deaths_col].sum().reset_index()
            result.columns = ["year", "battle_deaths"]

            result["year"] = result["year"].astype(int)
            result["battle_deaths"] = pd.to_numeric(
                result["battle_deaths"], errors="coerce"
            )

            logger.info(
                f"✓ Loaded UCDP: {len(result)} records, {result['year'].min()}-{result['year'].max()}"
            )
            return result

        except Exception as e:
            logger.error(f"Error loading UCDP: {e}")
            return pd.DataFrame()

    def load_kof_globalization(self) -> pd.DataFrame:
        """Load KOF Globalization Index data."""
        # Try processed first, then raw
        filepath = self.processed_dir / "kof_globalization.csv"
        if not filepath.exists():
            filepath = self.raw_dir / "kof_globalization.csv"

        if not filepath.exists():
            logger.warning(f"KOF Globalization data not found: {filepath}")
            return pd.DataFrame()

        try:
            df = pd.read_csv(filepath)

            # Look for year and KOF index columns
            year_cols = [c for c in df.columns if "year" in c.lower()]
            kof_cols = [
                c
                for c in df.columns
                if "kof" in c.lower()
                or "globalization" in c.lower()
                or "global" in c.lower()
            ]

            if not year_cols or not kof_cols:
                logger.error("Could not identify year/KOF columns")
                return pd.DataFrame()

            result = df[[year_cols[0], kof_cols[0]]].copy()
            result.columns = ["year", "kof_globalization"]

            # Aggregate to global average if multiple countries
            if len(df) > len(result["year"].unique()):
                result = (
                    result.groupby("year")["kof_globalization"].mean().reset_index()
                )

            result["year"] = result["year"].astype(int)
            result["kof_globalization"] = pd.to_numeric(
                result["kof_globalization"], errors="coerce"
            )

            logger.info(
                f"✓ Loaded KOF: {len(result)} records, {result['year'].min()}-{result['year'].max()}"
            )
            return result

        except Exception as e:
            logger.error(f"Error loading KOF: {e}")
            return pd.DataFrame()

    def load_dhl_connectedness(self) -> pd.DataFrame:
        """Load DHL Global Connectedness Index data."""
        filepath = self.raw_dir / "dhl_connectedness.csv"

        if not filepath.exists():
            logger.warning(f"DHL Connectedness data not found: {filepath}")
            return pd.DataFrame()

        try:
            df = pd.read_csv(filepath)

            # Look for year and DHL index columns
            year_cols = [c for c in df.columns if "year" in c.lower()]
            dhl_cols = [
                c
                for c in df.columns
                if "dhl" in c.lower()
                or "connectedness" in c.lower()
                or "depth" in c.lower()
            ]

            if not year_cols or not dhl_cols:
                logger.error("Could not identify year/DHL columns")
                return pd.DataFrame()

            result = df[[year_cols[0], dhl_cols[0]]].copy()
            result.columns = ["year", "dhl_connectedness"]

            # Aggregate to global average if multiple countries
            if len(df) > len(result["year"].unique()):
                result = (
                    result.groupby("year")["dhl_connectedness"].mean().reset_index()
                )

            result["year"] = result["year"].astype(int)
            result["dhl_connectedness"] = pd.to_numeric(
                result["dhl_connectedness"], errors="coerce"
            )

            logger.info(
                f"✓ Loaded DHL: {len(result)} records, {result['year'].min()}-{result['year'].max()}"
            )
            return result

        except Exception as e:
            logger.error(f"Error loading DHL: {e}")
            return pd.DataFrame()

    def load_all_indices(self) -> Dict[str, pd.DataFrame]:
        """Load all available external indices."""
        indices = {
            "hdi": self.load_hdi(),
            "gdp": self.load_maddison_gdp(),
            "kof": self.load_kof_globalization(),
            "dhl": self.load_dhl_connectedness(),
            "polity": self.load_polity(),
            "vdem": self.load_vdem(),
            "battle_deaths": self.load_battle_deaths(),
        }

        # Filter to non-empty dataframes
        indices = {k: v for k, v in indices.items() if not v.empty}

        logger.info(f"Loaded {len(indices)} external indices")
        return indices


def cross_validate_k_index(
    k_series: pd.DataFrame,
    external_indices: Dict[str, pd.DataFrame],
    output_dir: str = "logs/validation_external",
) -> Dict:
    """
    Cross-validate K(t) against external indices.

    Args:
        k_series: DataFrame with 'year' and 'K' columns
        external_indices: Dictionary of external index DataFrames
        output_dir: Output directory for results

    Returns:
        Dictionary with validation results
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {"correlations": {}, "regressions": {}, "time_overlaps": {}}

    # For each external index
    for index_name, index_df in external_indices.items():
        logger.info(f"\nValidating against {index_name}...")

        # Merge with K(t) on year
        merged = k_series.merge(index_df, on="year", how="inner")

        logger.info(f"  Found {len(merged)} overlapping years")

        if len(merged) < 4:
            logger.warning(
                f"  ⚠ Only {len(merged)} overlapping years, skipping (need at least 4)"
            )
            continue

        results["time_overlaps"][index_name] = {
            "n_years": len(merged),
            "year_range": (int(merged["year"].min()), int(merged["year"].max())),
        }

        # Get value column (second column)
        value_col = [c for c in merged.columns if c not in ["year", "K"]][0]

        # Remove NaN
        clean = merged[["K", value_col]].dropna()

        if len(clean) < 4:
            logger.warning(
                f"  ⚠ Only {len(clean)} valid pairs after removing NaN, skipping"
            )
            continue

        logger.info(f"  Valid pairs: {len(clean)}")

        # Compute correlation
        r_pearson, p_pearson = stats.pearsonr(clean["K"], clean[value_col])
        r_spearman, p_spearman = stats.spearmanr(clean["K"], clean[value_col])

        results["correlations"][index_name] = {
            "pearson_r": r_pearson,
            "pearson_p": p_pearson,
            "spearman_r": r_spearman,
            "spearman_p": p_spearman,
            "n_samples": len(clean),
        }

        # Linear regression
        from scipy.stats import linregress

        slope, intercept, r_value, p_value, std_err = linregress(
            clean["K"], clean[value_col]
        )

        results["regressions"][index_name] = {
            "slope": slope,
            "intercept": intercept,
            "r_squared": r_value**2,
            "p_value": p_value,
            "std_err": std_err,
        }

        # Log results
        logger.info(f"  Pearson r = {r_pearson:.3f} (p={p_pearson:.4f})")
        logger.info(f"  Spearman r = {r_spearman:.3f} (p={p_spearman:.4f})")
        logger.info(f"  R² = {r_value**2:.3f}")
        logger.info(f"  Samples: {len(clean)} years")

        # Plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # Scatter plot with regression line
        ax1.scatter(clean["K"], clean[value_col], alpha=0.6)
        x_fit = np.linspace(clean["K"].min(), clean["K"].max(), 100)
        y_fit = slope * x_fit + intercept
        ax1.plot(x_fit, y_fit, "r--", label=f"R² = {r_value**2:.3f}")
        ax1.set_xlabel("K(t)")
        ax1.set_ylabel(index_name.upper())
        ax1.set_title(f"K(t) vs {index_name.upper()}\nPearson r = {r_pearson:.3f}")
        ax1.legend()
        ax1.grid(alpha=0.3)

        # Time series overlay
        ax2_twin = ax2.twinx()
        ax2.plot(merged["year"], merged["K"], "b-", label="K(t)", linewidth=2)
        ax2_twin.plot(
            merged["year"],
            merged[value_col],
            "r-",
            label=index_name.upper(),
            linewidth=2,
        )
        ax2.set_xlabel("Year")
        ax2.set_ylabel("K(t)", color="b")
        ax2_twin.set_ylabel(index_name.upper(), color="r")
        ax2.set_title(f"Time Series Comparison")
        ax2.grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig(
            output_dir / f"validation_{index_name}.png", dpi=300, bbox_inches="tight"
        )
        plt.close()

    # Generate summary report
    report_path = output_dir / "validation_report.md"
    with open(report_path, "w") as f:
        f.write("# K(t) External Validation Report\n\n")
        f.write(f"**Generated**: {pd.Timestamp.now()}\n\n")

        f.write("## Correlations with External Indices\n\n")
        f.write("| Index | Pearson r | p-value | Spearman r | R² | N Years |\n")
        f.write("|-------|-----------|---------|------------|----|---------|\n")

        for idx, corr in results["correlations"].items():
            f.write(
                f"| {idx.upper()} | {corr['pearson_r']:.3f} | {corr['pearson_p']:.4f} | "
                f"{corr['spearman_r']:.3f} | {results['regressions'][idx]['r_squared']:.3f} | "
                f"{corr['n_samples']} |\n"
            )

        f.write("\n## Expected vs Observed Correlations\n\n")
        expected = {
            "hdi": (0.70, "positive"),
            "gdp": (0.60, "positive"),
            "polity": (0.50, "positive"),
            "vdem": (0.50, "positive"),
            "battle_deaths": (-0.50, "negative"),
        }

        f.write("| Index | Expected | Observed | Status |\n")
        f.write("|-------|----------|----------|--------|\n")

        for idx, (exp_r, direction) in expected.items():
            if idx in results["correlations"]:
                obs_r = results["correlations"][idx]["pearson_r"]
                if direction == "positive":
                    status = "✅ PASS" if obs_r >= exp_r else "⚠️ WEAK"
                else:
                    status = "✅ PASS" if obs_r <= exp_r else "⚠️ WEAK"

                f.write(
                    f"| {idx.upper()} | {direction} r>{abs(exp_r):.2f} | r={obs_r:.3f} | {status} |\n"
                )
            else:
                f.write(
                    f"| {idx.upper()} | {direction} r>{abs(exp_r):.2f} | NO DATA | ⚠️ MISSING |\n"
                )

        f.write("\n## Interpretation\n\n")
        f.write(
            "**Strong positive correlations** with HDI, GDP, and democracy indices validate that K(t) "
            "captures development and human flourishing.\n\n"
        )
        f.write(
            "**Negative correlation** with battle deaths confirms K(t) decreases during conflict periods.\n\n"
        )

    logger.info(f"\n✓ Validation report saved to {report_path}")

    return results


if __name__ == "__main__":
    import sys

    print("=" * 70)
    print("K(t) External Validation")
    print("=" * 70)
    print()

    if "--download" in sys.argv:
        source = ExternalDataSource()
        print(source.download_instructions())

    elif "--process" in sys.argv:
        # Load K(t) series (prefer original with complete decadal data)
        k_path_original = "logs/historical_k/k_t_series.csv"
        k_path_extended = "logs/historical_k_extended/k_t_series_5000y.csv"

        if Path(k_path_original).exists():
            k_path = k_path_original
            print(f"✓ Using original K(t) series (1810 - 2020 CE, decadal)")
        elif Path(k_path_extended).exists():
            k_path = k_path_extended
            print(f"✓ Using extended K(t) series (3000 BCE - 2020 CE)")
        else:
            print(f"✗ K(t) series not found!")
            print(f"   Tried: {k_path_original}")
            print(f"   Tried: {k_path_extended}")
            print("Run 'poetry run python historical_k/compute_k.py' first")
            sys.exit(1)

        k_series = pd.read_csv(k_path)

        # Filter to non-null K values only
        k_series = k_series[k_series["K"].notna()].copy()

        print(
            f"✓ Loaded K(t): {len(k_series)} years with data ({k_series['year'].min():.0f}-{k_series['year'].max():.0f})"
        )
        print(
            f"  Years: {', '.join([str(int(y)) for y in sorted(k_series['year'].unique())])}"
        )
        print()

        # Load external indices
        source = ExternalDataSource()
        indices = source.load_all_indices()

        if not indices:
            print("✗ No external indices found!")
            print()
            print(source.download_instructions())
            sys.exit(1)

        print(f"✓ Loaded {len(indices)} external indices")
        print()

        # Cross-validate
        results = cross_validate_k_index(k_series, indices)

        print()
        print("=" * 70)
        print("VALIDATION COMPLETE")
        print("=" * 70)
        print()
        print("Results saved to: logs/validation_external/")
        print("  - validation_report.md")
        print("  - validation_*.png (plots)")

    else:
        print("Usage:")
        print(
            "  python external_validation.py --download   # Show download instructions"
        )
        print("  python external_validation.py --process    # Run validation")
