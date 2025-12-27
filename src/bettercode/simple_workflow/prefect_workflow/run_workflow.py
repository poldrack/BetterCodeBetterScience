#!/usr/bin/env python3
"""CLI entry point for the simple correlation Prefect workflow.

Usage:
    python run_workflow.py --output-dir ./output
    python run_workflow.py --output-dir ./output --no-cache
"""

import argparse
from pathlib import Path

from bettercode.simple_workflow.prefect_workflow.flows import run_workflow


def main():
    """Run the simple correlation workflow from the command line."""
    parser = argparse.ArgumentParser(
        description="Run the simple correlation workflow with Prefect"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory to save outputs",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Do not cache downloaded data locally",
    )

    args = parser.parse_args()

    result = run_workflow(
        output_dir=args.output_dir,
        cache_data=not args.no_cache,
    )

    print(f"\nWorkflow complete! Heatmap saved to: {result}")


if __name__ == "__main__":
    main()
