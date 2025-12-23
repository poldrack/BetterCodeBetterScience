"""Snakemake script for Step 11: Predictive Modeling."""

import json
from pathlib import Path

import pandas as pd

from BetterCodeBetterScience.rnaseq.modular_workflow.predictive_modeling import (
    run_predictive_modeling_pipeline,
)
from BetterCodeBetterScience.rnaseq.stateless_workflow.checkpoint import (
    load_checkpoint,
    save_checkpoint,
)


def unsanitize_cell_type(sanitized: str, cell_types_file: Path) -> str:
    """Convert sanitized cell type back to original name."""
    # ruff: noqa: F821
    with open(cell_types_file) as f:
        data = json.load(f)
    # Reverse lookup
    for original, sanitized_name in data["sanitized_names"].items():
        if sanitized_name == sanitized:
            return original
    raise ValueError(f"Unknown sanitized cell type: {sanitized}")


def main():
    """Run predictive modeling for a cell type."""
    counts_df_file = Path(snakemake.input.counts_df)
    pseudobulk_file = Path(snakemake.input.pseudobulk)
    cell_types_file = Path(snakemake.input.cell_types)
    output_file = Path(snakemake.output.prediction_results)

    # Get parameters
    sanitized_cell_type = snakemake.params.cell_type
    n_splits = snakemake.params.n_splits
    figure_dir = Path(snakemake.params.figure_dir)

    # Get original cell type name
    cell_type = unsanitize_cell_type(sanitized_cell_type, cell_types_file)

    print(f"Running predictive modeling for cell type: {cell_type}")

    # Create output directories
    output_file.parent.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)

    # Load counts
    counts_df = pd.read_parquet(counts_df_file)

    # Load pseudobulk to get metadata
    pb_adata = load_checkpoint(pseudobulk_file)

    # Get metadata for this cell type
    pb_adata_ct = pb_adata[pb_adata.obs["cell_type"] == cell_type].copy()
    pb_adata_ct.obs["age"] = (
        pb_adata_ct.obs["development_stage"]
        .str.extract(r"(\d+)-year-old")[0]
        .astype(float)
    )
    metadata = pb_adata_ct.obs.copy()

    # Run predictive modeling
    prediction_results = run_predictive_modeling_pipeline(
        counts_df,
        metadata,
        n_splits=n_splits,
        figure_dir=figure_dir,
    )

    # Save results
    save_checkpoint(prediction_results, output_file)
    print(f"Prediction results saved: {output_file}")


if __name__ == "__main__":
    main()
