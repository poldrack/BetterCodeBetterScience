"""Snakemake script for Step 3: Quality Control."""

from pathlib import Path

from BetterCodeBetterScience.rnaseq.modular_workflow.quality_control import (
    run_qc_pipeline,
)
from BetterCodeBetterScience.rnaseq.stateless_workflow.checkpoint import (
    load_checkpoint,
    save_checkpoint,
)


def main():
    """Run quality control pipeline."""
    # ruff: noqa: F821
    input_file = Path(snakemake.input[0])
    output_file = Path(snakemake.output[0])

    # Get parameters
    min_genes = snakemake.params.min_genes
    max_genes = snakemake.params.max_genes
    min_counts = snakemake.params.min_counts
    max_counts = snakemake.params.max_counts
    max_hb_pct = snakemake.params.max_hb_pct
    expected_doublet_rate = snakemake.params.expected_doublet_rate
    figure_dir = (
        Path(snakemake.params.figure_dir) if snakemake.params.figure_dir else None
    )

    # Create output directories
    output_file.parent.mkdir(parents=True, exist_ok=True)
    if figure_dir:
        figure_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading data from: {input_file}")
    adata = load_checkpoint(input_file)
    print(f"Loaded dataset: {adata}")

    print("Running QC pipeline...")
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
    print(f"Dataset after QC: {adata}")

    # Save checkpoint
    save_checkpoint(adata, output_file)
    print(f"Saved checkpoint: {output_file}")


if __name__ == "__main__":
    main()
