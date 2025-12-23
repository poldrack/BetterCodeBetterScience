"""Common helper functions and wildcards for Snakemake workflow."""

import json
from pathlib import Path


def sanitize_cell_type(cell_type: str) -> str:
    """Sanitize cell type name for filesystem use.

    Matches the function used in Prefect workflow.
    """
    return cell_type.replace(" ", "_").replace(",", "").replace("-", "_")


def unsanitize_cell_type(sanitized: str, cell_types_file: Path) -> str:
    """Convert sanitized cell type back to original name.

    Parameters
    ----------
    sanitized : str
        Sanitized cell type name
    cell_types_file : Path
        Path to cell_types.json file from pseudobulk step

    Returns
    -------
    str
        Original cell type name
    """
    with open(cell_types_file) as f:
        data = json.load(f)
    # Reverse lookup
    for original, sanitized_name in data["sanitized_names"].items():
        if sanitized_name == sanitized:
            return original
    raise ValueError(f"Unknown sanitized cell type: {sanitized}")


def bids_checkpoint_name(
    dataset_name: str, step_number: int, description: str, extension: str = "h5ad"
) -> str:
    """Generate BIDS-compliant checkpoint filename.

    Matches the naming convention used in stateless_workflow.
    """
    return f"dataset-{dataset_name}_step-{step_number:02d}_desc-{description}.{extension}"


def get_valid_cell_types(wildcards):
    """Get list of valid cell types from pseudobulk checkpoint.

    This function is used as an input function after the checkpoint
    to determine which cell types to process.
    """
    checkpoint_output = checkpoints.pseudobulk.get(**wildcards)
    cell_types_file = checkpoint_output.output.cell_types

    with open(cell_types_file) as f:
        data = json.load(f)

    return data["valid_cell_types"]


def aggregate_per_cell_type_outputs(wildcards):
    """Aggregate function to collect all per-cell-type outputs.

    This is called after the pseudobulk checkpoint is resolved to
    generate the list of expected outputs for all valid cell types.
    """
    checkpoint_output = checkpoints.pseudobulk.get(**wildcards)
    cell_types_file = checkpoint_output.output.cell_types

    with open(cell_types_file) as f:
        data = json.load(f)

    valid_cell_types = data["valid_cell_types"]

    outputs = []
    for ct in valid_cell_types:
        ct_sanitized = sanitize_cell_type(ct)
        ct_dir = RESULTS_DIR / "per_cell_type" / ct_sanitized
        outputs.extend(
            [
                ct_dir / "de_results.parquet",
                ct_dir / "gsea_results.pkl",
                ct_dir / "enrichr_up.pkl",
                ct_dir / "enrichr_down.pkl",
                ct_dir / "prediction_results.pkl",
            ]
        )

    return outputs
