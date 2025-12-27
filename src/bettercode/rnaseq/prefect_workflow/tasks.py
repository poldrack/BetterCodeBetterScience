"""Prefect task definitions for scRNA-seq workflow.

Wraps modular workflow functions as Prefect tasks for orchestration.
"""

from pathlib import Path
from typing import Any

import anndata as ad
import pandas as pd
from prefect import task

from bettercode.rnaseq.modular_workflow.clustering import (
    run_clustering_pipeline,
)
from bettercode.rnaseq.modular_workflow.data_filtering import (
    run_filtering_pipeline,
)
from bettercode.rnaseq.modular_workflow.data_loading import (
    download_data,
    load_lazy_anndata,
)
from bettercode.rnaseq.modular_workflow.differential_expression import (
    run_differential_expression_pipeline,
)
from bettercode.rnaseq.modular_workflow.dimensionality_reduction import (
    run_dimensionality_reduction_pipeline,
)
from bettercode.rnaseq.modular_workflow.overrepresentation_analysis import (
    run_overrepresentation_pipeline,
)
from bettercode.rnaseq.modular_workflow.pathway_analysis import (
    run_gsea_pipeline,
)
from bettercode.rnaseq.modular_workflow.predictive_modeling import (
    run_predictive_modeling_pipeline,
)
from bettercode.rnaseq.modular_workflow.preprocessing import (
    run_preprocessing_pipeline,
)
from bettercode.rnaseq.modular_workflow.pseudobulk import (
    run_pseudobulk_pipeline,
)
from bettercode.rnaseq.modular_workflow.quality_control import (
    run_qc_pipeline,
)
from bettercode.rnaseq.stateless_workflow.checkpoint import (
    load_checkpoint,
    save_checkpoint,
)


@task(name="download_data", retries=2, retry_delay_seconds=30)
def download_data_task(datafile: Path, url: str) -> Path:
    """Download data file if it doesn't exist.

    Returns the datafile path for chaining.
    """
    download_data(datafile, url)
    return datafile


@task(name="load_and_filter")
def load_and_filter_task(
    datafile: Path,
    checkpoint_file: Path,
    cutoff_percentile: float = 1.0,
    min_cells_per_celltype: int = 10,
    percent_donors: float = 0.95,
    figure_dir: Path | None = None,
    force: bool = False,
) -> ad.AnnData:
    """Load data and run filtering pipeline with checkpointing."""
    if checkpoint_file.exists() and not force:
        print(f"Loading from checkpoint: {checkpoint_file.name}")
        return load_checkpoint(checkpoint_file)

    adata = load_lazy_anndata(datafile)
    print(f"Loaded dataset: {adata}")
    adata = run_filtering_pipeline(
        adata,
        cutoff_percentile=cutoff_percentile,
        min_cells_per_celltype=min_cells_per_celltype,
        percent_donors=percent_donors,
        figure_dir=figure_dir,
    )
    save_checkpoint(adata, checkpoint_file)
    return adata


@task(name="quality_control")
def quality_control_task(
    adata: ad.AnnData,
    checkpoint_file: Path,
    min_genes: int = 200,
    max_genes: int = 6000,
    min_counts: int = 500,
    max_counts: int = 30000,
    max_hb_pct: float = 5.0,
    expected_doublet_rate: float = 0.06,
    figure_dir: Path | None = None,
    force: bool = False,
) -> ad.AnnData:
    """Run quality control pipeline with checkpointing."""
    if checkpoint_file.exists() and not force:
        print(f"Loading from checkpoint: {checkpoint_file.name}")
        return load_checkpoint(checkpoint_file)

    adata = run_qc_pipeline(
        adata,
        min_genes=min_genes,
        max_genes=max_genes,
        min_counts=min_counts,
        max_counts=max_counts,
        max_hb_pct=max_hb_pct,
        expected_doublet_rate=expected_doublet_rate,
        figure_dir=figure_dir,
    )
    save_checkpoint(adata, checkpoint_file)
    return adata


@task(name="preprocessing")
def preprocessing_task(
    adata: ad.AnnData,
    checkpoint_file: Path,
    target_sum: float = 1e4,
    n_top_genes: int = 3000,
    batch_key: str = "donor_id",
    force: bool = False,
) -> ad.AnnData:
    """Run preprocessing pipeline with checkpointing."""
    if checkpoint_file.exists() and not force:
        print(f"Loading from checkpoint: {checkpoint_file.name}")
        return load_checkpoint(checkpoint_file)

    adata = run_preprocessing_pipeline(
        adata,
        target_sum=target_sum,
        n_top_genes=n_top_genes,
        batch_key=batch_key,
    )
    # Remove counts layer after preprocessing to save space
    if "counts" in adata.layers:
        del adata.layers["counts"]
        print("Removed counts layer to save checkpoint space")

    save_checkpoint(adata, checkpoint_file)
    return adata


@task(name="dimensionality_reduction")
def dimensionality_reduction_task(
    adata: ad.AnnData,
    checkpoint_file: Path,
    batch_key: str = "donor_id",
    n_neighbors: int = 30,
    n_pcs: int = 40,
    figure_dir: Path | None = None,
    force: bool = False,
) -> ad.AnnData:
    """Run dimensionality reduction pipeline with checkpointing."""
    if checkpoint_file.exists() and not force:
        print(f"Loading from checkpoint: {checkpoint_file.name}")
        return load_checkpoint(checkpoint_file)

    adata = run_dimensionality_reduction_pipeline(
        adata,
        batch_key=batch_key,
        n_neighbors=n_neighbors,
        n_pcs=n_pcs,
        figure_dir=figure_dir,
    )
    save_checkpoint(adata, checkpoint_file)
    return adata


@task(name="clustering")
def clustering_task(
    adata: ad.AnnData,
    checkpoint_file: Path,
    resolution: float = 1.0,
    figure_dir: Path | None = None,
    force: bool = False,
) -> ad.AnnData:
    """Run clustering pipeline with checkpointing."""
    if checkpoint_file.exists() and not force:
        print(f"Loading from checkpoint: {checkpoint_file.name}")
        return load_checkpoint(checkpoint_file)

    adata = run_clustering_pipeline(
        adata,
        resolution=resolution,
        figure_dir=figure_dir,
    )
    save_checkpoint(adata, checkpoint_file)
    return adata


@task(name="pseudobulk")
def pseudobulk_task(
    adata: ad.AnnData,
    checkpoint_file: Path,
    group_col: str = "cell_type",
    donor_col: str = "donor_id",
    metadata_cols: list[str] | None = None,
    min_cells: int = 10,
    figure_dir: Path | None = None,
    layer: str | None = None,
    force: bool = False,
) -> ad.AnnData:
    """Run pseudobulking pipeline with checkpointing."""
    if checkpoint_file.exists() and not force:
        print(f"Loading from checkpoint: {checkpoint_file.name}")
        return load_checkpoint(checkpoint_file)

    pb_adata = run_pseudobulk_pipeline(
        adata,
        group_col=group_col,
        donor_col=donor_col,
        metadata_cols=metadata_cols,
        min_cells=min_cells,
        figure_dir=figure_dir,
        layer=layer,
    )
    save_checkpoint(pb_adata, checkpoint_file)
    return pb_adata


@task(name="differential_expression", retries=1)
def differential_expression_task(
    pb_adata: ad.AnnData,
    cell_type: str,
    var_to_feature: dict[str, str],
    output_dir: Path,
    design_factors: list[str] | None = None,
    n_cpus: int = 8,
) -> dict[str, Any]:
    """Run differential expression for a specific cell type.

    Returns dict with stat_res, de_results, and counts_df.
    """
    print(f"\n{'=' * 60}")
    print(f"Running DE for cell type: {cell_type}")
    print(f"{'=' * 60}")

    stat_res, de_results, counts_df = run_differential_expression_pipeline(
        pb_adata,
        cell_type=cell_type,
        design_factors=design_factors,
        var_to_feature=var_to_feature,
        n_cpus=n_cpus,
    )

    # Save results to cell-type specific directory
    ct_dir = output_dir / _sanitize_cell_type(cell_type)
    ct_dir.mkdir(parents=True, exist_ok=True)

    save_checkpoint(stat_res, ct_dir / "stat_res.pkl")
    de_results.to_parquet(ct_dir / "de_results.parquet")
    counts_df.to_parquet(ct_dir / "counts.parquet")

    return {
        "cell_type": cell_type,
        "stat_res": stat_res,
        "de_results": de_results,
        "counts_df": counts_df,
    }


@task(name="pathway_analysis")
def pathway_analysis_task(
    de_results: pd.DataFrame,
    cell_type: str,
    output_dir: Path,
    gene_sets: list[str] | None = None,
    n_top: int = 10,
) -> dict[str, Any]:
    """Run GSEA pathway analysis for a cell type."""
    print(f"\n{'=' * 60}")
    print(f"Running GSEA for cell type: {cell_type}")
    print(f"{'=' * 60}")

    ct_dir = output_dir / _sanitize_cell_type(cell_type)
    ct_dir.mkdir(parents=True, exist_ok=True)
    figure_dir = ct_dir / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    gsea_results = run_gsea_pipeline(
        de_results,
        gene_sets=gene_sets,
        n_top=n_top,
        figure_dir=figure_dir,
    )

    save_checkpoint(gsea_results, ct_dir / "gsea_results.pkl")

    return {
        "cell_type": cell_type,
        "gsea_results": gsea_results,
    }


@task(name="overrepresentation")
def overrepresentation_task(
    de_results: pd.DataFrame,
    cell_type: str,
    output_dir: Path,
    gene_sets: list[str] | None = None,
    padj_threshold: float = 0.05,
    n_top: int = 10,
) -> dict[str, Any]:
    """Run Enrichr overrepresentation analysis for a cell type."""
    print(f"\n{'=' * 60}")
    print(f"Running Enrichr for cell type: {cell_type}")
    print(f"{'=' * 60}")

    ct_dir = output_dir / _sanitize_cell_type(cell_type)
    ct_dir.mkdir(parents=True, exist_ok=True)
    figure_dir = ct_dir / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    enr_up, enr_down = run_overrepresentation_pipeline(
        de_results,
        gene_sets=gene_sets,
        padj_threshold=padj_threshold,
        n_top=n_top,
        figure_dir=figure_dir,
    )

    save_checkpoint(enr_up, ct_dir / "enrichr_up.pkl")
    save_checkpoint(enr_down, ct_dir / "enrichr_down.pkl")

    return {
        "cell_type": cell_type,
        "enr_up": enr_up,
        "enr_down": enr_down,
    }


@task(name="predictive_modeling")
def predictive_modeling_task(
    counts_df: pd.DataFrame,
    metadata: pd.DataFrame,
    cell_type: str,
    output_dir: Path,
    n_splits: int = 5,
) -> dict[str, Any]:
    """Run predictive modeling for a cell type."""
    print(f"\n{'=' * 60}")
    print(f"Running predictive modeling for cell type: {cell_type}")
    print(f"{'=' * 60}")

    ct_dir = output_dir / _sanitize_cell_type(cell_type)
    ct_dir.mkdir(parents=True, exist_ok=True)
    figure_dir = ct_dir / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    prediction_results = run_predictive_modeling_pipeline(
        counts_df,
        metadata,
        n_splits=n_splits,
        figure_dir=figure_dir,
    )

    save_checkpoint(prediction_results, ct_dir / "prediction_results.pkl")

    return {
        "cell_type": cell_type,
        "prediction_results": prediction_results,
    }


def _sanitize_cell_type(cell_type: str) -> str:
    """Sanitize cell type name for use as directory name."""
    return cell_type.replace(" ", "_").replace(",", "").replace("-", "_")
