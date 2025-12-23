"""Preprocessing rules (Steps 1-6).

These rules handle the initial data processing pipeline:
1. Data Download
2. Data Filtering
3. Quality Control
4. Preprocessing (normalization, HVG selection)
5. Dimensionality Reduction (PCA, UMAP)
6. Clustering
"""


# Step 1: Data Download
rule download_data:
    output:
        DATADIR / f"dataset-{DATASET}_subset-immune_raw.h5ad",
    params:
        url=config["url"],
    log:
        LOG_DIR / "step01_download.log",
    script:
        "../scripts/download.py"


# Step 2: Data Filtering
rule filter_data:
    input:
        DATADIR / f"dataset-{DATASET}_subset-immune_raw.h5ad",
    output:
        CHECKPOINT_DIR / bids_checkpoint_name(DATASET, 2, "filtered"),
    params:
        cutoff_percentile=config["filtering"]["cutoff_percentile"],
        min_cells_per_celltype=config["filtering"]["min_cells_per_celltype"],
        percent_donors=config["filtering"]["percent_donors"],
        figure_dir=str(FIGURE_DIR),
    log:
        LOG_DIR / "step02_filtering.log",
    script:
        "../scripts/filter.py"


# Step 3: Quality Control
rule quality_control:
    input:
        CHECKPOINT_DIR / bids_checkpoint_name(DATASET, 2, "filtered"),
    output:
        CHECKPOINT_DIR / bids_checkpoint_name(DATASET, 3, "qc"),
    threads: workflow.cores
    params:
        min_genes=config["qc"]["min_genes"],
        max_genes=config["qc"]["max_genes"],
        min_counts=config["qc"]["min_counts"],
        max_counts=config["qc"]["max_counts"],
        max_hb_pct=config["qc"]["max_hb_pct"],
        expected_doublet_rate=config["qc"]["expected_doublet_rate"],
        figure_dir=str(FIGURE_DIR),
    log:
        LOG_DIR / "step03_qc.log",
    script:
        "../scripts/qc.py"


# Step 4: Preprocessing
rule preprocess:
    input:
        CHECKPOINT_DIR / bids_checkpoint_name(DATASET, 3, "qc"),
    output:
        CHECKPOINT_DIR / bids_checkpoint_name(DATASET, 4, "preprocessed"),
    threads: workflow.cores
    params:
        target_sum=config["preprocessing"]["target_sum"],
        n_top_genes=config["preprocessing"]["n_top_genes"],
        batch_key=config["preprocessing"]["batch_key"],
    log:
        LOG_DIR / "step04_preprocessing.log",
    script:
        "../scripts/preprocess.py"


# Step 5: Dimensionality Reduction
rule dimensionality_reduction:
    input:
        CHECKPOINT_DIR / bids_checkpoint_name(DATASET, 4, "preprocessed"),
    output:
        CHECKPOINT_DIR / bids_checkpoint_name(DATASET, 5, "dimreduced"),
    threads: workflow.cores
    params:
        batch_key=config["dimred"]["batch_key"],
        n_neighbors=config["dimred"]["n_neighbors"],
        n_pcs=config["dimred"]["n_pcs"],
        figure_dir=str(FIGURE_DIR),
    log:
        LOG_DIR / "step05_dimred.log",
    script:
        "../scripts/dimred.py"


# Step 6: Clustering
rule clustering:
    input:
        CHECKPOINT_DIR / bids_checkpoint_name(DATASET, 5, "dimreduced"),
    output:
        CHECKPOINT_DIR / bids_checkpoint_name(DATASET, 6, "clustered"),
    params:
        resolution=config["clustering"]["resolution"],
        figure_dir=str(FIGURE_DIR),
    log:
        LOG_DIR / "step06_clustering.log",
    script:
        "../scripts/cluster.py"
