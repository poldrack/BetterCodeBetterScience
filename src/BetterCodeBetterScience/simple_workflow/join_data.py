"""Data joining module for the simple workflow example.

This module provides functions to join dataframes based on their index.
"""

import pandas as pd


def join_dataframes(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    how: str = "inner",
) -> pd.DataFrame:
    """Join two dataframes based on their index.

    Parameters
    ----------
    df1 : pd.DataFrame
        First dataframe
    df2 : pd.DataFrame
        Second dataframe
    how : str
        Type of join: 'inner', 'outer', 'left', 'right' (default: 'inner')

    Returns
    -------
    pd.DataFrame
        Joined dataframe
    """
    return df1.join(df2, how=how, lsuffix="_mv", rsuffix="_demo")


def join_meaningful_and_demographics(
    meaningful_vars: pd.DataFrame,
    demographics: pd.DataFrame,
    how: str = "inner",
) -> pd.DataFrame:
    """Join meaningful variables and demographics dataframes.

    Parameters
    ----------
    meaningful_vars : pd.DataFrame
        Meaningful variables dataframe (filtered to numerical)
    demographics : pd.DataFrame
        Demographics dataframe (filtered to numerical)
    how : str
        Type of join (default: 'inner')

    Returns
    -------
    pd.DataFrame
        Joined dataframe
    """
    return join_dataframes(meaningful_vars, demographics, how=how)
