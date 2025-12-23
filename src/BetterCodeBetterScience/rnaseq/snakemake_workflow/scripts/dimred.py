"""Snakemake script for Step 5: Dimensionality Reduction."""
# ruff: noqa: F821

import os
from pathlib import Path

# Set thread count for numba/pynndescent before importing scanpy
os.environ["NUMBA_NUM_THREADS"] = str(snakemake.threads)
os.environ["OMP_NUM_THREADS"] = str(snakemake.threads)

from BetterCodeBetterScience.rnaseq.modular_workflow.dimensionality_reduction import (
    run_dimensionality_reduction_pipeline,
)
from BetterCodeBetterScience.rnaseq.stateless_workflow.checkpoint import (
    load_checkpoint,
    save_checkpoint,
)


def main():
    """Run dimensionality reduction pipeline."""
    print(f"Running with {snakemake.threads} threads")

    input_file = Path(snakemake.input[0])
    output_file = Path(snakemake.output[0])

    # Get parameters
    batch_key = snakemake.params.batch_key
    n_neighbors = snakemake.params.n_neighbors
    n_pcs = snakemake.params.n_pcs
    figure_dir = (
        Path(snakemake.params.figure_dir) if snakemake.params.figure_dir else None
    )

    print(f"Loading data from: {input_file}")
    adata = load_checkpoint(input_file)
    print(f"Loaded dataset: {adata}")

    print("Running dimensionality reduction pipeline...")
    adata = run_dimensionality_reduction_pipeline(
        adata,
        batch_key=batch_key,
        n_neighbors=n_neighbors,
        n_pcs=n_pcs,
        figure_dir=figure_dir,
    )

    # Save checkpoint
    save_checkpoint(adata, output_file)
    print(f"Saved checkpoint: {output_file}")


if __name__ == "__main__":
    main()
