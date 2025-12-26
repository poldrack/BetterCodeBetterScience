#!/usr/bin/env python3
"""Filter dataframes to numerical columns only.

Usage:
    python filter_data.py <data_dir>
"""

import sys
from pathlib import Path

import pandas as pd

from BetterCodeBetterScience.simple_workflow.filter_data import (
    filter_numerical_columns,
)


def main():
    """Filter both datasets to numerical columns."""
    if len(sys.argv) != 2:
        print("Usage: python filter_data.py <data_dir>")
        sys.exit(1)

    data_dir = Path(sys.argv[1])

    # Filter meaningful variables
    mv_df = pd.read_csv(data_dir / "meaningful_variables.csv", index_col=0)
    mv_num = filter_numerical_columns(mv_df)
    mv_num.to_csv(data_dir / "meaningful_variables_numerical.csv")
    print(f"Filtered meaningful_variables: {mv_df.shape} -> {mv_num.shape}")

    # Filter demographics
    demo_df = pd.read_csv(data_dir / "demographics.csv", index_col=0)
    demo_num = filter_numerical_columns(demo_df)
    demo_num.to_csv(data_dir / "demographics_numerical.csv")
    print(f"Filtered demographics: {demo_df.shape} -> {demo_num.shape}")


if __name__ == "__main__":
    main()
