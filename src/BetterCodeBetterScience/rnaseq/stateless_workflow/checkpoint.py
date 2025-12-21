"""Checkpoint utilities for stateless workflow execution.

Provides functions to save and load intermediate results, enabling
workflow resumption from any step.
"""

from __future__ import annotations

import hashlib
import json
import pickle
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any

import anndata as ad
import pandas as pd

if TYPE_CHECKING:
    from BetterCodeBetterScience.rnaseq.stateless_workflow.execution_log import (
        ExecutionLog,
    )


def get_file_type(filepath: Path) -> str:
    """Determine file type from extension.

    Parameters
    ----------
    filepath : Path
        Path to the file

    Returns
    -------
    str
        File type identifier: 'h5ad', 'parquet', or 'pickle'
    """
    suffix = filepath.suffix.lower()
    if suffix == ".h5ad":
        return "h5ad"
    elif suffix == ".parquet":
        return "parquet"
    else:
        return "pickle"


def save_checkpoint(data: Any, filepath: Path) -> None:
    """Save data to a checkpoint file.

    Automatically selects serialization format based on file extension:
    - .h5ad: AnnData objects
    - .parquet: pandas DataFrames
    - .pkl: Any picklable object

    Parameters
    ----------
    data : Any
        Data to save
    filepath : Path
        Path to save the checkpoint
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    file_type = get_file_type(filepath)

    if file_type == "h5ad":
        if not isinstance(data, ad.AnnData):
            raise TypeError(f"Expected AnnData for .h5ad file, got {type(data)}")
        data.write(filepath)
    elif file_type == "parquet":
        if not isinstance(data, pd.DataFrame):
            raise TypeError(f"Expected DataFrame for .parquet file, got {type(data)}")
        data.to_parquet(filepath)
    else:
        with open(filepath, "wb") as f:
            pickle.dump(data, f)


def load_checkpoint(filepath: Path) -> Any:
    """Load data from a checkpoint file.

    Automatically selects deserialization format based on file extension.

    Parameters
    ----------
    filepath : Path
        Path to the checkpoint file

    Returns
    -------
    Any
        Loaded data
    """
    file_type = get_file_type(filepath)

    if file_type == "h5ad":
        return ad.read_h5ad(filepath)
    elif file_type == "parquet":
        return pd.read_parquet(filepath)
    else:
        with open(filepath, "rb") as f:
            return pickle.load(f)


def hash_parameters(**kwargs) -> str:
    """Create a hash of parameters for cache invalidation.

    Parameters
    ----------
    **kwargs
        Parameters to hash

    Returns
    -------
    str
        8-character hash string
    """
    param_str = json.dumps(kwargs, sort_keys=True, default=str)
    return hashlib.md5(param_str.encode()).hexdigest()[:8]


def run_with_checkpoint(
    step_name: str,
    checkpoint_file: Path,
    func: Callable,
    *args,
    force: bool = False,
    execution_log: ExecutionLog | None = None,
    step_number: int | None = None,
    log_parameters: dict[str, Any] | None = None,
    **kwargs,
) -> Any:
    """Execute a function with checkpoint caching.

    If the checkpoint file exists and force=False, loads and returns
    the cached result. Otherwise, executes the function, saves the
    result, and returns it.

    Parameters
    ----------
    step_name : str
        Human-readable name for logging
    checkpoint_file : Path
        Path to save/load the checkpoint
    func : Callable
        Function to execute
    *args
        Positional arguments for func
    force : bool
        If True, ignore existing checkpoint and re-run
    execution_log : ExecutionLog, optional
        Execution log to record step details
    step_number : int, optional
        Step number for logging
    log_parameters : dict, optional
        Parameters to record in the execution log
    **kwargs
        Keyword arguments for func

    Returns
    -------
    Any
        Result of func(*args, **kwargs) or cached result
    """
    # Start logging if provided
    step_record = None
    if execution_log is not None and step_number is not None:
        step_record = execution_log.add_step(
            step_number=step_number,
            step_name=step_name,
            parameters=log_parameters,
            checkpoint_file=str(checkpoint_file),
        )

    from_cache = False
    error_message = None

    try:
        if checkpoint_file.exists() and not force:
            print(f"[{step_name}] Loading from checkpoint: {checkpoint_file.name}")
            from_cache = True
            result = load_checkpoint(checkpoint_file)
        else:
            print(f"[{step_name}] Executing...")
            result = func(*args, **kwargs)

            print(f"[{step_name}] Saving checkpoint: {checkpoint_file.name}")
            save_checkpoint(result, checkpoint_file)

        return result

    except Exception as e:
        error_message = str(e)
        raise

    finally:
        if step_record is not None:
            execution_log.complete_step(
                step_record, from_cache=from_cache, error_message=error_message
            )


def run_with_checkpoint_multi(
    step_name: str,
    checkpoint_files: dict[str, Path],
    func: Callable,
    *args,
    force: bool = False,
    execution_log: ExecutionLog | None = None,
    step_number: int | None = None,
    log_parameters: dict[str, Any] | None = None,
    **kwargs,
) -> dict[str, Any]:
    """Execute a function that returns multiple outputs with checkpoint caching.

    The function must return a dict with keys matching checkpoint_files.

    Parameters
    ----------
    step_name : str
        Human-readable name for logging
    checkpoint_files : dict[str, Path]
        Mapping of output names to checkpoint file paths
    func : Callable
        Function to execute (must return dict)
    *args
        Positional arguments for func
    force : bool
        If True, ignore existing checkpoints and re-run
    execution_log : ExecutionLog, optional
        Execution log to record step details
    step_number : int, optional
        Step number for logging
    log_parameters : dict, optional
        Parameters to record in the execution log
    **kwargs
        Keyword arguments for func

    Returns
    -------
    dict[str, Any]
        Dict of results keyed by output names
    """
    # Start logging if provided
    step_record = None
    if execution_log is not None and step_number is not None:
        checkpoint_files_str = {k: str(v) for k, v in checkpoint_files.items()}
        step_record = execution_log.add_step(
            step_number=step_number,
            step_name=step_name,
            parameters=log_parameters,
            checkpoint_file=str(checkpoint_files_str),
        )

    from_cache = False
    error_message = None

    try:
        all_exist = all(fp.exists() for fp in checkpoint_files.values())

        if all_exist and not force:
            print(f"[{step_name}] Loading from checkpoints...")
            from_cache = True
            return {key: load_checkpoint(fp) for key, fp in checkpoint_files.items()}

        print(f"[{step_name}] Executing...")
        results = func(*args, **kwargs)

        if not isinstance(results, dict):
            raise TypeError(
                f"Function must return dict for multi-checkpoint, got {type(results)}"
            )

        print(f"[{step_name}] Saving checkpoints...")
        for key, filepath in checkpoint_files.items():
            if key not in results:
                raise KeyError(f"Function result missing key: {key}")
            save_checkpoint(results[key], filepath)

        return results

    except Exception as e:
        error_message = str(e)
        raise

    finally:
        if step_record is not None:
            execution_log.complete_step(
                step_record, from_cache=from_cache, error_message=error_message
            )


def clear_checkpoints(checkpoint_dir: Path, pattern: str = "step*.") -> list[Path]:
    """Remove checkpoint files matching a pattern.

    Parameters
    ----------
    checkpoint_dir : Path
        Directory containing checkpoints
    pattern : str
        Glob pattern for files to remove

    Returns
    -------
    list[Path]
        List of removed files
    """
    removed = []
    for filepath in checkpoint_dir.glob(pattern + "*"):
        filepath.unlink()
        removed.append(filepath)
        print(f"Removed: {filepath.name}")
    return removed


def clear_checkpoints_from_step(checkpoint_dir: Path, from_step: int) -> list[Path]:
    """Remove checkpoints from a specific step onwards.

    Useful for invalidating downstream results when re-running an upstream step.

    Parameters
    ----------
    checkpoint_dir : Path
        Directory containing checkpoints
    from_step : int
        Step number to start clearing from (inclusive)

    Returns
    -------
    list[Path]
        List of removed files
    """
    removed = []
    for filepath in checkpoint_dir.glob("step*"):
        try:
            step_num = int(filepath.name.split("_")[0].replace("step", ""))
            if step_num >= from_step:
                filepath.unlink()
                removed.append(filepath)
                print(f"Removed: {filepath.name}")
        except (ValueError, IndexError):
            continue
    return removed
