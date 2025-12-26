#!/usr/bin/env python3
"""Join two dataframes based on their index.

Usage:
    python join_data.py <data_dir>
"""

import sys
from pathlib import Path

import pandas as pd

from BetterCodeBetterScience.simple_workflow.join_data import join_dataframes


def main():
    """Join the two datasets."""
    if len(sys.argv) != 2:
        print("Usage: python join_data.py <data_dir>")
        sys.exit(1)

    data_dir = Path(sys.argv[1])

    # Load filtered data
    mv_df = pd.read_csv(data_dir / "meaningful_variables_numerical.csv", index_col=0)
    demo_df = pd.read_csv(data_dir / "demographics_numerical.csv", index_col=0)

    print(f"Meaningful variables: {mv_df.shape}")
    print(f"Demographics: {demo_df.shape}")

    # Join
    joined = join_dataframes(mv_df, demo_df)
    joined.to_csv(data_dir / "joined_data.csv")
    print(f"Joined: {joined.shape}")


if __name__ == "__main__":
    main()
