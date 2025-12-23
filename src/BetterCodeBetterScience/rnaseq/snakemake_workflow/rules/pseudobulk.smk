"""Pseudobulking rule (Step 7) - Uses Snakemake checkpoint for dynamic cell types.

This step aggregates single-cell data to pseudobulk samples per cell-type and donor.
It outputs a JSON file listing valid cell types, which enables dynamic downstream rules.

IMPORTANT: This uses 'checkpoint' instead of 'rule' because:
- The number of cell types is not known until this step completes
- Downstream rules (steps 8-11) need to run for each discovered cell type
- Snakemake's checkpoint mechanism re-evaluates the DAG after this step
"""


# Step 7: Pseudobulking (CHECKPOINT - enables dynamic per-cell-type rules)
checkpoint pseudobulk:
    input:
        # Step 2 provides feature_name column for var_to_feature mapping
        filtered_checkpoint=CHECKPOINT_DIR / bids_checkpoint_name(DATASET, 2, "filtered"),
        # Step 3 provides raw counts in .X (after QC filtering)
        qc_checkpoint=CHECKPOINT_DIR / bids_checkpoint_name(DATASET, 3, "qc"),
        # Step 6 listed for workflow ordering (ensures clustering completes first)
        clustered_checkpoint=CHECKPOINT_DIR / bids_checkpoint_name(DATASET, 6, "clustered"),
    output:
        # Main pseudobulk AnnData
        pseudobulk=CHECKPOINT_DIR / bids_checkpoint_name(DATASET, 7, "pseudobulk"),
        # JSON file listing valid cell types (enables dynamic downstream rules)
        cell_types=CHECKPOINT_DIR / f"dataset-{DATASET}_step-07_cell_types.json",
        # Gene name mapping (needed for DE analysis)
        var_to_feature=CHECKPOINT_DIR / f"dataset-{DATASET}_step-07_var_to_feature.json",
    params:
        group_col=config["pseudobulk"]["group_col"],
        donor_col=config["pseudobulk"]["donor_col"],
        metadata_cols=config["pseudobulk"]["metadata_cols"],
        min_cells=config["pseudobulk"]["min_cells"],
        min_samples_per_cell_type=config["min_samples_per_cell_type"],
        figure_dir=str(FIGURE_DIR),
    log:
        LOG_DIR / "step07_pseudobulk.log",
    script:
        "../scripts/pseudobulk.py"
