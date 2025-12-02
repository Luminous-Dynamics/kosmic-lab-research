#!/usr/bin/env python3
"""
Process USPTO Patent Data for H7 Technology Component

Parses HTML table of USPTO patent counts, creates annual time series
for 1963-2023, and normalizes to 0-1 scale.

Input: data_sources/h7_tech/uspto_patent_counts.html (49 KB)
Output: data_sources/processed/h7_tech_1963_2023.csv
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
import re

def process_tech_data():
    """Process USPTO patent data to normalized annual time series."""

    # Define paths (relative to historical_k directory)
    script_dir = Path(__file__).parent
    input_path = script_dir / 'data_sources/h7_tech/uspto_patent_counts.html'
    output_path = script_dir / 'data_sources/processed/h7_tech_1963_2023.csv'

    print("=" * 60)
    print("H7 Technology Component Processing")
    print("=" * 60)
    print()

    # Check input file exists
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        sys.exit(1)

    print(f"Loading USPTO patent data from {input_path}...")
    with open(input_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    print(f"  File size: {len(html_content)} bytes")
    print()

    # Parse HTML using regex (no BeautifulSoup needed)
    print("Parsing HTML content with regex...")

    # Find table rows with <tr> tags
    tr_pattern = r'<tr[^>]*>(.*?)</tr>'
    tr_matches = re.findall(tr_pattern, html_content, re.DOTALL | re.IGNORECASE)
    print(f"  Found {len(tr_matches)} table rows")

    # Parse rows
    patent_data = []
    for i, row_content in enumerate(tr_matches):
        # Extract all <td> or <th> cells
        cell_pattern = r'<t[dh][^>]*>(.*?)</t[dh]>'
        cells = re.findall(cell_pattern, row_content, re.DOTALL | re.IGNORECASE)

        if len(cells) < 2:
            continue

        # Clean HTML tags from cell content
        cell_texts = []
        for cell in cells:
            # Remove HTML tags
            clean_text = re.sub(r'<[^>]+>', '', cell).strip()
            cell_texts.append(clean_text)

        # Skip header rows
        if 'Year' in cell_texts[0] or 'Calendar' in cell_texts[0]:
            continue

        # Extract year and count
        try:
            year_text = cell_texts[0]
            count_text = cell_texts[1]

            # Clean year (handle ranges like "1963-1992", take first year)
            year_match = re.search(r'(\d{4})', year_text)
            if not year_match:
                continue
            year = int(year_match.group(1))

            # Clean count (remove commas, handle footnotes)
            count_clean = re.sub(r'[^\d]', '', count_text)
            if not count_clean:
                continue
            count = int(count_clean)

            patent_data.append({'year': year, 'patents': count})

        except (ValueError, IndexError) as e:
            # Silently skip problematic rows
            continue

    print(f"  Extracted {len(patent_data)} data points")
    print()

    # Convert to DataFrame
    patents_df = pd.DataFrame(patent_data)

    # Check for duplicates (some years might appear multiple times)
    if patents_df['year'].duplicated().any():
        print("  Warning: Duplicate years found, keeping first occurrence")
        patents_df = patents_df.drop_duplicates(subset='year', keep='first')

    # Sort by year
    patents_df = patents_df.sort_values('year').reset_index(drop=True)

    print(f"Year range: {patents_df['year'].min()} - {patents_df['year'].max()}")
    print(f"Total years: {len(patents_df)}")
    print()

    # Display sample
    print("Sample raw data:")
    print(patents_df.head(10).to_string(index=False))
    print()

    # Normalize to 0-1 scale
    print("Normalizing to 0-1 scale...")
    min_val = patents_df['patents'].min()
    max_val = patents_df['patents'].max()

    print(f"  Min patents: {min_val:,}")
    print(f"  Max patents: {max_val:,}")
    print(f"  Range: {max_val - min_val:,}")

    patents_df['tech_normalized'] = (patents_df['patents'] - min_val) / (max_val - min_val)

    # Verify normalization
    norm_min = patents_df['tech_normalized'].min()
    norm_max = patents_df['tech_normalized'].max()
    print(f"  Normalized min: {norm_min:.6f}")
    print(f"  Normalized max: {norm_max:.6f}")
    print()

    # Create output dataframe
    output_df = patents_df[['year', 'patents', 'tech_normalized']].copy()
    output_df = output_df.rename(columns={
        'patents': 'patent_count',
        'tech_normalized': 'h7_tech_component'
    })

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save processed data
    print(f"Saving processed data to {output_path}...")
    output_df.to_csv(output_path, index=False)
    print(f"  File size: {output_path.stat().st_size / 1024:.1f} KB")
    print()

    # Display sample data
    print("Sample of processed data:")
    print("=" * 60)

    # Show first 5 rows
    print("\nFirst 5 years:")
    print(output_df.head().to_string(index=False))

    # Show last 5 rows
    print("\nLast 5 years:")
    print(output_df.tail().to_string(index=False))

    # Show some key years
    key_years = [1970, 1980, 1990, 2000, 2010, 2020]
    print("\nKey years:")
    for year in key_years:
        row = output_df[output_df['year'] == year]
        if not row.empty:
            print(f"  {year}: {row['patent_count'].values[0]:,} patents → {row['h7_tech_component'].values[0]:.6f}")

    print()
    print("=" * 60)
    print("✅ Technology data processing COMPLETE")
    print(f"✅ Output: {output_path}")
    print(f"✅ Coverage: {len(output_df)} years ({output_df['year'].min()}-{output_df['year'].max()})")
    print("=" * 60)

    return output_df

if __name__ == '__main__':
    try:
        result = process_tech_data()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
