## Problems to be fixed

Open problems marked with [ ]
Fixed problems marked with [x]

[x] I would like to add a new workflow, with code saved to src/BetterCodeBetterScience/rnaseq/prefect_workflow. This workflow will use the Prefect workflow manager (https://github.com/PrefectHQ/prefect) to manage the workflow that was previously developed in src/BetterCodeBetterScience/rnaseq/stateless_workflow. The one new feature that I would like to add here is to perform steps 8-11 separately on each different cell type that survives the initial filtering.
    - Created `prefect_workflow/` directory with:
      - `tasks.py`: Prefect task definitions wrapping modular workflow functions
      - `flows.py`: Main workflow flow with parallel per-cell-type analysis
      - `run_workflow.py`: CLI entry point with argument parsing
    - Steps 1-7 run sequentially with checkpoint caching (reuses existing system)
    - Steps 8-11 run in parallel for each cell type:
      - DE tasks submitted in parallel across all cell types
      - GSEA, Enrichr, and predictive modeling run in parallel within each cell type
    - Added `prefect>=3.0` dependency to pyproject.toml
    - Results organized by cell type in `workflow/results/per_cell_type/`
    - CLI supports: `--force-from`, `--cell-type`, `--list-cell-types`, `--min-samples`  
