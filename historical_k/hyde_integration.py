#!/usr/bin/env python3
"""
HYDE 3.2 Historical Population & Land Use Integration (PRODUCTION)

This module provides real integration with the History Database of the Global Environment (HYDE 3.2)
for historical demographics and land use data (10,000 BCE - 2020 CE).

Data Source: https://doi.org/10.17026/dans-25g-gez3
Citation: Klein Goldewijk, K., Beusen, A., Doelman, J., & Stehfest, E. (2017).
          Anthropogenic land use estimates for the Holocene – HYDE 3.2.
          Earth System Science Data, 9(2), 927-953.
          https://doi.org/10.5194/essd-9-927-2017

HOW TO OBTAIN HYDE 3.2 DATA:
============================

Option 1: DANS EASY Archive (Recommended)
-----------------------------------------
1. Visit: https://easy.dans.knaw.nl/ui/datasets/id/easy-dataset:74466
2. Download: "HYDE 3.2 baseline" dataset (~2 GB compressed)
3. Extract to: data/sources/hyde/raw/
4. Required files:
   - population/ (global population grids)
   - cropland/ (agricultural land use)
   - pasture/ (grazing land use)
   - urban/ (urban extent)

File Structure:
- Files are NetCDF format (.nc) or ASCII grids (.asc)
- Spatial resolution: 5 arc-minute (~10km at equator)
- Temporal resolution: Varies (1000-year to 10-year intervals)
- Coverage: 10,000 BCE to 2020 CE

Option 2: PBL Netherlands Website
---------------------------------
1. Visit: https://themasites.pbl.nl/tridion/en/themasites/hyde/
2. Download individual variable datasets
3. Same file structure as Option 1

Variables Available:
====================

Population:
- popc: Total population count per grid cell
- popd: Population density (people/km²)

Land Use:
- cropland: Fraction of grid cell used for crops
- grazing: Fraction of grid cell used for pasture
- urban: Urban extent (fraction of grid cell)
- rangeland: Rangeland extent

Derived Metrics:
- Total global population (sum of all cells)
- Agricultural intensity (cropland + pasture fractions)
- Urbanization rate (urban fraction)
- Land use intensity (total modified land)

For K(t) Computation:
====================
We aggregate global metrics:
1. Total population → Interconnection harmony
2. Agricultural land → Reciprocity harmony (resource management)
3. Urbanization → Flourishing harmony (social complexity)
4. Land use intensity → Wisdom harmony (environmental impact)
"""

import gzip
import logging
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import requests

try:
    import netCDF4 as nc

    NETCDF_AVAILABLE = True
except ImportError:
    NETCDF_AVAILABLE = False
    logging.warning("netCDF4 not available. Install with: pip install netCDF4")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HYDEDataSource:
    """Interface to HYDE 3.2 Historical Demographics Database."""

    def __init__(self, data_dir: str = "data/sources/hyde"):
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        self.cache_dir = self.data_dir / "cache"

        # Create directories
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Detect data format (NetCDF organized by variable, or ASC organized by time period)
        self.asc_dir = self.raw_dir / "asc"
        self.has_asc_format = self.asc_dir.exists()

        if self.has_asc_format:
            logger.info("Detected ASC format (organized by time period)")
        else:
            logger.info("Looking for NetCDF format (organized by variable)")

        # HYDE time periods and their BCE/CE years
        self.time_periods = self._define_time_periods()

    def _define_time_periods(self) -> pd.DataFrame:
        """Define HYDE 3.2 time periods with corresponding years."""
        # HYDE uses BP (Before Present, 1950 CE) and CE notation
        periods = []

        # Ancient period: 10,000 BCE to 0 CE (1000-year intervals)
        for year in range(-10000, 0, 1000):
            periods.append(
                {
                    "year": year,
                    "hyde_year": year,
                    "period": "ancient",
                    "granularity": 1000,
                }
            )

        # Medieval period: 0 CE to 1700 CE (100-year intervals)
        for year in range(0, 1700, 100):
            periods.append(
                {
                    "year": year,
                    "hyde_year": year,
                    "period": "medieval",
                    "granularity": 100,
                }
            )

        # Early modern: 1700 to 1950 (10-year intervals)
        for year in range(1700, 1950, 10):
            periods.append(
                {
                    "year": year,
                    "hyde_year": year,
                    "period": "early_modern",
                    "granularity": 10,
                }
            )

        # Modern: 1950 to 2020 (1-year intervals)
        for year in range(1950, 2021, 1):
            periods.append(
                {"year": year, "hyde_year": year, "period": "modern", "granularity": 1}
            )

        return pd.DataFrame(periods)

    def check_data_availability(self) -> Dict[str, Dict[str, bool]]:
        """Check which HYDE datasets are available locally."""
        variables = ["population", "cropland", "grazing", "urban"]
        availability = {}

        if self.has_asc_format:
            # ASC format: check time period directories
            for var in variables:
                available_years = self.list_available_years(var)
                availability[var] = {
                    "directory_exists": self.asc_dir.exists(),
                    "has_files": len(available_years) > 0,
                    "file_count": len(available_years),
                    "format": "ASC",
                }
        else:
            # NetCDF format: check variable directories
            for var in variables:
                var_dir = self.raw_dir / var
                availability[var] = {
                    "directory_exists": var_dir.exists(),
                    "has_files": False,
                    "file_count": 0,
                    "format": "NetCDF",
                }

                if var_dir.exists():
                    files = list(var_dir.glob("*"))
                    availability[var]["has_files"] = len(files) > 0
                    availability[var]["file_count"] = len(files)

        return availability

    def download_instructions(self) -> str:
        """Return detailed download instructions."""
        instructions = """
=============================================================================
                        HYDE 3.2 Download Instructions
=============================================================================

HYDE 3.2 is a ~2 GB dataset that must be downloaded manually due to size
and access requirements.

STEP 1: Download the Dataset
----------------------------
Visit: https://doi.org/10.17026/dans-25g-gez3

Click "Download" to get the complete HYDE 3.2 baseline dataset.
File: HYDE3.2_baseline.zip (~2 GB)

Alternative: https://themasites.pbl.nl/tridion/en/themasites/hyde/

STEP 2: Extract Files
---------------------
Extract the ZIP file to: {data_dir}/raw/

Expected directory structure:
{data_dir}/raw/
    ├── population/
    │   ├── popc_-10000BC.nc
    │   ├── popc_-9000BC.nc
    │   ├── ...
    │   └── popc_2020AD.nc
    ├── cropland/
    │   ├── cropland_-10000BC.nc
    │   └── ...
    ├── grazing/
    │   ├── grazing_-10000BC.nc
    │   └── ...
    └── urban/
        ├── urban_-10000BC.nc
        └── ...

STEP 3: Verify Installation
---------------------------
Run: python hyde_integration.py --check

This will verify all required files are present.

STEP 4: Process Data
--------------------
Run: python hyde_integration.py --process

This will:
1. Load NetCDF files
2. Aggregate to global metrics
3. Save processed CSV files
4. Cache results for fast access

=============================================================================
""".format(
            data_dir=self.data_dir
        )
        return instructions

    def list_available_years(self, variable: str = "population") -> List[int]:
        """List years available for a given variable."""
        years = []

        if self.has_asc_format:
            # ASC format: organized by time period (e.g., 2000AD_pop/, 2000AD_lu/)
            # Determine which suffix to look for based on variable
            if variable in ["population"]:
                suffix = "_pop"
            else:  # cropland, grazing, pasture, urban
                suffix = "_lu"

            # Scan for time period directories
            for dir_path in self.asc_dir.glob(f"*{suffix}"):
                try:
                    # Extract year from directory name (e.g., "2000AD_pop" -> 2000)
                    dir_name = dir_path.name
                    year_str = dir_name.replace(suffix, "")

                    if "BC" in year_str:
                        year = -int(year_str.replace("BC", ""))
                    elif "AD" in year_str:
                        year = int(year_str.replace("AD", ""))
                    else:
                        year = int(year_str)

                    years.append(year)
                except ValueError:
                    continue

        else:
            # NetCDF format: organized by variable (population/, cropland/, etc.)
            var_dir = self.raw_dir / variable

            if not var_dir.exists():
                return []

            # Parse years from filenames (e.g., popc_1000AD.nc -> 1000)
            for filepath in var_dir.glob("*.nc"):
                try:
                    # Extract year from filename
                    filename = filepath.stem
                    year_str = filename.split("_")[-1]

                    if "BC" in year_str:
                        year = -int(year_str.replace("BC", ""))
                    elif "AD" in year_str:
                        year = int(year_str.replace("AD", ""))
                    else:
                        year = int(year_str)

                    years.append(year)
                except ValueError:
                    continue

        return sorted(years)

    def load_netcdf_global_sum(
        self, filepath: Path, variable: str = "population"
    ) -> float:
        """
        Load NetCDF file and compute global sum.

        Args:
            filepath: Path to NetCDF file
            variable: Variable name in NetCDF file

        Returns:
            Global sum of the variable
        """
        if not NETCDF_AVAILABLE:
            raise ImportError(
                "netCDF4 required to load HYDE data. "
                "Install with: pip install netCDF4"
            )

        try:
            dataset = nc.Dataset(filepath, "r")

            # Try common variable names
            var_names = [
                variable,
                variable + "c",
                variable + "d",
                "popc",
                "popd",
                "data",
                "Band1",
            ]

            data = None
            for var_name in var_names:
                if var_name in dataset.variables:
                    data = dataset.variables[var_name][:]
                    break

            if data is None:
                raise ValueError(f"Could not find variable in {filepath}")

            # Compute global sum (ignoring NaN/missing)
            global_sum = np.nansum(data)

            dataset.close()
            return float(global_sum)

        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
            return np.nan

    def load_netcdf_global_mean(
        self, filepath: Path, variable: str = "cropland"
    ) -> float:
        """Load NetCDF and compute global mean (for fractions like cropland)."""
        if not NETCDF_AVAILABLE:
            return np.nan

        try:
            dataset = nc.Dataset(filepath, "r")

            var_names = [variable, "data", "Band1"]
            data = None
            for var_name in var_names:
                if var_name in dataset.variables:
                    data = dataset.variables[var_name][:]
                    break

            if data is None:
                raise ValueError(f"Could not find variable in {filepath}")

            # Compute global mean
            global_mean = np.nanmean(data)

            dataset.close()
            return float(global_mean)

        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
            return np.nan

    def load_asc_file(self, filepath: Path, aggregation: str = "sum") -> float:
        """
        Load ASCII raster (.asc) file and compute global aggregate.

        ASC Format:
        ncols         4320
        nrows         2160
        xllcorner     -180.0
        yllcorner     -90.0
        cellsize      0.0833333
        NODATA_value  -9999.0
        <data values row by row>

        Args:
            filepath: Path to .asc file
            aggregation: 'sum' for totals, 'mean' for fractions

        Returns:
            Global sum or mean of the variable
        """
        try:
            with open(filepath, "r") as f:
                # Read header (6 lines)
                header = {}
                for _ in range(6):
                    line = f.readline().strip().split()
                    if len(line) == 2:
                        header[line[0]] = float(line[1])

                # Get NODATA value
                nodata = header.get("NODATA_value", -9999.0)

                # Read data values
                data = []
                for line in f:
                    values = [float(x) for x in line.strip().split()]
                    data.extend(values)

            # Convert to numpy array
            data = np.array(data)

            # Replace NODATA with NaN
            data[data == nodata] = np.nan

            # Compute aggregate
            if aggregation == "sum":
                result = np.nansum(data)
            else:
                result = np.nanmean(data)

            return float(result)

        except Exception as e:
            logger.error(f"Error loading ASC file {filepath}: {e}")
            return np.nan

    def extract_time_series(
        self,
        variable: str,
        start_year: int = -3000,
        end_year: int = 2020,
        aggregation: str = "sum",
    ) -> pd.DataFrame:
        """
        Extract time series for a variable across available years.

        Args:
            variable: Variable name (population, cropland, grazing, urban)
            start_year: Start year (negative for BCE)
            end_year: End year
            aggregation: 'sum' for totals, 'mean' for fractions

        Returns:
            DataFrame with year and aggregated values
        """
        available_years = self.list_available_years(variable)
        logger.info(f"Found {len(available_years)} years for {variable}")

        # Filter to requested range
        years_in_range = [y for y in available_years if start_year <= y <= end_year]

        if not years_in_range:
            logger.warning(
                f"No data available for {variable} in range {start_year}-{end_year}"
            )
            return pd.DataFrame()

        results = []
        for year in years_in_range:
            filepath = None

            if self.has_asc_format:
                # ASC format: files in time period directories
                # Construct directory name
                if year < 0:
                    year_str = f"{abs(year)}BC"
                else:
                    year_str = f"{year}AD"

                # Determine subdirectory and file pattern
                if variable == "population":
                    time_dir = self.asc_dir / f"{year_str}_pop"
                    file_pattern = f"popc_{year_str}.asc"
                elif variable == "cropland":
                    time_dir = self.asc_dir / f"{year_str}_lu"
                    file_pattern = f"cropland*.asc"
                elif variable == "grazing":
                    time_dir = self.asc_dir / f"{year_str}_lu"
                    file_pattern = f"pasture*.asc"  # HYDE uses "pasture" for grazing
                elif variable == "urban":
                    time_dir = self.asc_dir / f"{year_str}_lu"
                    file_pattern = f"uopp_{year_str}.asc"  # Urban population percentage
                else:
                    time_dir = self.asc_dir / f"{year_str}_lu"
                    file_pattern = f"{variable}*.asc"

                # Find file
                if time_dir.exists():
                    filepaths = list(time_dir.glob(file_pattern))
                    if filepaths:
                        filepath = filepaths[0]

                # Load ASC file
                if filepath:
                    value = self.load_asc_file(filepath, aggregation)

            else:
                # NetCDF format: files organized by variable
                var_dir = self.raw_dir / variable

                if not var_dir.exists():
                    logger.warning(f"Variable directory not found: {var_dir}")
                    logger.info(self.download_instructions())
                    return pd.DataFrame()

                # Construct filename (handle BC/AD notation)
                if year < 0:
                    filename = f"*_{abs(year)}BC.nc"
                else:
                    filename = f"*_{year}AD.nc"

                filepaths = list(var_dir.glob(filename))

                if not filepaths:
                    # Try without BC/AD suffix
                    filename = f"*_{abs(year)}.nc"
                    filepaths = list(var_dir.glob(filename))

                if filepaths:
                    filepath = filepaths[0]

                    # Aggregate based on type
                    if aggregation == "sum":
                        value = self.load_netcdf_global_sum(filepath, variable)
                    else:
                        value = self.load_netcdf_global_mean(filepath, variable)

            if filepath:
                results.append({"year": year, variable: value})

                logger.debug(f"{year}: {value:.2e}")

        df = pd.DataFrame(results)
        logger.info(f"Extracted {len(df)} records for {variable}")

        return df

    def compute_aggregated_metrics(
        self, start_year: int = -3000, end_year: int = 2020
    ) -> pd.DataFrame:
        """
        Compute all HYDE metrics for K(t) computation.

        Args:
            start_year: Start year (negative for BCE)
            end_year: End year

        Returns:
            DataFrame with year and all demographic/land use metrics
        """
        logger.info("Extracting HYDE time series...")

        # Extract each variable
        population = self.extract_time_series("population", start_year, end_year, "sum")
        cropland = self.extract_time_series("cropland", start_year, end_year, "mean")
        grazing = self.extract_time_series("grazing", start_year, end_year, "mean")
        urban = self.extract_time_series("urban", start_year, end_year, "mean")

        # Merge all time series on year
        dfs = [
            df.set_index("year")
            for df in [population, cropland, grazing, urban]
            if not df.empty
        ]

        if not dfs:
            logger.error("No HYDE data could be loaded!")
            logger.info(self.download_instructions())
            return pd.DataFrame()

        result = pd.concat(dfs, axis=1).reset_index()

        # Compute derived metrics
        if "population" in result.columns:
            result["log_population"] = np.log10(result["population"] + 1)

        if "cropland" in result.columns and "grazing" in result.columns:
            result["agricultural_fraction"] = result["cropland"] + result["grazing"]

        if "urban" in result.columns:
            result["urbanization_rate"] = result["urban"]

        # Normalize to [0, 1] for K(t) computation
        for col in result.columns:
            if col != "year":
                min_val = result[col].min()
                max_val = result[col].max()
                if max_val > min_val:
                    result[f"{col}_normalized"] = (result[col] - min_val) / (
                        max_val - min_val
                    )

        logger.info(f"Computed metrics for {len(result)} time periods")

        # Save processed data
        output_path = (
            self.processed_dir / f"hyde_aggregated_{start_year}_{end_year}.csv"
        )
        result.to_csv(output_path, index=False)
        logger.info(f"✓ Saved processed data to {output_path}")

        return result


def fetch_hyde_data(
    start_year: int = -3000, end_year: int = 2020, output_dir: str = "data/sources/hyde"
) -> pd.DataFrame:
    """
    Main interface function for fetching HYDE 3.2 data.

    This function handles the complete workflow:
    1. Check for local HYDE installation
    2. Provide download instructions if needed
    3. Process NetCDF files
    4. Aggregate to global metrics
    5. Return processed DataFrame

    Args:
        start_year: Start year (negative for BCE)
        end_year: End year
        output_dir: Output directory for processed data

    Returns:
        DataFrame with demographic and land use metrics for K(t) computation
    """
    hyde = HYDEDataSource(output_dir)

    # Check availability
    availability = hyde.check_data_availability()
    logger.info(f"HYDE data availability: {availability}")

    # Check if any data is available
    has_data = any(v["has_files"] for v in availability.values())

    if not has_data:
        logger.warning("No HYDE data found locally!")
        print(hyde.download_instructions())
        raise FileNotFoundError(
            "HYDE 3.2 data not found. Please download following instructions above."
        )

    # Compute aggregated metrics
    logger.info("Computing aggregated HYDE metrics...")
    data = hyde.compute_aggregated_metrics(start_year, end_year)

    if data.empty:
        raise ValueError("Failed to extract HYDE data. Check logs for errors.")

    return data


if __name__ == "__main__":
    import sys

    print("=" * 70)
    print("HYDE 3.2 Historical Demographics Integration")
    print("=" * 70)
    print()

    if "--check" in sys.argv:
        hyde = HYDEDataSource()
        availability = hyde.check_data_availability()

        print("Data availability check:")
        for var, status in availability.items():
            symbol = "✓" if status["has_files"] else "✗"
            print(f"  {symbol} {var}: {status['file_count']} files")

        if not any(v["has_files"] for v in availability.values()):
            print()
            print(hyde.download_instructions())

    elif "--process" in sys.argv:
        print("Processing HYDE data...")
        print()

        try:
            data = fetch_hyde_data(
                start_year=-3000, end_year=2020, output_dir="data/sources/hyde"
            )

            print()
            print("✓ SUCCESS!")
            print(f"  Processed {len(data)} time periods")
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

    else:
        print("Usage:")
        print("  python hyde_integration.py --check     # Check data availability")
        print("  python hyde_integration.py --process   # Process HYDE data")
        print()
        print("First time setup:")
        print("1. Download HYDE 3.2 from: https://doi.org/10.17026/dans-25g-gez3")
        print("2. Extract to: data/sources/hyde/raw/")
        print("3. Run: python hyde_integration.py --check")
        print("4. Run: python hyde_integration.py --process")
