"""Data filtering module for scRNA-seq analysis workflow.

Functions for filtering donors and cell types with insufficient observations.
"""

from pathlib import Path

import anndata as ad
import matplotlib.pyplot as plt
import pandas as pd
import scanpy as sc
from scipy.stats import scoreatpercentile


def compute_donor_cell_counts(adata: ad.AnnData) -> pd.Series:
    """Calculate how many cells each donor has.

    Parameters
    ----------
    adata : AnnData
        AnnData object with 'donor_id' in obs

    Returns
    -------
    pd.Series
        Cell counts per donor
    """
    return pd.Series(adata.obs["donor_id"]).value_counts()


def plot_donor_cell_distribution(
    donor_cell_counts: pd.Series,
    cutoff_percentile: float = 1.0,
    figure_dir: Path | None = None,
) -> int:
    """Plot distribution of cells per donor and determine cutoff.

    Parameters
    ----------
    donor_cell_counts : pd.Series
        Cell counts per donor
    cutoff_percentile : float
        Percentile to use as cutoff (default: 1.0)
    figure_dir : Path, optional
        Directory to save figure

    Returns
    -------
    int
        Minimum cells per donor cutoff
    """
    min_cells_per_donor = int(
        scoreatpercentile(donor_cell_counts.values, cutoff_percentile)
    )

    plt.figure(figsize=(10, 6))
    plt.hist(donor_cell_counts.values, bins=50, color="skyblue", edgecolor="black")
    plt.title("Distribution of Total Cells per Donor")
    plt.xlabel("Number of Cells Captured")
    plt.ylabel("Number of Donors")
    plt.grid(axis="y", alpha=0.5)

    print(
        f"cutoff of {min_cells_per_donor} would exclude "
        f"{(donor_cell_counts < min_cells_per_donor).sum()} donors"
    )
    plt.axvline(
        min_cells_per_donor,
        color="red",
        linestyle="dashed",
        linewidth=1,
        label=f"Cutoff ({min_cells_per_donor} cells)",
    )
    plt.legend()

    if figure_dir is not None:
        plt.savefig(
            figure_dir / "donor_cell_counts_distribution.png",
            dpi=300,
            bbox_inches="tight",
        )
    plt.close()

    return min_cells_per_donor


def filter_donors_by_cell_count(
    adata: ad.AnnData, min_cells_per_donor: int
) -> ad.AnnData:
    """Filter to keep only donors with sufficient cells.

    Parameters
    ----------
    adata : AnnData
        AnnData object
    min_cells_per_donor : int
        Minimum cells required per donor

    Returns
    -------
    AnnData
        Filtered AnnData object
    """
    donor_cell_counts = compute_donor_cell_counts(adata)
    print(f"Filtering to keep only donors with at least {min_cells_per_donor} cells.")
    print(
        f"Number of donors excluded: {(donor_cell_counts < min_cells_per_donor).sum()}"
    )
    valid_donors = donor_cell_counts[donor_cell_counts >= min_cells_per_donor].index
    filtered = adata[adata.obs["donor_id"].isin(valid_donors)]
    print(f"Number of donors after filtering: {len(valid_donors)}")
    return filtered


def filter_cell_types_by_frequency(
    adata: ad.AnnData, min_cells: int = 10, percent_donors: float = 0.95
) -> ad.AnnData:
    """Filter cell types that don't have sufficient observations.

    Keep cell types with at least min_cells in at least percent_donors of donors.

    Parameters
    ----------
    adata : AnnData
        AnnData object
    min_cells : int
        Minimum cells per cell type per donor
    percent_donors : float
        Fraction of donors that must meet the min_cells threshold

    Returns
    -------
    AnnData
        Filtered AnnData object
    """
    counts_per_donor = pd.crosstab(adata.obs["donor_id"], adata.obs["cell_type"])
    donor_count = counts_per_donor.shape[0]

    cell_types_to_keep = counts_per_donor.columns[
        (counts_per_donor >= min_cells).sum(axis=0) >= (donor_count * percent_donors)
    ]

    print(
        f"Keeping {len(cell_types_to_keep)} cell types out of "
        f"{len(counts_per_donor.columns)}"
    )
    print(f"Cell types to keep: {cell_types_to_keep.tolist()}")

    return adata[adata.obs["cell_type"].isin(cell_types_to_keep)]


def filter_donors_with_missing_cell_types(
    adata: ad.AnnData, min_cells: int = 10
) -> ad.AnnData:
    """Filter donors who have zeros in any remaining cell types.

    Parameters
    ----------
    adata : AnnData
        AnnData object
    min_cells : int
        Minimum cells per cell type per donor

    Returns
    -------
    AnnData
        Filtered AnnData object
    """
    donor_celltype_counts = pd.crosstab(adata.obs["donor_id"], adata.obs["cell_type"])
    valid_donors = donor_celltype_counts.index[
        (donor_celltype_counts >= min_cells).all(axis=1)
    ]
    filtered = adata[adata.obs["donor_id"].isin(valid_donors)]
    print(f"Final number of donors after filtering: {len(valid_donors)}")
    return filtered


def load_to_memory_and_filter_genes(adata: ad.AnnData) -> ad.AnnData:
    """Load lazy AnnData to memory and filter zero-count genes.

    Parameters
    ----------
    adata : AnnData
        Lazy AnnData object

    Returns
    -------
    AnnData
        In-memory AnnData with filtered genes
    """
    print("Loading data into memory (this can take a few minutes)...")
    adata_loaded = adata.to_memory()

    print("Filtering genes with zero counts...")
    sc.pp.filter_genes(adata_loaded, min_counts=1)

    return adata_loaded


def run_filtering_pipeline(
    adata: ad.AnnData,
    cutoff_percentile: float = 1.0,
    min_cells_per_celltype: int = 10,
    percent_donors: float = 0.95,
    figure_dir: Path | None = None,
) -> ad.AnnData:
    """Run complete filtering pipeline.

    Parameters
    ----------
    adata : AnnData
        Input AnnData object (can be lazy)
    cutoff_percentile : float
        Percentile for donor cell count cutoff
    min_cells_per_celltype : int
        Minimum cells per cell type per donor
    percent_donors : float
        Fraction of donors that must meet cell count threshold
    figure_dir : Path, optional
        Directory to save figures

    Returns
    -------
    AnnData
        Filtered and loaded AnnData object
    """
    # Step 1: Filter donors by total cell count
    donor_counts = compute_donor_cell_counts(adata)
    min_cells = plot_donor_cell_distribution(
        donor_counts, cutoff_percentile, figure_dir
    )
    adata = filter_donors_by_cell_count(adata, min_cells)

    # Step 2: Filter cell types by frequency
    adata = filter_cell_types_by_frequency(
        adata, min_cells_per_celltype, percent_donors
    )

    # Step 3: Filter donors with missing cell types
    adata = filter_donors_with_missing_cell_types(adata, min_cells_per_celltype)

    # Step 4: Load to memory and filter genes
    adata = load_to_memory_and_filter_genes(adata)

    print(f"Final dataset shape: {adata.shape}")
    return adata
