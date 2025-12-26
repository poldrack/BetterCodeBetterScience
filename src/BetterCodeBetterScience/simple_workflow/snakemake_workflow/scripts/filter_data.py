"""Snakemake script for filtering data to numerical columns."""

from pathlib import Path

import pandas as pd

from BetterCodeBetterScience.simple_workflow.filter_data import (
    filter_numerical_columns,
)


def main():
    """Filter data to numerical columns."""
    # ruff: noqa: F821
    input_path = Path(snakemake.input[0]).expanduser()
    output_path = Path(snakemake.output[0]).expanduser()

    # Load data
    df = pd.read_csv(input_path, index_col=0)
    print(f"Loaded {df.shape} from {input_path}")

    # Filter to numerical columns
    df_num = filter_numerical_columns(df)
    print(f"Filtered to {df_num.shape} (numerical columns only)")

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_num.to_csv(output_path)
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()
