#!/usr/bin/env python3
"""
H7 Data Acquisition Script
Downloads all datasets needed for H7 reconstruction:
- Energy: BP Statistical Review, Smil data
- Technology: Economic Complexity Index, USPTO patents
- Institutions: Polity V, V-Dem
- Computation: Nordhaus computing power
- Knowledge: Publication data
"""

import requests
import pandas as pd
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Data directory
DATA_DIR = Path("data_sources")
DATA_DIR.mkdir(exist_ok=True)

# Dataset URLs and metadata
DATASETS = {
    "energy": {
        "bp_statistical_review": {
            "url": "https://www.bp.com/content/dam/bp/business-sites/en/global/corporate/xlsx/energy-economics/statistical-review/bp-stats-review-2023-all-data.xlsx",
            "desc": "BP Statistical Review of World Energy (1965-2023)",
            "output": "h7_energy/bp_statistical_review_2023.xlsx"
        },
        "smil_energy": {
            "url": None,  # Requires manual download or academic access
            "desc": "Vaclav Smil - Energy Transitions: Global and National Perspectives (1800-1965)",
            "output": "h7_energy/smil_energy_historical.csv",
            "note": "Manual download required from: https://vaclavsmil.com/energy-transitions/"
        }
    },
    "technology": {
        "economic_complexity": {
            "url": "https://intl-atlas-downloads.s3.amazonaws.com/ECI/country_eci_rank.csv",
            "desc": "Economic Complexity Index - Harvard Growth Lab (1962-2020)",
            "output": "h7_tech/eci_country_ranks.csv"
        },
        "uspto_patents": {
            "url": "https://www.uspto.gov/web/offices/ac/ido/oeip/taf/h_counts.htm",
            "desc": "USPTO Patent Counts by Year (1963-2023)",
            "output": "h7_tech/uspto_patent_counts.html",
            "note": "HTML table - will need parsing"
        }
    },
    "institutions": {
        "polity5": {
            "url": "http://www.systemicpeace.org/inscr/p5v2018.xls",
            "desc": "Polity V Dataset (1800-2018)",
            "output": "h7_institutions/polity5_2018.xls"
        },
        "vdem": {
            "url": "https://v-dem.net/static/website/img/refs/vdemds_v14.csv",
            "desc": "V-Dem Democracy Indicators v14 (1789-2023)",
            "output": "h7_institutions/vdem_v14.csv",
            "note": "Large file (~500MB), may need background download"
        }
    },
    "computation": {
        "nordhaus_computing": {
            "url": None,  # Academic paper data
            "desc": "Nordhaus (2007) - Two Centuries of Computing Power",
            "output": "h7_computation/nordhaus_2007_computing.csv",
            "note": "Data from paper Table 1 - will need manual entry or OCR"
        }
    },
    "knowledge": {
        "unesco_publications": {
            "url": None,  # Requires UIS API access
            "desc": "UNESCO Institute for Statistics - Scientific Publications",
            "output": "h7_knowledge/unesco_publications.csv",
            "note": "Requires API access: http://data.uis.unesco.org/"
        }
    }
}


def download_file(url, output_path, description):
    """Download a file with progress tracking."""
    output_file = DATA_DIR / output_path
    output_file.parent.mkdir(parents=True, exist_ok=True)

    if output_file.exists():
        logger.info(f"✅ Already exists: {output_path}")
        return True

    if url is None:
        logger.warning(f"⚠️  Manual download required: {description}")
        logger.warning(f"   Output path: {output_file}")
        return False

    try:
        logger.info(f"⬇️  Downloading: {description}")
        logger.info(f"   URL: {url}")

        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        # Get file size if available
        total_size = int(response.headers.get('content-length', 0))

        with open(output_file, 'wb') as f:
            if total_size == 0:
                f.write(response.content)
            else:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        logger.info(f"   Progress: {percent:.1f}%")

        logger.info(f"✅ Downloaded: {output_path}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to download {description}: {e}")
        return False


def download_all_datasets():
    """Download all H7 datasets."""
    logger.info("=" * 80)
    logger.info("H7 DATA ACQUISITION - Week 1, Days 1-2")
    logger.info("=" * 80)

    results = {"success": [], "manual": [], "failed": []}

    for category, datasets in DATASETS.items():
        logger.info(f"\n📂 Category: {category.upper()}")
        logger.info("-" * 80)

        for dataset_name, info in datasets.items():
            desc = info["desc"]
            url = info["url"]
            output = info["output"]
            note = info.get("note", "")

            if note:
                logger.info(f"📝 Note: {note}")

            success = download_file(url, output, desc)

            if success:
                results["success"].append(dataset_name)
            elif url is None:
                results["manual"].append(dataset_name)
            else:
                results["failed"].append(dataset_name)

    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("DOWNLOAD SUMMARY")
    logger.info("=" * 80)
    logger.info(f"✅ Successfully downloaded: {len(results['success'])}")
    for name in results["success"]:
        logger.info(f"   - {name}")

    logger.info(f"\n⚠️  Require manual download: {len(results['manual'])}")
    for name in results["manual"]:
        logger.info(f"   - {name}")

    if results["failed"]:
        logger.info(f"\n❌ Failed downloads: {len(results['failed'])}")
        for name in results["failed"]:
            logger.info(f"   - {name}")

    return results


def create_manual_download_guide():
    """Create a guide for manual downloads."""
    guide_path = DATA_DIR / "MANUAL_DOWNLOAD_GUIDE.md"

    with open(guide_path, 'w') as f:
        f.write("# Manual Download Guide for H7 Data\n\n")
        f.write("Some datasets require manual download due to access restrictions.\n\n")

        for category, datasets in DATASETS.items():
            manual_datasets = {k: v for k, v in datasets.items() if v["url"] is None}

            if manual_datasets:
                f.write(f"\n## {category.upper()}\n\n")

                for dataset_name, info in manual_datasets.items():
                    f.write(f"### {dataset_name}\n")
                    f.write(f"- **Description**: {info['desc']}\n")
                    f.write(f"- **Save to**: `{info['output']}`\n")
                    f.write(f"- **Note**: {info.get('note', 'N/A')}\n\n")

    logger.info(f"📝 Manual download guide created: {guide_path}")


if __name__ == "__main__":
    # Download all datasets
    results = download_all_datasets()

    # Create manual download guide
    create_manual_download_guide()

    logger.info("\n✨ Data acquisition script complete!")
    logger.info(f"📁 All data saved to: {DATA_DIR.absolute()}")

    # Next steps
    logger.info("\n📋 NEXT STEPS:")
    logger.info("1. Complete any manual downloads (see MANUAL_DOWNLOAD_GUIDE.md)")
    logger.info("2. Run data processing scripts (Week 1, Days 3-4)")
    logger.info("3. Construct H7 composite index (Week 1, Day 5)")
