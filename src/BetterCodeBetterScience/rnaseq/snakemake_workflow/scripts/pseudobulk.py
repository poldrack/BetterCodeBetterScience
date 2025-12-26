"""Snakemake script for Step 7: Pseudobulking.

This script creates the pseudobulk data AND outputs a JSON file listing
all valid cell types, which enables downstream dynamic rules.
"""
# ruff: noqa: F821

import json
from pathlib import Path

from BetterCodeBetterScience.rnaseq.modular_workflow.pseudobulk import (
    run_pseudobulk_pipeline,
)
from BetterCodeBetterScience.rnaseq.stateless_workflow.checkpoint import (
    load_checkpoint,
    save_checkpoint,
)


def sanitize_cell_type(cell_type: str) -> str:
    """Sanitize cell type name for filesystem use."""
    return cell_type.replace(" ", "_").replace(",", "").replace("-", "_")


def main():
    """Run pseudobulking pipeline and output cell types JSON."""
    filtered_checkpoint = Path(snakemake.input.filtered_checkpoint)
    qc_checkpoint = Path(snakemake.input.qc_checkpoint)
    # Note: clustered_checkpoint is listed as input for dependency ordering
    output_pseudobulk = Path(snakemake.output.pseudobulk)
    output_cell_types = Path(snakemake.output.cell_types)
    output_var_to_feature = Path(snakemake.output.var_to_feature)

    # Get parameters
    group_col = snakemake.params.group_col
    donor_col = snakemake.params.donor_col
    metadata_cols = snakemake.params.metadata_cols
    min_cells = snakemake.params.min_cells
    min_samples_per_cell_type = snakemake.params.min_samples_per_cell_type
    figure_dir = (
        Path(snakemake.params.figure_dir) if snakemake.params.figure_dir else None
    )

    # Create output directories
    output_pseudobulk.parent.mkdir(parents=True, exist_ok=True)
    if figure_dir:
        figure_dir.mkdir(parents=True, exist_ok=True)

    # Load step 2 checkpoint to get var_to_feature mapping (has feature_name)
    print(f"Loading filtered data for var_to_feature: {filtered_checkpoint}")
    adata_filtered = load_checkpoint(filtered_checkpoint)
    var_to_feature = dict(
        zip(adata_filtered.var_names, adata_filtered.var["feature_name"])
    )
    print(f"Built var_to_feature mapping with {len(var_to_feature)} genes")

    # Load step 3 checkpoint for raw counts (after QC filtering)
    print(f"Loading raw counts from: {qc_checkpoint}")
    adata_raw = load_checkpoint(qc_checkpoint)
    print(f"Loaded: {adata_raw}")

    # Run pseudobulking on raw counts
    print("Running pseudobulking pipeline...")
    pb_adata = run_pseudobulk_pipeline(
        adata_raw,
        group_col=group_col,
        donor_col=donor_col,
        metadata_cols=metadata_cols,
        min_cells=min_cells,
        figure_dir=figure_dir,
        layer=None,  # Use .X directly (raw counts)
    )
    print(f"Pseudobulk data: {pb_adata}")

    # Save pseudobulk checkpoint
    save_checkpoint(pb_adata, output_pseudobulk)
    print(f"Saved pseudobulk checkpoint: {output_pseudobulk}")

    # Determine valid cell types (with sufficient samples)
    all_cell_types = pb_adata.obs[group_col].unique().tolist()
    cell_type_counts = pb_adata.obs[group_col].value_counts()

    valid_cell_types = [
        ct for ct in all_cell_types if cell_type_counts[ct] >= min_samples_per_cell_type
    ]
    skipped_cell_types = [ct for ct in all_cell_types if ct not in valid_cell_types]

    print(f"\nFound {len(all_cell_types)} cell types total")
    print(
        f"Valid cell types (>= {min_samples_per_cell_type} samples): {len(valid_cell_types)}"
    )
    if skipped_cell_types:
        print(f"Skipped cell types (insufficient samples): {skipped_cell_types}")

    # Write cell types JSON (enables dynamic rules)
    cell_types_data = {
        "all_cell_types": all_cell_types,
        "valid_cell_types": valid_cell_types,
        "skipped_cell_types": skipped_cell_types,
        "cell_type_counts": {str(k): int(v) for k, v in cell_type_counts.items()},
        "min_samples_threshold": min_samples_per_cell_type,
        # Include sanitized names for filesystem use
        "sanitized_names": {ct: sanitize_cell_type(ct) for ct in valid_cell_types},
    }

    with open(output_cell_types, "w") as f:
        json.dump(cell_types_data, f, indent=2)
    print(f"Saved cell types JSON: {output_cell_types}")

    # Write var_to_feature mapping (needed for DE)
    with open(output_var_to_feature, "w") as f:
        json.dump(var_to_feature, f)
    print(f"Saved var_to_feature mapping: {output_var_to_feature}")


if __name__ == "__main__":
    main()
