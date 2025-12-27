"""Per-cell-type analysis rules (Steps 8-11).

These rules are triggered dynamically based on the cell types discovered
in the pseudobulk checkpoint (step 7). Each rule uses the {cell_type}
wildcard to process all valid cell types.

The workflow is:
- Step 8: Differential Expression (required first - provides DE results and counts)
- Step 9: Pathway Analysis (GSEA) - depends on DE results
- Step 10: Overrepresentation Analysis (Enrichr) - depends on DE results
- Step 11: Predictive Modeling - depends on counts from DE step
"""


# Step 8: Differential Expression (per cell type)
rule differential_expression:
    input:
        pseudobulk=CHECKPOINT_DIR / bids_checkpoint_name(DATASET, 7, "pseudobulk"),
        var_to_feature=CHECKPOINT_DIR / f"dataset-{DATASET}_step-07_var_to_feature.json",
        cell_types=CHECKPOINT_DIR / f"dataset-{DATASET}_step-07_cell_types.json",
    output:
        stat_res=RESULTS_DIR / "per_cell_type" / "{cell_type}" / "stat_res.pkl",
        de_results=RESULTS_DIR / "per_cell_type" / "{cell_type}" / "de_results.parquet",
        counts_df=RESULTS_DIR / "per_cell_type" / "{cell_type}" / "counts.parquet",
    params:
        cell_type=lambda wildcards: wildcards.cell_type,
        design_factors=config["differential_expression"]["design_factors"],
        n_cpus=config["differential_expression"]["n_cpus"],
    threads: config["differential_expression"]["n_cpus"]
    log:
        LOG_DIR / "step08_de_{cell_type}.log",
    script:
        "../scripts/differential_expression.py"


# Step 9: Pathway Analysis (GSEA) (per cell type)
rule pathway_analysis:
    input:
        de_results=RESULTS_DIR / "per_cell_type" / "{cell_type}" / "de_results.parquet",
    output:
        gsea_results=RESULTS_DIR / "per_cell_type" / "{cell_type}" / "gsea_results.pkl",
        fig_gsea=report(
            RESULTS_DIR / "per_cell_type" / "{cell_type}" / "figures" / "gsea_pathways.png",
            caption="../report/gsea.rst",
            category="Step 9: Pathway Analysis (GSEA)",
            subcategory="{cell_type}",
        ),
    params:
        cell_type=lambda wildcards: wildcards.cell_type,
        gene_sets=config["pathway_analysis"]["gene_sets"],
        n_top=config["pathway_analysis"]["n_top"],
        figure_dir=lambda wildcards: str(
            RESULTS_DIR / "per_cell_type" / wildcards.cell_type / "figures"
        ),
    log:
        LOG_DIR / "step09_gsea_{cell_type}.log",
    script:
        "../scripts/gsea.py"


# Step 10: Overrepresentation Analysis (Enrichr) (per cell type)
rule overrepresentation:
    input:
        de_results=RESULTS_DIR / "per_cell_type" / "{cell_type}" / "de_results.parquet",
    output:
        enr_up=RESULTS_DIR / "per_cell_type" / "{cell_type}" / "enrichr_up.pkl",
        enr_down=RESULTS_DIR / "per_cell_type" / "{cell_type}" / "enrichr_down.pkl",
        fig_enrichr=report(
            RESULTS_DIR / "per_cell_type" / "{cell_type}" / "figures" / "enrichr_pathways.png",
            caption="../report/enrichr.rst",
            category="Step 10: Overrepresentation Analysis",
            subcategory="{cell_type}",
        ),
    params:
        cell_type=lambda wildcards: wildcards.cell_type,
        gene_sets=config["overrepresentation"]["gene_sets"],
        padj_threshold=config["overrepresentation"]["padj_threshold"],
        n_top=config["overrepresentation"]["n_top"],
        figure_dir=lambda wildcards: str(
            RESULTS_DIR / "per_cell_type" / wildcards.cell_type / "figures"
        ),
    log:
        LOG_DIR / "step10_enrichr_{cell_type}.log",
    script:
        "../scripts/enrichr.py"


# Step 11: Predictive Modeling (per cell type)
rule predictive_modeling:
    input:
        counts_df=RESULTS_DIR / "per_cell_type" / "{cell_type}" / "counts.parquet",
        pseudobulk=CHECKPOINT_DIR / bids_checkpoint_name(DATASET, 7, "pseudobulk"),
        cell_types=CHECKPOINT_DIR / f"dataset-{DATASET}_step-07_cell_types.json",
    output:
        prediction_results=RESULTS_DIR
        / "per_cell_type"
        / "{cell_type}"
        / "prediction_results.pkl",
        fig_prediction=report(
            RESULTS_DIR / "per_cell_type" / "{cell_type}" / "figures" / "age_prediction_performance.png",
            caption="../report/prediction.rst",
            category="Step 11: Predictive Modeling",
            subcategory="{cell_type}",
        ),
    params:
        cell_type=lambda wildcards: wildcards.cell_type,
        n_splits=config["predictive_modeling"]["n_splits"],
        figure_dir=lambda wildcards: str(
            RESULTS_DIR / "per_cell_type" / wildcards.cell_type / "figures"
        ),
    log:
        LOG_DIR / "step11_prediction_{cell_type}.log",
    script:
        "../scripts/prediction.py"
