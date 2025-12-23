"""Snakemake script for joining two dataframes."""

from pathlib import Path

import pandas as pd

from BetterCodeBetterScience.simple_workflow.join_data import join_dataframes


def main():
    """Join the two datasets."""
    # ruff: noqa: F821
    mv_path = Path(snakemake.input.meaningful_vars)
    demo_path = Path(snakemake.input.demographics)
    output_path = Path(snakemake.output[0])

    # Load data
    meaningful_vars = pd.read_csv(mv_path, index_col=0)
    demographics = pd.read_csv(demo_path, index_col=0)

    print(f"Meaningful variables: {meaningful_vars.shape}")
    print(f"Demographics: {demographics.shape}")

    # Join
    joined = join_dataframes(meaningful_vars, demographics)
    print(f"Joined: {joined.shape}")

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joined.to_csv(output_path)
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()
