# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.18.1
#   kernelspec:
#     display_name: BetterCodeBetterScience
#     language: python
#     name: python3
# ---

# %% [markdown]
# ### Immune system gene expression and aging
#
# We will use a dataset distributed by the [OneK1K](https://onek1k.org/) project, which includes single-cell RNA-seq data from peripheral blood mononuclear cells (PBMCs) obtained from 982 donors, comprising more than 1.2 million cells in total.  These data are released under a Creative Commons Zero Public Domain Dedication and are thus free to reuse, with the restriction that users agree not to attempt to reidentify the participants.
#
# The flagship paper for this study is:
#
# Yazar S., Alquicira-Hernández J., Wing K., Senabouth A., Gordon G., Andersen S., Lu Q., Rowson A., Taylor T., Clarke L., Maccora L., Chen C., Cook A., Ye J., Fairfax K., Hewitt A., Powell J. Single cell eQTL mapping identified cell type specific control of autoimmune disease. Science, 376, 6589 (2022)
#
# We will use the data to ask a simple question: how does gene expression in PBMCs change with age?


# %%
import anndata as ad
import h5py
import numpy as np
import scanpy as sc
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from anndata.experimental import read_lazy
import os
import pandas as pd
from scipy.stats import scoreatpercentile
import re
import scanpy.external as sce
from sklearn.preprocessing import OneHotEncoder
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats
from sklearn.preprocessing import StandardScaler
import gseapy as gp
from sklearn.svm import LinearSVR
from sklearn.model_selection import ShuffleSplit
from sklearn.metrics import r2_score, mean_absolute_error


datadir = Path('/Users/poldrack/data_unsynced/BCBS/immune_aging/')


# %% [markdown]
# ### Immune system gene expression and aging
#
# We will use a dataset distributed by the [OneK1K](https://onek1k.org/) project, which includes single-cell RNA-seq data from peripheral blood mononuclear cells (PBMCs) obtained from 982 donors, comprising more than 1.2 million cells in total.  These data are released under a Creative Commons Zero Public Domain Dedication and are thus free to reuse, with the restriction that users agree not to attempt to reidentify the participants.
#
# The flagship paper for this study is:
#
# Yazar S., Alquicira-Hernández J., Wing K., Senabouth A., Gordon G., Andersen S., Lu Q., Rowson A., Taylor T., Clarke L., Maccora L., Chen C., Cook A., Ye J., Fairfax K., Hewitt A., Powell J. Single cell eQTL mapping identified cell type specific control of autoimmune disease. Science, 376, 6589 (2022)
#
# We will use the data to ask a simple question: how does gene expression in PBMCs change with age?
#
# # Code in this notebook primarily generated using Gemini 3.0


# %%

datadir = Path('/Users/poldrack/data_unsynced/BCBS/immune_aging/')

# %%
datafile = datadir / 'a3f5651f-cd1a-4d26-8165-74964b79b4f2.h5ad'
url = 'https://datasets.cellxgene.cziscience.com/a3f5651f-cd1a-4d26-8165-74964b79b4f2.h5ad'
dataset_name = 'OneK1K'

if not datafile.exists():
    cmd = f'wget -O {datafile.as_posix()} {url}'
    print(f'Downloading data from {url} to {datafile.as_posix()}')
    os.system(cmd)

load_annotation_index = True
adata = read_lazy(
    h5py.File(datafile, 'r'), load_annotation_index=load_annotation_index
)

# %%
print(adata)

# %%
unique_cell_types = np.unique(adata.obs['cell_type'])
print(unique_cell_types)

# %% [markdown]
# ### Filtering out bad donors

# %%


# 1. Calculate how many cells each donor has
donor_cell_counts = pd.Series(adata.obs['donor_id']).value_counts()

# Print some basic statistics to read the exact numbers
print('Donor Cell Count Statistics:')
print(donor_cell_counts.describe())

# 2. Plot the histogram
plt.figure(figsize=(10, 6))
# Bins set to 'auto' or a fixed number depending on your N of donors
plt.hist(donor_cell_counts.values, bins=50, color='skyblue', edgecolor='black')

plt.title('Distribution of Total Cells per Donor')
plt.xlabel('Number of Cells Captured')
plt.ylabel('Number of Donors')
plt.grid(axis='y', alpha=0.5)

# Optional: Draw a vertical line at the propsoed cutoff
# This helps you visualize how many donors you would lose.
cutoff_percentile = 10  # e.g., 10th percentile
min_cells_per_donor = int(
    scoreatpercentile(donor_cell_counts.values, cutoff_percentile)
)
print(
    f'cutoff of {min_cells_per_donor} would exclude {(donor_cell_counts < min_cells_per_donor).sum()} donors'
)
plt.axvline(
    min_cells_per_donor,
    color='red',
    linestyle='dashed',
    linewidth=1,
    label=f'Cutoff ({min_cells_per_donor} cells)',
)
plt.legend()

plt.show()

# %%
print(
    f'Filtering to keep only donors with at least {min_cells_per_donor} cells.'
)
print(
    f'Number of donors excluded: {(donor_cell_counts < min_cells_per_donor).sum()}'
)
valid_donors = donor_cell_counts[
    donor_cell_counts >= min_cells_per_donor
].index
adata = adata[adata.obs['donor_id'].isin(valid_donors)]

# %%
print(f'Number of donors after filtering: {len(valid_donors)}')

# %% [markdown]
# ### Filtering cell types by frequency
#
# Drop cell types that don't have at least 10 cells for at least 95% of people

# %%

# 1. Calculate the count of cells for each 'cell_type' within each 'donor_id'
# We use pandas crosstab on adata.obs, which is loaded in memory.
counts_per_donor = pd.crosstab(adata.obs['donor_id'], adata.obs['cell_type'])

# 2. Identify cell types to keep
# Keep if >= 10 cells in at least 90% of donors

min_cells = 10
percent_donors = 0.9
donor_count = counts_per_donor.shape[0]
cell_types_to_keep = counts_per_donor.columns[
    (counts_per_donor >= min_cells).sum(axis=0)
    >= (donor_count * percent_donors)
]

print(
    f'Keeping {len(cell_types_to_keep)} cell types out of {len(counts_per_donor.columns)}'
)
print(f'Cell types to keep: {cell_types_to_keep.tolist()}')

# 3. Filter the AnnData object
# We subset the AnnData to include only observations belonging to the valid cell types.
adata_filtered = adata[adata.obs['cell_type'].isin(cell_types_to_keep)]

# %%
# now drop subjects who have any zeros in these cell types
donor_celltype_counts = pd.crosstab(
    adata_filtered.obs['donor_id'], adata_filtered.obs['cell_type']
)
valid_donors_final = donor_celltype_counts.index[
    (donor_celltype_counts >= min_cells).all(axis=1)
]
adata_filtered = adata_filtered[
    adata_filtered.obs['donor_id'].isin(valid_donors_final)
]
print(f'Final number of donors after filtering: {len(valid_donors_final)}')

# %%

print('Loading data into memory (this can take a few minutes)...')
adata_loaded = adata_filtered.to_memory()

# filter out genes with zero counts across all selected cells
print('Filtering genes with zero counts...')
sc.pp.filter_genes(adata_loaded, min_counts=1)


# %%
print(adata_loaded)


# %%
adata_loaded.write(
    datadir / f'dataset-{dataset_name}_subset-immune_filtered.h5ad'
)
del adata_loaded

# %%
adata = ad.read_h5ad(
    datadir / f'dataset-{dataset_name}_subset-immune_filtered.h5ad'
)
print(adata)

# %%
var_to_feature = dict(zip(adata.var_names, adata.var['feature_name']))

# %% [markdown]
# Preprocessing based on suggestions from Google Gemini
#
# based on https://www.sc-best-practices.org/preprocessing_visualization/quality_control.html
#
# and https://www.10xgenomics.com/analysis-guides/common-considerations-for-quality-control-filters-for-single-cell-rna-seq-data
#

# %% [markdown]
# ### Quality control
#
# based on https://www.sc-best-practices.org/preprocessing_visualization/quality_control.html
#

# %%
# mitochondrial genes
adata.var['mt'] = adata.var['feature_name'].str.startswith('MT-')
print(f"Number of mitochondrial genes: {adata.var['mt'].sum()}")

# ribosomal genes
adata.var['ribo'] = adata.var['feature_name'].str.startswith(('RPS', 'RPL'))
print(f"Number of ribosomal genes: {adata.var['ribo'].sum()}")

# hemoglobin genes.
adata.var['hb'] = adata.var['feature_name'].str.contains('^HB[^(P)]')
print(f"Number of hemoglobin genes: {adata.var['hb'].sum()}")

sc.pp.calculate_qc_metrics(
    adata,
    qc_vars=['mt', 'ribo', 'hb'],
    inplace=True,
    percent_top=[20],
    log1p=True,
)


# %% [markdown]
# #### Visualization of distributions

# %%

# 1. Violin plots to see the distribution of QC metrics
# Note: I am using the exact column names from your adata output
p1 = sc.pl.violin(
    adata,
    ['total_counts', 'n_genes_by_counts', 'pct_counts_mt'],
    jitter=0.4,
    multi_panel=True,
)

# 2. Scatter plot to spot doublets and dying cells
# High mito + low genes = dying cell
# High counts + high genes = potential doublet
sc.pl.scatter(
    adata, x='total_counts', y='n_genes_by_counts', color='pct_counts_mt'
)

# %% [markdown]
# ####  Check Hemoglobin (RBC contamination)
#

# %%

plt.figure(figsize=(6, 4))
sns.histplot(
    adata.obs['pct_counts_hb'], bins=50, log_scale=(False, True)
)   # Log scale y to see small RBC populations
plt.title('Hemoglobin Content Distribution')
plt.xlabel('% Hemoglobin Counts')
plt.axvline(5, color='red', linestyle='--', label='5% Cutoff')
plt.legend()
plt.show()

# %% [markdown]
# #### Create a copy of the data and apply QC cutoffs
#

# %%
# Create a copy or view to avoid modifying the original if needed
adata_qc = adata.copy()

# --- Define Thresholds ---
# Low quality (Empty droplets / debris)
min_genes = 200       # Standard for immune cells (T-cells can be small)
min_counts = 500      # Minimum UMIs

# Doublets (Two cells stuck together)
# Adjust this based on the scatter plot above.
# 4000-6000 is common for 10x Genomics data.
max_genes = 6000
max_counts = 30000    # Very high counts often indicate doublets

# Contaminants
max_hb_pct = 5.0      # Remove Red Blood Cells (> 5% hemoglobin)

# --- Apply Filtering ---
print(f'Before filtering: {adata_qc.n_obs} cells')

# 1. Filter Low Quality & Doublets
adata_qc = adata_qc[
    (adata_qc.obs['n_genes_by_counts'] > min_genes)
    & (adata_qc.obs['n_genes_by_counts'] < max_genes)
    & (adata_qc.obs['total_counts'] > min_counts)
    & (adata_qc.obs['total_counts'] < max_counts)
]

# 2. Filter Red Blood Cells (Hemoglobin)
# Only run this if you want to remove RBCs
adata_qc = adata_qc[adata_qc.obs['pct_counts_hb'] < max_hb_pct]

print(f'After filtering: {adata_qc.n_obs} cells')

# %% [markdown]
# ### Perform doublet detection
#
# According to Gemini:
#
# You must do this before normalization or clustering because doublets create "hybrid" expression profiles that can form fake clusters (e.g., a "cluster" that looks like a mix of T-cells and B-cells) or distort your normalization factors.
#
# **Important: Run Per Donor**
#
# Since you have multiple people, you must run doublet detection separately for each donor. The doublet rate is a technical artifact of the physical loading of the machine (10x Genomics chip), which varies per run. If you run it on the whole dataset at once, the algorithm will get confused by biological differences between people.
#

# %%

# 1. Check preliminary requirements
# Scrublet needs RAW counts. Ensure adata.X contains integers, not log-normalized data.
# If your main layer is already normalized, use adata.raw or a specific layer.
print(f'Data shape before doublet detection: {adata_qc.shape}')

# 2. Run Scrublet per donor
# We split the data, run detection, and then recombine.
# This prevents the algorithm from comparing a cell from Person A to a cell from Person B.

adatas_list = []
# Get list of unique donors
donors = adata_qc.obs['donor_id'].unique()

print(f'Running Scrublet on {len(donors)} donors...')

for donor in donors:
    # Subset to current donor
    curr_adata = adata_qc[adata_qc.obs['donor_id'] == donor].copy()

    # Skip donors with too few cells (Scrublet needs statistical power)
    if curr_adata.n_obs < 100:
        print(f'Skipping donor {donor}: too few cells ({curr_adata.n_obs})')
        # We still add it back to keep the data, but mark as singlet (or filter later)
        curr_adata.obs['doublet_score'] = 0
        curr_adata.obs['predicted_doublet'] = False
        adatas_list.append(curr_adata)
        continue

    # Run Scrublet
    # expected_doublet_rate=0.06 is standard for 10x (approx ~0.8% per 1000 cells recovered)
    # If you loaded very heavily (20k cells/well), increase this to 0.10
    sc.pp.scrublet(curr_adata, expected_doublet_rate=0.06)

    adatas_list.append(curr_adata)

# 3. Merge back into one object
adata_qc = sc.concat(adatas_list)

# 4. Check results
print(
    f"Detected {adata_qc.obs['predicted_doublet'].sum()} doublets across all donors."
)
print(adata_qc.obs['predicted_doublet'].value_counts())

# %% [markdown]
# #### Visualize doublets
#
#

# %%
sc.pl.umap(adata_qc, color=['doublet_score', 'predicted_doublet'], size=20)

# %% [markdown]
# #### Filter doublets
# - Question: how consistent are these results with other methods for doublet detection? https://www.sc-best-practices.org/preprocessing_visualization/quality_control.html#doublet-detection

# %%
# Check how many doublets were found
print(f'found {adata_qc.obs["predicted_doublet"].sum()} predicted doublets')

# Filter the data to keep only singlets (False)
# write back to adata for simplicity
adata = adata_qc[not adata_qc.obs['predicted_doublet'], :]
print(f'Remaining cells: {adata.n_obs}')

# %% [markdown]
# #### Save raw counts for later use

# %%
#  set the .raw attribute (standard Scanpy convention)
adata.layers['counts'] = adata.X.copy()

# %% [markdown]
# ### Total Count Normalization
# This scales each cell so that they all have the same total number of counts (default is often 10,000, known as "CP10k").

# %%
# Normalize to 10,000 reads per cell
# target_sum=1e4 is the standard for 10x data
sc.pp.normalize_total(adata, target_sum=1e4)

# %% [markdown]
# ### Log Transformation (Log1p)
# This applies a natural logarithm to the data:  log(X+1). This reduces the skewness of the data (since gene expression follows a power law) and stabilizes the variance.

# %%
# Logarithmically transform the data
sc.pp.log1p(adata)

# %% [markdown]
# ### select high-variance features
#
# according to Gemini:
# For a large immune dataset (PBMCs, ~1.2M cells), the standard defaults often fail to capture the subtle biological variation needed to distinguish similar cell types (like CD4+ T-cell subsets).
#
# Here are the reasonable parameters and, more importantly, the **immune-specific strategy** you should use.
#
# #### The Recommended Parameters
#
# For a dataset of your size, the **`seurat_v3`** flavor is generally superior because it selects genes based on standardized variance (handling the mean-variance relationship better than the dispersion-based method).
#
# *   **`flavor`**: `'seurat_v3'` (Requires **RAW integer counts** in `adata.X` or a layer)
# *   **`n_top_genes`**: **2000 - 3000** (3000 is safer for immune data to capture rare cytokines/markers)
# *   **`batch_key`**: **`'donor_id'`** (CRITICAL)
#     *   *Why?* With 1.2M cells across many people, you have massive batch effects. If you don't set this, "highly variable genes" will just be the genes that differ between Person A and Person B (e.g., HLA genes, gender-specific genes like XIST/RPS4Y1), rather than genes distinguishing cell types.
#
# #### The "Expert" Trick: Blocklisting Nuisance Genes
# In immune datasets, "highly variable" does not always mean "biologically interesting." You often need to **exclude** specific gene families from the HVG list *after* calculation but *before* PCA, or they will hijack your clustering:
# 1.  **TCR/BCR Variable Regions (IG*, TR*):** These are hyper-variable by definition (V(D)J recombination). If you keep them, T-cells will cluster by **clone** (clonotype) rather than by **phenotype** (state).
# 2.  **Mitochondrial/Ribosomal:** Usually technical noise.
# 3.  **Cell Cycle:** (Optional) If you don't want proliferating cells to cluster separately.
#
#
#
# #### Why 3000 genes instead of 2000?
# Immune cells are dense with specific markers. The difference between a *Naive CD8 T-cell* and a *Central Memory CD8 T-cell* might rest on a handful of genes (e.g., *CCR7, SELL, IL7R* vs *GZMK*). If you limit to 2000 genes in a massive, diverse dataset, you might accidentally drop a subtle marker required to resolve these fine-grained states.

# %%


# 2. Run Highly Variable Gene Selection
# batch_key is critical here to find genes variable WITHIN donors, not BETWEEN them.
sc.pp.highly_variable_genes(
    adata,
    n_top_genes=3000,
    flavor='seurat_v3',
    batch_key='donor_id',
    span=0.8,  # helps avoid numerical issues with LOESS
    layer='counts',  # Change this to None if adata.X is raw counts
    subset=False,  # Keep False so we can manually filter the list below
)

# 3. Filter out "Nuisance" Genes from the HVG list
# We don't remove the genes from the object, we just set their 'highly_variable' status to False
# so they aren't used in PCA.

# A. Identify TCR/BCR genes (starts with IG or TR)
# Regex: IG or TR followed by a V, D, J, or C gene part

immune_receptor_genes = [
    name
    for name in adata.var_names
    if re.match(r'^(IG[HKL]|TR[ABDG])[VDJC]', name)
]

# B. Identify Ribosomal/Mitochondrial (if not already handled)
mt_genes = adata.var_names[adata.var_names.str.startswith('MT-')]
rb_genes = adata.var_names[adata.var_names.str.startswith(('RPS', 'RPL'))]

# C. Manually set them to False
genes_to_block = list(immune_receptor_genes) + list(mt_genes) + list(rb_genes)

# Using set operations for speed
adata.var.loc[adata.var_names.isin(genes_to_block), 'highly_variable'] = False

print(
    f'Blocked {len(immune_receptor_genes)} immune receptor genes from HVG list.'
)
print(f"Final HVG count: {adata.var['highly_variable'].sum()}")

# 4. Proceed to PCA
sc.tl.pca(adata, svd_solver='arpack', use_highly_variable=True)


# %% [markdown]
# ### Dimensionality reduction

# %%

# 1. Run Harmony
# This adjusts the PCA coordinates to mix donors together while preserving biology.
# It creates a new entry in obsm: 'X_pca_harmony'
try:
    sce.pp.harmony_integrate(
        adata, key='donor_id', basis='X_pca', adjusted_basis='X_pca_harmony'
    )
    use_rep = 'X_pca_harmony'
    print('Harmony integration successful. Using corrected PCA.')
except ImportError:
    print(
        'Harmony not installed. Proceeding with standard PCA (Warning: Batch effects may persist).'
    )
    print('To install: pip install harmony-pytorch')
    use_rep = 'X_pca'

# %%
# Reality check: Check if PC1 is just "Cell Size":

sc.pl.pca(adata, color=['total_counts', 'cell_type'], components=['1,2'])

# %% [markdown]
# PC1 separates cell types and isn't driven only by the number of cells.

# %%
# 2. Compute Neighbors
# n_neighbors: 15-30 is standard. Higher (30-50) is better for large datasets to preserve global structure.
# n_pcs: 30-50 is standard.
sc.pp.neighbors(adata, n_neighbors=30, n_pcs=40, use_rep=use_rep)

# 3. Compute UMAP
# This projects the graph into 2D for you to look at.
sc.tl.umap(adata, init_pos='X_pca_harmony')

# %%
sc.pl.umap(adata, color='total_counts')


# %% [markdown]
# ### Clustering
#

# %%
# 4. Run Clustering (Leiden algorithm)
# We run multiple resolutions so you can choose the best one later.
# sc.tl.leiden(adata, resolution=0.5, key_added='leiden_0.5')
sc.tl.leiden(
    adata,
    resolution=1.0,
    key_added='leiden_1.0',
    flavor='igraph',
    n_iterations=2,
)


# %%
# Plot UMAP colored by Donor (to check integration) and Clusters
sc.pl.umap(adata, color=['cell_type', 'leiden_1.0'], wspace=0.3)

# %%
# compute overlap between clusters and cell types
contingency_table = pd.crosstab(
    adata.obs['leiden_1.0'], adata.obs['cell_type']
)
print(contingency_table)

# %% [markdown]
# ### Pseudobulking

# %%


def create_pseudobulk(
    adata, group_col, donor_col, layer='counts', metadata_cols=None
):
    """
    Sum raw counts for each (Donor, CellType) pair.

    Parameters:
    -----------
    adata : AnnData
        Input single-cell data
    group_col : str
        Column name for grouping (e.g., 'cell_type')
    donor_col : str
        Column name for donor ID
    layer : str
        Layer to use for aggregation (default: 'counts')
    metadata_cols : list of str, optional
        Additional metadata columns to preserve from obs (e.g., ['development_stage', 'sex'])
        These should have consistent values within each donor
    """
    # 1. Create a combined key (e.g., "Bcell::Donor1")
    groups = adata.obs[group_col].astype(str)
    donors = adata.obs[donor_col].astype(str)

    # Create a DataFrame to manage the unique combinations
    group_df = pd.DataFrame({'group': groups, 'donor': donors})
    group_df['combined'] = group_df['group'] + '::' + group_df['donor']

    # 2. Build the Aggregation Matrix (One-Hot Encoding)
    enc = OneHotEncoder(sparse_output=True, dtype=np.float32)
    membership_matrix = enc.fit_transform(group_df[['combined']])

    # 3. Aggregation (Summing)
    if layer is not None and layer in adata.layers:
        X_source = adata.layers[layer]
    else:
        X_source = adata.X

    pseudobulk_X = membership_matrix.T @ X_source

    # 4. Create the Obs Metadata for the new object
    unique_ids = enc.categories_[0]

    # Split back into Donor and Cell Type
    obs_data = []
    for uid in unique_ids:
        ctype, donor = uid.split('::')
        obs_data.append({'cell_type': ctype, 'donor_id': donor})

    pb_obs = pd.DataFrame(obs_data, index=unique_ids)

    # 5. Count how many cells went into each sum
    cell_counts = np.array(membership_matrix.sum(axis=0)).flatten()
    pb_obs['n_cells'] = cell_counts.astype(int)

    # 6. Add additional metadata columns
    if metadata_cols is not None:
        for col in metadata_cols:
            if col in adata.obs.columns:
                # For each pseudobulk sample, get the first (should be consistent) value
                # from the original data for that donor
                col_values = []
                for uid in unique_ids:
                    ctype, donor = uid.split('::')
                    # Get value from any cell with this donor (should all be the same)
                    donor_mask = adata.obs[donor_col] == donor
                    if donor_mask.any():
                        col_values.append(
                            adata.obs.loc[donor_mask, col].iloc[0]
                        )
                    else:
                        col_values.append(None)
                pb_obs[col] = col_values

    # 7. Assemble the AnnData
    pb_adata = ad.AnnData(X=pseudobulk_X, obs=pb_obs, var=adata.var.copy())

    return pb_adata


# --- Execute ---

target_cluster_col = 'cell_type'

print('Aggregating counts...')
pb_adata = create_pseudobulk(
    adata,
    group_col=target_cluster_col,
    donor_col='donor_id',
    layer='counts',
    metadata_cols=[
        'development_stage',
        'sex',
    ],  # Add any other donor-level metadata here
)

print('Pseudobulk complete.')
print(f'Original shape: {adata.shape}')
print(f'Pseudobulk shape: {pb_adata.shape} (Samples x Genes)')
print(pb_adata.obs.head())

# %%
min_cells = 10
print(f'Dropping samples with < {min_cells} cells...')

pb_adata = pb_adata[pb_adata.obs['n_cells'] >= min_cells].copy()

print(f'Remaining samples: {pb_adata.n_obs}')

# Optional: Visualize the 'depth' of your new pseudobulk samples

pb_adata.obs['total_counts'] = np.array(pb_adata.X.sum(axis=1)).flatten()
sc.pl.violin(pb_adata, ['n_cells', 'total_counts'], multi_panel=True)

# %% [markdown]
# ### Differential expression with age
#
# First need to z-score the age variable to put it on same scale as expression, to help with convergence

# %%
# first need to create 'age_scaled' variable from 'development_stage'
# eg. from '19-year-old stage' to 19
ages = (
    pb_adata.obs['development_stage']
    .str.extract(r'(\d+)-year-old')
    .astype(float)
)
pb_adata.obs['age'] = ages


# %%


# Assume pb_adata is your pseudobulk object from the previous step
# 1. Extract counts and metadata
counts_df = pd.DataFrame(
    pb_adata.X.toarray(),
    index=pb_adata.obs_names,
    columns=[var_to_feature.get(var, var) for var in pb_adata.var_names],
)
# remove duplicate columns if any
counts_df = counts_df.loc[:, ~counts_df.columns.duplicated()]

metadata = pb_adata.obs.copy()

# 2. IMPORTANT: Scale the continuous variable
# This prevents convergence errors.
scaler = StandardScaler()
metadata['age_scaled'] = scaler.fit_transform(metadata[['age']]).flatten()
metadata['age_scaled'] = metadata['age_scaled'].astype(float)


# Check the scaling (Mean should be ~0, Std ~1)
print(metadata[['age', 'age_scaled']].head())

# %%
# Perform DE analysis separately for each cell type
# For this example we just choose one of them

cell_type = 'central memory CD4-positive, alpha-beta T cell'
pb_adata_ct = pb_adata[pb_adata.obs['cell_type'] == cell_type].copy()
counts_df_ct = counts_df.loc[pb_adata_ct.obs_names].copy()

metadata_ct = metadata.loc[pb_adata_ct.obs_names].copy()

assert (
    'age_scaled' in metadata_ct.columns
), 'age_scaled column missing in metadata'
assert 'sex' in metadata_ct.columns, 'sex column missing in metadata'

# 3. Initialize DeseqDataSet
dds = DeseqDataSet(
    counts=counts_df_ct,
    metadata=metadata_ct,
    design_factors=['age_scaled', 'sex'],  # Use the scaled column
    refit_cooks=True,
    n_cpus=8,
)

# 4. Run the fitting (Dispersions & LFCs)
dds.deseq2()


# %% [markdown]
# #### Compute statistics

# %%
model_vars = dds.varm['LFC'].columns
contrast = np.array([0, 1, 0])
print(f'contrast: {contrast}, model_vars: {model_vars}')

# 5. Statistical Test (Wald Test)
# Syntax for continuous: ["variable", "", ""]
stat_res = DeseqStats(dds, contrast=contrast)

stat_res.summary()


# %%
stat_res.run_wald_test()

# %% [markdown]
# #### Find significant genes

# %%
# 1. Get the results dataframe
res = stat_res.results_df

# 2. Filter for significant genes (e.g., FDR < 0.05)
# This automatically excludes NaNs (since NaN < 0.05 is False)
sigs = res[res['padj'] < 0.05]

# 3. Sort by effect size (Log2 Fold Change) to see top hits
sigs = sigs.sort_values('log2FoldChange', ascending=False)

print(f'Found {len(sigs)} significant genes.')
print(sigs[['log2FoldChange', 'padj']].head())

# %% [markdown]
# ### Pathway enrichment: GSEA
#
# - what pathways are enriched in the differentially expressed genes?

# %%


# 1. Prepare the Ranked List
# We use the 'stat' column if available (best metric).
# If 'stat' isn't there, approximate it with -log10(pvalue) * sign(log2FoldChange)
rank_df = res[['stat']].dropna().sort_values('stat', ascending=False)

# 2. Run GSEA Preranked
# We look at GO Biological Process and the "Hallmark" set (good for general states)
# For immune specific, you can also add 'Reactome_2022' or 'KEGG_2021_Human'
prerank_res = gp.prerank(
    rnk=rank_df,
    gene_sets=['MSigDB_Hallmark_2020'],
    threads=4,
    min_size=10,  # Min genes in pathway
    max_size=1000,
    permutation_num=1000,  # Reduce to 100 for speed if testing
    seed=42,
)

# 3. View Results
# 'NES' = Normalized Enrichment Score (Positive = Upregulated in Age, Negative = Downregulated)
# 'FDR q-val' = Significance
terms = prerank_res.res2d.sort_values('NES', ascending=False)

print('Top Upregulated Pathways:')
print(terms[['Term', 'NES', 'FDR q-val']].head(10))

print('\nTop Downregulated Pathways:')
print(terms[['Term', 'NES', 'FDR q-val']].tail(10))


# %% [markdown]
# #### Create a plot for the results

# %%

# 1. Get the results table
# (Assumes 'prerank_res' is your output from gp.prerank)
gsea_df = prerank_res.res2d.copy()

# 2. Sort by NES to separate Up vs Down
gsea_df = gsea_df.sort_values('NES', ascending=False)

# 3. Select Top 10 Up and Top 10 Down
top_up = gsea_df.head(10).copy()
top_down = gsea_df.tail(10).copy()

# 4. Combine them
combined_gsea = pd.concat([top_up, top_down])

# 5. Create metrics for plotting
# Direction based on NES sign
combined_gsea['Direction'] = combined_gsea['NES'].apply(
    lambda x: 'Upregulated' if x > 0 else 'Downregulated'
)

# Significance for X-axis (-log10 FDR)
# We add a tiny epsilon (1e-10) to avoid log(0) errors if FDR is exactly 0
combined_gsea['FDR q-val'] = pd.to_numeric(
    combined_gsea['FDR q-val'], errors='coerce'
)
combined_gsea['log_FDR'] = -np.log10(combined_gsea['FDR q-val'] + 1e-10)

# Gene Count for Dot Size
# GSEApy stores the leading edge genes as a semi-colon separated string in 'Lead_genes'
combined_gsea['Count'] = combined_gsea['Lead_genes'].apply(
    lambda x: len(str(x).split(';'))
)

## remove MSigDB label from Term
combined_gsea['Term'] = combined_gsea['Term'].str.replace(
    'MSigDB_Hallmark_2020__', '', regex=False
)

print(f'Plotting {len(combined_gsea)} pathways.')
print(combined_gsea[['Term', 'NES', 'FDR q-val', 'Count']].head())

# %%
plt.figure(figsize=(10, 8))

# Create the scatter plot
sns.scatterplot(
    data=combined_gsea,
    x='log_FDR',
    y='Term',
    hue='Direction',  # Color by NES Direction
    size='Count',  # Size by number of Leading Edge genes
    palette={'Upregulated': '#E41A1C', 'Downregulated': '#377EB8'},  # Red/Blue
    sizes=(50, 400),  # Range of dot sizes
    alpha=0.8,
)

# Customization
plt.title('Top GSEA Pathways (Up vs Down)', fontsize=14)
plt.xlabel('-log10(FDR q-value)', fontsize=12)
plt.ylabel('')

# Add a vertical line for significance (FDR < 0.05 => -log10(0.05) ~= 1.3)
plt.axvline(
    -np.log10(0.25),
    color='gray',
    linestyle=':',
    label='FDR=0.25 (GSEA standard)',
)
plt.axvline(-np.log10(0.05), color='gray', linestyle='--', label='FDR=0.05')

plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.0)
plt.grid(axis='x', alpha=0.3)
plt.tight_layout()

plt.show()

# %% [markdown]
# ### Enrichr analysis for overrepresentation

# %%
# 1. Define your significant gene lists
# Up in Age
up_genes = res[
    (res['padj'] < 0.05) & (res['log2FoldChange'] > 0)
].index.tolist()

# Down in Age
down_genes = res[
    (res['padj'] < 0.05) & (res['log2FoldChange'] < 0)
].index.tolist()

print(
    f'Analyzing {len(up_genes)} upregulated and {len(down_genes)} downregulated genes.'
)

# 2. Run Enrichr (Over-Representation Analysis)
if len(up_genes) > 0:
    enr_up = gp.enrichr(
        gene_list=up_genes,
        gene_sets=['MSigDB_Hallmark_2020'],
        organism='human',
        outdir=None,
    )
    print('Upregulated Pathways:')
    print(enr_up.results[['Term', 'Adjusted P-value', 'Overlap']].head(10))


if len(down_genes) > 0:
    enr_down = gp.enrichr(
        gene_list=down_genes,
        gene_sets=['MSigDB_Hallmark_2020'],
        organism='human',
        outdir=None,
    )
    print('Downregulated Pathways:')
    print(enr_down.results[['Term', 'Adjusted P-value', 'Overlap']].head(10))


# %%

# 1. Add a "Direction" column to distinguish them
up_res = enr_up.results.copy()
up_res['Direction'] = 'Upregulated'
up_res['Color'] = 'Red'  # For custom palette

down_res = enr_down.results.copy()
down_res['Direction'] = 'Downregulated'
down_res['Color'] = 'Blue'

# 2. Filter for top 10 pathways by Adjusted P-value
# (You can also filter by 'Combined Score' if you prefer)
top_up = up_res.sort_values('Adjusted P-value').head(10)
top_down = down_res.sort_values('Adjusted P-value').head(10)

# 3. Concatenate
combined = pd.concat([top_up, top_down])

# 4. Create a "-log10(P-value)" column for plotting
combined['log_p'] = -np.log10(combined['Adjusted P-value'])

# 5. Extract "Count" from the "Overlap" column (e.g., "5/200" -> 5)
# This is used to size the dots
combined['Gene_Count'] = combined['Overlap'].apply(
    lambda x: int(x.split('/')[0])
)

print(f'Plotting {len(combined)} pathways.')


# %%


plt.figure(figsize=(10, 8))

# Create the scatter plot
sns.scatterplot(
    data=combined,
    x='log_p',
    y='Term',
    hue='Direction',  # Color by Up/Down
    size='Gene_Count',  # Size by number of genes in pathway
    palette={'Upregulated': '#E41A1C', 'Downregulated': '#377EB8'},  # Red/Blue
    sizes=(50, 400),  # Range of dot sizes
    alpha=0.8,
)

# Customization
plt.title('Top Enriched Pathways (Up vs Down)', fontsize=14)
plt.xlabel('-log10(Adjusted P-value)', fontsize=12)
plt.ylabel('')
plt.axvline(
    -np.log10(0.05), color='gray', linestyle='--', alpha=0.5, label='p=0.05'
)   # Significance threshold line
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.0)
plt.grid(axis='x', alpha=0.3)
plt.tight_layout()

plt.show()

# %% [markdown]
# ### Age prediction from gene expression
#
# Here we will build a predictive model and assess our ability to predict age from held-out individuals.  We also test against a baseline model with only sex as a covariate.

# %% [markdown]
#

# %%


# 1. Prepare features and target
# Features: all genes from counts_df_ct + sex variable
X_genes = counts_df_ct.copy()

# Add sex as a binary feature (encode as 0/1)
sex_encoded = pd.get_dummies(metadata_ct['sex'], drop_first=True)
X = pd.concat([X_genes, sex_encoded], axis=1)

# Target: age
y = metadata_ct['age'].values

print(f'Feature matrix shape: {X.shape}')
print(f'Number of samples: {len(y)}')
print(f'Age range: {y.min():.1f} - {y.max():.1f} years')

# 2. Set up ShuffleSplit cross-validation
# Using 5 splits with 20% test size
cv = ShuffleSplit(n_splits=5, test_size=0.2, random_state=42)

# 3. Store results
r2_scores = []
mae_scores = []
predictions_list = []
actual_list = []

# 4. Train and evaluate model for each split
for fold, (train_idx, test_idx) in enumerate(cv.split(X)):
    print(f'\nFold {fold + 1}/5')

    # Split data
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    # Scale features (important for SVR)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train Linear SVR
    # C parameter controls regularization (smaller = more regularization)
    model = LinearSVR(C=1.0, max_iter=10000, random_state=42, dual='auto')
    model.fit(X_train_scaled, y_train)

    # Predict on test set
    y_pred = model.predict(X_test_scaled)

    # Calculate metrics
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)

    r2_scores.append(r2)
    mae_scores.append(mae)
    predictions_list.extend(y_pred)
    actual_list.extend(y_test)

    print(f'  R² Score: {r2:.3f}')
    print(f'  MAE: {mae:.2f} years')

# 5. Summary statistics
print('\n' + '=' * 50)
print('CROSS-VALIDATION RESULTS')
print('=' * 50)
print(f'R² Score: {np.mean(r2_scores):.3f} ± {np.std(r2_scores):.3f}')
print(f'MAE: {np.mean(mae_scores):.2f} ± {np.std(mae_scores):.2f} years')
print('=' * 50)

# %%
# Visualize predictions vs actual ages

plt.figure(figsize=(8, 6))

# Scatter plot of predictions vs actual
plt.scatter(actual_list, predictions_list, alpha=0.6, s=80)

# Add diagonal line (perfect predictions)
min_age = min(min(actual_list), min(predictions_list))
max_age = max(max(actual_list), max(predictions_list))
plt.plot(
    [min_age, max_age],
    [min_age, max_age],
    'r--',
    linewidth=2,
    label='Perfect Prediction',
)

plt.xlabel('Actual Age (years)', fontsize=12)
plt.ylabel('Predicted Age (years)', fontsize=12)
plt.title(
    f'Age Prediction Performance\nR² = {np.mean(r2_scores):.3f}, MAE = {np.mean(mae_scores):.2f} years',
    fontsize=14,
)
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

# %% [markdown]
# #### Baseline model: Sex only
#
# Compare against a baseline model that only uses sex as a predictor to assess the contribution of gene expression.

# %%
# Baseline model: Sex only
X_baseline = sex_encoded.copy()

# Store baseline results
baseline_r2_scores = []
baseline_mae_scores = []

# Train and evaluate baseline model for each split
for fold, (train_idx, test_idx) in enumerate(cv.split(X_baseline)):
    # Split data
    X_train, X_test = X_baseline.iloc[train_idx], X_baseline.iloc[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train Linear SVR
    model = LinearSVR(C=1.0, max_iter=10000, random_state=42, dual='auto')
    model.fit(X_train_scaled, y_train)

    # Predict on test set
    y_pred = model.predict(X_test_scaled)

    # Calculate metrics
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)

    baseline_r2_scores.append(r2)
    baseline_mae_scores.append(mae)

# Summary comparison
print('=' * 60)
print('MODEL COMPARISON')
print('=' * 60)
print('Full Model (Genes + Sex):')
print(f'  R² Score: {np.mean(r2_scores):.3f} ± {np.std(r2_scores):.3f}')
print(f'  MAE: {np.mean(mae_scores):.2f} ± {np.std(mae_scores):.2f} years')
print('\nBaseline Model (Sex Only):')
print(
    f'  R² Score: {np.mean(baseline_r2_scores):.3f} ± {np.std(baseline_r2_scores):.3f}'
)
print(
    f'  MAE: {np.mean(baseline_mae_scores):.2f} ± {np.std(baseline_mae_scores):.2f} years'
)
print('\nImprovement:')
print(f'  ΔR²: {np.mean(r2_scores) - np.mean(baseline_r2_scores):.3f}')
print(
    f'  ΔMAE: {np.mean(baseline_mae_scores) - np.mean(mae_scores):.2f} years'
)
print('=' * 60)

# %%
