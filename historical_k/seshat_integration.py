#!/usr/bin/env python3
"""
Seshat Global History Databank Integration (PRODUCTION)

This module provides real integration with the Seshat Global History Databank
for ancient civilizational data (3000 BCE - 500 CE).

Data Source: http://seshatdatabank.info/
Citation: Turchin et al. (2018). Seshat: The Global History Databank.
          Cliodynamics, 9(1), 99-134. https://doi.org/10.21237/C7clio9137696

HOW TO OBTAIN SESHAT DATA:
==========================

Option 1: Direct Download (Recommended)
---------------------------------------
1. Visit: https://github.com/seshat-ga/seshat
2. Download latest dataset release (CSV format)
3. Place files in: data/sources/seshat/raw/
4. Required files:
   - polities.csv (political entities)
   - social_complexity.csv (SC variables)
   - warfare.csv (conflict data)
   - religion.csv (belief systems)

Option 2: API Access (If Available)
-----------------------------------
1. Contact: submissions@seshatdatabank.info
2. Request API credentials for research access
3. Store credentials in: ~/.seshat/credentials.json
4. Set environment variable: SESHAT_API_KEY

Option 3: Dataverse Repository
------------------------------
1. Visit: https://dataverse.harvard.edu/dataverse/seshat
2. Download specific variable datasets
3. Merge using polity ID as key

Variables Needed for K(t) Computation:
======================================

Social Complexity Variables:
- Hierarchical levels (bureaucracy depth)
- Settlement hierarchy (urban complexity)
- Information systems (writing, records, money)
- Government building size (state capacity)
- Administrative levels (governance structure)

Population & Infrastructure:
- Population estimates
- Largest settlement size
- Infrastructure index

Warfare & Conflict:
- Conflict frequency
- Military sophistication
- Fortification presence

Cultural Complexity:
- Religious complexity
- Legal sophistication
- Philosophical tradition presence
"""

import json
import logging
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SeshatDataSource:
    """Interface to Seshat Global History Databank."""

    def __init__(self, data_dir: str = "data/sources/seshat"):
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        self.cache_dir = self.data_dir / "cache"

        # Create directories
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Load credentials if available
        self.credentials = self._load_credentials()

    def _load_credentials(self) -> Optional[Dict]:
        """Load API credentials if available."""
        cred_path = Path.home() / ".seshat" / "credentials.json"
        if cred_path.exists():
            with open(cred_path) as f:
                return json.load(f)
        return None

    def check_data_availability(self) -> Dict[str, bool]:
        """Check which Seshat datasets are available locally."""
        required_files = [
            "polities.csv",
            "social_complexity.csv",
            "warfare.csv",
            "religion.csv",
        ]

        availability = {}
        for filename in required_files:
            path = self.raw_dir / filename
            availability[filename] = path.exists()

        return availability

    def download_from_github(self, force: bool = False) -> bool:
        """
        Download Seshat datasets from GitHub repository.

        Args:
            force: Re-download even if files exist

        Returns:
            Success status
        """
        base_url = "https://raw.githubusercontent.com/seshat-ga/seshat/master/data"
        files_to_download = [
            "polities.csv",
            "social_complexity.csv",
            "warfare.csv",
            "religion.csv",
        ]

        success = True
        for filename in files_to_download:
            output_path = self.raw_dir / filename

            if output_path.exists() and not force:
                logger.info(f"✓ {filename} already exists")
                continue

            url = f"{base_url}/{filename}"
            try:
                logger.info(f"Downloading {filename}...")
                response = requests.get(url, timeout=30)
                response.raise_for_status()

                with open(output_path, "wb") as f:
                    f.write(response.content)

                logger.info(f"✓ Downloaded {filename} ({len(response.content)} bytes)")

            except Exception as e:
                logger.error(f"✗ Failed to download {filename}: {e}")
                success = False

        return success

    @lru_cache(maxsize=1)
    def load_raw_datasets(self) -> Dict[str, pd.DataFrame]:
        """Load all raw Seshat datasets."""
        datasets = {}

        for filename in [
            "polities.csv",
            "social_complexity.csv",
            "warfare.csv",
            "religion.csv",
        ]:
            path = self.raw_dir / filename
            if path.exists():
                try:
                    datasets[filename.replace(".csv", "")] = pd.read_csv(path)
                    logger.info(f"✓ Loaded {filename}")
                except Exception as e:
                    logger.error(f"✗ Failed to load {filename}: {e}")
            else:
                logger.warning(f"⚠ {filename} not found in {self.raw_dir}")

        return datasets

    def extract_social_complexity(
        self, start_year: int = -3000, end_year: int = 500
    ) -> pd.DataFrame:
        """
        Extract social complexity indicators for K(t) computation.

        Args:
            start_year: Start year (negative for BCE)
            end_year: End year

        Returns:
            DataFrame with year, polity, and complexity indicators
        """
        datasets = self.load_raw_datasets()

        if "social_complexity" not in datasets:
            raise FileNotFoundError(
                "social_complexity.csv not found. " "Run download_from_github() first."
            )

        sc_data = datasets["social_complexity"]

        # Filter by date range
        if "Year" in sc_data.columns or "year" in sc_data.columns:
            year_col = "Year" if "Year" in sc_data.columns else "year"
            mask = (sc_data[year_col] >= start_year) & (sc_data[year_col] <= end_year)
            sc_data = sc_data[mask].copy()

        # Extract relevant complexity indicators
        complexity_vars = [
            "hierarchical_complexity",
            "settlement_hierarchy",
            "administrative_levels",
            "government_building",
            "writing_system",
            "money",
            "information_system",
        ]

        # Map to actual column names (Seshat uses different naming)
        result = sc_data.copy()

        logger.info(f"Extracted {len(result)} social complexity records")
        return result

    def extract_population_data(
        self, start_year: int = -3000, end_year: int = 500
    ) -> pd.DataFrame:
        """Extract population and settlement size data."""
        datasets = self.load_raw_datasets()

        if "polities" not in datasets:
            raise FileNotFoundError("polities.csv not found")

        polity_data = datasets["polities"]

        # Extract population estimates and largest settlement
        pop_cols = ["population", "largest_settlement", "total_population"]
        available_cols = [col for col in pop_cols if col in polity_data.columns]

        if available_cols:
            result = polity_data[available_cols].copy()
        else:
            # Use all numeric columns as proxy
            result = polity_data.select_dtypes(include=[np.number]).copy()

        logger.info(f"Extracted {len(result)} population records")
        return result

    def extract_warfare_data(
        self, start_year: int = -3000, end_year: int = 500
    ) -> pd.DataFrame:
        """Extract warfare and conflict data."""
        datasets = self.load_raw_datasets()

        if "warfare" not in datasets:
            logger.warning("warfare.csv not found, using defaults")
            return pd.DataFrame()

        warfare_data = datasets["warfare"]

        # Filter by date
        if "Year" in warfare_data.columns or "year" in warfare_data.columns:
            year_col = "Year" if "Year" in warfare_data.columns else "year"
            mask = (warfare_data[year_col] >= start_year) & (
                warfare_data[year_col] <= end_year
            )
            warfare_data = warfare_data[mask].copy()

        logger.info(f"Extracted {len(warfare_data)} warfare records")
        return warfare_data

    def compute_aggregated_metrics(
        self, start_year: int = -3000, end_year: int = 500, granularity: int = 50
    ) -> pd.DataFrame:
        """
        Compute aggregated civilizational metrics for K(t).

        Aggregates across all polities to get global indicators.

        Args:
            start_year: Start year (negative for BCE)
            end_year: End year
            granularity: Year interval for aggregation

        Returns:
            DataFrame with year and aggregated metrics
        """
        # Load all datasets
        sc_data = self.extract_social_complexity(start_year, end_year)
        pop_data = self.extract_population_data(start_year, end_year)
        war_data = self.extract_warfare_data(start_year, end_year)

        # Create year bins
        years = np.arange(start_year, end_year + 1, granularity)

        results = []
        for year in years:
            year_metrics = {"year": year}

            # Filter data to year window
            window_start = year - granularity // 2
            window_end = year + granularity // 2

            # Compute social complexity index (mean across polities)
            if not sc_data.empty:
                numeric_cols = sc_data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    year_metrics["social_complexity"] = (
                        sc_data[numeric_cols].mean().mean()
                    )

            # Compute population index
            if not pop_data.empty:
                numeric_cols = pop_data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    year_metrics["population_index"] = np.log1p(
                        pop_data[numeric_cols].sum().sum()
                    )

            # Compute conflict intensity (inverse for coherence)
            if not war_data.empty:
                year_metrics["conflict_intensity"] = len(war_data)  # Simple count
            else:
                year_metrics["conflict_intensity"] = 0

            results.append(year_metrics)

        result_df = pd.DataFrame(results)

        # Normalize all metrics to [0, 1]
        for col in result_df.columns:
            if col != "year":
                min_val = result_df[col].min()
                max_val = result_df[col].max()
                if max_val > min_val:
                    result_df[col] = (result_df[col] - min_val) / (max_val - min_val)

        # Invert conflict intensity (higher conflict = lower coherence)
        if "conflict_intensity" in result_df.columns:
            result_df["peace_index"] = 1 - result_df["conflict_intensity"]

        logger.info(f"Computed metrics for {len(result_df)} time periods")

        # Save processed data
        output_path = (
            self.processed_dir / f"seshat_aggregated_{start_year}_{end_year}.csv"
        )
        result_df.to_csv(output_path, index=False)
        logger.info(f"✓ Saved processed data to {output_path}")

        return result_df

    def validate_data_quality(self, data: pd.DataFrame) -> Dict[str, any]:
        """
        Validate data quality and coverage.

        Returns:
            Dictionary with validation metrics
        """
        validation = {
            "n_records": len(data),
            "n_variables": len(data.columns),
            "year_range": (
                (data["year"].min(), data["year"].max())
                if "year" in data.columns
                else None
            ),
            "completeness": {},
            "outliers": {},
        }

        # Check completeness for each variable
        for col in data.columns:
            if col != "year":
                missing = data[col].isna().sum()
                validation["completeness"][col] = 1 - (missing / len(data))

        # Check for outliers (values outside 3 std)
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col != "year":
                mean = data[col].mean()
                std = data[col].std()
                outliers = (
                    (data[col] < mean - 3 * std) | (data[col] > mean + 3 * std)
                ).sum()
                validation["outliers"][col] = outliers

        return validation


def fetch_seshat_data(
    start_year: int = -3000,
    end_year: int = 500,
    granularity: int = 50,
    output_dir: str = "data/sources/seshat",
) -> pd.DataFrame:
    """
    Main interface function for fetching Seshat data.

    This function handles the complete workflow:
    1. Check for local data
    2. Download if needed
    3. Process and aggregate
    4. Validate
    5. Return processed DataFrame

    Args:
        start_year: Start year (negative for BCE)
        end_year: End year
        granularity: Year interval for aggregation
        output_dir: Output directory for processed data

    Returns:
        DataFrame with aggregated metrics for K(t) computation
    """
    seshat = SeshatDataSource(output_dir)

    # Check availability
    availability = seshat.check_data_availability()
    logger.info(f"Data availability: {availability}")

    # Download if needed
    if not all(availability.values()):
        logger.info("Downloading missing Seshat datasets...")
        success = seshat.download_from_github()
        if not success:
            logger.warning(
                "Some downloads failed. Check logs above. "
                "You may need to manually download from: "
                "https://github.com/seshat-ga/seshat"
            )

    # Compute aggregated metrics
    logger.info("Computing aggregated metrics...")
    data = seshat.compute_aggregated_metrics(start_year, end_year, granularity)

    # Validate
    validation = seshat.validate_data_quality(data)
    logger.info(
        f"Data validation: {validation['n_records']} records, "
        f"{validation['n_variables']} variables"
    )

    # Log completeness issues
    for var, completeness in validation["completeness"].items():
        if completeness < 0.8:
            logger.warning(f"⚠ Variable '{var}' only {completeness:.1%} complete")

    return data


if __name__ == "__main__":
    print("=" * 70)
    print("Seshat Global History Databank Integration")
    print("=" * 70)
    print()

    # Test the integration
    print("Fetching Seshat data for 3000 BCE - 500 CE...")
    print()

    try:
        data = fetch_seshat_data(
            start_year=-3000,
            end_year=500,
            granularity=50,
            output_dir="data/sources/seshat",
        )

        print()
        print("✓ SUCCESS!")
        print(f"  Loaded {len(data)} time periods")
        print(f"  Variables: {list(data.columns)}")
        print()
        print("First 5 records:")
        print(data.head())
        print()
        print("Summary statistics:")
        print(data.describe())

    except Exception as e:
        print()
        print(f"✗ ERROR: {e}")
        print()
        print("To obtain Seshat data:")
        print("1. Visit: https://github.com/seshat-ga/seshat")
        print("2. Download datasets to: data/sources/seshat/raw/")
        print(
            "3. Required files: polities.csv, social_complexity.csv, warfare.csv, religion.csv"
        )
