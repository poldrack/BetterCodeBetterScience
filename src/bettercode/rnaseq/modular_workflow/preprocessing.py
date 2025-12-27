"""Preprocessing module for scRNA-seq analysis workflow.

Functions for normalization, log transformation, and feature selection.
"""

import re

import anndata as ad
import scanpy as sc


def normalize_counts(adata: ad.AnnData, target_sum: float = 1e4) -> ad.AnnData:
    """Normalize counts to target sum per cell.

    Parameters
    ----------
    adata : AnnData
        AnnData object with raw counts
    target_sum : float
        Target sum for normalization (default: 10,000)

    Returns
    -------
    AnnData
        Normalized AnnData object
    """
    sc.pp.normalize_total(adata, target_sum=target_sum)
    return adata


def log_transform(adata: ad.AnnData) -> ad.AnnData:
    """Apply log1p transformation.

    Parameters
    ----------
    adata : AnnData
        AnnData object

    Returns
    -------
    AnnData
        Log-transformed AnnData object
    """
    sc.pp.log1p(adata)
    return adata


def select_highly_variable_genes(
    adata: ad.AnnData,
    n_top_genes: int = 3000,
    batch_key: str = "donor_id",
    layer: str = "counts",
    span: float = 0.8,
) -> ad.AnnData:
    """Select highly variable genes using seurat_v3 method.

    Parameters
    ----------
    adata : AnnData
        AnnData object
    n_top_genes : int
        Number of top variable genes to select
    batch_key : str
        Column name for batch correction
    layer : str
        Layer containing raw counts
    span : float
        LOESS span parameter

    Returns
    -------
    AnnData
        AnnData with highly_variable annotation
    """
    sc.pp.highly_variable_genes(
        adata,
        n_top_genes=n_top_genes,
        flavor="seurat_v3",
        batch_key=batch_key,
        span=span,
        layer=layer,
        subset=False,
    )
    return adata


def identify_nuisance_genes(adata: ad.AnnData) -> list[str]:
    """Identify nuisance genes to exclude from HVG list.

    Identifies TCR/BCR variable regions, mitochondrial, and ribosomal genes.

    Parameters
    ----------
    adata : AnnData
        AnnData object

    Returns
    -------
    list[str]
        List of gene names to block
    """
    # TCR/BCR genes (V(D)J recombination genes)
    immune_receptor_genes = [
        name for name in adata.var_names if re.match(r"^(IG[HKL]|TR[ABDG])[VDJC]", name)
    ]

    # Mitochondrial genes
    mt_genes = adata.var_names[adata.var_names.str.startswith("MT-")]

    # Ribosomal genes
    rb_genes = adata.var_names[adata.var_names.str.startswith(("RPS", "RPL"))]

    genes_to_block = list(immune_receptor_genes) + list(mt_genes) + list(rb_genes)
    return genes_to_block


def filter_nuisance_genes_from_hvg(adata: ad.AnnData) -> ad.AnnData:
    """Remove nuisance genes from HVG list.

    Parameters
    ----------
    adata : AnnData
        AnnData object with highly_variable annotation

    Returns
    -------
    AnnData
        AnnData with filtered HVG list
    """
    genes_to_block = identify_nuisance_genes(adata)

    # Count immune receptor genes separately for reporting
    immune_receptor_genes = [
        name for name in adata.var_names if re.match(r"^(IG[HKL]|TR[ABDG])[VDJC]", name)
    ]

    # Set blocked genes to not highly variable
    adata.var.loc[adata.var_names.isin(genes_to_block), "highly_variable"] = False

    print(f"Blocked {len(immune_receptor_genes)} immune receptor genes from HVG list.")
    print(f"Final HVG count: {adata.var['highly_variable'].sum()}")

    return adata


def run_pca(
    adata: ad.AnnData,
    svd_solver: str = "arpack",
    use_highly_variable: bool = True,
) -> ad.AnnData:
    """Run PCA on the data.

    Parameters
    ----------
    adata : AnnData
        AnnData object
    svd_solver : str
        SVD solver to use
    use_highly_variable : bool
        Whether to use only HVGs

    Returns
    -------
    AnnData
        AnnData with PCA results
    """
    sc.tl.pca(adata, svd_solver=svd_solver, use_highly_variable=use_highly_variable)
    return adata


def run_preprocessing_pipeline(
    adata: ad.AnnData,
    target_sum: float = 1e4,
    n_top_genes: int = 3000,
    batch_key: str = "donor_id",
) -> ad.AnnData:
    """Run complete preprocessing pipeline.

    Parameters
    ----------
    adata : AnnData
        Input AnnData object with raw counts in 'counts' layer
    target_sum : float
        Target sum for normalization
    n_top_genes : int
        Number of HVGs to select
    batch_key : str
        Column for batch correction

    Returns
    -------
    AnnData
        Preprocessed AnnData object
    """
    # Normalize
    adata = normalize_counts(adata, target_sum)

    # Log transform
    adata = log_transform(adata)

    # Select HVGs
    adata = select_highly_variable_genes(adata, n_top_genes, batch_key)

    # Filter nuisance genes
    adata = filter_nuisance_genes_from_hvg(adata)

    # Run PCA
    adata = run_pca(adata)

    return adata
