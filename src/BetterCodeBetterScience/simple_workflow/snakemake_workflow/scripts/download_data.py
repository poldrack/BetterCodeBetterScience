"""Snakemake script for downloading data from URL."""

from pathlib import Path

import pandas as pd


def main():
    """Download data from URL."""
    # ruff: noqa: F821
    url = snakemake.params.url
    output_path = Path(snakemake.output[0]).expanduser()

    # Create output directory
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Download and save
    df = pd.read_csv(url, index_col=0)
    df.to_csv(output_path)

    print(f"Downloaded {len(df)} rows from {url}")
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()
