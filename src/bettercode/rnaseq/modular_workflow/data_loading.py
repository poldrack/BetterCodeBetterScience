"""Data loading module for scRNA-seq analysis workflow.

Functions for downloading and loading single-cell RNA-seq data.
"""

import os
from pathlib import Path

import anndata as ad
import h5py
from anndata.experimental import read_lazy


def download_data(datafile: Path, url: str) -> None:
    """Download data file if it doesn't exist.

    Parameters
    ----------
    datafile : Path
        Path to save the downloaded file
    url : str
        URL to download from
    """
    if not datafile.exists():
        cmd = f"wget -O {datafile.as_posix()} {url}"
        print(f"Downloading data from {url} to {datafile.as_posix()}")
        os.system(cmd)


def load_lazy_anndata(datafile: Path, load_annotation_index: bool = True) -> ad.AnnData:
    """Load AnnData object lazily from h5ad file.

    Parameters
    ----------
    datafile : Path
        Path to h5ad file
    load_annotation_index : bool
        Whether to load annotation index

    Returns
    -------
    AnnData
        Lazily loaded AnnData object
    """
    adata = read_lazy(
        h5py.File(datafile, "r"), load_annotation_index=load_annotation_index
    )
    return adata


def load_anndata(datafile: Path) -> ad.AnnData:
    """Load AnnData object from h5ad file.

    Parameters
    ----------
    datafile : Path
        Path to h5ad file

    Returns
    -------
    AnnData
        AnnData object
    """
    return ad.read_h5ad(datafile)


def save_anndata(adata: ad.AnnData, filepath: Path) -> None:
    """Save AnnData object to h5ad file.

    Parameters
    ----------
    adata : AnnData
        AnnData object to save
    filepath : Path
        Path to save the file
    """
    adata.write(filepath)
