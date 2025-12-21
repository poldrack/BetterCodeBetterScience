"""Clustering module for scRNA-seq analysis workflow.

Functions for cell clustering using Leiden algorithm.
"""

from pathlib import Path

import anndata as ad
import matplotlib.pyplot as plt
import pandas as pd
import scanpy as sc


def run_leiden_clustering(
    adata: ad.AnnData,
    resolution: float = 1.0,
    key_added: str = "leiden_1.0",
    flavor: str = "igraph",
    n_iterations: int = 2,
) -> ad.AnnData:
    """Run Leiden clustering algorithm.

    Parameters
    ----------
    adata : AnnData
        AnnData object with neighbor graph
    resolution : float
        Resolution parameter for clustering
    key_added : str
        Key to store cluster assignments
    flavor : str
        Implementation flavor
    n_iterations : int
        Number of iterations

    Returns
    -------
    AnnData
        AnnData with cluster assignments
    """
    sc.tl.leiden(
        adata,
        resolution=resolution,
        key_added=key_added,
        flavor=flavor,
        n_iterations=n_iterations,
    )
    return adata


def plot_clusters(
    adata: ad.AnnData,
    cluster_key: str = "leiden_1.0",
    cell_type_key: str = "cell_type",
    figure_dir: Path | None = None,
) -> None:
    """Plot UMAP colored by clusters and cell types.

    Parameters
    ----------
    adata : AnnData
        AnnData object with UMAP and clusters
    cluster_key : str
        Key for cluster assignments
    cell_type_key : str
        Key for cell type annotations
    figure_dir : Path, optional
        Directory to save figures
    """
    sc.pl.umap(adata, color=[cell_type_key, cluster_key], wspace=0.3, show=False)
    if figure_dir is not None:
        plt.savefig(
            figure_dir / "umap_cell_type_leiden.png", dpi=300, bbox_inches="tight"
        )
    plt.close()


def compute_cluster_celltype_overlap(
    adata: ad.AnnData,
    cluster_key: str = "leiden_1.0",
    cell_type_key: str = "cell_type",
) -> pd.DataFrame:
    """Compute contingency table between clusters and cell types.

    Parameters
    ----------
    adata : AnnData
        AnnData object with clusters and cell types
    cluster_key : str
        Key for cluster assignments
    cell_type_key : str
        Key for cell type annotations

    Returns
    -------
    pd.DataFrame
        Contingency table
    """
    contingency_table = pd.crosstab(adata.obs[cluster_key], adata.obs[cell_type_key])
    return contingency_table


def run_clustering_pipeline(
    adata: ad.AnnData,
    resolution: float = 1.0,
    figure_dir: Path | None = None,
) -> ad.AnnData:
    """Run complete clustering pipeline.

    Parameters
    ----------
    adata : AnnData
        Input AnnData object with UMAP computed
    resolution : float
        Leiden resolution parameter
    figure_dir : Path, optional
        Directory to save figures

    Returns
    -------
    AnnData
        AnnData with cluster assignments
    """
    cluster_key = f"leiden_{resolution}"

    # Run Leiden clustering
    adata = run_leiden_clustering(adata, resolution, cluster_key)

    # Plot clusters
    plot_clusters(adata, cluster_key, figure_dir=figure_dir)

    # Compute and print overlap
    contingency = compute_cluster_celltype_overlap(adata, cluster_key)
    print("Cluster-Cell Type Contingency Table:")
    print(contingency)

    return adata
