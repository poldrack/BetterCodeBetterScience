# Snakemake scRNA-seq Immune Aging Workflow

## Overview

This workflow analyzes single-cell RNA sequencing (scRNA-seq) data to investigate gene expression changes associated with aging in immune cells. It processes data from the OneK1K dataset (peripheral blood mononuclear cells from 982 donors) through quality control, normalization, dimensionality reduction, and per-cell-type differential expression analysis.

The workflow is divided into two phases:
- **Global Steps (1-7)**: Process the entire dataset
- **Per-Cell-Type Steps (8-11)**: Run independently for each cell type discovered in Step 7

---

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         GLOBAL STEPS (1-7)                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Step 1: Download ──► Step 2: Filter ──► Step 3: QC ──► Step 4: Preprocess
│                                                               │         │
│                                                               ▼         │
│             Step 7: Pseudobulk ◄── Step 6: Cluster ◄── Step 5: DimRed.  |
│                              │                                          │
└──────────────────────────────┼──────────────────────────────────────────┘
                               │
                               ▼ (discovers N cell types)
┌──────────────────────────────────────────────────────────────────────────┐
│                    PER-CELL-TYPE STEPS (8-11)                            │
│                    Runs in parallel for each cell type                   │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  For each cell type:                                                     │
│                                                                          │
│    Step 8: Differential Expression                                       │
│         │                                                                │
│         ├──► Step 9: GSEA (Pathway Analysis)                             │
│         │                                                                │
│         ├──► Step 10: Enrichr (Overrepresentation)                       │
│         │                                                                │
│         └──► Step 11: Predictive Modeling (Age Prediction)               │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Step Details

### Step 1: Data Download

**Purpose**: Download the raw scRNA-seq dataset from CELLxGENE.

| Parameter | Default Value | Description |
|-----------|--------------|-------------|
| `url` | CELLxGENE URL | Source URL for the h5ad file |
| `dataset_name` | "OneK1K" | Dataset identifier |

**Input**: None (downloads from URL)
**Output**: Raw h5ad file (~1.2M cells × 35K genes)

---

### Step 2: Data Filtering

**Purpose**: Remove low-quality donors and rare cell types to ensure robust downstream analysis.

**Operations**:
1. **Donor filtering**: Remove donors with abnormally low cell counts
   - Uses percentile-based cutoff to identify outliers
2. **Cell type filtering**: Keep only cell types present in sufficient donors
   - Requires minimum cells per cell type in a threshold percentage of donors
3. **Zero-count gene removal**: Remove genes with no expression across retained cells
4. **Memory loading**: Convert lazy-loaded data to in-memory representation

| Parameter | Default Value | Description |
|-----------|--------------|-------------|
| `cutoff_percentile` | 1.0 | Percentile for donor cell count cutoff |
| `min_cells_per_celltype` | 10 | Minimum cells per cell type per donor |
| `percent_donors` | 0.95 | Fraction of donors that must have the cell type |

**Input**: Raw h5ad file
**Output**: Filtered h5ad checkpoint

---

### Step 3: Quality Control (QC)

**Purpose**: Identify and remove low-quality cells, dying cells, and doublets.

**Operations**:
1. **Gene annotation**: Identify mitochondrial (MT-), ribosomal (RPS/RPL), and hemoglobin (HB) genes
2. **QC metric calculation**: Compute per-cell metrics using scanpy
   - Total counts, genes detected, % mitochondrial, % ribosomal, % hemoglobin
3. **Cell filtering**: Remove cells outside quality thresholds
4. **Doublet detection**: Run Scrublet per-donor to identify and remove doublets
5. **Raw count preservation**: Store raw counts in a layer for pseudobulking

| Parameter | Default Value | Description |
|-----------|--------------|-------------|
| `min_genes` | 200 | Minimum genes per cell |
| `max_genes` | 6000 | Maximum genes per cell (doublet filter) |
| `min_counts` | 500 | Minimum UMIs per cell |
| `max_counts` | 30000 | Maximum UMIs per cell (doublet filter) |
| `max_hb_pct` | 5.0 | Maximum hemoglobin % (RBC contamination) |
| `expected_doublet_rate` | 0.06 | Expected doublet rate for Scrublet |

**Algorithm**: Scrublet (doublet detection)
**Input**: Filtered h5ad
**Output**: QC-filtered h5ad checkpoint

---

### Step 4: Preprocessing

**Purpose**: Normalize expression values and select informative genes for downstream analysis.

**Operations**:
1. **Normalization**: Scale counts to target sum per cell (CPM-like)
2. **Log transformation**: Apply log1p transformation for variance stabilization
3. **HVG selection**: Identify highly variable genes using Seurat v3 method
   - Accounts for batch effects using donor as batch key
4. **Nuisance gene removal**: Exclude from HVG list:
   - TCR/BCR variable region genes (IG[HKL]V, TR[ABDG]V patterns)
   - Mitochondrial genes (MT-*)
   - Ribosomal genes (RPS*, RPL*)
5. **PCA**: Compute principal components on HVG subset

| Parameter | Default Value | Description |
|-----------|--------------|-------------|
| `target_sum` | 10000 | Target sum for normalization |
| `n_top_genes` | 3000 | Number of highly variable genes |
| `batch_key` | "donor_id" | Column for batch correction in HVG selection |

**Algorithms**:
- Normalization: scanpy `normalize_total`
- HVG: Seurat v3 method (`flavor="seurat_v3"`)
- PCA: ARPACK solver

**Input**: QC-filtered h5ad
**Output**: Preprocessed h5ad checkpoint

---

### Step 5: Dimensionality Reduction

**Purpose**: Reduce dimensionality and correct for batch effects for visualization and clustering.

**Operations**:
1. **Batch correction**: Run Harmony integration on PCA coordinates
   - Corrects for donor-specific technical effects
2. **Neighbor graph**: Compute k-nearest neighbor graph in corrected PCA space
3. **UMAP**: Generate 2D embedding for visualization

| Parameter | Default Value | Description |
|-----------|--------------|-------------|
| `batch_key` | "donor_id" | Column for batch correction |
| `n_neighbors` | 30 | Number of neighbors for graph |
| `n_pcs` | 40 | Number of PCs to use |

**Algorithms**:
- Batch correction: Harmony (harmony-pytorch)
- Neighbor graph: scanpy `pp.neighbors` (uses pynndescent/numba)
- UMAP: scanpy `tl.umap`

**Input**: Preprocessed h5ad
**Output**: Dimensionality-reduced h5ad checkpoint

---

### Step 6: Clustering

**Purpose**: Cluster cells for visualization and validation (uses pre-existing cell type annotations).

**Operations**:
1. **Leiden clustering**: Community detection on neighbor graph
2. **UMAP visualization**: Plot clusters colored by cell type

| Parameter | Default Value | Description |
|-----------|--------------|-------------|
| `resolution` | 1.0 | Leiden clustering resolution |

**Algorithm**: Leiden clustering (scanpy `tl.leiden`)

**Input**: Dimensionality-reduced h5ad
**Output**: Clustered h5ad checkpoint

---

### Step 7: Pseudobulking (Checkpoint)

**Purpose**: Aggregate single-cell counts to donor-level pseudobulk samples for differential expression analysis.

**Operations**:
1. **Count aggregation**: Sum raw counts per (cell_type, donor) combination
   - Uses one-hot encoding for efficient sparse matrix multiplication
2. **Metadata preservation**: Retain donor-level metadata (age, sex, etc.)
3. **Sample filtering**: Remove pseudobulk samples with too few contributing cells
4. **Cell type discovery**: Identify cell types with sufficient samples for analysis

| Parameter | Default Value | Description |
|-----------|--------------|-------------|
| `group_col` | "cell_type" | Column for grouping cells |
| `donor_col` | "donor_id" | Column for donor identity |
| `metadata_cols` | ["development_stage", "sex"] | Metadata to preserve |
| `min_cells` | 10 | Minimum cells per pseudobulk sample |
| `min_samples_per_cell_type` | 10 | Minimum samples to include cell type |

**Note**: This step uses Snakemake's `checkpoint` mechanism to dynamically determine which cell types to analyze in subsequent steps.

**Input**: QC checkpoint (raw counts), filtered checkpoint (gene names)
**Output**: Pseudobulk h5ad, cell_types.json, var_to_feature.json

---

### Step 8: Differential Expression (Per-Cell-Type)

**Purpose**: Identify genes associated with aging within each cell type.

**Operations**:
1. **Age extraction**: Parse numeric age from development_stage field
2. **Age scaling**: Z-score normalize age for stable model fitting
3. **DESeq2 analysis**: Fit negative binomial GLM with design `~ age_scaled + sex`
4. **Wald test**: Test for age effect (contrast on age_scaled coefficient)
5. **Multiple testing**: Apply Benjamini-Hochberg FDR correction

| Parameter | Default Value | Description |
|-----------|--------------|-------------|
| `design_factors` | ["age_scaled", "sex"] | Model covariates |
| `n_cpus` | 8 | CPUs for DESeq2 |

**Algorithm**: DESeq2 (via PyDESeq2)
- Dispersion estimation with shrinkage
- Wald test for coefficient significance
- Cook's distance for outlier detection

**Input**: Pseudobulk h5ad, var_to_feature mapping
**Output**: DESeq2 statistics (pkl), results table (parquet), counts (parquet)

---

### Step 9: Pathway Analysis - GSEA (Per-Cell-Type)

**Purpose**: Identify biological pathways enriched in aging-associated genes using ranked gene set enrichment.

**Operations**:
1. **Gene ranking**: Rank genes by DESeq2 test statistic
2. **Preranked GSEA**: Run against MSigDB Hallmark gene sets
3. **NES calculation**: Compute normalized enrichment scores
4. **Visualization**: Generate pathway enrichment plots

| Parameter | Default Value | Description |
|-----------|--------------|-------------|
| `gene_sets` | ["MSigDB_Hallmark_2020"] | Gene set databases |
| `n_top` | 10 | Number of top pathways to display |

**Algorithm**: GSEA prerank (via gseapy)
- 1000 permutations for p-value estimation
- Min pathway size: 10 genes, Max: 1000 genes

**Input**: DE results (parquet)
**Output**: GSEA results (pkl)

---

### Step 10: Overrepresentation Analysis - Enrichr (Per-Cell-Type)

**Purpose**: Test for pathway enrichment in significantly up/down-regulated gene sets.

**Operations**:
1. **Gene set extraction**: Separate significant genes (padj < 0.05) by direction
2. **Enrichr analysis**: Query Enrichr web service for pathway enrichment
3. **Visualization**: Generate dot plots for enriched pathways

| Parameter | Default Value | Description |
|-----------|--------------|-------------|
| `gene_sets` | ["MSigDB_Hallmark_2020"] | Gene set databases |
| `padj_threshold` | 0.05 | Significance threshold for gene selection |
| `n_top` | 10 | Number of top pathways to display |

**Algorithm**: Enrichr (via gseapy)
- Fisher's exact test with FDR correction

**Input**: DE results (parquet)
**Output**: Enrichr results for up/down genes (pkl)

---

### Step 11: Predictive Modeling (Per-Cell-Type)

**Purpose**: Assess whether gene expression in each cell type can predict donor age.

**Operations**:
1. **Feature preparation**: Combine gene expression with sex as features
2. **Cross-validation**: 5-fold shuffle split
3. **Model training**: Linear Support Vector Regression with scaling
4. **Baseline comparison**: Compare full model (genes + sex) vs. baseline (sex only)
5. **Metrics**: R² score and Mean Absolute Error (MAE)

| Parameter | Default Value | Description |
|-----------|--------------|-------------|
| `n_splits` | 5 | Number of CV folds |

**Algorithm**: Linear SVR (scikit-learn)
- StandardScaler for feature normalization
- C=1.0 regularization
- Max 10,000 iterations

**Input**: Counts (parquet), pseudobulk metadata
**Output**: Prediction results with CV metrics (pkl)

---

## Output Structure

```
{datadir}/wf_snakemake/
├── checkpoints/
│   ├── dataset-{name}_step-02_desc-filtered.h5ad
│   ├── dataset-{name}_step-03_desc-qc.h5ad
│   ├── dataset-{name}_step-04_desc-preprocessed.h5ad
│   ├── dataset-{name}_step-05_desc-dimreduced.h5ad
│   ├── dataset-{name}_step-06_desc-clustered.h5ad
│   ├── dataset-{name}_step-07_desc-pseudobulk.h5ad
│   ├── dataset-{name}_step-07_cell_types.json
│   └── dataset-{name}_step-07_var_to_feature.json
├── results/
│   └── per_cell_type/
│       └── {cell_type}/
│           ├── stat_res.pkl
│           ├── de_results.parquet
│           ├── counts.parquet
│           ├── gsea_results.pkl
│           ├── enrichr_up.pkl
│           ├── enrichr_down.pkl
│           └── prediction_results.pkl
├── figures/
│   ├── donor_cell_counts_distribution.png
│   ├── qc_violin_plots.png
│   ├── hemoglobin_distribution.png
│   ├── pca_cell_type.png
│   ├── umap_total_counts.png
│   └── per_cell_type/{cell_type}/
│       ├── gsea_pathways.png
│       └── enrichr_*.png
└── logs/
    └── step*.log
```

---

## Usage

```bash
# Run full workflow
snakemake --cores 16 --config datadir=/path/to/data

# Dry run (see what would be executed)
snakemake -n --config datadir=/path/to/data

# Run only preprocessing (steps 1-6)
snakemake --cores 16 preprocessing_only --config datadir=/path/to/data

# Force re-run from a specific step
snakemake --cores 16 --forcerun dimensionality_reduction --config datadir=/path/to/data
```

---

## Key Dependencies

| Package | Purpose |
|---------|---------|
| scanpy | scRNA-seq analysis framework |
| anndata | Data structure for scRNA-seq |
| harmony-pytorch | Batch correction |
| pydeseq2 | Differential expression |
| gseapy | GSEA and Enrichr analysis |
| scikit-learn | Predictive modeling |
| snakemake | Workflow management |
