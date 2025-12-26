"""Main workflow runner for scRNA-seq immune aging analysis.

This script orchestrates the complete analysis workflow using the modular components.
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
    load_anndata,
    load_lazy_anndata,
    save_anndata,
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


def run_full_workflow(
    datadir: Path,
    dataset_name: str = "OneK1K",
    url: str = "https://datasets.cellxgene.cziscience.com/a3f5651f-cd1a-4d26-8165-74964b79b4f2.h5ad",
    cell_type_for_de: str = "central memory CD4-positive, alpha-beta T cell",
    skip_download: bool = False,
    skip_filtering: bool = False,
    skip_qc: bool = False,
) -> dict:
    """Run the complete immune aging scRNA-seq analysis workflow.

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
    skip_download : bool
        Skip data download step
    skip_filtering : bool
        Skip filtering, load pre-filtered data
    skip_qc : bool
        Skip QC, load post-QC data

    Returns
    -------
    dict
        Dictionary containing all results
    """
    # Setup directories
    figure_dir = datadir / "workflow/figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    # =====================================================================
    # STEP 1: Data Loading
    # =====================================================================
    print("\n" + "=" * 60)
    print("STEP 1: DATA LOADING")
    print("=" * 60)

    datafile = datadir / f"dataset-{dataset_name}_subset-immune_raw.h5ad"
    filtered_file = datadir / f"dataset-{dataset_name}_subset-immune_filtered.h5ad"

    if not skip_download:
        download_data(datafile, url)

    # =====================================================================
    # STEP 2: Data Filtering
    # =====================================================================
    print("\n" + "=" * 60)
    print("STEP 2: DATA FILTERING")
    print("=" * 60)

    if skip_filtering and filtered_file.exists():
        print("Loading pre-filtered data...")
        adata = load_anndata(filtered_file)
    else:
        adata = load_lazy_anndata(datafile)
        print(f"Loaded dataset: {adata}")

        adata = run_filtering_pipeline(
            adata,
            cutoff_percentile=1.0,
            min_cells_per_celltype=10,
            percent_donors=0.95,
            figure_dir=figure_dir,
        )

        # Save filtered data
        save_anndata(adata, filtered_file)
        print(f"Saved filtered data to {filtered_file}")

    print(f"Dataset after filtering: {adata}")

    # Build var_to_feature mapping
    var_to_feature = dict(zip(adata.var_names, adata.var["feature_name"]))

    # =====================================================================
    # STEP 3: Quality Control
    # =====================================================================
    print("\n" + "=" * 60)
    print("STEP 3: QUALITY CONTROL")
    print("=" * 60)

    qc_file = datadir / f"dataset-{dataset_name}_subset-immune_qc.h5ad"

    if skip_qc and qc_file.exists():
        print("Loading post-QC data...")
        adata = load_anndata(qc_file)
    else:
        adata = run_qc_pipeline(
            adata,
            min_genes=200,
            max_genes=6000,
            min_counts=500,
            max_counts=30000,
            max_hb_pct=5.0,
            expected_doublet_rate=0.06,
            figure_dir=figure_dir,
        )
        save_anndata(adata, qc_file)

    print(f"Dataset after QC: {adata}")

    # =====================================================================
    # STEP 4: Preprocessing
    # =====================================================================
    print("\n" + "=" * 60)
    print("STEP 4: PREPROCESSING")
    print("=" * 60)

    adata = run_preprocessing_pipeline(
        adata,
        target_sum=1e4,
        n_top_genes=3000,
        batch_key="donor_id",
    )

    # =====================================================================
    # STEP 5: Dimensionality Reduction
    # =====================================================================
    print("\n" + "=" * 60)
    print("STEP 5: DIMENSIONALITY REDUCTION")
    print("=" * 60)

    adata = run_dimensionality_reduction_pipeline(
        adata,
        batch_key="donor_id",
        n_neighbors=30,
        n_pcs=40,
        figure_dir=figure_dir,
    )

    # =====================================================================
    # STEP 6: Clustering
    # =====================================================================
    print("\n" + "=" * 60)
    print("STEP 6: CLUSTERING")
    print("=" * 60)

    adata = run_clustering_pipeline(
        adata,
        resolution=1.0,
        figure_dir=figure_dir,
    )

    results["adata"] = adata

    # =====================================================================
    # STEP 7: Pseudobulking
    # =====================================================================
    print("\n" + "=" * 60)
    print("STEP 7: PSEUDOBULKING")
    print("=" * 60)

    pb_adata = run_pseudobulk_pipeline(
        adata,
        group_col="cell_type",
        donor_col="donor_id",
        metadata_cols=["development_stage", "sex"],
        min_cells=10,
        figure_dir=figure_dir,
    )

    results["pb_adata"] = pb_adata

    # =====================================================================
    # STEP 8: Differential Expression
    # =====================================================================
    print("\n" + "=" * 60)
    print("STEP 8: DIFFERENTIAL EXPRESSION")
    print("=" * 60)

    stat_res, de_results, counts_df_ct = run_differential_expression_pipeline(
        pb_adata,
        cell_type=cell_type_for_de,
        design_factors=["age_scaled", "sex"],
        var_to_feature=var_to_feature,
        n_cpus=8,
    )

    results["de_results"] = de_results
    results["counts_df"] = counts_df_ct

    # =====================================================================
    # STEP 9: Pathway Analysis (GSEA)
    # =====================================================================
    print("\n" + "=" * 60)
    print("STEP 9: PATHWAY ANALYSIS (GSEA)")
    print("=" * 60)

    gsea_results = run_gsea_pipeline(
        de_results,
        gene_sets=["MSigDB_Hallmark_2020"],
        n_top=10,
        figure_dir=figure_dir,
    )

    results["gsea"] = gsea_results

    # =====================================================================
    # STEP 10: Overrepresentation Analysis (Enrichr)
    # =====================================================================
    print("\n" + "=" * 60)
    print("STEP 10: OVERREPRESENTATION ANALYSIS (Enrichr)")
    print("=" * 60)

    enr_up, enr_down = run_overrepresentation_pipeline(
        de_results,
        gene_sets=["MSigDB_Hallmark_2020"],
        padj_threshold=0.05,
        n_top=10,
        figure_dir=figure_dir,
    )

    results["enrichr_up"] = enr_up
    results["enrichr_down"] = enr_down

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

    prediction_results = run_predictive_modeling_pipeline(
        counts_df_ct,
        metadata_ct,
        n_splits=5,
        figure_dir=figure_dir,
    )

    results["prediction"] = prediction_results

    print("\n" + "=" * 60)
    print("WORKFLOW COMPLETE")
    print("=" * 60)
    print(f"Figures saved to: {figure_dir}")

    return results


if __name__ == "__main__":
    load_dotenv()

    datadir_env = os.getenv("DATADIR")
    if datadir_env is None:
        raise ValueError("DATADIR environment variable not set")

    datadir = Path(datadir_env) / "immune_aging"
    results = run_full_workflow(datadir)
