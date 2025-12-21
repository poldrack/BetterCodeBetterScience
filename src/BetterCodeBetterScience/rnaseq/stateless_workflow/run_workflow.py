"""Stateless workflow runner for scRNA-seq immune aging analysis.

This script orchestrates the complete analysis workflow using checkpointing
to enable stateless execution and resumption from any step.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

from BetterCodeBetterScience.rnaseq.modular_workflow.clustering import (
    run_clustering_pipeline,
)
from BetterCodeBetterScience.rnaseq.modular_workflow.data_filtering import (
    run_filtering_pipeline,
)
from BetterCodeBetterScience.rnaseq.modular_workflow.data_loading import (
    download_data,
    load_lazy_anndata,
)
from BetterCodeBetterScience.rnaseq.modular_workflow.differential_expression import (
    run_differential_expression_pipeline,
)
from BetterCodeBetterScience.rnaseq.modular_workflow.dimensionality_reduction import (
    run_dimensionality_reduction_pipeline,
)
from BetterCodeBetterScience.rnaseq.modular_workflow.overrepresentation_analysis import (
    run_overrepresentation_pipeline,
)
from BetterCodeBetterScience.rnaseq.modular_workflow.pathway_analysis import (
    run_gsea_pipeline,
)
from BetterCodeBetterScience.rnaseq.modular_workflow.predictive_modeling import (
    run_predictive_modeling_pipeline,
)
from BetterCodeBetterScience.rnaseq.modular_workflow.preprocessing import (
    run_preprocessing_pipeline,
)
from BetterCodeBetterScience.rnaseq.modular_workflow.pseudobulk import (
    run_pseudobulk_pipeline,
)
from BetterCodeBetterScience.rnaseq.modular_workflow.quality_control import (
    run_qc_pipeline,
)
from BetterCodeBetterScience.rnaseq.stateless_workflow.checkpoint import (
    clear_checkpoints_from_step,
    run_with_checkpoint,
    run_with_checkpoint_multi,
)
from BetterCodeBetterScience.rnaseq.stateless_workflow.execution_log import (
    ExecutionLog,
    create_execution_log,
    serialize_parameters,
)


def _run_differential_expression_as_dict(
    pb_adata,
    cell_type,
    design_factors,
    var_to_feature,
    n_cpus,
):
    """Wrapper to return DE results as dict for checkpointing."""
    stat_res, de_results, counts_df = run_differential_expression_pipeline(
        pb_adata,
        cell_type=cell_type,
        design_factors=design_factors,
        var_to_feature=var_to_feature,
        n_cpus=n_cpus,
    )
    return {
        "stat_res": stat_res,
        "de_results": de_results,
        "counts_df": counts_df,
    }


def _run_overrepresentation_as_dict(
    de_results,
    gene_sets,
    padj_threshold,
    n_top,
    figure_dir,
):
    """Wrapper to return enrichment results as dict for checkpointing."""
    enr_up, enr_down = run_overrepresentation_pipeline(
        de_results,
        gene_sets=gene_sets,
        padj_threshold=padj_threshold,
        n_top=n_top,
        figure_dir=figure_dir,
    )
    return {
        "enr_up": enr_up,
        "enr_down": enr_down,
    }


def run_stateless_workflow(
    datadir: Path,
    dataset_name: str = "OneK1K",
    url: str = "https://datasets.cellxgene.cziscience.com/a3f5651f-cd1a-4d26-8165-74964b79b4f2.h5ad",
    cell_type_for_de: str = "central memory CD4-positive, alpha-beta T cell",
    force_from_step: int | None = None,
) -> dict:
    """Run the complete immune aging scRNA-seq analysis workflow with checkpointing.

    Each step saves its output to a checkpoint file. On subsequent runs,
    completed steps are skipped by loading from checkpoints.

    Parameters
    ----------
    datadir : Path
        Base directory for data files
    dataset_name : str
        Name of the dataset
    url : str
        URL to download data from
    cell_type_for_de : str
        Cell type to use for differential expression
    force_from_step : int, optional
        If provided, clears checkpoints from this step onwards and re-runs

    Returns
    -------
    dict
        Dictionary containing all results
    """
    # Setup directories
    figure_dir = datadir / "workflow/figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    checkpoint_dir = datadir / "workflow/checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    log_dir = datadir / "workflow/logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Clear downstream checkpoints if forcing re-run
    if force_from_step is not None:
        print(f"\nClearing checkpoints from step {force_from_step} onwards...")
        clear_checkpoints_from_step(checkpoint_dir, force_from_step)

    # Initialize execution log
    execution_log = create_execution_log(
        workflow_name="immune_aging_scrnaseq",
        workflow_parameters=serialize_parameters(
            datadir=datadir,
            dataset_name=dataset_name,
            url=url,
            cell_type_for_de=cell_type_for_de,
            force_from_step=force_from_step,
        ),
    )

    results = {}
    error_occurred = None

    try:
        # =====================================================================
        # STEP 1: Data Download
        # =====================================================================
        print("\n" + "=" * 60)
        print("STEP 1: DATA DOWNLOAD")
        print("=" * 60)

        datafile = datadir / f"dataset-{dataset_name}_subset-immune_raw.h5ad"

        # Log step 1 manually (no checkpoint wrapper for download)
        step1_record = execution_log.add_step(
            step_number=1,
            step_name="data_download",
            parameters=serialize_parameters(datafile=datafile, url=url),
        )
        download_data(datafile, url)
        execution_log.complete_step(
            step1_record, from_cache=datafile.exists(), error_message=None
        )

        # =====================================================================
        # STEP 2: Data Filtering
        # =====================================================================
        print("\n" + "=" * 60)
        print("STEP 2: DATA FILTERING")
        print("=" * 60)

        step2_params = {
            "cutoff_percentile": 1.0,
            "min_cells_per_celltype": 10,
            "percent_donors": 0.95,
        }

        def _load_and_filter():
            adata = load_lazy_anndata(datafile)
            print(f"Loaded dataset: {adata}")
            return run_filtering_pipeline(
                adata,
                cutoff_percentile=step2_params["cutoff_percentile"],
                min_cells_per_celltype=step2_params["min_cells_per_celltype"],
                percent_donors=step2_params["percent_donors"],
                figure_dir=figure_dir,
            )

        adata = run_with_checkpoint(
            "filtering",
            checkpoint_dir / "step02_filtered.h5ad",
            _load_and_filter,
            execution_log=execution_log,
            step_number=2,
            log_parameters=step2_params,
        )
        print(f"Dataset after filtering: {adata}")

        # Build var_to_feature mapping
        var_to_feature = dict(zip(adata.var_names, adata.var["feature_name"]))

        # =====================================================================
        # STEP 3: Quality Control
        # =====================================================================
        print("\n" + "=" * 60)
        print("STEP 3: QUALITY CONTROL")
        print("=" * 60)

        step3_params = {
            "min_genes": 200,
            "max_genes": 6000,
            "min_counts": 500,
            "max_counts": 30000,
            "max_hb_pct": 5.0,
            "expected_doublet_rate": 0.06,
        }

        adata = run_with_checkpoint(
            "quality_control",
            checkpoint_dir / "step03_qc.h5ad",
            run_qc_pipeline,
            adata,
            min_genes=step3_params["min_genes"],
            max_genes=step3_params["max_genes"],
            min_counts=step3_params["min_counts"],
            max_counts=step3_params["max_counts"],
            max_hb_pct=step3_params["max_hb_pct"],
            expected_doublet_rate=step3_params["expected_doublet_rate"],
            figure_dir=figure_dir,
            execution_log=execution_log,
            step_number=3,
            log_parameters=step3_params,
        )
        print(f"Dataset after QC: {adata}")

        # =====================================================================
        # STEP 4: Preprocessing
        # =====================================================================
        print("\n" + "=" * 60)
        print("STEP 4: PREPROCESSING")
        print("=" * 60)

        step4_params = {
            "target_sum": 1e4,
            "n_top_genes": 3000,
            "batch_key": "donor_id",
        }

        adata = run_with_checkpoint(
            "preprocessing",
            checkpoint_dir / "step04_preprocessed.h5ad",
            run_preprocessing_pipeline,
            adata,
            target_sum=step4_params["target_sum"],
            n_top_genes=step4_params["n_top_genes"],
            batch_key=step4_params["batch_key"],
            execution_log=execution_log,
            step_number=4,
            log_parameters=step4_params,
        )

        # =====================================================================
        # STEP 5: Dimensionality Reduction
        # =====================================================================
        print("\n" + "=" * 60)
        print("STEP 5: DIMENSIONALITY REDUCTION")
        print("=" * 60)

        step5_params = {
            "batch_key": "donor_id",
            "n_neighbors": 30,
            "n_pcs": 40,
        }

        adata = run_with_checkpoint(
            "dimensionality_reduction",
            checkpoint_dir / "step05_dimreduced.h5ad",
            run_dimensionality_reduction_pipeline,
            adata,
            batch_key=step5_params["batch_key"],
            n_neighbors=step5_params["n_neighbors"],
            n_pcs=step5_params["n_pcs"],
            figure_dir=figure_dir,
            execution_log=execution_log,
            step_number=5,
            log_parameters=step5_params,
        )

        # =====================================================================
        # STEP 6: Clustering
        # =====================================================================
        print("\n" + "=" * 60)
        print("STEP 6: CLUSTERING")
        print("=" * 60)

        step6_params = {"resolution": 1.0}

        adata = run_with_checkpoint(
            "clustering",
            checkpoint_dir / "step06_clustered.h5ad",
            run_clustering_pipeline,
            adata,
            resolution=step6_params["resolution"],
            figure_dir=figure_dir,
            execution_log=execution_log,
            step_number=6,
            log_parameters=step6_params,
        )

        results["adata"] = adata

        # =====================================================================
        # STEP 7: Pseudobulking
        # =====================================================================
        print("\n" + "=" * 60)
        print("STEP 7: PSEUDOBULKING")
        print("=" * 60)

        step7_params = {
            "group_col": "cell_type",
            "donor_col": "donor_id",
            "metadata_cols": ["development_stage", "sex"],
            "min_cells": 10,
        }

        pb_adata = run_with_checkpoint(
            "pseudobulking",
            checkpoint_dir / "step07_pseudobulk.h5ad",
            run_pseudobulk_pipeline,
            adata,
            group_col=step7_params["group_col"],
            donor_col=step7_params["donor_col"],
            metadata_cols=step7_params["metadata_cols"],
            min_cells=step7_params["min_cells"],
            figure_dir=figure_dir,
            execution_log=execution_log,
            step_number=7,
            log_parameters=step7_params,
        )

        results["pb_adata"] = pb_adata

        # =====================================================================
        # STEP 8: Differential Expression
        # =====================================================================
        print("\n" + "=" * 60)
        print("STEP 8: DIFFERENTIAL EXPRESSION")
        print("=" * 60)

        step8_params = {
            "cell_type": cell_type_for_de,
            "design_factors": ["age_scaled", "sex"],
            "n_cpus": 8,
        }

        de_outputs = run_with_checkpoint_multi(
            "differential_expression",
            {
                "stat_res": checkpoint_dir / "step08_stat_res.pkl",
                "de_results": checkpoint_dir / "step08_de_results.parquet",
                "counts_df": checkpoint_dir / "step08_counts.parquet",
            },
            _run_differential_expression_as_dict,
            pb_adata,
            cell_type=step8_params["cell_type"],
            design_factors=step8_params["design_factors"],
            var_to_feature=var_to_feature,
            n_cpus=step8_params["n_cpus"],
            execution_log=execution_log,
            step_number=8,
            log_parameters=step8_params,
        )

        de_results = de_outputs["de_results"]
        counts_df_ct = de_outputs["counts_df"]

        results["stat_res"] = de_outputs["stat_res"]
        results["de_results"] = de_results
        results["counts_df"] = counts_df_ct

        # =====================================================================
        # STEP 9: Pathway Analysis (GSEA)
        # =====================================================================
        print("\n" + "=" * 60)
        print("STEP 9: PATHWAY ANALYSIS (GSEA)")
        print("=" * 60)

        step9_params = {
            "gene_sets": ["MSigDB_Hallmark_2020"],
            "n_top": 10,
        }

        gsea_results = run_with_checkpoint(
            "gsea",
            checkpoint_dir / "step09_gsea.pkl",
            run_gsea_pipeline,
            de_results,
            gene_sets=step9_params["gene_sets"],
            n_top=step9_params["n_top"],
            figure_dir=figure_dir,
            execution_log=execution_log,
            step_number=9,
            log_parameters=step9_params,
        )

        results["gsea"] = gsea_results

        # =====================================================================
        # STEP 10: Overrepresentation Analysis (Enrichr)
        # =====================================================================
        print("\n" + "=" * 60)
        print("STEP 10: OVERREPRESENTATION ANALYSIS (Enrichr)")
        print("=" * 60)

        step10_params = {
            "gene_sets": ["MSigDB_Hallmark_2020"],
            "padj_threshold": 0.05,
            "n_top": 10,
        }

        enr_outputs = run_with_checkpoint_multi(
            "overrepresentation",
            {
                "enr_up": checkpoint_dir / "step10_enr_up.pkl",
                "enr_down": checkpoint_dir / "step10_enr_down.pkl",
            },
            _run_overrepresentation_as_dict,
            de_results,
            gene_sets=step10_params["gene_sets"],
            padj_threshold=step10_params["padj_threshold"],
            n_top=step10_params["n_top"],
            figure_dir=figure_dir,
            execution_log=execution_log,
            step_number=10,
            log_parameters=step10_params,
        )

        results["enrichr_up"] = enr_outputs["enr_up"]
        results["enrichr_down"] = enr_outputs["enr_down"]

        # =====================================================================
        # STEP 11: Predictive Modeling
        # =====================================================================
        print("\n" + "=" * 60)
        print("STEP 11: PREDICTIVE MODELING")
        print("=" * 60)

        # Get metadata for the cell type
        pb_adata_ct = pb_adata[pb_adata.obs["cell_type"] == cell_type_for_de].copy()
        pb_adata_ct.obs["age"] = (
            pb_adata_ct.obs["development_stage"]
            .str.extract(r"(\d+)-year-old")[0]
            .astype(float)
        )
        metadata_ct = pb_adata_ct.obs.copy()

        step11_params = {"n_splits": 5}

        prediction_results = run_with_checkpoint(
            "predictive_modeling",
            checkpoint_dir / "step11_prediction.pkl",
            run_predictive_modeling_pipeline,
            counts_df_ct,
            metadata_ct,
            n_splits=step11_params["n_splits"],
            figure_dir=figure_dir,
            execution_log=execution_log,
            step_number=11,
            log_parameters=step11_params,
        )

        results["prediction"] = prediction_results

    except Exception as e:
        error_occurred = str(e)
        raise

    finally:
        # Complete and save execution log
        execution_log.complete(error_message=error_occurred)
        log_file = execution_log.save(log_dir)
        execution_log.print_summary()
        print(f"\nExecution log saved to: {log_file}")

    print("\n" + "=" * 60)
    print("WORKFLOW COMPLETE")
    print("=" * 60)
    print(f"Figures saved to: {figure_dir}")
    print(f"Checkpoints saved to: {checkpoint_dir}")

    return results


def list_checkpoints(datadir: Path) -> list[tuple[str, Path]]:
    """List all checkpoint files in the workflow directory.

    Parameters
    ----------
    datadir : Path
        Base directory for data files

    Returns
    -------
    list[tuple[str, Path]]
        List of (step_name, file_path) tuples
    """
    checkpoint_dir = datadir / "workflow/checkpoints"
    if not checkpoint_dir.exists():
        return []

    checkpoints = []
    for filepath in sorted(checkpoint_dir.glob("step*")):
        step_name = (
            filepath.stem.split("_", 1)[1] if "_" in filepath.stem else filepath.stem
        )
        checkpoints.append((step_name, filepath))

    return checkpoints


def print_checkpoint_status(datadir: Path) -> None:
    """Print the status of all workflow checkpoints.

    Parameters
    ----------
    datadir : Path
        Base directory for data files
    """
    checkpoints = list_checkpoints(datadir)

    if not checkpoints:
        print("No checkpoints found.")
        return

    print("\nCheckpoint Status:")
    print("-" * 50)
    for step_name, filepath in checkpoints:
        size_mb = filepath.stat().st_size / (1024 * 1024)
        print(f"  {step_name:<30} ({size_mb:.1f} MB)")
    print("-" * 50)


def list_execution_logs(datadir: Path) -> list[Path]:
    """List all execution log files.

    Parameters
    ----------
    datadir : Path
        Base directory for data files

    Returns
    -------
    list[Path]
        List of log file paths, sorted by date (newest first)
    """
    log_dir = datadir / "workflow/logs"
    if not log_dir.exists():
        return []

    return sorted(log_dir.glob("execution_log_*.json"), reverse=True)


def load_execution_log(log_file: Path) -> ExecutionLog:
    """Load an execution log from a JSON file.

    Parameters
    ----------
    log_file : Path
        Path to the log file

    Returns
    -------
    ExecutionLog
        Loaded execution log
    """
    import json

    from BetterCodeBetterScience.rnaseq.stateless_workflow.execution_log import (
        StepRecord,
    )

    with open(log_file) as f:
        data = json.load(f)

    log = ExecutionLog(
        workflow_name=data["workflow_name"],
        run_id=data["run_id"],
        start_time=data["start_time"],
        end_time=data.get("end_time"),
        total_duration_seconds=data.get("total_duration_seconds"),
        status=data.get("status", "unknown"),
        workflow_parameters=data.get("workflow_parameters", {}),
    )

    for step_data in data.get("steps", []):
        step = StepRecord(
            step_number=step_data["step_number"],
            step_name=step_data["step_name"],
            start_time=step_data["start_time"],
            end_time=step_data.get("end_time"),
            duration_seconds=step_data.get("duration_seconds"),
            parameters=step_data.get("parameters", {}),
            from_cache=step_data.get("from_cache", False),
            status=step_data.get("status", "unknown"),
            checkpoint_file=step_data.get("checkpoint_file"),
            error_message=step_data.get("error_message"),
        )
        log.steps.append(step)

    return log


if __name__ == "__main__":
    load_dotenv()

    datadir_env = os.getenv("DATADIR")
    if datadir_env is None:
        raise ValueError("DATADIR environment variable not set")

    datadir = Path(datadir_env) / "immune_aging"

    # Print current checkpoint status
    print_checkpoint_status(datadir)

    # Show recent execution logs
    logs = list_execution_logs(datadir)
    if logs:
        print(f"\nRecent execution logs: {len(logs)} found")
        for log_path in logs[:3]:
            print(f"  {log_path.name}")

    # Run the workflow (will resume from last checkpoint)
    results = run_stateless_workflow(datadir)
