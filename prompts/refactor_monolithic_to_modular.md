Prompt: please read CLAUDE.md for guidelines, and then read refactor_monolithic_to_modular.md for a description of your task.

# Goal

src/BetterCodeBetterScience/rnaseq/immune_scrnaseq_monolithic.py is currently a single monolithic script for a data analysis workflow.  I would like to refactor it into a modular script based on the following decomposition of the workflow:

- Data (down)loading
- Data filtering (removing subjects or cell types with insufficient observations)
- Quality control
    - identifying bad cells on the basis of mitochondrial, ribosomal, or hemoglobin genes or hemoglobin contamination
    - identifying "doublets" (multiple cells identified as one)
- Preprocessing
    - Count normalization
    - Log transformation
    - Identification of high-variance features
    - Filtering of nuisance genes
- Dimensionality reduction
- UMAP generation
- Clustering
- Pseudobulking
- Differential expression analysis
- Pathway enrichment analysis (GSEA)
- Overrepresentation analysis (Enrichr)
- Predictive modeling

Please generate a new set of scripts within a new directory called `src/BetterCodeBetterScience/rnaseq/modular_workflow` that implements the same workflow in a modular way.

