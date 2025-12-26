This workflow performs single-cell RNA-seq analysis of immune aging data.

The analysis consists of 11 steps:

**Global Preprocessing (Steps 1-7)**

1. Data Download - Retrieve raw data from repository
2. Data Filtering - Remove low-quality cells and cell types
3. Quality Control - Filter cells based on QC metrics and detect doublets
4. Preprocessing - Normalize and select highly variable genes
5. Dimensionality Reduction - PCA and UMAP computation
6. Clustering - Leiden clustering for cell type identification
7. Pseudobulking - Aggregate single-cell data to pseudobulk per donor/cell-type

**Per-Cell-Type Analysis (Steps 8-11)**

For each cell type discovered in step 7:

8. Differential Expression - Compare gene expression between conditions
9. Pathway Analysis (GSEA) - Identify enriched biological pathways
10. Overrepresentation Analysis - Enrichr analysis of DE genes
11. Predictive Modeling - Age prediction from gene expression

Configuration
=============

Dataset: ``{{ snakemake.config["dataset_name"] }}``

Data directory: ``{{ snakemake.config["datadir"] }}``
