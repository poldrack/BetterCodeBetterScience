"""Prefect flow definitions for the simple correlation workflow.

This workflow demonstrates Prefect features with a simple pandas-based analysis:
1. Load two datasets from URLs
2. Filter to numerical columns
3. Join the datasets
4. Compute Spearman correlation
5. Generate a clustered heatmap
"""

from pathlib import Path

from prefect import flow, get_run_logger

from bettercode.simple_workflow.prefect_workflow.tasks import (
    compute_correlation_task,
    filter_numerical_task,
    generate_heatmap_task,
    join_dataframes_task,
    load_demographics_task,
    load_meaningful_variables_task,
    save_correlation_task,
)


@flow(name="simple_correlation_workflow", log_prints=True)
def run_workflow(
    output_dir: Path,
    cache_data: bool = True,
) -> Path:
    """Run the simple correlation workflow.

    Steps:
    1. Load meaningful variables and demographics datasets
    2. Filter both to numerical columns only
    3. Join the datasets on their index
    4. Compute Spearman correlation matrix
    5. Generate clustered heatmap

    Parameters
    ----------
    output_dir : Path
        Directory to save outputs (correlation matrix CSV and heatmap)
    cache_data : bool
        Whether to cache downloaded data locally (default: True)

    Returns
    -------
    Path
        Path to the generated heatmap
    """
    logger = get_run_logger()

    # Setup directories
    output_dir = Path(output_dir)
    data_dir = output_dir / "data"
    results_dir = output_dir / "results"
    figures_dir = output_dir / "figures"

    for d in [data_dir, results_dir, figures_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Step 1: Load data (can run in parallel)
    logger.info("Step 1: Loading datasets...")
    mv_cache = data_dir / "meaningful_variables.csv" if cache_data else None
    demo_cache = data_dir / "demographics.csv" if cache_data else None

    meaningful_vars = load_meaningful_variables_task(cache_path=mv_cache)
    demographics = load_demographics_task(cache_path=demo_cache)

    logger.info(f"  Meaningful variables: {meaningful_vars.shape}")
    logger.info(f"  Demographics: {demographics.shape}")

    # Step 2: Filter to numerical columns
    logger.info("Step 2: Filtering to numerical columns...")
    meaningful_vars_num = filter_numerical_task(meaningful_vars)
    demographics_num = filter_numerical_task(demographics)

    logger.info(f"  Meaningful variables (numerical): {meaningful_vars_num.shape}")
    logger.info(f"  Demographics (numerical): {demographics_num.shape}")

    # Step 3: Join datasets
    logger.info("Step 3: Joining datasets...")
    joined_df = join_dataframes_task(meaningful_vars_num, demographics_num)
    logger.info(f"  Joined dataset: {joined_df.shape}")

    # Step 4: Compute correlation matrix
    logger.info("Step 4: Computing Spearman correlation matrix...")
    corr_matrix = compute_correlation_task(joined_df)
    logger.info(f"  Correlation matrix: {corr_matrix.shape}")

    # Save correlation matrix
    corr_path = results_dir / "correlation_matrix.csv"
    save_correlation_task(corr_matrix, corr_path)
    logger.info(f"  Saved correlation matrix to: {corr_path}")

    # Step 5: Generate heatmap
    logger.info("Step 5: Generating clustered heatmap...")
    heatmap_path = figures_dir / "correlation_heatmap.png"
    generate_heatmap_task(corr_matrix, heatmap_path)
    logger.info(f"  Saved heatmap to: {heatmap_path}")

    logger.info("Workflow complete!")
    return heatmap_path


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python flows.py <output_dir>")
        sys.exit(1)

    output_dir = Path(sys.argv[1])
    run_workflow(output_dir)
