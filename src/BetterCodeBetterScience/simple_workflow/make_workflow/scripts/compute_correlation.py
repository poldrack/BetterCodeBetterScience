#!/usr/bin/env python3
"""Compute Spearman correlation matrix.

Usage:
    python compute_correlation.py <input_path> <output_path>
"""

import sys
from pathlib import Path

import pandas as pd

from BetterCodeBetterScience.simple_workflow.correlation import (
    compute_spearman_correlation,
)


def main():
    """Compute Spearman correlation matrix."""
    if len(sys.argv) != 3:
        print("Usage: python compute_correlation.py <input_path> <output_path>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    # Load data
    df = pd.read_csv(input_path, index_col=0)
    print(f"Loaded {df.shape} from {input_path}")

    # Compute correlation
    corr_matrix = compute_spearman_correlation(df)
    print(f"Computed Spearman correlation matrix: {corr_matrix.shape}")

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    corr_matrix.to_csv(output_path)
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()
