"""Correlation computation module for the simple workflow example.

This module provides functions to compute correlation matrices.
"""

import pandas as pd


def compute_spearman_correlation(df: pd.DataFrame) -> pd.DataFrame:
    """Compute Spearman correlation matrix for a dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe with numerical columns

    Returns
    -------
    pd.DataFrame
        Spearman correlation matrix
    """
    return df.corr(method="spearman")


def compute_correlation_matrix(
    df: pd.DataFrame,
    method: str = "spearman",
) -> pd.DataFrame:
    """Compute correlation matrix using the specified method.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe with numerical columns
    method : str
        Correlation method: 'pearson', 'spearman', or 'kendall' (default: 'spearman')

    Returns
    -------
    pd.DataFrame
        Correlation matrix
    """
    return df.corr(method=method)
