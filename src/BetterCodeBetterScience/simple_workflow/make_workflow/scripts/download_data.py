#!/usr/bin/env python3
"""Download data from URL and save to CSV.

Usage:
    python download_data.py <url> <output_path>
"""

import sys
from pathlib import Path

import pandas as pd


def main():
    """Download data from URL."""
    if len(sys.argv) != 3:
        print("Usage: python download_data.py <url> <output_path>")
        sys.exit(1)

    url = sys.argv[1]
    output_path = Path(sys.argv[2])

    # Create output directory
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Download and save
    df = pd.read_csv(url, index_col=0)
    df.to_csv(output_path)

    print(f"Downloaded {len(df)} rows from {url}")
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()
