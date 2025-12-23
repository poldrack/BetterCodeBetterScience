#!/usr/bin/env python3
"""Filter dataframe to numerical columns only.

Usage:
    python filter_data.py <input_path> <output_path>
"""

import sys
from pathlib import Path

import pandas as pd

from BetterCodeBetterScience.simple_workflow.filter_data import (
    filter_numerical_columns,
)


def main():
    """Filter data to numerical columns."""
    if len(sys.argv) != 3:
        print("Usage: python filter_data.py <input_path> <output_path>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    # Load data
    df = pd.read_csv(input_path, index_col=0)
    print(f"Loaded {df.shape} from {input_path}")

    # Filter to numerical columns
    df_num = filter_numerical_columns(df)
    print(f"Filtered to {df_num.shape} (numerical columns only)")

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_num.to_csv(output_path)
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()
