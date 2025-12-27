"""Snakemake script for aggregating all per-cell-type results.

This script runs after all per-cell-type analyses are complete.
It creates a summary file indicating successful completion.
"""
# ruff: noqa: F821

from datetime import datetime
from pathlib import Path


def main():
    """Aggregate results and create completion marker."""
    output_file = Path(snakemake.output[0])
    input_files = [Path(f) for f in snakemake.input]

    print(f"Aggregating {len(input_files)} result files...")

    # Group files by cell type
    cell_types = set()
    for f in input_files:
        # Extract cell type from path: results/per_cell_type/{cell_type}/...
        parts = f.parts
        if "per_cell_type" in parts:
            idx = parts.index("per_cell_type")
            if idx + 1 < len(parts):
                cell_types.add(parts[idx + 1])

    # Create summary
    summary = {
        "workflow": "snakemake_scrna_immune_aging",
        "completed_at": datetime.now().isoformat(),
        "cell_types_analyzed": sorted(cell_types),
        "total_cell_types": len(cell_types),
        "output_files": len(input_files),
    }

    # Write summary to output file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        f.write("Workflow completed successfully!\n")
        f.write(f"Completed at: {summary['completed_at']}\n")
        f.write(f"Cell types analyzed: {summary['total_cell_types']}\n")
        f.write("\n")
        f.write("Cell types:\n")
        for ct in summary["cell_types_analyzed"]:
            f.write(f"  - {ct}\n")
        f.write("\n")
        f.write(f"Total output files: {summary['output_files']}\n")

    print(f"Summary written to: {output_file}")
    print(f"Analyzed {len(cell_types)} cell types")


if __name__ == "__main__":
    main()
