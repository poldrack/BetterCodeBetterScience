"""Overrepresentation analysis module for scRNA-seq analysis workflow.

Functions for Enrichr-based overrepresentation analysis.
"""

from pathlib import Path

import gseapy as gp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def get_significant_gene_lists(
    results_df: pd.DataFrame,
    padj_threshold: float = 0.05,
) -> tuple[list[str], list[str]]:
    """Extract lists of up and down regulated genes.

    Parameters
    ----------
    results_df : pd.DataFrame
        DESeq2 results dataframe
    padj_threshold : float
        Adjusted p-value threshold

    Returns
    -------
    tuple[list[str], list[str]]
        Lists of upregulated and downregulated genes
    """
    up_genes = results_df[
        (results_df["padj"] < padj_threshold) & (results_df["log2FoldChange"] > 0)
    ].index.tolist()

    down_genes = results_df[
        (results_df["padj"] < padj_threshold) & (results_df["log2FoldChange"] < 0)
    ].index.tolist()

    print(
        f"Analyzing {len(up_genes)} upregulated and "
        f"{len(down_genes)} downregulated genes."
    )

    return up_genes, down_genes


def run_enrichr(
    gene_list: list[str],
    gene_sets: list[str] | None = None,
    organism: str = "human",
) -> gp.Enrichr | None:
    """Run Enrichr overrepresentation analysis.

    Parameters
    ----------
    gene_list : list[str]
        List of gene names
    gene_sets : list[str], optional
        Gene set databases to use
    organism : str
        Organism name

    Returns
    -------
    gp.Enrichr or None
        Enrichr results object or None if no genes
    """
    if len(gene_list) == 0:
        print("No genes to analyze.")
        return None

    if gene_sets is None:
        gene_sets = ["MSigDB_Hallmark_2020"]

    enr = gp.enrichr(
        gene_list=gene_list,
        gene_sets=gene_sets,
        organism=organism,
        outdir=None,
    )

    return enr


def run_enrichr_both_directions(
    results_df: pd.DataFrame,
    gene_sets: list[str] | None = None,
    padj_threshold: float = 0.05,
) -> tuple[gp.Enrichr | None, gp.Enrichr | None]:
    """Run Enrichr for both up and down regulated genes.

    Parameters
    ----------
    results_df : pd.DataFrame
        DESeq2 results dataframe
    gene_sets : list[str], optional
        Gene set databases
    padj_threshold : float
        Adjusted p-value threshold

    Returns
    -------
    tuple[gp.Enrichr, gp.Enrichr]
        Enrichr results for up and down genes
    """
    up_genes, down_genes = get_significant_gene_lists(results_df, padj_threshold)

    enr_up = None
    enr_down = None

    if len(up_genes) > 0:
        enr_up = run_enrichr(up_genes, gene_sets)
        if enr_up is not None:
            print("Upregulated Pathways:")
            print(enr_up.results[["Term", "Adjusted P-value", "Overlap"]].head(10))

    if len(down_genes) > 0:
        enr_down = run_enrichr(down_genes, gene_sets)
        if enr_down is not None:
            print("Downregulated Pathways:")
            print(enr_down.results[["Term", "Adjusted P-value", "Overlap"]].head(10))

    return enr_up, enr_down


def prepare_enrichr_plot_data(
    enr_up: gp.Enrichr | None,
    enr_down: gp.Enrichr | None,
    n_top: int = 10,
) -> pd.DataFrame | None:
    """Prepare Enrichr results for plotting.

    Parameters
    ----------
    enr_up : gp.Enrichr
        Enrichr results for upregulated genes
    enr_down : gp.Enrichr
        Enrichr results for downregulated genes
    n_top : int
        Number of top pathways per direction

    Returns
    -------
    pd.DataFrame or None
        Combined dataframe for plotting
    """
    dfs = []

    if enr_up is not None:
        up_res = enr_up.results.copy()
        up_res["Direction"] = "Upregulated"
        up_res["Color"] = "Red"
        top_up = up_res.sort_values("Adjusted P-value").head(n_top)
        dfs.append(top_up)

    if enr_down is not None:
        down_res = enr_down.results.copy()
        down_res["Direction"] = "Downregulated"
        down_res["Color"] = "Blue"
        top_down = down_res.sort_values("Adjusted P-value").head(n_top)
        dfs.append(top_down)

    if not dfs:
        return None

    combined = pd.concat(dfs)

    # Compute -log10(P-value)
    combined["log_p"] = -np.log10(combined["Adjusted P-value"])

    # Extract gene count from Overlap (e.g., "5/200" -> 5)
    combined["Gene_Count"] = combined["Overlap"].apply(lambda x: int(x.split("/")[0]))

    return combined


def plot_enrichr_results(
    combined: pd.DataFrame,
    figure_dir: Path | None = None,
    title: str = "Top Enriched Pathways (Up vs Down)",
) -> None:
    """Plot Enrichr results as dot plot.

    Parameters
    ----------
    combined : pd.DataFrame
        Prepared Enrichr dataframe
    figure_dir : Path, optional
        Directory to save figures
    title : str
        Plot title
    """
    print(f"Plotting {len(combined)} pathways.")

    plt.figure(figsize=(10, 8))

    sns.scatterplot(
        data=combined,
        x="log_p",
        y="Term",
        hue="Direction",
        size="Gene_Count",
        palette={"Upregulated": "#E41A1C", "Downregulated": "#377EB8"},
        sizes=(50, 400),
        alpha=0.8,
    )

    plt.title(title, fontsize=14)
    plt.xlabel("-log10(Adjusted P-value)", fontsize=12)
    plt.ylabel("")
    plt.axvline(
        -np.log10(0.05), color="gray", linestyle="--", alpha=0.5, label="p=0.05"
    )
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left", borderaxespad=0.0)
    plt.grid(axis="x", alpha=0.3)
    plt.tight_layout()

    if figure_dir is not None:
        plt.savefig(figure_dir / "enrichr_pathways.png", dpi=300, bbox_inches="tight")
    plt.close()


def run_overrepresentation_pipeline(
    results_df: pd.DataFrame,
    gene_sets: list[str] | None = None,
    padj_threshold: float = 0.05,
    n_top: int = 10,
    figure_dir: Path | None = None,
) -> tuple[gp.Enrichr | None, gp.Enrichr | None]:
    """Run complete overrepresentation analysis pipeline.

    Parameters
    ----------
    results_df : pd.DataFrame
        DESeq2 results dataframe
    gene_sets : list[str], optional
        Gene set databases
    padj_threshold : float
        Adjusted p-value threshold
    n_top : int
        Number of top pathways to show
    figure_dir : Path, optional
        Directory to save figures

    Returns
    -------
    tuple[gp.Enrichr, gp.Enrichr]
        Enrichr results for up and down genes
    """
    # Run Enrichr
    enr_up, enr_down = run_enrichr_both_directions(
        results_df, gene_sets, padj_threshold
    )

    # Prepare and plot
    combined = prepare_enrichr_plot_data(enr_up, enr_down, n_top)
    if combined is not None:
        plot_enrichr_results(combined, figure_dir)

    return enr_up, enr_down
