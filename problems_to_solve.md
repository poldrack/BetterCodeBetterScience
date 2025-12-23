## Problems to be fixed

Open problems marked with [ ]
Fixed problems marked with [x]

[x] For the Prefect workflow, the default parameters for each workflow module are embedded in the python code for the workflow. I would rather that they be defined using a configuration file.  Please extract all of the parameters into a configuration file (using whatever format you think is most appropriate) and read those in during workflow execution rather than hard-coding.
    - Created `prefect_workflow/config/config.yaml` with all workflow parameters
    - Parameters organized by step: filtering, qc, preprocessing, dimred, clustering, pseudobulk, differential_expression, pathway_analysis, overrepresentation, predictive_modeling
    - Added `load_config()` function to flows.py that loads from YAML file
    - Updated `run_workflow()` and `analyze_single_cell_type()` to accept `config_path` parameter
    - Added `--config` CLI argument to run_workflow.py
    - Default config bundled with package; custom configs can be specified via CLI
[x] For the Prefect workflow, please save the output to a folder called "wf_prefect" (rather than "workflow")
    - Updated all output directories in flows.py and run_workflow.py to use `wf_prefect/` instead of `workflow/`
[x] For the Snakemake workflow, please save the output to a folder called "wf_snakemake" (rather than "workflow")
    - Updated Snakefile to use `wf_snakemake/` for CHECKPOINT_DIR, RESULTS_DIR, FIGURE_DIR, LOG_DIR
    - Updated WORKFLOW_OVERVIEW.md to reflect new output structure

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
