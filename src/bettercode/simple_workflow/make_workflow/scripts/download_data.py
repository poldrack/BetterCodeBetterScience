#!/usr/bin/env python3
"""Download data files.

Usage:
    python download_data.py <data_dir>
"""

import sys
from pathlib import Path

import pandas as pd

MV_URL = "https://raw.githubusercontent.com/IanEisenberg/Self_Regulation_Ontology/refs/heads/master/Data/Complete_02-16-2019/meaningful_variables_clean.csv"
DEMO_URL = "https://raw.githubusercontent.com/IanEisenberg/Self_Regulation_Ontology/refs/heads/master/Data/Complete_02-16-2019/demographics.csv"


def main():
    """Download both data files."""
    if len(sys.argv) != 2:
        print("Usage: python download_data.py <data_dir>")
        sys.exit(1)

    data_dir = Path(sys.argv[1])

    # Download meaningful variables
    mv_df = pd.read_csv(MV_URL, index_col=0)
    mv_df.to_csv(data_dir / "meaningful_variables.csv")
    print(f"Downloaded meaningful_variables.csv ({len(mv_df)} rows)")

    # Download demographics
    demo_df = pd.read_csv(DEMO_URL, index_col=0)
    demo_df.to_csv(data_dir / "demographics.csv")
    print(f"Downloaded demographics.csv ({len(demo_df)} rows)")


if __name__ == "__main__":
    main()
