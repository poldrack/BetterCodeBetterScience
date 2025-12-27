# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: bettercode
#     language: python
#     name: python3
# ---

# %% [markdown]
# ### Database examples
#
# This is a worked example of the use of several NoSQL databases (MongoDB, ChromaDB, and Neo4j) for the chapter on Data Management.
#
# The question that we will ask in this analysis is: Can the biological similarity between two traits (estimated using pathway enrichment of genome-wide association study [GWAS] data) be estimated from the semantic similarity of published abstracts that mention that trait?

# %%
import pandas as pd
import pymongo
import dotenv
import os
from neo4j import GraphDatabase
from chromadb import PersistentClient
from tqdm.notebook import tqdm
from pathlib import Path
from database import (
    setup_mongo_collection,
    get_chromadb_collection,
    get_neo4j_session,
)
from bettercode.database_example_funcs import (
    get_exploded_gwas_data,
    import_geneset_annotations_by_trait,
    get_trait_info_from_ols,
    annotate_geneset_annotations_by_trait,
    get_pathway_info_by_trait,
    compute_phenotype_similarities,
    compute_text_similarities,
)
from bettercode.database import get_mongo_client
import seaborn as sns
import matplotlib.pyplot as plt

# %load_ext rpy2.ipython

dotenv.load_dotenv()
datadir = Path(os.getenv('DATA_DIR', '../../data'))

# %% [markdown]
# ### Step 1: load gwas-phenotype associations
#
# We will use a database of GWAS results from [EBI](https://www.ebi.ac.uk/gwas/docs/file-downloads).
#
# These might seem perfect for a relational database, but they are not quite ready, because one of the columns of interest (`SNP_GENE_IDS`, which maps the snp to one or more genes) maps to multiple genes in some cases, and thus violates the First Normal Form. We could fix this by exploding the column:

# %%
gwas_data = get_exploded_gwas_data()

# %% [markdown]
# This is now ready to import to a relational database. However, for this example we will use a document store (MongoDB) to store the records, since it I find it much easier to work with.  We will first generate a collection that links trait identifiers to the gene sets that have been identified for that trait in GWAS.

# %%
import_geneset_annotations_by_trait(gwas_data)

# %% [markdown]
# ### Functional annotation of gene sets
#
# Each trait is associated with one or more genes based on the GWAS data.  However, given that genes work together in networks, we would like to estimate the similarity using the biological products or pathways that are associated with each set of genes, rather the similarity of the specific genes associated with each phenotype.  We will perform this annotation using the [g:Profiler](https://biit.cs.ut.ee/gprofiler/gost) tool from ELIXIR, which comes with a handy [Python package](https://pypi.org/project/gprofiler-official/).   This tool returns a set of pathways that are statistically enriched for each gene set.
#

# %%
annotate_geneset_annotations_by_trait()

# %% [markdown]
# ### Get trait info
#
# Next we will create a database collection that stores information about each of the traits in the GWAS dataset, using the EBI OLS API. In particular, we want to obtain a list of synonyms for the name of each trait, which we will use in our literature search.

# %%
get_trait_info_from_ols()

# %% [markdown]
# ## ???
#
# Next we want to create another database collection that will map from trait identifiers to the specific pathways that were obtained in the earlier step based on the associated gene sets.

# %%
get_pathway_info_by_trait()

# %% [markdown]
# ### Graph database example
#
# Next we want to compute the similarity of traits in terms of the biological processes that they are associated with.  We will do this using the Neo4j graph database, which has a set of data analysis methods that will allow us to easily compute the required similarity metric.
#
# First we need to add our trait and pathway information to the Neo4j database.  We start by adding the traits as nodes, and then add the pathways along with their links to each trait.

# %%

# %%
# Assuming Neo4j is running locally with default credentials
# For production, use environment variables or secure config
# browse db at http://localhost:7474/browser/


build_neo4j_graph()

# %%
similarity_result_df = compute_phenotype_similarities()

# %%

# %% [markdown]
# ### Get pubmed abstracts for each trait using trait name and synonyms
#
# Next we want to obtain some abstracts related to each trait, which we will use to compute semantic similarity between traits.  We will download abstracts from Pubmed, using the trait name and any synonyms that were obtained in the previous step.  First we will submit each query (using the `Biopython.Entrez` module) and obtain the first 100 pubmed IDs that are returned for the query.

# %%
get_pmids_for_traits()


# %% [markdown]
# Now we create a separate database collection to store the retrieved abstracts from Pubmed.

# %%
fetch_and_store_pubmed_abstracts()

# %% [markdown]
# ### Add documents to chromadb vector db
#
# We want to use the documents downloaded from Pubmed to compute the semantic similarity between traits.  This is a good application for a *vector database*, which can ingest documents, embed them into a vector space, and then perform similarity computations between documents based on their vector embeddings.  We will use ChromaDB which is a popular open-source vector database.

# %%
# add to chromadb vector db
add_pubmed_abstracts_to_chromadb()

# %% [markdown]
# Now use chromadb to get average text similarity for

# %%

text_similarity_df = compute_text_similarities(similarity_result_df)


# %%
sns.scatterplot(
    data=text_similarity_df,
    x='pathway_similarity',
    y='text_similarity',
    alpha=0.5,
    size=1,
)
plt.title(
    f'Pathway Similarity vs Text Similarity (r={text_similarity_df["pathway_similarity"].corr(text_similarity_df["text_similarity"]):.2f})'
)

# %% magic_args="-i results_df" language="R"
#
# if (!requireNamespace("lme4", quietly = TRUE)) {
#     install.packages("lme4")
# }
# library(lme4)
# model <- lmer(text_similarity ~ pathway_similarity + (1 | phenotype1) + (1 | phenotype2), data = results_df)
# summary(model)
