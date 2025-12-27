"""Snakemake script for Step 1: Data Download."""

from pathlib import Path

from bettercode.rnaseq.modular_workflow.data_loading import download_data


def main():
    """Download data file if it doesn't exist."""
    # ruff: noqa: F821
    datafile = Path(snakemake.output[0])
    url = snakemake.params.url

    print(f"Downloading data from: {url}")
    print(f"Output file: {datafile}")

    download_data(datafile, url)

    print(f"Download complete: {datafile}")


if __name__ == "__main__":
    main()
