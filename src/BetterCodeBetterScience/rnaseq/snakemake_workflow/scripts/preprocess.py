"""Snakemake script for Step 4: Preprocessing."""

from pathlib import Path

from BetterCodeBetterScience.rnaseq.modular_workflow.preprocessing import (
    run_preprocessing_pipeline,
)
from BetterCodeBetterScience.rnaseq.stateless_workflow.checkpoint import (
    load_checkpoint,
    save_checkpoint,
)


def main():
    """Run preprocessing pipeline."""
    # ruff: noqa: F821
    input_file = Path(snakemake.input[0])
    output_file = Path(snakemake.output[0])

    # Get parameters
    target_sum = snakemake.params.target_sum
    n_top_genes = snakemake.params.n_top_genes
    batch_key = snakemake.params.batch_key

    print(f"Loading data from: {input_file}")
    adata = load_checkpoint(input_file)
    print(f"Loaded dataset: {adata}")

    print("Running preprocessing pipeline...")
    adata = run_preprocessing_pipeline(
        adata,
        target_sum=target_sum,
        n_top_genes=n_top_genes,
        batch_key=batch_key,
    )

    # Remove counts layer after preprocessing to save space
    if "counts" in adata.layers:
        del adata.layers["counts"]
        print("Removed counts layer to save checkpoint space")

    # Save checkpoint
    save_checkpoint(adata, output_file)
    print(f"Saved checkpoint: {output_file}")


if __name__ == "__main__":
    main()
