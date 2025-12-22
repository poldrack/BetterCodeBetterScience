"""Pseudobulking module for scRNA-seq analysis workflow.

Functions for aggregating single-cell counts to pseudobulk samples.
"""

from pathlib import Path

import anndata as ad
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scanpy as sc
from sklearn.preprocessing import OneHotEncoder


def create_pseudobulk(
    adata: ad.AnnData,
    group_col: str,
    donor_col: str,
    layer: str = "counts",
    metadata_cols: list[str] | None = None,
) -> ad.AnnData:
    """Sum raw counts for each (Donor, CellType) pair.

    Parameters
    ----------
    adata : AnnData
        Input single-cell data
    group_col : str
        Column name for grouping (e.g., 'cell_type')
    donor_col : str
        Column name for donor ID
    layer : str
        Layer to use for aggregation (default: 'counts')
    metadata_cols : list of str, optional
        Additional metadata columns to preserve from obs

    Returns
    -------
    AnnData
        Pseudobulk AnnData object
    """
    # Create a combined key (e.g., "Bcell::Donor1")
    groups = adata.obs[group_col].astype(str)
    donors = adata.obs[donor_col].astype(str)

    group_df = pd.DataFrame({"group": groups, "donor": donors})
    group_df["combined"] = group_df["group"] + "::" + group_df["donor"]

    # Build the aggregation matrix (One-Hot Encoding)
    enc = OneHotEncoder(sparse_output=True, dtype=np.float32)
    membership_matrix = enc.fit_transform(group_df[["combined"]])

    # Get source matrix
    if layer is not None and layer in adata.layers:
        X_source = adata.layers[layer]
    else:
        X_source = adata.X

    # Aggregate by summing
    pseudobulk_X = membership_matrix.T @ X_source

    # Create obs metadata for the new object
    unique_ids = enc.categories_[0]

    obs_data = []
    for uid in unique_ids:
        ctype, donor = uid.split("::")
        obs_data.append({"cell_type": ctype, "donor_id": donor})

    pb_obs = pd.DataFrame(obs_data, index=unique_ids)

    # Count cells per pseudobulk sample
    cell_counts = np.array(membership_matrix.sum(axis=0)).flatten()
    pb_obs["n_cells"] = cell_counts.astype(int)

    # Add additional metadata columns
    if metadata_cols is not None:
        for col in metadata_cols:
            if col in adata.obs.columns:
                col_values = []
                for uid in unique_ids:
                    ctype, donor = uid.split("::")
                    donor_mask = adata.obs[donor_col] == donor
                    if donor_mask.any():
                        col_values.append(adata.obs.loc[donor_mask, col].iloc[0])
                    else:
                        col_values.append(None)
                pb_obs[col] = col_values

    # Assemble the AnnData
    pb_adata = ad.AnnData(X=pseudobulk_X, obs=pb_obs, var=adata.var.copy())

    return pb_adata


def filter_pseudobulk_by_cell_count(
    pb_adata: ad.AnnData, min_cells: int = 10
) -> ad.AnnData:
    """Filter pseudobulk samples with too few cells.

    Parameters
    ----------
    pb_adata : AnnData
        Pseudobulk AnnData object
    min_cells : int
        Minimum cells required per sample

    Returns
    -------
    AnnData
        Filtered pseudobulk AnnData
    """
    print(f"Dropping samples with < {min_cells} cells...")
    pb_adata = pb_adata[pb_adata.obs["n_cells"] >= min_cells].copy()
    print(f"Remaining samples: {pb_adata.n_obs}")
    return pb_adata


def compute_pseudobulk_qc(pb_adata: ad.AnnData) -> ad.AnnData:
    """Compute QC metrics for pseudobulk samples.

    Parameters
    ----------
    pb_adata : AnnData
        Pseudobulk AnnData object

    Returns
    -------
    AnnData
        Pseudobulk AnnData with QC metrics
    """
    pb_adata.obs["total_counts"] = np.array(pb_adata.X.sum(axis=1)).flatten()
    return pb_adata


def plot_pseudobulk_qc(pb_adata: ad.AnnData, figure_dir: Path | None = None) -> None:
    """Plot QC metrics for pseudobulk samples.

    Parameters
    ----------
    pb_adata : AnnData
        Pseudobulk AnnData object
    figure_dir : Path, optional
        Directory to save figures
    """
    sc.pl.violin(pb_adata, ["n_cells", "total_counts"], multi_panel=True, show=False)
    if figure_dir is not None:
        plt.savefig(figure_dir / "pseudobulk_violin.png", dpi=300, bbox_inches="tight")
    plt.close()


def run_pseudobulk_pipeline(
    adata: ad.AnnData,
    group_col: str = "cell_type",
    donor_col: str = "donor_id",
    metadata_cols: list[str] | None = None,
    min_cells: int = 10,
    figure_dir: Path | None = None,
    layer: str | None = None,
) -> ad.AnnData:
    """Run complete pseudobulking pipeline.

    Parameters
    ----------
    adata : AnnData
        Input single-cell AnnData object
    group_col : str
        Column for cell type grouping
    donor_col : str
        Column for donor ID
    metadata_cols : list of str, optional
        Metadata columns to preserve
    min_cells : int
        Minimum cells per pseudobulk sample
    figure_dir : Path, optional
        Directory to save figures
    layer : str, optional
        Layer to use for counts. If None, uses .X directly.

    Returns
    -------
    AnnData
        Pseudobulk AnnData object
    """
    if metadata_cols is None:
        metadata_cols = ["development_stage", "sex"]

    print("Aggregating counts...")
    pb_adata = create_pseudobulk(
        adata,
        group_col=group_col,
        donor_col=donor_col,
        layer=layer,
        metadata_cols=metadata_cols,
    )

    print("Pseudobulk complete.")
    print(f"Original shape: {adata.shape}")
    print(f"Pseudobulk shape: {pb_adata.shape} (Samples x Genes)")
    print(pb_adata.obs.head())

    # Filter by cell count
    pb_adata = filter_pseudobulk_by_cell_count(pb_adata, min_cells)

    # Compute and plot QC
    pb_adata = compute_pseudobulk_qc(pb_adata)
    plot_pseudobulk_qc(pb_adata, figure_dir)

    return pb_adata
