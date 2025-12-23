"""Prefect flow definitions for scRNA-seq workflow.

Main workflow flow that orchestrates all tasks.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
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
from BetterCodeBetterScience.rnaseq.stateless_workflow.execution_log import (
    create_execution_log,
    serialize_parameters,
)


def get_default_config_path() -> Path:
    """Get the path to the default config file bundled with the package."""
    return Path(__file__).parent / "config" / "config.yaml"


def load_config(config_path: Path | None = None) -> dict[str, Any]:
    """Load workflow configuration from YAML file.

    Parameters
    ----------
    config_path : Path, optional
        Path to config file. If None, uses the default config bundled with the package.

    Returns
    -------
    dict
        Configuration dictionary
    """
    if config_path is None:
        config_path = get_default_config_path()

    with open(config_path) as f:
        return yaml.safe_load(f)


def setup_file_logging(log_dir: Path) -> tuple[Path, logging.FileHandler]:
    """Set up file-based logging for the workflow.

    Parameters
    ----------
    log_dir : Path
        Directory to save log files

    Returns
    -------
    tuple[Path, logging.FileHandler]
        Path to log file and the file handler (for cleanup)
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"prefect_workflow_{timestamp}.log"

    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)

    # Add handler to root logger to capture all logs
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)

    # Also add to prefect logger
    prefect_logger = logging.getLogger("prefect")
    prefect_logger.addHandler(file_handler)

    return log_file, file_handler


@flow(name="immune_aging_scrna_workflow", log_prints=False)
def run_workflow(
    datadir: Path,
    config_path: Path | None = None,
    force_from_step: int | None = None,
) -> dict[str, Any]:
    """Run the complete immune aging scRNA-seq workflow with Prefect.

    All steps run sequentially to minimize memory usage.

    Parameters
    ----------
    datadir : Path
        Base directory for data files
    config_path : Path, optional
        Path to config file. If None, uses the default config bundled with the package.
    force_from_step : int, optional
        If provided, forces re-run from this step onwards

    Returns
    -------
    dict
        Dictionary containing all results organized by cell type
    """
    logger = get_run_logger()

    # Load configuration
    config = load_config(config_path)
    dataset_name = config["dataset_name"]
    url = config["url"]
    min_samples_per_cell_type = config["min_samples_per_cell_type"]

    # Setup directories (using wf_prefect folder)
    figure_dir = datadir / "wf_prefect/figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    checkpoint_dir = datadir / "wf_prefect/checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    results_dir = datadir / "wf_prefect/results/per_cell_type"
    results_dir.mkdir(parents=True, exist_ok=True)

    log_dir = datadir / "wf_prefect/logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Set up file logging
    log_file, file_handler = setup_file_logging(log_dir)
    logger.info(f"Logging to file: {log_file}")

    # Initialize execution log for structured tracking
    execution_log = create_execution_log(
        workflow_name="immune_aging_scrnaseq_prefect",
        workflow_parameters=serialize_parameters(
            datadir=datadir,
            dataset_name=dataset_name,
            url=url,
            force_from_step=force_from_step,
            min_samples_per_cell_type=min_samples_per_cell_type,
        ),
    )

    # Determine which steps to force re-run
    force = {i: False for i in range(1, 12)}
    if force_from_step is not None:
        for i in range(force_from_step, 12):
            force[i] = True

    error_occurred = None

    try:
        # =====================================================================
        # STEP 1: Data Download
        # =====================================================================
        logger.info("=" * 60)
        logger.info("STEP 1: DATA DOWNLOAD")
        logger.info("=" * 60)

        step_record = execution_log.add_step(
            step_number=1,
            step_name="data_download",
            parameters=serialize_parameters(url=url),
        )
        datafile = datadir / f"dataset-{dataset_name}_subset-immune_raw.h5ad"
        download_data_task(datafile, url)
        execution_log.complete_step(step_record, from_cache=datafile.exists())

        # =====================================================================
        # STEP 2: Data Filtering
        # =====================================================================
        logger.info("=" * 60)
        logger.info("STEP 2: DATA FILTERING")
        logger.info("=" * 60)

        step2_params = config["filtering"]
        step_record = execution_log.add_step(
            step_number=2,
            step_name="data_filtering",
            parameters=step2_params,
        )
        checkpoint_file = checkpoint_dir / bids_checkpoint_name(
            dataset_name, 2, "filtered"
        )
        from_cache = checkpoint_file.exists() and not force[2]
        adata = load_and_filter_task(
            datafile=datafile,
            checkpoint_file=checkpoint_file,
            cutoff_percentile=step2_params["cutoff_percentile"],
            min_cells_per_celltype=step2_params["min_cells_per_celltype"],
            percent_donors=step2_params["percent_donors"],
            figure_dir=figure_dir,
            force=force[2],
        )
        execution_log.complete_step(step_record, from_cache=from_cache)

        # Build var_to_feature mapping
        var_to_feature = dict(zip(adata.var_names, adata.var["feature_name"]))

        # =====================================================================
        # STEP 3: Quality Control
        # =====================================================================
        logger.info("=" * 60)
        logger.info("STEP 3: QUALITY CONTROL")
        logger.info("=" * 60)

        step3_params = config["qc"]
        step_record = execution_log.add_step(
            step_number=3,
            step_name="quality_control",
            parameters=step3_params,
        )
        checkpoint_file = checkpoint_dir / bids_checkpoint_name(dataset_name, 3, "qc")
        from_cache = checkpoint_file.exists() and not force[3]
        adata = quality_control_task(
            adata=adata,
            checkpoint_file=checkpoint_file,
            min_genes=step3_params["min_genes"],
            max_genes=step3_params["max_genes"],
            min_counts=step3_params["min_counts"],
            max_counts=step3_params["max_counts"],
            max_hb_pct=step3_params["max_hb_pct"],
            expected_doublet_rate=step3_params["expected_doublet_rate"],
            figure_dir=figure_dir,
            force=force[3],
        )
        execution_log.complete_step(step_record, from_cache=from_cache)

        # =====================================================================
        # STEP 4: Preprocessing
        # =====================================================================
        logger.info("=" * 60)
        logger.info("STEP 4: PREPROCESSING")
        logger.info("=" * 60)

        step4_params = config["preprocessing"]
        step_record = execution_log.add_step(
            step_number=4,
            step_name="preprocessing",
            parameters=step4_params,
        )
        checkpoint_file = checkpoint_dir / bids_checkpoint_name(
            dataset_name, 4, "preprocessed"
        )
        from_cache = checkpoint_file.exists() and not force[4]
        adata = preprocessing_task(
            adata=adata,
            checkpoint_file=checkpoint_file,
            target_sum=step4_params["target_sum"],
            n_top_genes=step4_params["n_top_genes"],
            batch_key=step4_params["batch_key"],
            force=force[4],
        )
        execution_log.complete_step(step_record, from_cache=from_cache)

        # =====================================================================
        # STEP 5: Dimensionality Reduction
        # =====================================================================
        logger.info("=" * 60)
        logger.info("STEP 5: DIMENSIONALITY REDUCTION")
        logger.info("=" * 60)

        step5_params = config["dimred"]
        step_record = execution_log.add_step(
            step_number=5,
            step_name="dimensionality_reduction",
            parameters=step5_params,
        )
        checkpoint_file = checkpoint_dir / bids_checkpoint_name(
            dataset_name, 5, "dimreduced"
        )
        from_cache = checkpoint_file.exists() and not force[5]
        adata = dimensionality_reduction_task(
            adata=adata,
            checkpoint_file=checkpoint_file,
            batch_key=step5_params["batch_key"],
            n_neighbors=step5_params["n_neighbors"],
            n_pcs=step5_params["n_pcs"],
            figure_dir=figure_dir,
            force=force[5],
        )
        execution_log.complete_step(step_record, from_cache=from_cache)

        # =====================================================================
        # STEP 6: Clustering
        # =====================================================================
        logger.info("=" * 60)
        logger.info("STEP 6: CLUSTERING")
        logger.info("=" * 60)

        step6_params = config["clustering"]
        step_record = execution_log.add_step(
            step_number=6,
            step_name="clustering",
            parameters=step6_params,
        )
        checkpoint_file = checkpoint_dir / bids_checkpoint_name(
            dataset_name, 6, "clustered"
        )
        from_cache = checkpoint_file.exists() and not force[6]
        adata = clustering_task(
            adata=adata,
            checkpoint_file=checkpoint_file,
            resolution=step6_params["resolution"],
            figure_dir=figure_dir,
            force=force[6],
        )
        execution_log.complete_step(step_record, from_cache=from_cache)

        # =====================================================================
        # STEP 7: Pseudobulking
        # =====================================================================
        logger.info("=" * 60)
        logger.info("STEP 7: PSEUDOBULKING")
        logger.info("=" * 60)

        step7_params = config["pseudobulk"]
        step_record = execution_log.add_step(
            step_number=7,
            step_name="pseudobulking",
            parameters=step7_params,
        )
        # Load step 3 checkpoint for raw counts
        step3_checkpoint = checkpoint_dir / bids_checkpoint_name(dataset_name, 3, "qc")
        adata_raw_counts = load_checkpoint(step3_checkpoint)
        logger.info(f"Loaded raw counts from step 3: {adata_raw_counts.shape}")

        checkpoint_file = checkpoint_dir / bids_checkpoint_name(
            dataset_name, 7, "pseudobulk"
        )
        from_cache = checkpoint_file.exists() and not force[7]
        pb_adata = pseudobulk_task(
            adata=adata_raw_counts,
            checkpoint_file=checkpoint_file,
            group_col=step7_params["group_col"],
            donor_col=step7_params["donor_col"],
            metadata_cols=step7_params["metadata_cols"],
            min_cells=step7_params["min_cells"],
            figure_dir=figure_dir,
            layer=None,  # Use .X directly (raw counts)
            force=force[7],
        )
        execution_log.complete_step(step_record, from_cache=from_cache)

        # =====================================================================
        # STEPS 8-11: Per-Cell-Type Analysis (Sequential)
        # =====================================================================
        logger.info("=" * 60)
        logger.info("STEPS 8-11: PER-CELL-TYPE ANALYSIS (SEQUENTIAL)")
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
                f"Skipping {len(skipped_cell_types)} cell types with "
                f"< {min_samples_per_cell_type} samples: {skipped_cell_types}"
            )

        logger.info(f"Analyzing {len(valid_cell_types)} cell types sequentially")

        # Initialize results
        all_results = {
            "adata": adata,
            "pb_adata": pb_adata,
            "per_cell_type": {},
        }

        # Process each cell type sequentially
        for i, cell_type in enumerate(valid_cell_types):
            logger.info(f"\n[{i + 1}/{len(valid_cell_types)}] Processing: {cell_type}")

            # Get config for per-cell-type steps
            de_config = config["differential_expression"]
            gsea_config = config["pathway_analysis"]
            enrichr_config = config["overrepresentation"]
            pred_config = config["predictive_modeling"]

            # Log combined steps 8-11 for this cell type
            step_record = execution_log.add_step(
                step_number=8,
                step_name=f"per_cell_type_analysis ({cell_type})",
                parameters=serialize_parameters(
                    cell_type=cell_type,
                    design_factors=de_config["design_factors"],
                    gene_sets=gsea_config["gene_sets"],
                    n_splits=pred_config["n_splits"],
                ),
            )

            try:
                # Step 8: Differential Expression
                de_result = differential_expression_task(
                    pb_adata=pb_adata,
                    cell_type=cell_type,
                    var_to_feature=var_to_feature,
                    output_dir=results_dir,
                    design_factors=de_config["design_factors"],
                    n_cpus=de_config["n_cpus"],
                )

                # Get metadata for this cell type (for predictive modeling)
                pb_adata_ct = pb_adata[pb_adata.obs["cell_type"] == cell_type].copy()
                pb_adata_ct.obs["age"] = (
                    pb_adata_ct.obs["development_stage"]
                    .str.extract(r"(\d+)-year-old")[0]
                    .astype(float)
                )
                metadata_ct = pb_adata_ct.obs.copy()

                # Step 9: Pathway Analysis (GSEA)
                gsea_result = pathway_analysis_task(
                    de_results=de_result["de_results"],
                    cell_type=cell_type,
                    output_dir=results_dir,
                    gene_sets=gsea_config["gene_sets"],
                    n_top=gsea_config["n_top"],
                )

                # Step 10: Overrepresentation Analysis (Enrichr)
                enrichr_result = overrepresentation_task(
                    de_results=de_result["de_results"],
                    cell_type=cell_type,
                    output_dir=results_dir,
                    gene_sets=enrichr_config["gene_sets"],
                    padj_threshold=enrichr_config["padj_threshold"],
                    n_top=enrichr_config["n_top"],
                )

                # Step 11: Predictive Modeling
                prediction_result = predictive_modeling_task(
                    counts_df=de_result["counts_df"],
                    metadata=metadata_ct,
                    cell_type=cell_type,
                    output_dir=results_dir,
                    n_splits=pred_config["n_splits"],
                )

                all_results["per_cell_type"][cell_type] = {
                    "de": de_result,
                    "gsea": gsea_result,
                    "enrichment": enrichr_result,
                    "prediction": prediction_result,
                }
                logger.info(f"Completed analysis for: {cell_type}")
                execution_log.complete_step(step_record)

            except Exception as e:
                logger.error(f"Failed analysis for {cell_type}: {e}")
                all_results["per_cell_type"][cell_type] = {"error": str(e)}
                execution_log.complete_step(step_record, error_message=str(e))

        # =====================================================================
        # Summary
        # =====================================================================
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

    except Exception as e:
        error_occurred = str(e)
        raise

    finally:
        # Complete and save execution log
        execution_log.complete(error_message=error_occurred)
        execution_log_file = execution_log.save(log_dir)
        execution_log.print_summary()
        logger.info(f"Execution log saved to: {execution_log_file}")
        logger.info(f"Workflow log saved to: {log_file}")

        # Clean up file handler
        logging.getLogger().removeHandler(file_handler)
        logging.getLogger("prefect").removeHandler(file_handler)
        file_handler.close()

    return all_results


@flow(name="analyze_single_cell_type", log_prints=False)
def analyze_single_cell_type(
    datadir: Path,
    cell_type: str,
    config_path: Path | None = None,
) -> dict[str, Any]:
    """Run analysis for a single cell type (useful for debugging/testing).

    Requires that steps 1-7 have already been run.

    Parameters
    ----------
    datadir : Path
        Base directory for data files
    cell_type : str
        Cell type to analyze
    config_path : Path, optional
        Path to config file. If None, uses the default config bundled with the package.

    Returns
    -------
    dict
        Results for the specified cell type
    """
    logger = get_run_logger()

    # Load configuration
    config = load_config(config_path)
    dataset_name = config["dataset_name"]
    de_config = config["differential_expression"]
    gsea_config = config["pathway_analysis"]
    enrichr_config = config["overrepresentation"]
    pred_config = config["predictive_modeling"]

    checkpoint_dir = datadir / "wf_prefect/checkpoints"
    results_dir = datadir / "wf_prefect/results/per_cell_type"
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
        design_factors=de_config["design_factors"],
        n_cpus=de_config["n_cpus"],
    )

    # Get metadata
    pb_adata_ct = pb_adata[pb_adata.obs["cell_type"] == cell_type].copy()
    pb_adata_ct.obs["age"] = (
        pb_adata_ct.obs["development_stage"]
        .str.extract(r"(\d+)-year-old")[0]
        .astype(float)
    )
    metadata_ct = pb_adata_ct.obs.copy()

    # Run tasks sequentially
    gsea_result = pathway_analysis_task(
        de_results=de_result["de_results"],
        cell_type=cell_type,
        output_dir=results_dir,
        gene_sets=gsea_config["gene_sets"],
        n_top=gsea_config["n_top"],
    )

    enrichr_result = overrepresentation_task(
        de_results=de_result["de_results"],
        cell_type=cell_type,
        output_dir=results_dir,
        gene_sets=enrichr_config["gene_sets"],
        padj_threshold=enrichr_config["padj_threshold"],
        n_top=enrichr_config["n_top"],
    )

    prediction_result = predictive_modeling_task(
        counts_df=de_result["counts_df"],
        metadata=metadata_ct,
        cell_type=cell_type,
        output_dir=results_dir,
        n_splits=pred_config["n_splits"],
    )

    return {
        "cell_type": cell_type,
        "de": de_result,
        "gsea": gsea_result,
        "enrichment": enrichr_result,
        "prediction": prediction_result,
    }
