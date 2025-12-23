"""Snakemake script for Step 2: Data Filtering."""

from pathlib import Path

from BetterCodeBetterScience.rnaseq.modular_workflow.data_filtering import (
    run_filtering_pipeline,
)
from BetterCodeBetterScience.rnaseq.modular_workflow.data_loading import (
    load_lazy_anndata,
)
from BetterCodeBetterScience.rnaseq.stateless_workflow.checkpoint import save_checkpoint


def main():
    """Load data and run filtering pipeline."""
    # ruff: noqa: F821
    input_file = Path(snakemake.input[0])
    output_file = Path(snakemake.output[0])

    # Get parameters
    cutoff_percentile = snakemake.params.cutoff_percentile
    min_cells_per_celltype = snakemake.params.min_cells_per_celltype
    percent_donors = snakemake.params.percent_donors
    figure_dir = (
        Path(snakemake.params.figure_dir) if snakemake.params.figure_dir else None
    )

    print(f"Loading data from: {input_file}")
    adata = load_lazy_anndata(input_file)
    print(f"Loaded dataset: {adata}")

    print("Running filtering pipeline...")
    adata = run_filtering_pipeline(
        adata,
        cutoff_percentile=cutoff_percentile,
        min_cells_per_celltype=min_cells_per_celltype,
        percent_donors=percent_donors,
        figure_dir=figure_dir,
    )
    print(f"Dataset after filtering: {adata}")

    # Save checkpoint
    save_checkpoint(adata, output_file)
    print(f"Saved checkpoint: {output_file}")


if __name__ == "__main__":
    main()
