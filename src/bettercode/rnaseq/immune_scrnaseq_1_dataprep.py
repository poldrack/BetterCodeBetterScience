# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.18.1
#   kernelspec:
#     display_name: bettercode
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
from anndata.experimental import read_lazy
import dask.array as da
import h5py
import numpy as np
import scanpy as sc
from pathlib import Path
import os

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
adata = read_lazy(h5py.File(datafile, 'r'),
    load_annotation_index=load_annotation_index)

# %%
print(adata)

# %%
unique_cell_types = np.unique(adata.obs['cell_type'])
print(unique_cell_types)

# %% [markdown]
# ### Filtering out bad donors

# %%
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import scoreatpercentile

# 1. Calculate how many cells each donor has
donor_cell_counts = pd.Series(adata.obs['donor_id']).value_counts()

# Print some basic statistics to read the exact numbers
print("Donor Cell Count Statistics:")
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
min_cells_per_donor = int(scoreatpercentile(donor_cell_counts.values, cutoff_percentile))
print(f'cutoff of {min_cells_per_donor} would exclude {(donor_cell_counts < min_cells_per_donor).sum()} donors')
plt.axvline(min_cells_per_donor, color='red', linestyle='dashed', linewidth=1, label=f'Cutoff ({min_cells_per_donor} cells)')
plt.legend()

plt.show()

# %%
print(f"Filtering to keep only donors with at least {min_cells_per_donor} cells.")
print(f"Number of donors excluded: {(donor_cell_counts < min_cells_per_donor).sum()}")
valid_donors = donor_cell_counts[donor_cell_counts >= min_cells_per_donor].index
adata = adata[adata.obs['donor_id'].isin(valid_donors)]

# %%
print(f'Number of donors after filtering: {len(valid_donors)}')

# %% [markdown]
# ### Filtering cell types by frequency
#
# Drop cell types that don't have at least 10 cells for at least 95% of people

# %%
import pandas as pd

# 1. Calculate the count of cells for each 'cell_type' within each 'donor_id'
# We use pandas crosstab on adata.obs, which is loaded in memory.
counts_per_donor = pd.crosstab(adata.obs['donor_id'], adata.obs['cell_type'])

# 2. Identify cell types to keep
# Keep if >= 10 cells in at least 90% of donors

min_cells = 10
percent_donors = 0.9
donor_count = counts_per_donor.shape[0]
cell_types_to_keep = counts_per_donor.columns[
    (counts_per_donor >= min_cells).sum(axis=0) >= (donor_count * percent_donors)]

print(f"Keeping {len(cell_types_to_keep)} cell types out of {len(counts_per_donor.columns)}")
print(f"Cell types to keep: {cell_types_to_keep.tolist()}")

# 3. Filter the AnnData object
# We subset the AnnData to include only observations belonging to the valid cell types.
adata_filtered = adata[adata.obs['cell_type'].isin(cell_types_to_keep)]

# %%
# now drop subjects who have any zeros in these cell types
donor_celltype_counts = pd.crosstab(adata_filtered.obs['donor_id'], adata_filtered.obs['cell_type'])
valid_donors_final = donor_celltype_counts.index[
    (donor_celltype_counts >= min_cells).all(axis=1)]
adata_filtered = adata_filtered[adata_filtered.obs['donor_id'].isin(valid_donors_final)]
print(f"Final number of donors after filtering: {len(valid_donors_final)}")

# %%

print("Loading data into memory (this can take a few minutes)...")
adata_loaded = adata_filtered.to_memory()

# filter out genes with zero counts across all selected cells
print("Filtering genes with zero counts...")
sc.pp.filter_genes(adata_loaded, min_counts=1)


# %%
print(adata_loaded)


# %%
adata_loaded.write(datadir /  f'dataset-{dataset_name}_subset-immune_filtered.h5ad')

# %%
# !ls -lh /Users/poldrack/data_unsynced/BCBS/immune_aging
