# Running the scRNA-seq Immune Aging Workflows

This document provides examples of how to run each of the four workflow implementations for the immune aging scRNA-seq analysis.

All workflows perform the same 11-step analysis pipeline:
1. Data Download
2. Data Filtering
3. Quality Control
4. Preprocessing
5. Dimensionality Reduction
6. Clustering
7. Pseudobulking
8. Differential Expression (per cell type)
9. Pathway Analysis / GSEA (per cell type)
10. Overrepresentation Analysis / Enrichr (per cell type)
11. Predictive Modeling (per cell type)

---

## Prerequisites

### Environment Setup

All workflows require the `DATADIR` environment variable to be set, pointing to the base data directory. The workflows will create an `immune_aging/` subdirectory within this path.

```bash
# Option 1: Set environment variable directly
export DATADIR=/path/to/your/data

# Option 2: Create a .env file in your working directory
echo "DATADIR=/path/to/your/data" > .env
```

### Install Dependencies

```bash
# From the repository root
uv pip install -e .
```

---

## 1. Monolithic Workflow

The monolithic workflow is a single Python script that runs all analysis steps sequentially. It's the simplest implementation but lacks checkpointing and resumability.

**Location:** `immune_scrnaseq_monolithic.py`

### Running as a Script

```bash
# Edit the datadir path in the script first, then run:
python src/bettercode/rnaseq/immune_scrnaseq_monolithic.py
```

### Running as a Jupyter Notebook

The script uses jupytext format and can be opened directly in Jupyter:

```bash
jupyter notebook src/bettercode/rnaseq/immune_scrnaseq_monolithic.py
```

### Output Location

```
{datadir}/workflow/figures/
```

### Notes

- No checkpointing - must run from start each time
- Analyzes only one cell type (hardcoded in script)
- Best for understanding the analysis pipeline

---

## 2. Modular Workflow

The modular workflow uses reusable pipeline functions organized by analysis step. It provides better code organization than the monolithic version but still lacks robust checkpointing.

**Location:** `modular_workflow/run_workflow.py`

### Running the Workflow

```bash
# Using environment variable
export DATADIR=/path/to/your/data
python -m bettercode.rnaseq.modular_workflow.run_workflow

# Or import and run programmatically
python -c "
from pathlib import Path
from bettercode.rnaseq.modular_workflow.run_workflow import run_full_workflow

datadir = Path('/path/to/your/data/immune_aging')
results = run_full_workflow(datadir)
"
```

### Available Options

The `run_full_workflow()` function accepts these parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `datadir` | Required | Base directory for data files |
| `dataset_name` | "OneK1K" | Name of the dataset |
| `url` | CELLxGENE URL | Source URL for the h5ad file |
| `cell_type_for_de` | "central memory CD4-positive, alpha-beta T cell" | Cell type for differential expression |
| `skip_download` | False | Skip data download if file exists |
| `skip_filtering` | False | Load pre-filtered data |
| `skip_qc` | False | Load post-QC data |

### Output Location

```
{datadir}/workflow/figures/
```

### Notes

- Basic skip functionality for early steps
- Analyzes only one cell type
- Outputs figures only (no result files saved)

---

## 3. Stateless Workflow (with Checkpointing)

The stateless workflow adds robust checkpointing using BIDS-compliant naming. It can resume from any step and tracks execution history.

**Location:** `stateless_workflow/run_workflow.py`

### Running the Workflow

```bash
# Basic run (resumes from last checkpoint automatically)
export DATADIR=/path/to/your/data
python -m bettercode.rnaseq.stateless_workflow.run_workflow
```

### Force Re-run from a Specific Step

```python
from pathlib import Path
from bettercode.rnaseq.stateless_workflow.run_workflow import (
    run_stateless_workflow,
    print_checkpoint_status,
)

datadir = Path('/path/to/your/data/immune_aging')

# Check current checkpoint status
print_checkpoint_status(datadir)

# Force re-run from step 5 onwards
results = run_stateless_workflow(datadir, force_from_step=5)
```

### Available Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `datadir` | Required | Base directory for data files |
| `dataset_name` | "OneK1K" | Name of the dataset |
| `url` | CELLxGENE URL | Source URL for the h5ad file |
| `cell_type_for_de` | "central memory CD4-positive, alpha-beta T cell" | Cell type for differential expression |
| `force_from_step` | None | Clear checkpoints from this step onwards |
| `checkpoint_steps` | {2,3,5,8,9,10,11} | Which steps to save checkpoints for |

### Utility Functions

```python
from bettercode.rnaseq.stateless_workflow.run_workflow import (
    list_checkpoints,
    print_checkpoint_status,
    list_execution_logs,
    load_execution_log,
)

# List all checkpoints
checkpoints = list_checkpoints(datadir)

# Print checkpoint status with file sizes
print_checkpoint_status(datadir)

# View execution history
logs = list_execution_logs(datadir)
if logs:
    log = load_execution_log(logs[0])  # Load most recent
    log.print_summary()
```

### Output Location

```
{datadir}/workflow/
├── checkpoints/    # BIDS-named checkpoint files
├── figures/        # Visualization outputs
└── logs/           # Execution logs (JSON)
```

### Notes

- Automatic checkpointing and resumption
- Execution logging with timing information
- Analyzes only one cell type
- Step 3 checkpoint required for pseudobulking

---

## 4. Prefect Workflow

The Prefect workflow uses the Prefect orchestration framework and analyzes all cell types in parallel.

**Location:** `prefect_workflow/run_workflow.py`

### Running the Workflow

```bash
# Basic run with default config
python -m bettercode.rnaseq.prefect_workflow.run_workflow --datadir /path/to/data/immune_aging

# With custom config file
python -m bettercode.rnaseq.prefect_workflow.run_workflow \
    --datadir /path/to/data/immune_aging \
    --config /path/to/custom_config.yaml

# Force re-run from step 8
python -m bettercode.rnaseq.prefect_workflow.run_workflow \
    --datadir /path/to/data/immune_aging \
    --force-from 8
```

### List Available Cell Types

```bash
python -m bettercode.rnaseq.prefect_workflow.run_workflow \
    --datadir /path/to/data/immune_aging \
    --list-cell-types
```

### Analyze a Single Cell Type

```bash
python -m bettercode.rnaseq.prefect_workflow.run_workflow \
    --datadir /path/to/data/immune_aging \
    --cell-type "central memory CD4-positive, alpha-beta T cell"
```

### CLI Options

| Option | Description |
|--------|-------------|
| `--datadir` | Base directory for data files |
| `--config` | Path to custom config YAML file |
| `--force-from` | Force re-run from this step onwards (1-11) |
| `--cell-type` | Analyze a single cell type only |
| `--list-cell-types` | List available cell types and exit |

### Configuration File

The default configuration is in `prefect_workflow/config/config.yaml`. You can create a custom config to override any parameters:

```yaml
# Custom config example
dataset_name: "MyDataset"

filtering:
  cutoff_percentile: 2.0
  min_cells_per_celltype: 20

qc:
  min_genes: 300
  max_genes: 5000

differential_expression:
  n_cpus: 16

min_samples_per_cell_type: 20
```

### Output Location

```
{datadir}/wf_prefect/
├── checkpoints/           # BIDS-named checkpoint files
├── figures/               # Visualization outputs
├── results/per_cell_type/ # Per-cell-type analysis results
│   └── {cell_type}/
│       ├── stat_res.pkl
│       ├── de_results.parquet
│       ├── counts.parquet
│       ├── gsea_results.pkl
│       ├── enrichr_up.pkl
│       ├── enrichr_down.pkl
│       └── prediction_results.pkl
└── logs/                  # Execution logs
```

### Notes

- Analyzes ALL cell types (not just one)
- Configuration via YAML file
- Results saved per cell type
- Uses Prefect for orchestration and logging

---

## 5. Snakemake Workflow

The Snakemake workflow uses the Snakemake workflow management system with dynamic rule generation for per-cell-type analysis.

**Location:** `snakemake_workflow/Snakefile`

### Running the Workflow

```bash
cd src/bettercode/rnaseq/snakemake_workflow

# Run full workflow
snakemake --cores 16 --config datadir=/path/to/data/immune_aging

# Dry run (see what would be executed)
snakemake -n --config datadir=/path/to/data/immune_aging

# Run only preprocessing (steps 1-6)
snakemake --cores 16 preprocessing_only --config datadir=/path/to/data/immune_aging

# Run only through pseudobulking (steps 1-7)
snakemake --cores 16 pseudobulk_only --config datadir=/path/to/data/immune_aging
```

### Force Re-run from a Specific Rule

```bash
# Force re-run from dimensionality reduction
snakemake --cores 16 --forcerun dimensionality_reduction \
    --config datadir=/path/to/data/immune_aging

# Force re-run from a specific cell type's DE
snakemake --cores 16 --forcerun differential_expression \
    --config datadir=/path/to/data/immune_aging
```

### Configuration

Configuration is in `snakemake_workflow/config/config.yaml`. Override any parameter via command line:

```bash
snakemake --cores 16 --config \
    datadir=/path/to/data/immune_aging \
    dataset_name=MyDataset \
    min_samples_per_cell_type=20
```

### Generate Workflow Visualization

```bash
# Generate rule graph
snakemake --rulegraph --config datadir=/path/to/data/immune_aging | dot -Tpng > rulegraph.png

# Generate DAG for specific run
snakemake --dag --config datadir=/path/to/data/immune_aging | dot -Tpng > dag.png
```

### Output Location

```
{datadir}/wf_snakemake/
├── checkpoints/           # BIDS-named checkpoint files
├── figures/               # Visualization outputs
├── results/
│   ├── per_cell_type/     # Per-cell-type analysis results
│   │   └── {cell_type}/
│   │       ├── stat_res.pkl
│   │       ├── de_results.parquet
│   │       ├── counts.parquet
│   │       ├── gsea_results.pkl
│   │       ├── enrichr_up.pkl
│   │       ├── enrichr_down.pkl
│   │       └── prediction_results.pkl
│   └── workflow_complete.txt
└── logs/                  # Step logs
```

### Notes

- Uses Snakemake checkpoint mechanism for dynamic cell type discovery
- Analyzes ALL cell types
- Automatic dependency tracking and parallel execution
- See `WORKFLOW_OVERVIEW.md` for detailed step documentation

---

## Workflow Comparison

| Feature | Monolithic | Modular | Stateless | Prefect | Snakemake |
|---------|------------|---------|-----------|---------|-----------|
| Checkpointing | No | Limited | Yes | Yes | Yes |
| Resume from step | No | Limited | Yes | Yes | Yes |
| All cell types | No | No | No | Yes | Yes |
| Config file | No | No | No | Yes | Yes |
| Execution logs | No | No | Yes | Yes | Yes |
| Parallel execution | No | No | No | Sequential | Yes |
| Output folder | workflow | workflow | workflow | wf_prefect | wf_snakemake |

---

## Troubleshooting

### Memory Issues

The dataset is large (~1.2M cells). If you encounter memory issues:

1. Use a machine with at least 64GB RAM
2. For Prefect/Snakemake workflows, reduce `--cores` to limit parallel jobs
3. For the stateless workflow, ensure checkpoints are saved to reduce memory pressure

### Missing Dependencies

```bash
# Install all dependencies
uv pip install -e ".[dev]"

# For Snakemake specifically
uv pip install snakemake>=8.0
```

### Environment Variable Not Set

If you see "DATADIR environment variable not set":

```bash
# Set it for your session
export DATADIR=/path/to/your/data

# Or create .env file
echo "DATADIR=/path/to/your/data" > .env
```
