"""Visualization module for the simple workflow example.

This module provides functions to generate heatmaps from correlation matrices.
"""

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
    """Generate a clustered heatmap from a correlation matrix.

    Parameters
    ----------
    corr_matrix : pd.DataFrame
        Correlation matrix
    output_path : Path, optional
        If provided, save the figure to this path
    figsize : tuple
        Figure size (width, height) in inches
    cmap : str
        Colormap name (default: 'coolwarm')
    vmin : float
        Minimum value for color scale
    vmax : float
        Maximum value for color scale

    Returns
    -------
    sns.matrix.ClusterGrid
        The ClusterGrid object containing the heatmap
    """
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


def save_correlation_matrix(
    corr_matrix: pd.DataFrame,
    output_path: Path,
) -> None:
    """Save a correlation matrix to a CSV file.

    Parameters
    ----------
    corr_matrix : pd.DataFrame
        Correlation matrix
    output_path : Path
        Path to save the CSV file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    corr_matrix.to_csv(output_path)
