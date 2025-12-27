"""Differential expression module for scRNA-seq analysis workflow.

Functions for running DESeq2-based differential expression analysis.
"""

import anndata as ad
import numpy as np
import pandas as pd
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats
from sklearn.preprocessing import StandardScaler


def extract_age_from_development_stage(pb_adata: ad.AnnData) -> ad.AnnData:
    """Extract numeric age from development_stage column.

    Parameters
    ----------
    pb_adata : AnnData
        Pseudobulk AnnData with 'development_stage' in obs

    Returns
    -------
    AnnData
        AnnData with 'age' column added to obs
    """
    ages = (
        pb_adata.obs["development_stage"].str.extract(r"(\d+)-year-old").astype(float)
    )
    pb_adata.obs["age"] = ages
    return pb_adata


def prepare_deseq_inputs(
    pb_adata: ad.AnnData,
    var_to_feature: dict | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Prepare counts and metadata for DESeq2.

    Parameters
    ----------
    pb_adata : AnnData
        Pseudobulk AnnData object
    var_to_feature : dict, optional
        Mapping from var_names to feature names

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        Counts dataframe and metadata dataframe
    """
    # Extract counts
    if var_to_feature is not None:
        columns = [var_to_feature.get(var, var) for var in pb_adata.var_names]
    else:
        columns = pb_adata.var_names.tolist()

    counts_df = pd.DataFrame(
        pb_adata.X.toarray(),
        index=pb_adata.obs_names,
        columns=columns,
    )
    # Remove duplicate columns
    counts_df = counts_df.loc[:, ~counts_df.columns.duplicated()]

    # Extract metadata
    metadata = pb_adata.obs.copy()

    # Scale continuous variables
    if "age" in metadata.columns:
        scaler = StandardScaler()
        metadata["age_scaled"] = scaler.fit_transform(metadata[["age"]]).flatten()
        metadata["age_scaled"] = metadata["age_scaled"].astype(float)
        print("Age scaling applied:")
        print(metadata[["age", "age_scaled"]].head())

    return counts_df, metadata


def subset_by_cell_type(
    pb_adata: ad.AnnData,
    counts_df: pd.DataFrame,
    metadata: pd.DataFrame,
    cell_type: str,
) -> tuple[ad.AnnData, pd.DataFrame, pd.DataFrame]:
    """Subset data to a specific cell type.

    Parameters
    ----------
    pb_adata : AnnData
        Pseudobulk AnnData object
    counts_df : pd.DataFrame
        Counts dataframe
    metadata : pd.DataFrame
        Metadata dataframe
    cell_type : str
        Cell type to subset to

    Returns
    -------
    tuple[AnnData, pd.DataFrame, pd.DataFrame]
        Subsetted AnnData, counts, and metadata
    """
    pb_adata_ct = pb_adata[pb_adata.obs["cell_type"] == cell_type].copy()
    counts_df_ct = counts_df.loc[pb_adata_ct.obs_names].copy()
    metadata_ct = metadata.loc[pb_adata_ct.obs_names].copy()

    return pb_adata_ct, counts_df_ct, metadata_ct


def run_deseq2(
    counts_df: pd.DataFrame,
    metadata: pd.DataFrame,
    design_factors: list[str],
    n_cpus: int = 2,
) -> DeseqDataSet:
    """Initialize and fit DESeq2 model.

    Parameters
    ----------
    counts_df : pd.DataFrame
        Counts dataframe
    metadata : pd.DataFrame
        Metadata dataframe
    design_factors : list[str]
        Design factors for the model
    n_cpus : int
        Number of CPUs for parallel processing

    Returns
    -------
    DeseqDataSet
        Fitted DESeq2 dataset
    """
    # Validate required columns
    for factor in design_factors:
        assert factor in metadata.columns, f"{factor} column missing in metadata"

    # Initialize and fit
    dds = DeseqDataSet(
        counts=counts_df,
        metadata=metadata,
        design_factors=design_factors,
        refit_cooks=True,
        n_cpus=n_cpus,
    )
    dds.deseq2()

    return dds


def run_wald_test(
    dds: DeseqDataSet,
    contrast: np.ndarray | None = None,
) -> DeseqStats:
    """Run Wald test for differential expression.

    Parameters
    ----------
    dds : DeseqDataSet
        Fitted DESeq2 dataset
    contrast : np.ndarray, optional
        Contrast vector for the test

    Returns
    -------
    DeseqStats
        Statistics results object
    """
    model_vars = dds.varm["LFC"].columns
    print(f"Model variables: {model_vars.tolist()}")

    if contrast is None:
        # Default: test second variable (typically age_scaled)
        contrast = np.zeros(len(model_vars))
        contrast[1] = 1

    print(f"Contrast: {contrast}")

    stat_res = DeseqStats(dds, contrast=contrast)
    stat_res.summary()
    stat_res.run_wald_test()

    return stat_res


def get_significant_genes(
    stat_res: DeseqStats,
    padj_threshold: float = 0.05,
) -> pd.DataFrame:
    """Extract significant genes from DESeq2 results.

    Parameters
    ----------
    stat_res : DeseqStats
        DESeq2 statistics results
    padj_threshold : float
        Adjusted p-value threshold

    Returns
    -------
    pd.DataFrame
        Significant genes sorted by log2 fold change
    """
    res = stat_res.results_df
    sigs = res[res["padj"] < padj_threshold]
    sigs = sigs.sort_values("log2FoldChange", ascending=False)

    print(f"Found {len(sigs)} significant genes.")
    print(sigs[["log2FoldChange", "padj"]].head())

    return sigs


def run_differential_expression_pipeline(
    pb_adata: ad.AnnData,
    cell_type: str,
    design_factors: list[str] | None = None,
    var_to_feature: dict | None = None,
    n_cpus: int = 8,
) -> tuple[DeseqStats, pd.DataFrame, pd.DataFrame]:
    """Run complete differential expression pipeline for a cell type.

    Parameters
    ----------
    pb_adata : AnnData
        Pseudobulk AnnData object
    cell_type : str
        Cell type to analyze
    design_factors : list[str], optional
        Design factors (default: ['age_scaled', 'sex'])
    var_to_feature : dict, optional
        Mapping from var_names to feature names
    n_cpus : int
        Number of CPUs

    Returns
    -------
    tuple[DeseqStats, pd.DataFrame, pd.DataFrame]
        Statistics results, full results dataframe, and counts dataframe
    """
    if design_factors is None:
        design_factors = ["age_scaled", "sex"]

    # Extract age
    pb_adata = extract_age_from_development_stage(pb_adata)

    # Prepare inputs
    counts_df, metadata = prepare_deseq_inputs(pb_adata, var_to_feature)

    # Subset to cell type
    _, counts_df_ct, metadata_ct = subset_by_cell_type(
        pb_adata, counts_df, metadata, cell_type
    )

    print(f"Running DE analysis for cell type: {cell_type}")
    print(f"Number of samples: {len(counts_df_ct)}")

    # Run DESeq2
    dds = run_deseq2(counts_df_ct, metadata_ct, design_factors, n_cpus)

    # Run Wald test
    stat_res = run_wald_test(dds)

    # Get significant genes
    _ = get_significant_genes(stat_res)

    return stat_res, stat_res.results_df, counts_df_ct
