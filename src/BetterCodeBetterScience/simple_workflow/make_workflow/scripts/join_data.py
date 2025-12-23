#!/usr/bin/env python3
"""Join two dataframes based on their index.

Usage:
    python join_data.py <input1_path> <input2_path> <output_path>
"""

import sys
from pathlib import Path

import pandas as pd

from BetterCodeBetterScience.simple_workflow.join_data import join_dataframes


def main():
    """Join the two datasets."""
    if len(sys.argv) != 4:
        print("Usage: python join_data.py <input1_path> <input2_path> <output_path>")
        sys.exit(1)

    input1_path = Path(sys.argv[1])
    input2_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3])

    # Load data
    df1 = pd.read_csv(input1_path, index_col=0)
    df2 = pd.read_csv(input2_path, index_col=0)

    print(f"Dataset 1: {df1.shape}")
    print(f"Dataset 2: {df2.shape}")

    # Join
    joined = join_dataframes(df1, df2)
    print(f"Joined: {joined.shape}")

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joined.to_csv(output_path)
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()
