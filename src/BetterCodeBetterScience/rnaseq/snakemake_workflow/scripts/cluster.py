"""Snakemake script for Step 6: Clustering."""

from pathlib import Path

from BetterCodeBetterScience.rnaseq.modular_workflow.clustering import (
    run_clustering_pipeline,
)
from BetterCodeBetterScience.rnaseq.stateless_workflow.checkpoint import (
    load_checkpoint,
    save_checkpoint,
)


def main():
    """Run clustering pipeline."""
    # ruff: noqa: F821
    input_file = Path(snakemake.input[0])
    output_file = Path(snakemake.output[0])

    # Get parameters
    resolution = snakemake.params.resolution
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

    print("Running clustering pipeline...")
    adata = run_clustering_pipeline(
        adata,
        resolution=resolution,
        figure_dir=figure_dir,
    )

    # Save checkpoint
    save_checkpoint(adata, output_file)
    print(f"Saved checkpoint: {output_file}")


if __name__ == "__main__":
    main()
