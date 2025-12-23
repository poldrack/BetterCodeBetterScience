"""Data filtering module for the simple workflow example.

This module provides functions to filter dataframes to keep only numerical columns.
"""

import pandas as pd


def filter_numerical_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Filter a dataframe to keep only numerical columns.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe

    Returns
    -------
    pd.DataFrame
        Dataframe with only numerical columns
    """
    numerical_df = df.select_dtypes(include=["number"])
    return numerical_df


def filter_meaningful_variables(df: pd.DataFrame) -> pd.DataFrame:
    """Filter meaningful variables dataframe to numerical columns only.

    Parameters
    ----------
    df : pd.DataFrame
        Meaningful variables dataframe

    Returns
    -------
    pd.DataFrame
        Filtered dataframe with only numerical columns
    """
    return filter_numerical_columns(df)


def filter_demographics(df: pd.DataFrame) -> pd.DataFrame:
    """Filter demographics dataframe to numerical columns only.

    Parameters
    ----------
    df : pd.DataFrame
        Demographics dataframe

    Returns
    -------
    pd.DataFrame
        Filtered dataframe with only numerical columns
    """
    return filter_numerical_columns(df)
