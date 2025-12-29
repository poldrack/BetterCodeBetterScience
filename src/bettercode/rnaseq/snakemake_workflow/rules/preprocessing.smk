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
    conda:
        "bettercode"
    script:
        "../scripts/download.py"


# Step 2: Data Filtering
rule filter_data:
    input:
        DATADIR / f"dataset-{DATASET}_subset-immune_raw.h5ad",
    output:
        checkpoint=CHECKPOINT_DIR / bids_checkpoint_name(DATASET, 2, "filtered"),
        fig_donor_counts=report(
            FIGURE_DIR / "donor_cell_counts_distribution.png",
            caption="../report/filtering.rst",
            category="Step 2: Filtering",
        ),
    params:
        cutoff_percentile=config["filtering"]["cutoff_percentile"],
        min_cells_per_celltype=config["filtering"]["min_cells_per_celltype"],
        percent_donors=config["filtering"]["percent_donors"],
        figure_dir=str(FIGURE_DIR),
    log:
        LOG_DIR / "step02_filtering.log",
    conda:
        "bettercode"
    script:
        "../scripts/filter.py"


# Step 3: Quality Control
rule quality_control:
    input:
        CHECKPOINT_DIR / bids_checkpoint_name(DATASET, 2, "filtered"),
    output:
        checkpoint=CHECKPOINT_DIR / bids_checkpoint_name(DATASET, 3, "qc"),
        fig_violin=report(
            FIGURE_DIR / "qc_violin_plots.png",
            caption="../report/qc_violin.rst",
            category="Step 3: Quality Control",
        ),
        fig_scatter=report(
            FIGURE_DIR / "qc_scatter_doublets.png",
            caption="../report/qc_scatter.rst",
            category="Step 3: Quality Control",
        ),
        fig_hemoglobin=report(
            FIGURE_DIR / "hemoglobin_distribution.png",
            caption="../report/hemoglobin.rst",
            category="Step 3: Quality Control",
        ),
        fig_doublet_umap=report(
            FIGURE_DIR / "doublet_detection_umap.png",
            caption="../report/doublet_umap.rst",
            category="Step 3: Quality Control",
        ),
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
    conda:
        "bettercode"
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
    conda:
        "bettercode"
    script:
        "../scripts/preprocess.py"


# Step 5: Dimensionality Reduction
rule dimensionality_reduction:
    input:
        CHECKPOINT_DIR / bids_checkpoint_name(DATASET, 4, "preprocessed"),
    output:
        checkpoint=CHECKPOINT_DIR / bids_checkpoint_name(DATASET, 5, "dimreduced"),
        fig_pca=report(
            FIGURE_DIR / "pca_cell_type.png",
            caption="../report/pca.rst",
            category="Step 5: Dimensionality Reduction",
        ),
        fig_umap=report(
            FIGURE_DIR / "umap_total_counts.png",
            caption="../report/umap.rst",
            category="Step 5: Dimensionality Reduction",
        ),
    threads: workflow.cores
    params:
        batch_key=config["dimred"]["batch_key"],
        n_neighbors=config["dimred"]["n_neighbors"],
        n_pcs=config["dimred"]["n_pcs"],
        figure_dir=str(FIGURE_DIR),
    log:
        LOG_DIR / "step05_dimred.log",
    conda:
        "bettercode"
    script:
        "../scripts/dimred.py"


# Step 6: Clustering
rule clustering:
    input:
        CHECKPOINT_DIR / bids_checkpoint_name(DATASET, 5, "dimreduced"),
    output:
        checkpoint=CHECKPOINT_DIR / bids_checkpoint_name(DATASET, 6, "clustered"),
        fig_clustering=report(
            FIGURE_DIR / "umap_cell_type_leiden.png",
            caption="../report/clustering.rst",
            category="Step 6: Clustering",
        ),
    params:
        resolution=config["clustering"]["resolution"],
        figure_dir=str(FIGURE_DIR),
    log:
        LOG_DIR / "step06_clustering.log",
    conda:
        "bettercode"
    script:
        "../scripts/cluster.py"
