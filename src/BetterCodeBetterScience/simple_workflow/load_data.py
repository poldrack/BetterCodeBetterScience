"""Data loading module for the simple workflow example.

This module provides functions to load CSV data from URLs or local files.
"""

from pathlib import Path

import pandas as pd


def load_csv_from_url(url: str, index_col: int = 0) -> pd.DataFrame:
    """Load a CSV file from a URL.

    Parameters
    ----------
    url : str
        URL to the CSV file
    index_col : int
        Column to use as index (default: 0, first column)

    Returns
    -------
    pd.DataFrame
        Loaded dataframe with the first column as index
    """
    return pd.read_csv(url, index_col=index_col)


def load_meaningful_variables(
    url: str = "https://raw.githubusercontent.com/IanEisenberg/Self_Regulation_Ontology/refs/heads/master/Data/Complete_02-16-2019/meaningful_variables_clean.csv",
    cache_path: Path | None = None,
) -> pd.DataFrame:
    """Load the meaningful variables dataset.

    Parameters
    ----------
    url : str
        URL to the meaningful variables CSV file
    cache_path : Path, optional
        If provided, save/load from this local path

    Returns
    -------
    pd.DataFrame
        Meaningful variables dataframe
    """
    if cache_path is not None and cache_path.exists():
        return pd.read_csv(cache_path, index_col=0)

    df = load_csv_from_url(url)

    if cache_path is not None:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(cache_path)

    return df


def load_demographics(
    url: str = "https://raw.githubusercontent.com/IanEisenberg/Self_Regulation_Ontology/refs/heads/master/Data/Complete_02-16-2019/demographics.csv",
    cache_path: Path | None = None,
) -> pd.DataFrame:
    """Load the demographics dataset.

    Parameters
    ----------
    url : str
        URL to the demographics CSV file
    cache_path : Path, optional
        If provided, save/load from this local path

    Returns
    -------
    pd.DataFrame
        Demographics dataframe
    """
    if cache_path is not None and cache_path.exists():
        return pd.read_csv(cache_path, index_col=0)

    df = load_csv_from_url(url)

    if cache_path is not None:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(cache_path)

    return df
