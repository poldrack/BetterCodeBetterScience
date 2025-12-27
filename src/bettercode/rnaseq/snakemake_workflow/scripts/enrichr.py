"""Snakemake script for Step 10: Overrepresentation Analysis (Enrichr)."""

from pathlib import Path

import pandas as pd

from bettercode.rnaseq.modular_workflow.overrepresentation_analysis import (
    run_overrepresentation_pipeline,
)
from bettercode.rnaseq.stateless_workflow.checkpoint import save_checkpoint


def main():
    """Run Enrichr overrepresentation analysis for a cell type."""
    # ruff: noqa: F821
    de_results_file = Path(snakemake.input.de_results)
    output_enr_up = Path(snakemake.output.enr_up)
    output_enr_down = Path(snakemake.output.enr_down)

    # Get parameters
    cell_type = snakemake.params.cell_type
    gene_sets = snakemake.params.gene_sets
    padj_threshold = snakemake.params.padj_threshold
    n_top = snakemake.params.n_top
    figure_dir = Path(snakemake.params.figure_dir)

    print(f"Running Enrichr for cell type: {cell_type}")

    # Create output directories
    output_enr_up.parent.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)

    # Load DE results
    de_results = pd.read_parquet(de_results_file)

    # Run overrepresentation analysis
    enr_up, enr_down = run_overrepresentation_pipeline(
        de_results,
        gene_sets=gene_sets,
        padj_threshold=padj_threshold,
        n_top=n_top,
        figure_dir=figure_dir,
    )

    # Save results
    save_checkpoint(enr_up, output_enr_up)
    save_checkpoint(enr_down, output_enr_down)
    print("Enrichr results saved:")
    print(f"  - enr_up: {output_enr_up}")
    print(f"  - enr_down: {output_enr_down}")


if __name__ == "__main__":
    main()
