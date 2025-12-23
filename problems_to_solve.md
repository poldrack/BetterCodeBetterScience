## Problems to be fixed

Open problems marked with [ ]
Fixed problems marked with [x]


[x] I would now like to add another workflow, with code saved to src/BetterCodeBetterScience/rnaseq/snakemake_workflow. This workflow will use the Snakemake workflow manager (https://snakemake.readthedocs.io/en/stable/index.html); otherwise it should be functionally equivalent to the other workflows already developed.
    - Created `snakemake_workflow/` directory with:
      - `Snakefile`: Main workflow entry point
      - `config/config.yaml`: All workflow parameters with defaults
      - `rules/common.smk`: Helper functions (sanitize_cell_type, aggregate functions)
      - `rules/preprocessing.smk`: Steps 1-6 rules
      - `rules/pseudobulk.smk`: Step 7 as Snakemake checkpoint (enables dynamic rules)
      - `rules/per_cell_type.smk`: Steps 8-11 with {cell_type} wildcard
      - `scripts/*.py`: 12 Python scripts wrapping modular workflow functions
    - Uses Snakemake checkpoint for step 7 to discover cell types dynamically
    - Per-cell-type steps (8-11) triggered automatically for all valid cell types
    - Reuses existing modular workflow functions and checkpoint utilities
    - Added `snakemake>=8.0` dependency to pyproject.toml
    - Usage: `snakemake --cores 8 --config datadir=/path/to/data`  

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
