"""Snakemake script for generating clustered heatmap."""

from pathlib import Path

import pandas as pd

from BetterCodeBetterScience.simple_workflow.visualization import (
    generate_clustered_heatmap,
)


def main():
    """Generate and save clustered heatmap."""
    # ruff: noqa: F821
    input_path = Path(snakemake.input[0])
    output_path = Path(snakemake.output[0])
    figsize = tuple(snakemake.params.figsize)
    cmap = snakemake.params.cmap
    vmin = snakemake.params.vmin
    vmax = snakemake.params.vmax

    # Load correlation matrix
    corr_matrix = pd.read_csv(input_path, index_col=0)
    print(f"Loaded correlation matrix: {corr_matrix.shape}")

    # Generate heatmap
    output_path.parent.mkdir(parents=True, exist_ok=True)
    generate_clustered_heatmap(
        corr_matrix,
        output_path=output_path,
        figsize=figsize,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
    )
    print(f"Saved heatmap to {output_path}")


if __name__ == "__main__":
    main()
