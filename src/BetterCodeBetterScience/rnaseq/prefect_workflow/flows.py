"""Prefect flow definitions for scRNA-seq workflow.

Main workflow flow that orchestrates all tasks.
"""

from pathlib import Path
from typing import Any

from prefect import flow, get_run_logger

from BetterCodeBetterScience.rnaseq.prefect_workflow.tasks import (
    clustering_task,
    differential_expression_task,
    dimensionality_reduction_task,
    download_data_task,
    load_and_filter_task,
    overrepresentation_task,
    pathway_analysis_task,
    predictive_modeling_task,
    preprocessing_task,
    pseudobulk_task,
    quality_control_task,
)
from BetterCodeBetterScience.rnaseq.stateless_workflow.checkpoint import (
    bids_checkpoint_name,
    load_checkpoint,
)


@flow(name="immune_aging_scrna_workflow", log_prints=True)
def run_workflow(
    datadir: Path,
    dataset_name: str = "OneK1K",
    url: str = "https://datasets.cellxgene.cziscience.com/a3f5651f-cd1a-4d26-8165-74964b79b4f2.h5ad",
    force_from_step: int | None = None,
    min_samples_per_cell_type: int = 10,
) -> dict[str, Any]:
    """Run the complete immune aging scRNA-seq workflow with Prefect.

    Steps 1-7 run sequentially (shared preprocessing).
    Steps 8-11 run in parallel for each cell type.

    Parameters
    ----------
    datadir : Path
        Base directory for data files
    dataset_name : str
        Name of the dataset
    url : str
        URL to download data from
    force_from_step : int, optional
        If provided, forces re-run from this step onwards
    min_samples_per_cell_type : int
        Minimum samples required per cell type to run steps 8-11

    Returns
    -------
    dict
        Dictionary containing all results organized by cell type
    """
    logger = get_run_logger()

    # Setup directories
    figure_dir = datadir / "workflow/figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    checkpoint_dir = datadir / "workflow/checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    results_dir = datadir / "workflow/results/per_cell_type"
    results_dir.mkdir(parents=True, exist_ok=True)

    # Determine which steps to force re-run
    force = {i: False for i in range(1, 12)}
    if force_from_step is not None:
        for i in range(force_from_step, 12):
            force[i] = True

    # =========================================================================
    # STEP 1: Data Download
    # =========================================================================
    logger.info("=" * 60)
    logger.info("STEP 1: DATA DOWNLOAD")
    logger.info("=" * 60)

    datafile = datadir / f"dataset-{dataset_name}_subset-immune_raw.h5ad"
    download_data_task(datafile, url)

    # =========================================================================
    # STEP 2: Data Filtering
    # =========================================================================
    logger.info("=" * 60)
    logger.info("STEP 2: DATA FILTERING")
    logger.info("=" * 60)

    adata = load_and_filter_task(
        datafile=datafile,
        checkpoint_file=checkpoint_dir
        / bids_checkpoint_name(dataset_name, 2, "filtered"),
        cutoff_percentile=1.0,
        min_cells_per_celltype=10,
        percent_donors=0.95,
        figure_dir=figure_dir,
        force=force[2],
    )

    # Build var_to_feature mapping
    var_to_feature = dict(zip(adata.var_names, adata.var["feature_name"]))

    # =========================================================================
    # STEP 3: Quality Control
    # =========================================================================
    logger.info("=" * 60)
    logger.info("STEP 3: QUALITY CONTROL")
    logger.info("=" * 60)

    adata = quality_control_task(
        adata=adata,
        checkpoint_file=checkpoint_dir / bids_checkpoint_name(dataset_name, 3, "qc"),
        min_genes=200,
        max_genes=6000,
        min_counts=500,
        max_counts=30000,
        max_hb_pct=5.0,
        expected_doublet_rate=0.06,
        figure_dir=figure_dir,
        force=force[3],
    )

    # =========================================================================
    # STEP 4: Preprocessing
    # =========================================================================
    logger.info("=" * 60)
    logger.info("STEP 4: PREPROCESSING")
    logger.info("=" * 60)

    adata = preprocessing_task(
        adata=adata,
        checkpoint_file=checkpoint_dir
        / bids_checkpoint_name(dataset_name, 4, "preprocessed"),
        target_sum=1e4,
        n_top_genes=3000,
        batch_key="donor_id",
        force=force[4],
    )

    # =========================================================================
    # STEP 5: Dimensionality Reduction
    # =========================================================================
    logger.info("=" * 60)
    logger.info("STEP 5: DIMENSIONALITY REDUCTION")
    logger.info("=" * 60)

    adata = dimensionality_reduction_task(
        adata=adata,
        checkpoint_file=checkpoint_dir
        / bids_checkpoint_name(dataset_name, 5, "dimreduced"),
        batch_key="donor_id",
        n_neighbors=30,
        n_pcs=40,
        figure_dir=figure_dir,
        force=force[5],
    )

    # =========================================================================
    # STEP 6: Clustering
    # =========================================================================
    logger.info("=" * 60)
    logger.info("STEP 6: CLUSTERING")
    logger.info("=" * 60)

    adata = clustering_task(
        adata=adata,
        checkpoint_file=checkpoint_dir
        / bids_checkpoint_name(dataset_name, 6, "clustered"),
        resolution=1.0,
        figure_dir=figure_dir,
        force=force[6],
    )

    # =========================================================================
    # STEP 7: Pseudobulking
    # =========================================================================
    logger.info("=" * 60)
    logger.info("STEP 7: PSEUDOBULKING")
    logger.info("=" * 60)

    # Load step 3 checkpoint for raw counts
    step3_checkpoint = checkpoint_dir / bids_checkpoint_name(dataset_name, 3, "qc")
    adata_raw_counts = load_checkpoint(step3_checkpoint)
    logger.info(f"Loaded raw counts from step 3: {adata_raw_counts.shape}")

    pb_adata = pseudobulk_task(
        adata=adata_raw_counts,
        checkpoint_file=checkpoint_dir
        / bids_checkpoint_name(dataset_name, 7, "pseudobulk"),
        group_col="cell_type",
        donor_col="donor_id",
        metadata_cols=["development_stage", "sex"],
        min_cells=10,
        figure_dir=figure_dir,
        layer=None,  # Use .X directly (raw counts)
        force=force[7],
    )

    # =========================================================================
    # STEPS 8-11: Per-Cell-Type Analysis (Parallel)
    # =========================================================================
    logger.info("=" * 60)
    logger.info("STEPS 8-11: PER-CELL-TYPE ANALYSIS")
    logger.info("=" * 60)

    # Get all cell types from pseudobulk
    cell_types = pb_adata.obs["cell_type"].unique().tolist()
    logger.info(f"Found {len(cell_types)} cell types to analyze")

    # Filter cell types with insufficient samples
    cell_type_counts = pb_adata.obs["cell_type"].value_counts()
    valid_cell_types = [
        ct for ct in cell_types if cell_type_counts[ct] >= min_samples_per_cell_type
    ]
    skipped_cell_types = [ct for ct in cell_types if ct not in valid_cell_types]

    if skipped_cell_types:
        logger.warning(
            f"Skipping {len(skipped_cell_types)} cell types with < {min_samples_per_cell_type} samples: "
            f"{skipped_cell_types}"
        )

    logger.info(f"Analyzing {len(valid_cell_types)} cell types")

    # Step 8: Submit all DE tasks in parallel
    logger.info("Submitting differential expression tasks...")
    de_futures = {}
    for cell_type in valid_cell_types:
        de_futures[cell_type] = differential_expression_task.submit(
            pb_adata=pb_adata,
            cell_type=cell_type,
            var_to_feature=var_to_feature,
            output_dir=results_dir,
            design_factors=["age_scaled", "sex"],
            n_cpus=4,  # Reduced per-task to allow parallelism
        )

    # Steps 9-11: Submit pathway/enrichment/prediction tasks as DE completes
    gsea_futures = {}
    enrichr_futures = {}
    prediction_futures = {}

    for cell_type in valid_cell_types:
        # Wait for DE to complete for this cell type
        de_result = de_futures[cell_type].result()

        # Get metadata for this cell type (for predictive modeling)
        pb_adata_ct = pb_adata[pb_adata.obs["cell_type"] == cell_type].copy()
        pb_adata_ct.obs["age"] = (
            pb_adata_ct.obs["development_stage"]
            .str.extract(r"(\d+)-year-old")[0]
            .astype(float)
        )
        metadata_ct = pb_adata_ct.obs.copy()

        # Submit steps 9, 10, 11 in parallel for this cell type
        gsea_futures[cell_type] = pathway_analysis_task.submit(
            de_results=de_result["de_results"],
            cell_type=cell_type,
            output_dir=results_dir,
            gene_sets=["MSigDB_Hallmark_2020"],
            n_top=10,
        )

        enrichr_futures[cell_type] = overrepresentation_task.submit(
            de_results=de_result["de_results"],
            cell_type=cell_type,
            output_dir=results_dir,
            gene_sets=["MSigDB_Hallmark_2020"],
            padj_threshold=0.05,
            n_top=10,
        )

        prediction_futures[cell_type] = predictive_modeling_task.submit(
            counts_df=de_result["counts_df"],
            metadata=metadata_ct,
            cell_type=cell_type,
            output_dir=results_dir,
            n_splits=5,
        )

    # Collect all results
    logger.info("Collecting results...")
    all_results = {
        "adata": adata,
        "pb_adata": pb_adata,
        "per_cell_type": {},
    }

    for cell_type in valid_cell_types:
        try:
            all_results["per_cell_type"][cell_type] = {
                "de": de_futures[cell_type].result(),
                "gsea": gsea_futures[cell_type].result(),
                "enrichment": enrichr_futures[cell_type].result(),
                "prediction": prediction_futures[cell_type].result(),
            }
            logger.info(f"Completed analysis for: {cell_type}")
        except Exception as e:
            logger.error(f"Failed analysis for {cell_type}: {e}")
            all_results["per_cell_type"][cell_type] = {"error": str(e)}

    # =========================================================================
    # Summary
    # =========================================================================
    logger.info("=" * 60)
    logger.info("WORKFLOW COMPLETE")
    logger.info("=" * 60)

    successful = sum(
        1
        for ct_results in all_results["per_cell_type"].values()
        if "error" not in ct_results
    )
    failed = len(valid_cell_types) - successful

    logger.info(
        f"Successfully analyzed: {successful}/{len(valid_cell_types)} cell types"
    )
    if failed > 0:
        logger.warning(f"Failed: {failed} cell types")

    logger.info(f"Figures saved to: {figure_dir}")
    logger.info(f"Checkpoints saved to: {checkpoint_dir}")
    logger.info(f"Per-cell-type results saved to: {results_dir}")

    return all_results


@flow(name="analyze_single_cell_type", log_prints=True)
def analyze_single_cell_type(
    datadir: Path,
    cell_type: str,
    dataset_name: str = "OneK1K",
) -> dict[str, Any]:
    """Run analysis for a single cell type (useful for debugging/testing).

    Requires that steps 1-7 have already been run.

    Parameters
    ----------
    datadir : Path
        Base directory for data files
    cell_type : str
        Cell type to analyze
    dataset_name : str
        Name of the dataset

    Returns
    -------
    dict
        Results for the specified cell type
    """
    logger = get_run_logger()

    checkpoint_dir = datadir / "workflow/checkpoints"
    results_dir = datadir / "workflow/results/per_cell_type"
    results_dir.mkdir(parents=True, exist_ok=True)

    # Load required checkpoints
    pb_adata = load_checkpoint(
        checkpoint_dir / bids_checkpoint_name(dataset_name, 7, "pseudobulk")
    )
    adata_filtered = load_checkpoint(
        checkpoint_dir / bids_checkpoint_name(dataset_name, 2, "filtered")
    )
    var_to_feature = dict(
        zip(adata_filtered.var_names, adata_filtered.var["feature_name"])
    )

    # Verify cell type exists
    available_cell_types = pb_adata.obs["cell_type"].unique().tolist()
    if cell_type not in available_cell_types:
        raise ValueError(
            f"Cell type '{cell_type}' not found. Available: {available_cell_types}"
        )

    logger.info(f"Analyzing cell type: {cell_type}")

    # Run DE
    de_result = differential_expression_task(
        pb_adata=pb_adata,
        cell_type=cell_type,
        var_to_feature=var_to_feature,
        output_dir=results_dir,
    )

    # Get metadata
    pb_adata_ct = pb_adata[pb_adata.obs["cell_type"] == cell_type].copy()
    pb_adata_ct.obs["age"] = (
        pb_adata_ct.obs["development_stage"]
        .str.extract(r"(\d+)-year-old")[0]
        .astype(float)
    )
    metadata_ct = pb_adata_ct.obs.copy()

    # Run parallel tasks
    gsea_future = pathway_analysis_task.submit(
        de_results=de_result["de_results"],
        cell_type=cell_type,
        output_dir=results_dir,
    )

    enrichr_future = overrepresentation_task.submit(
        de_results=de_result["de_results"],
        cell_type=cell_type,
        output_dir=results_dir,
    )

    prediction_future = predictive_modeling_task.submit(
        counts_df=de_result["counts_df"],
        metadata=metadata_ct,
        cell_type=cell_type,
        output_dir=results_dir,
    )

    return {
        "cell_type": cell_type,
        "de": de_result,
        "gsea": gsea_future.result(),
        "enrichment": enrichr_future.result(),
        "prediction": prediction_future.result(),
    }
