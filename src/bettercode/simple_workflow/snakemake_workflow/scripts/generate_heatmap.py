"""Snakemake script for generating clustered heatmap."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def generate_clustered_heatmap(
    corr_matrix: pd.DataFrame,
    output_path: Path | None = None,
    figsize: tuple[int, int] = (8, 10),
    cmap: str = "coolwarm",
    vmin: float = -1.0,
    vmax: float = 1.0,
) -> sns.matrix.ClusterGrid:
    """Generate a clustered heatmap from a correlation matrix."""
    # Create clustered heatmap
    g = sns.clustermap(
        corr_matrix,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        figsize=figsize,
        dendrogram_ratio=(0.1, 0.1),
        cbar_pos=(0.02, 0.8, 0.03, 0.15),
        xticklabels=False,
        yticklabels=True,
    )

    # Set y-axis label font size
    plt.setp(g.ax_heatmap.get_yticklabels(), rotation=0, fontsize=3)

    # Set title
    g.fig.suptitle("Clustered Correlation Heatmap (Spearman)", y=1.02, fontsize=14)

    # Save if output path provided
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        g.savefig(output_path, dpi=300, bbox_inches="tight")

    return g


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
