#!/usr/bin/env python3
"""Compute Spearman correlation matrix.

Usage:
    python compute_correlation.py <data_dir> <results_dir>
"""

import sys
from pathlib import Path

import pandas as pd

from bettercode.simple_workflow.correlation import (
    compute_spearman_correlation,
)


def main():
    """Compute Spearman correlation matrix."""
    if len(sys.argv) != 3:
        print("Usage: python compute_correlation.py <data_dir> <results_dir>")
        sys.exit(1)

    data_dir = Path(sys.argv[1])
    results_dir = Path(sys.argv[2])

    # Load joined data
    df = pd.read_csv(data_dir / "joined_data.csv", index_col=0)
    print(f"Loaded joined data: {df.shape}")

    # Compute correlation
    corr_matrix = compute_spearman_correlation(df)
    corr_matrix.to_csv(results_dir / "correlation_matrix.csv")
    print(f"Saved correlation matrix: {corr_matrix.shape}")


if __name__ == "__main__":
    main()
