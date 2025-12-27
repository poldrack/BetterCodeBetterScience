"""Quality control module for scRNA-seq analysis workflow.

Functions for identifying bad cells and doublets.
"""

from pathlib import Path

import anndata as ad
import matplotlib.pyplot as plt
import scanpy as sc
import seaborn as sns


def annotate_gene_types(adata: ad.AnnData) -> ad.AnnData:
    """Annotate mitochondrial, ribosomal, and hemoglobin genes.

    Parameters
    ----------
    adata : AnnData
        AnnData object with 'feature_name' in var

    Returns
    -------
    AnnData
        AnnData with mt, ribo, hb annotations in var
    """
    # Mitochondrial genes
    adata.var["mt"] = adata.var["feature_name"].str.startswith("MT-")
    print(f"Number of mitochondrial genes: {adata.var['mt'].sum()}")

    # Ribosomal genes
    adata.var["ribo"] = adata.var["feature_name"].str.startswith(("RPS", "RPL"))
    print(f"Number of ribosomal genes: {adata.var['ribo'].sum()}")

    # Hemoglobin genes
    adata.var["hb"] = adata.var["feature_name"].str.contains("^HB[^(P)]")
    print(f"Number of hemoglobin genes: {adata.var['hb'].sum()}")

    return adata


def calculate_qc_metrics(adata: ad.AnnData) -> ad.AnnData:
    """Calculate QC metrics for cells.

    Parameters
    ----------
    adata : AnnData
        AnnData object with gene type annotations

    Returns
    -------
    AnnData
        AnnData with QC metrics in obs
    """
    sc.pp.calculate_qc_metrics(
        adata,
        qc_vars=["mt", "ribo", "hb"],
        inplace=True,
        percent_top=[20],
        log1p=True,
    )
    return adata


def plot_qc_metrics(adata: ad.AnnData, figure_dir: Path | None = None) -> None:
    """Plot QC metric distributions.

    Parameters
    ----------
    adata : AnnData
        AnnData object with QC metrics
    figure_dir : Path, optional
        Directory to save figures
    """
    # Violin plots for QC metrics
    sc.pl.violin(
        adata,
        ["total_counts", "n_genes_by_counts", "pct_counts_mt"],
        jitter=0.4,
        multi_panel=True,
        show=False,
    )
    if figure_dir is not None:
        plt.savefig(figure_dir / "qc_violin_plots.png", dpi=300, bbox_inches="tight")
    plt.close()

    # Scatter plot for doublets and dying cells
    sc.pl.scatter(
        adata,
        x="total_counts",
        y="n_genes_by_counts",
        color="pct_counts_mt",
        show=False,
    )
    if figure_dir is not None:
        plt.savefig(
            figure_dir / "qc_scatter_doublets.png", dpi=300, bbox_inches="tight"
        )
    plt.close()


def plot_hemoglobin_distribution(
    adata: ad.AnnData, figure_dir: Path | None = None
) -> None:
    """Plot hemoglobin content distribution to check RBC contamination.

    Parameters
    ----------
    adata : AnnData
        AnnData object with QC metrics
    figure_dir : Path, optional
        Directory to save figures
    """
    plt.figure(figsize=(6, 4))
    sns.histplot(adata.obs["pct_counts_hb"], bins=50, log_scale=(False, True))
    plt.title("Hemoglobin Content Distribution")
    plt.xlabel("% Hemoglobin Counts")
    plt.axvline(5, color="red", linestyle="--", label="5% Cutoff")
    plt.legend()
    if figure_dir is not None:
        plt.savefig(
            figure_dir / "hemoglobin_distribution.png", dpi=300, bbox_inches="tight"
        )
    plt.close()


def apply_qc_filters(
    adata: ad.AnnData,
    min_genes: int = 200,
    max_genes: int = 6000,
    min_counts: int = 500,
    max_counts: int = 30000,
    max_hb_pct: float = 5.0,
) -> ad.AnnData:
    """Apply QC filters to remove low quality cells and doublets.

    Parameters
    ----------
    adata : AnnData
        AnnData object with QC metrics
    min_genes : int
        Minimum genes per cell
    max_genes : int
        Maximum genes per cell (doublet filter)
    min_counts : int
        Minimum UMIs per cell
    max_counts : int
        Maximum UMIs per cell (doublet filter)
    max_hb_pct : float
        Maximum hemoglobin percentage (RBC filter)

    Returns
    -------
    AnnData
        Filtered AnnData object
    """
    adata_qc = adata.copy()
    print(f"Before filtering: {adata_qc.n_obs} cells")

    # Filter low quality and doublets
    adata_qc = adata_qc[
        (adata_qc.obs["n_genes_by_counts"] > min_genes)
        & (adata_qc.obs["n_genes_by_counts"] < max_genes)
        & (adata_qc.obs["total_counts"] > min_counts)
        & (adata_qc.obs["total_counts"] < max_counts)
    ]

    # Filter Red Blood Cells
    adata_qc = adata_qc[adata_qc.obs["pct_counts_hb"] < max_hb_pct]

    print(f"After filtering: {adata_qc.n_obs} cells")
    return adata_qc


def detect_doublets_per_donor(
    adata: ad.AnnData,
    expected_doublet_rate: float = 0.06,
    min_cells_per_donor: int = 100,
) -> ad.AnnData:
    """Run doublet detection separately for each donor.

    Parameters
    ----------
    adata : AnnData
        AnnData object with raw counts
    expected_doublet_rate : float
        Expected doublet rate for Scrublet
    min_cells_per_donor : int
        Minimum cells required to run Scrublet

    Returns
    -------
    AnnData
        AnnData with doublet annotations
    """
    print(f"Data shape before doublet detection: {adata.shape}")

    adatas_list = []
    donors = adata.obs["donor_id"].unique()

    print(f"Running Scrublet on {len(donors)} donors...")

    for donor in donors:
        curr_adata = adata[adata.obs["donor_id"] == donor].copy()

        if curr_adata.n_obs < min_cells_per_donor:
            print(f"Skipping donor {donor}: too few cells ({curr_adata.n_obs})")
            curr_adata.obs["doublet_score"] = 0
            curr_adata.obs["predicted_doublet"] = False
            adatas_list.append(curr_adata)
            continue

        sc.pp.scrublet(curr_adata, expected_doublet_rate=expected_doublet_rate)
        adatas_list.append(curr_adata)

    adata_combined = sc.concat(adatas_list)

    print(
        f"Detected {adata_combined.obs['predicted_doublet'].sum()} "
        f"doublets across all donors."
    )
    print(adata_combined.obs["predicted_doublet"].value_counts())

    return adata_combined


def compute_umap_for_qc(adata: ad.AnnData, n_pcs: int = 30) -> ad.AnnData:
    """Compute a simple UMAP embedding for QC visualization.

    This computes a quick UMAP on the raw counts for visualizing
    doublet detection results. This is separate from the main
    dimensionality reduction in step 5.

    Parameters
    ----------
    adata : AnnData
        AnnData object (raw counts in .X)
    n_pcs : int
        Number of principal components to use

    Returns
    -------
    AnnData
        AnnData with UMAP coordinates in .obsm['X_umap']
    """
    # Work on a copy to avoid modifying the original
    adata_temp = adata.copy()

    # Basic preprocessing for UMAP computation
    sc.pp.normalize_total(adata_temp, target_sum=1e4)
    sc.pp.log1p(adata_temp)
    sc.pp.highly_variable_genes(adata_temp, n_top_genes=2000, flavor="seurat_v3")
    sc.pp.pca(adata_temp, n_comps=n_pcs, use_highly_variable=True)
    sc.pp.neighbors(adata_temp, n_neighbors=15, n_pcs=n_pcs)
    sc.tl.umap(adata_temp)

    # Copy UMAP coordinates back to original
    adata.obsm["X_umap"] = adata_temp.obsm["X_umap"]

    return adata


def plot_doublets(adata: ad.AnnData, figure_dir: Path | None = None) -> None:
    """Visualize doublet detection results on UMAP.

    Parameters
    ----------
    adata : AnnData
        AnnData object with doublet annotations and UMAP coordinates
    figure_dir : Path, optional
        Directory to save figures
    """
    if "X_umap" not in adata.obsm:
        print("Warning: No UMAP coordinates found, skipping doublet plot")
        return

    sc.pl.umap(adata, color=["doublet_score", "predicted_doublet"], size=20, show=False)
    if figure_dir is not None:
        plt.savefig(
            figure_dir / "doublet_detection_umap.png", dpi=300, bbox_inches="tight"
        )
    plt.close()


def filter_doublets(adata: ad.AnnData) -> ad.AnnData:
    """Remove predicted doublets from the dataset.

    Parameters
    ----------
    adata : AnnData
        AnnData object with doublet predictions

    Returns
    -------
    AnnData
        Filtered AnnData with only singlets
    """
    print(f"Found {adata.obs['predicted_doublet'].sum()} predicted doublets")
    adata_filtered = adata[adata.obs["predicted_doublet"] == False, :]  # noqa: E712
    print(f"Remaining cells: {adata_filtered.n_obs}")
    return adata_filtered


def run_qc_pipeline(
    adata: ad.AnnData,
    min_genes: int = 200,
    max_genes: int = 6000,
    min_counts: int = 500,
    max_counts: int = 30000,
    max_hb_pct: float = 5.0,
    expected_doublet_rate: float = 0.06,
    figure_dir: Path | None = None,
) -> ad.AnnData:
    """Run complete quality control pipeline.

    Parameters
    ----------
    adata : AnnData
        Input AnnData object
    min_genes : int
        Minimum genes per cell
    max_genes : int
        Maximum genes per cell
    min_counts : int
        Minimum UMIs per cell
    max_counts : int
        Maximum UMIs per cell
    max_hb_pct : float
        Maximum hemoglobin percentage
    expected_doublet_rate : float
        Expected doublet rate
    figure_dir : Path, optional
        Directory to save figures

    Returns
    -------
    AnnData
        QC-filtered AnnData object
    """
    # Annotate gene types
    adata = annotate_gene_types(adata)

    # Calculate QC metrics
    adata = calculate_qc_metrics(adata)

    # Plot QC metrics
    plot_qc_metrics(adata, figure_dir)
    plot_hemoglobin_distribution(adata, figure_dir)

    # Apply QC filters
    adata = apply_qc_filters(
        adata, min_genes, max_genes, min_counts, max_counts, max_hb_pct
    )

    # Detect doublets
    adata = detect_doublets_per_donor(adata, expected_doublet_rate)

    # Compute UMAP for doublet visualization (before filtering)
    print("Computing UMAP for doublet visualization...")
    adata = compute_umap_for_qc(adata)
    plot_doublets(adata, figure_dir)

    # Filter doublets
    adata = filter_doublets(adata)

    # Save raw counts for HVG selection (step 4) and pseudobulking (step 7)
    # Note: Raw counts are also in .X at this point, which will be used
    # by pseudobulking when loading this checkpoint directly.
    adata.layers["counts"] = adata.X.copy()

    return adata
