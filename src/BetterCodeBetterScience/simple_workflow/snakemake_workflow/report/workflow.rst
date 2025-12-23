Simple Correlation Workflow
===========================

This workflow demonstrates a simple pandas-based data analysis pipeline:

1. **Data Loading**: Downloads two datasets from the Self-Regulation Ontology project
2. **Filtering**: Removes non-numerical columns from both datasets
3. **Joining**: Combines the datasets based on their common index (subject IDs)
4. **Correlation**: Computes Spearman correlation matrix across all measures
5. **Visualization**: Generates a clustered heatmap showing correlation patterns
