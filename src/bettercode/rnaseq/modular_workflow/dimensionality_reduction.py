"""Dimensionality reduction module for scRNA-seq analysis workflow.

Functions for batch correction, neighbor computation, and UMAP generation.
"""

from pathlib import Path

import anndata as ad
import matplotlib.pyplot as plt
import scanpy as sc
import scanpy.external as sce


def run_harmony_integration(
    adata: ad.AnnData,
    batch_key: str = "donor_id",
    basis: str = "X_pca",
    adjusted_basis: str = "X_pca_harmony",
) -> tuple[ad.AnnData, str]:
    """Run Harmony batch correction on PCA coordinates.

    Parameters
    ----------
    adata : AnnData
        AnnData object with PCA computed
    batch_key : str
        Column name for batch variable
    basis : str
        Name of PCA coordinates
    adjusted_basis : str
        Name for corrected coordinates

    Returns
    -------
    tuple[AnnData, str]
        AnnData with Harmony results and the representation to use
    """
    try:
        sce.pp.harmony_integrate(
            adata, key=batch_key, basis=basis, adjusted_basis=adjusted_basis
        )
        use_rep = adjusted_basis
        print("Harmony integration successful. Using corrected PCA.")
    except ImportError:
        print(
            "Harmony not installed. Proceeding with standard PCA "
            "(Warning: Batch effects may persist)."
        )
        print("To install: pip install harmony-pytorch")
        use_rep = basis

    return adata, use_rep


def plot_pca_qc(adata: ad.AnnData, figure_dir: Path | None = None) -> None:
    """Plot PCA colored by total counts and cell type.

    Parameters
    ----------
    adata : AnnData
        AnnData object with PCA computed
    figure_dir : Path, optional
        Directory to save figures
    """
    sc.pl.pca(
        adata, color=["total_counts", "cell_type"], components=["1,2"], show=False
    )
    if figure_dir is not None:
        plt.savefig(figure_dir / "pca_cell_type.png", dpi=300, bbox_inches="tight")
    plt.close()


def compute_neighbors(
    adata: ad.AnnData,
    n_neighbors: int = 30,
    n_pcs: int = 40,
    use_rep: str = "X_pca_harmony",
) -> ad.AnnData:
    """Compute neighborhood graph.

    Parameters
    ----------
    adata : AnnData
        AnnData object
    n_neighbors : int
        Number of neighbors
    n_pcs : int
        Number of PCs to use
    use_rep : str
        Representation to use

    Returns
    -------
    AnnData
        AnnData with neighbor graph
    """
    sc.pp.neighbors(adata, n_neighbors=n_neighbors, n_pcs=n_pcs, use_rep=use_rep)
    return adata


def compute_umap(
    adata: ad.AnnData,
    init_pos: str = "X_pca_harmony",
) -> ad.AnnData:
    """Compute UMAP embedding.

    Parameters
    ----------
    adata : AnnData
        AnnData object with neighbor graph
    init_pos : str
        Initial position for UMAP

    Returns
    -------
    AnnData
        AnnData with UMAP coordinates
    """
    sc.tl.umap(adata, init_pos=init_pos)
    return adata


def plot_umap_qc(adata: ad.AnnData, figure_dir: Path | None = None) -> None:
    """Plot UMAP colored by total counts.

    Parameters
    ----------
    adata : AnnData
        AnnData object with UMAP
    figure_dir : Path, optional
        Directory to save figures
    """
    sc.pl.umap(adata, color="total_counts", show=False)
    if figure_dir is not None:
        plt.savefig(figure_dir / "umap_total_counts.png", dpi=300, bbox_inches="tight")
    plt.close()


def run_dimensionality_reduction_pipeline(
    adata: ad.AnnData,
    batch_key: str = "donor_id",
    n_neighbors: int = 30,
    n_pcs: int = 40,
    figure_dir: Path | None = None,
) -> ad.AnnData:
    """Run complete dimensionality reduction pipeline.

    Parameters
    ----------
    adata : AnnData
        Input AnnData object with PCA computed
    batch_key : str
        Column for batch correction
    n_neighbors : int
        Number of neighbors for graph
    n_pcs : int
        Number of PCs to use
    figure_dir : Path, optional
        Directory to save figures

    Returns
    -------
    AnnData
        AnnData with UMAP coordinates
    """
    # Run Harmony integration
    adata, use_rep = run_harmony_integration(adata, batch_key)

    # Plot PCA QC
    plot_pca_qc(adata, figure_dir)

    # Compute neighbors
    adata = compute_neighbors(adata, n_neighbors, n_pcs, use_rep)

    # Compute UMAP
    init_pos = use_rep if use_rep == "X_pca_harmony" else "spectral"
    adata = compute_umap(adata, init_pos)

    # Plot UMAP QC
    plot_umap_qc(adata, figure_dir)

    return adata
