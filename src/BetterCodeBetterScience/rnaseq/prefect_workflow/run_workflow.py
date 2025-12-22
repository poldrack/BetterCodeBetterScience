"""Entry point for running the Prefect-based scRNA-seq workflow.

Usage:
    python -m BetterCodeBetterScience.rnaseq.prefect_workflow.run_workflow

Or with arguments:
    python -m BetterCodeBetterScience.rnaseq.prefect_workflow.run_workflow --force-from 8
"""

# Set numba environment variables BEFORE any imports
# NUMBA_CAPTURED_ERRORS='old_style' allows print in nopython functions
# See: https://github.com/ray-project/ray/issues/44714
import os

os.environ["NUMBA_CAPTURED_ERRORS"] = "old_style"

import argparse
from pathlib import Path

from dotenv import load_dotenv

from BetterCodeBetterScience.rnaseq.prefect_workflow.flows import (
    analyze_single_cell_type,
    run_workflow,
)


def main():
    """Run the Prefect workflow."""
    parser = argparse.ArgumentParser(
        description="Run the immune aging scRNA-seq workflow with Prefect"
    )
    parser.add_argument(
        "--datadir",
        type=Path,
        default=None,
        help="Base directory for data files (default: from DATADIR env var)",
    )
    parser.add_argument(
        "--dataset-name",
        type=str,
        default="OneK1K",
        help="Name of the dataset (default: OneK1K)",
    )
    parser.add_argument(
        "--force-from",
        type=int,
        default=None,
        dest="force_from_step",
        help="Force re-run from this step onwards (1-11)",
    )
    parser.add_argument(
        "--min-samples",
        type=int,
        default=10,
        dest="min_samples",
        help="Minimum samples per cell type for steps 8-11 (default: 10)",
    )
    parser.add_argument(
        "--cell-type",
        type=str,
        default=None,
        dest="cell_type",
        help="Run analysis for a single cell type only (requires prior completion of steps 1-7)",
    )
    parser.add_argument(
        "--list-cell-types",
        action="store_true",
        dest="list_cell_types",
        help="List available cell types and exit",
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Get data directory
    if args.datadir is not None:
        datadir = args.datadir
    else:
        datadir_env = os.getenv("DATADIR")
        if datadir_env is None:
            raise ValueError(
                "DATADIR environment variable not set. "
                "Set it or use --datadir argument."
            )
        datadir = Path(datadir_env) / "immune_aging"

    print(f"Data directory: {datadir}")

    # List cell types if requested
    if args.list_cell_types:
        from BetterCodeBetterScience.rnaseq.stateless_workflow.checkpoint import (
            bids_checkpoint_name,
            load_checkpoint,
        )

        checkpoint_dir = datadir / "workflow/checkpoints"
        pb_checkpoint = checkpoint_dir / bids_checkpoint_name(
            args.dataset_name, 7, "pseudobulk"
        )

        if not pb_checkpoint.exists():
            print(f"Pseudobulk checkpoint not found: {pb_checkpoint}")
            print("Run steps 1-7 first to generate pseudobulk data.")
            return

        pb_adata = load_checkpoint(pb_checkpoint)
        cell_types = pb_adata.obs["cell_type"].unique().tolist()
        cell_type_counts = pb_adata.obs["cell_type"].value_counts()

        print(f"\nAvailable cell types ({len(cell_types)} total):")
        print("-" * 60)
        for ct in sorted(cell_types):
            count = cell_type_counts[ct]
            status = (
                "OK" if count >= args.min_samples else f"< {args.min_samples} samples"
            )
            print(f"  {ct}: {count} samples ({status})")
        return

    # Run single cell type analysis
    if args.cell_type is not None:
        print(f"\nRunning analysis for single cell type: {args.cell_type}")
        results = analyze_single_cell_type(
            datadir=datadir,
            cell_type=args.cell_type,
            dataset_name=args.dataset_name,
        )
        print("\nResults:")
        print(f"  DE genes: {len(results['de']['de_results'])}")
        if results["gsea"]["gsea_results"] is not None:
            print(f"  GSEA pathways: {len(results['gsea']['gsea_results'].res2d)}")
        if results["prediction"]["prediction_results"]:
            pred = results["prediction"]["prediction_results"]
            import numpy as np

            print(f"  Prediction R2: {np.mean(pred['full_r2']):.3f}")
            print(f"  Prediction MAE: {np.mean(pred['full_mae']):.2f} years")
        return

    # Run full workflow
    print("\nRunning full workflow...")
    if args.force_from_step:
        print(f"Forcing re-run from step {args.force_from_step}")

    results = run_workflow(
        datadir=datadir,
        dataset_name=args.dataset_name,
        force_from_step=args.force_from_step,
        min_samples_per_cell_type=args.min_samples,
    )

    # Print summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    successful_cell_types = [
        ct for ct, res in results["per_cell_type"].items() if "error" not in res
    ]

    print(f"Analyzed {len(successful_cell_types)} cell types:")
    for ct in sorted(successful_cell_types):
        ct_res = results["per_cell_type"][ct]
        de_count = len(ct_res["de"]["de_results"])
        sig_genes = (ct_res["de"]["de_results"]["padj"] < 0.05).sum()
        print(f"  {ct}:")
        print(f"    - DE genes tested: {de_count}")
        print(f"    - Significant (padj<0.05): {sig_genes}")

    failed_cell_types = [
        ct for ct, res in results["per_cell_type"].items() if "error" in res
    ]
    if failed_cell_types:
        print(f"\nFailed cell types ({len(failed_cell_types)}):")
        for ct in failed_cell_types:
            print(f"  {ct}: {results['per_cell_type'][ct]['error']}")


if __name__ == "__main__":
    main()
