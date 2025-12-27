"""Pathway analysis module for scRNA-seq analysis workflow.

Functions for Gene Set Enrichment Analysis (GSEA).
"""

from pathlib import Path

import gseapy as gp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def prepare_ranked_list(results_df: pd.DataFrame) -> pd.DataFrame:
    """Prepare ranked gene list for GSEA from DE results.

    Parameters
    ----------
    results_df : pd.DataFrame
        DESeq2 results dataframe with 'stat' column

    Returns
    -------
    pd.DataFrame
        Ranked gene list sorted by statistic
    """
    rank_df = results_df[["stat"]].dropna().sort_values("stat", ascending=False)
    return rank_df


def run_gsea_prerank(
    rank_df: pd.DataFrame,
    gene_sets: list[str] | None = None,
    min_size: int = 10,
    max_size: int = 1000,
    permutation_num: int = 1000,
    threads: int = 4,
    seed: int = 42,
) -> gp.GSEA:
    """Run GSEA preranked analysis.

    Parameters
    ----------
    rank_df : pd.DataFrame
        Ranked gene list
    gene_sets : list[str], optional
        Gene set databases to use
    min_size : int
        Minimum genes in pathway
    max_size : int
        Maximum genes in pathway
    permutation_num : int
        Number of permutations
    threads : int
        Number of threads
    seed : int
        Random seed

    Returns
    -------
    gp.GSEA
        GSEA results object
    """
    if gene_sets is None:
        gene_sets = ["MSigDB_Hallmark_2020"]

    prerank_res = gp.prerank(
        rnk=rank_df,
        gene_sets=gene_sets,
        threads=threads,
        min_size=min_size,
        max_size=max_size,
        permutation_num=permutation_num,
        seed=seed,
    )

    return prerank_res


def get_gsea_top_terms(
    prerank_res: gp.GSEA,
    n_top: int = 10,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Get top upregulated and downregulated pathways.

    Parameters
    ----------
    prerank_res : gp.GSEA
        GSEA results object
    n_top : int
        Number of top terms to return

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        Top upregulated and downregulated pathways
    """
    terms = prerank_res.res2d.sort_values("NES", ascending=False)

    print("Top Upregulated Pathways:")
    print(terms[["Term", "NES", "FDR q-val"]].head(n_top))

    print("\nTop Downregulated Pathways:")
    print(terms[["Term", "NES", "FDR q-val"]].tail(n_top))

    top_up = terms.head(n_top)
    top_down = terms.tail(n_top)

    return top_up, top_down


def prepare_gsea_plot_data(
    prerank_res: gp.GSEA,
    n_top: int = 10,
    label_prefix: str = "MSigDB_Hallmark_2020__",
) -> pd.DataFrame:
    """Prepare GSEA results for plotting.

    Parameters
    ----------
    prerank_res : gp.GSEA
        GSEA results object
    n_top : int
        Number of top terms per direction
    label_prefix : str
        Prefix to remove from term names

    Returns
    -------
    pd.DataFrame
        Prepared dataframe for plotting
    """
    gsea_df = prerank_res.res2d.copy()
    gsea_df = gsea_df.sort_values("NES", ascending=False)

    top_up = gsea_df.head(n_top).copy()
    top_down = gsea_df.tail(n_top).copy()
    combined = pd.concat([top_up, top_down])

    # Add direction
    combined["Direction"] = combined["NES"].apply(
        lambda x: "Upregulated" if x > 0 else "Downregulated"
    )

    # Compute -log10(FDR)
    combined["FDR q-val"] = pd.to_numeric(combined["FDR q-val"], errors="coerce")
    combined["log_FDR"] = -np.log10(combined["FDR q-val"] + 1e-10)

    # Get gene count from leading edge
    combined["Count"] = combined["Lead_genes"].apply(lambda x: len(str(x).split(";")))

    # Clean term names
    combined["Term"] = combined["Term"].str.replace(label_prefix, "", regex=False)

    return combined


def plot_gsea_results(
    combined_gsea: pd.DataFrame,
    figure_dir: Path | None = None,
    title: str = "Top GSEA Pathways (Up vs Down)",
) -> None:
    """Plot GSEA results as dot plot.

    Parameters
    ----------
    combined_gsea : pd.DataFrame
        Prepared GSEA dataframe
    figure_dir : Path, optional
        Directory to save figures
    title : str
        Plot title
    """
    plt.figure(figsize=(10, 8))

    sns.scatterplot(
        data=combined_gsea,
        x="log_FDR",
        y="Term",
        hue="Direction",
        size="Count",
        palette={"Upregulated": "#E41A1C", "Downregulated": "#377EB8"},
        sizes=(50, 400),
        alpha=0.8,
    )

    plt.title(title, fontsize=14)
    plt.xlabel("-log10(FDR q-value)", fontsize=12)
    plt.ylabel("")

    plt.axvline(
        -np.log10(0.25),
        color="gray",
        linestyle=":",
        label="FDR=0.25 (GSEA standard)",
    )
    plt.axvline(-np.log10(0.05), color="gray", linestyle="--", label="FDR=0.05")

    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left", borderaxespad=0.0)
    plt.grid(axis="x", alpha=0.3)
    plt.tight_layout()

    if figure_dir is not None:
        plt.savefig(figure_dir / "gsea_pathways.png", dpi=300, bbox_inches="tight")
    plt.close()


def run_gsea_pipeline(
    results_df: pd.DataFrame,
    gene_sets: list[str] | None = None,
    n_top: int = 10,
    figure_dir: Path | None = None,
) -> gp.GSEA:
    """Run complete GSEA pipeline.

    Parameters
    ----------
    results_df : pd.DataFrame
        DESeq2 results dataframe
    gene_sets : list[str], optional
        Gene set databases
    n_top : int
        Number of top pathways to show
    figure_dir : Path, optional
        Directory to save figures

    Returns
    -------
    gp.GSEA
        GSEA results object
    """
    # Prepare ranked list
    rank_df = prepare_ranked_list(results_df)

    # Run GSEA
    prerank_res = run_gsea_prerank(rank_df, gene_sets)

    # Get top terms
    get_gsea_top_terms(prerank_res, n_top)

    # Prepare and plot
    combined = prepare_gsea_plot_data(prerank_res, n_top)
    print(f"Plotting {len(combined)} pathways.")
    print(combined[["Term", "NES", "FDR q-val", "Count"]].head())

    plot_gsea_results(combined, figure_dir)

    return prerank_res
