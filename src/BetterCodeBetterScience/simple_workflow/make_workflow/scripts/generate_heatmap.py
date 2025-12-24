#!/usr/bin/env python3
"""Generate clustered heatmap from correlation matrix.

Usage:
    python generate_heatmap.py <results_dir> <figures_dir>
"""

import sys
from pathlib import Path

import pandas as pd

from BetterCodeBetterScience.simple_workflow.visualization import (
    generate_clustered_heatmap,
)


def main():
    """Generate and save clustered heatmap."""
    if len(sys.argv) != 3:
        print("Usage: python generate_heatmap.py <results_dir> <figures_dir>")
        sys.exit(1)

    results_dir = Path(sys.argv[1])
    figures_dir = Path(sys.argv[2])

    # Load correlation matrix
    corr_matrix = pd.read_csv(results_dir / "correlation_matrix.csv", index_col=0)
    print(f"Loaded correlation matrix: {corr_matrix.shape}")

    # Generate heatmap
    output_path = figures_dir / "correlation_heatmap.png"
    generate_clustered_heatmap(corr_matrix, output_path=output_path)
    print(f"Saved heatmap to {output_path}")


if __name__ == "__main__":
    main()
