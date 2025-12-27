"""Prefect task definitions for the simple correlation workflow.

Each task wraps a function from the modular workflow modules.
"""

from pathlib import Path

import pandas as pd
from prefect import task

from bettercode.simple_workflow.correlation import (
    compute_spearman_correlation,
)
from bettercode.simple_workflow.filter_data import (
    filter_numerical_columns,
)
from bettercode.simple_workflow.join_data import join_dataframes
from bettercode.simple_workflow.load_data import (
    load_demographics,
    load_meaningful_variables,
)
from bettercode.simple_workflow.visualization import (
    generate_clustered_heatmap,
    save_correlation_matrix,
)


@task(name="load_meaningful_variables")
def load_meaningful_variables_task(
    cache_path: Path | None = None,
) -> pd.DataFrame:
    """Load meaningful variables dataset.

    Parameters
    ----------
    cache_path : Path, optional
        Path to cache the downloaded data

    Returns
    -------
    pd.DataFrame
        Meaningful variables dataframe
    """
    return load_meaningful_variables(cache_path=cache_path)


@task(name="load_demographics")
def load_demographics_task(
    cache_path: Path | None = None,
) -> pd.DataFrame:
    """Load demographics dataset.

    Parameters
    ----------
    cache_path : Path, optional
        Path to cache the downloaded data

    Returns
    -------
    pd.DataFrame
        Demographics dataframe
    """
    return load_demographics(cache_path=cache_path)


@task(name="filter_numerical_columns")
def filter_numerical_task(df: pd.DataFrame) -> pd.DataFrame:
    """Filter dataframe to keep only numerical columns.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe

    Returns
    -------
    pd.DataFrame
        Filtered dataframe
    """
    return filter_numerical_columns(df)


@task(name="join_dataframes")
def join_dataframes_task(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
) -> pd.DataFrame:
    """Join two dataframes based on their index.

    Parameters
    ----------
    df1 : pd.DataFrame
        First dataframe
    df2 : pd.DataFrame
        Second dataframe

    Returns
    -------
    pd.DataFrame
        Joined dataframe
    """
    return join_dataframes(df1, df2)


@task(name="compute_correlation")
def compute_correlation_task(df: pd.DataFrame) -> pd.DataFrame:
    """Compute Spearman correlation matrix.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe

    Returns
    -------
    pd.DataFrame
        Correlation matrix
    """
    return compute_spearman_correlation(df)


@task(name="save_correlation_matrix")
def save_correlation_task(
    corr_matrix: pd.DataFrame,
    output_path: Path,
) -> None:
    """Save correlation matrix to CSV.

    Parameters
    ----------
    corr_matrix : pd.DataFrame
        Correlation matrix
    output_path : Path
        Output path
    """
    save_correlation_matrix(corr_matrix, output_path)


@task(name="generate_heatmap")
def generate_heatmap_task(
    corr_matrix: pd.DataFrame,
    output_path: Path,
) -> None:
    """Generate and save clustered heatmap.

    Parameters
    ----------
    corr_matrix : pd.DataFrame
        Correlation matrix
    output_path : Path
        Output path for the figure
    """
    generate_clustered_heatmap(corr_matrix, output_path)
