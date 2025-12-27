# Workflow Management

In most parts of science today, data processing and analysis comprise many different steps.  We will refer to such a set of steps as a computational *workflow*. If you have been doing science for very long, you have very likely encountered a *mega-script* that implements such a workflow. Usually written in a scripting language like *Bash*, this is a script that may be hundreds or even thousands of lines long that runs a single workflow from start to end.  Often these scripts are handed down to new trainees over generations, such that users become afraid to make any changes lest the entire house of cards comes crashing down.  I think that most of us can agree that this is not an optimal workflow, and in this chapter I will discuss in detail how to move from a mega-script to a workflow that will meet all of the requirements to provide robust and reliable answers to our scientific questions.

## What do we want from a scientific workflow?

First let's ask: What do we want from a computational scientific workflow?  Here are some of the factors that I think are important.  First, we care about the *correctness* of the workflow, which includes the following factors:

- *Validity*:  The workflow includes validation procedures to ensure against known problems or edge cases.
- *Reproducibility*:  The workflow can be rerun from scratch on the same data and get the same answer, at least within the limits of uncontrollable factors such as floating point imprecision.
- *Robustness*: When there is a problem, the workflow fails quickly with explicit error messages, or degrades gracefully when possible.

Second, we care about the *usability* of the workflow. Factors related to usability include:

- *Configurability*: The workflow uses smart defaults, but allows the user to easily change the configuration in a way that is traceable.
- *Parameterizability*: Multiple runs of the workflow can be executed with different parameters, and the separate outputs can be tracked.
- *Standards compliance*:  The workflow leverages common standards to easily read in data and generates output using community standards for file formats and organization when available.

Third, we care about the *engineering quality* of the code, which includes:

- *Maintainability*: The workflow is structured and documented so that others (including your future self) can easily maintain, update, and extend it in the future.
- *Modularity*: The workflow is composed of a set of independently testable modules, which can be swapped in or out relatively easily.
- *Idempotency*: This term from computer science means that the result of the workflow does not change after its first successful run, which allows safely rerunning the workflow.
- *Traceability*:  All operations are logged, and provenance information is stored for outputs.

Finally, we care about the *efficiency* of the workflow implementation. This includes:

- *Incremental execution*: The workflow only reruns a module if necessary, such as when an input changes.
- *Cached computation*: The workflow pre-computes and reuses results from expensive operations when possible.

It's worth noting that these different desiderata will sometimes conflict with one another (such as configurability versus maintainability), and that no workflow will be perfect.  For example, a highly configurable workflow will often be more difficult to maintain.

## Pipelines versus workflows

The terms *workflow* and *pipeline* are sometimes used interchangeably, but in this chapter I will use them to refer to different kinds of applications. I will use *workflow* as the more general term to refer to any set of analysis procedures that are implemented as separate modules.  I will use the term *pipeline* to refer more specifically to a data analysis workflow where several operations are combined into a single command through the use of *pipes*, which are a syntactic construct that feed the results of one process directly into the next process.  Some readers may be familiar with pipes from the UNIX command line, where they are represented by the vertical bar "|".  For example, let's say that we had a log file that contains the following entries:

```bash
2024-01-15 10:23:45 ERROR: Database connection failed
2024-01-15 10:24:12 ERROR: Invalid user input
2024-01-15 10:25:33 ERROR: Database connection failed
2024-01-15 10:26:01 INFO: Request processed
2024-01-15 10:27:15 ERROR: Database connection failed
```

and that we wanted to generate a summary of errors. We could use the following pipeline:

```bash
grep "ERROR" app.log | sed 's/.*ERROR: //' | sort | uniq -c | sort -rn > error_summary.txt

```

where:

- `grep "ERROR" app.log` extracts lines containing the word "ERROR"
- `sed 's/.*ERROR: //'` replaces everything up to the actual message with an empty string
- `sort` sorts the rows alphabetically
- `uniq -c` counts the number of appearances of each unique error message
- `sort -rn`  sorts the rows in reverse numerical order (largest to smallest)
- `> error_summary.txt` redirects the output into a file called `error_summary.txt`

Pipes are also commonly used in the R ecosystem, where they are a fundamental component of the *tidyverse* group of packages.

#### Method chaining

One way that simple pipelines can be built in Python is using *method chaining*, where each method returns an object on which the next method is called; this is slightly different from the operation of UNIX pipes, where it is the result of each command that is being passed through the pipe.  This is commonly used to perform data transformations in `pandas`, as it allows composing multiple transformations into a single command.  As an example, we will work with the Eisenberg et al. dataset that we used in a previous chapter, to compute the probability of having ever been arrested separately for males and females in the sample. To do this we need to perform a number of operations:

- drop any observations that have missing values for the `Sex` or `ArrestedChargedLifeCount` variables
- replace the numeric values in the `Sex` variable with text labels
- create a new variable called `EverArrested` that binarizes the counts in the ArrestedChargedLifeCount variable
- group the data by the `Sex` variable
- select the column that we want to compute the mean of (`EverArrested`)
- compute the mean

We can do this in a single command using method chaining in `pandas`.  It's useful to format the code in a way that makes the pipeline steps explicit, by putting parentheses around the operation; in Python, any commands within parentheses are implicitly treated as a single line, which can be useful for making complex code more readable:

```python
arrest_stats_by_sex = (df
    .dropna(subset=['Sex', 'ArrestedChargedLifeCount'])
    .replace({'Sex': {0: 'Male', 1: 'Female'}})
    .assign(EverArrested=lambda x: (x['ArrestedChargedLifeCount'] > 0).astype(int))
    .groupby('Sex')
    ['EverArrested']
    .mean()
)
print(arrest_stats_by_sex)
```
```bash
Sex
Female    0.156489
Male      0.274131
Name: EverArrested, dtype: float64
```

Note that `pandas` data frames also include an explicit `.pipe` method that allows using arbitrary functions within a pipeline.  While these kinds of pipelines can be useful for simple data processing operations, they can become very difficult to debug, so I would generally avoid using complex functions within a method chain.


## FAIR-inspired practices for workflows
    - FAIR workflows 
        - https://pmc.ncbi.nlm.nih.gov/articles/PMC10538699/
        - https://www.nature.com/articles/s41597-025-04451-9
        - this seems really heavyweight.  
    - 80/20 approach to reproducible workflows
        - version control + documentation
        - requirements file or container
        - clear workflow structure
        - standard file formats
    - The full FAIR approach may be necessary in some contexts

In the earlier chapter on Data Management I discussed the FAIR (Findable, Accessible, Interoperable, and Reusable) principles for data.  Since those principles were proposed in 2016 they have been extended to many other types of research objects, including workflows (REFS - https://www.nature.com/articles/s41597-025-04451-9).  The reader who is not an informatician is likely to quickly glaze over when reading these articles, as they ...

Realizing that most scientists are unlikely to go to the lengths of a fully FAIR workflow, and preferring that the perfect never be the enemy of the good, I think that we can take an "80/20" approach, meaning that we can get 80% of the benefits for about 20% of the effort.  We can adhere to the spirit of the FAIR Workflows principle by adopting the following principles, based in part on the "Ten Quick Tips for FAIR Workflows" presented by de Visser et al., (2023; https://pmc.ncbi.nlm.nih.gov/articles/PMC10538699):

- *Metadata*:  Provide sufficient metadata in a standard machine-readable format to make the workflow findable once it is shared.
- *Version control*:  All workflow code should be kept under version control and hosted on a public repository such as Github.
- *Documentation*: Workflows should be well documented. Documentation should focus primarily on the scientific motivation and technical design of the workflow, along with instructions on how to run it and description of the outputs.
- *Standard organization schemes*: Both the workflow files (code and configuration) and data files should follow established standards for organization.
- *Standard file formats*: The inputs and outputs to the workflow should use established standard file formats rather than inventing new formats.
- *Configurability*: The workflow should be easily configurable, and example configuration files should be included in the repository.
- *Requirements*: The requirements for the workflow should be clearly specified, either in a file (such as `pyproject.toml` or `requiremets.txt`) or in a container configuration file (such as a Dockerfile).
- *Clear workflow structure*: The workflow structure should be easily understandable.

There are certainly some contexts where a more formal structure adhering in detail to the FAIR Workflows standard may be required, as in large collaborative projects with specific compliance objectives, but these rough guidelines should get a researcher most of the way there.


## A simple workflow example

Most real scientific workflows are complex and can often run for hours, and we will encounter such a complex workflow later in the chapter. However, we will start our discussion of workflows with a relatively simple and fast-running example that will help demonstrate the basic concepts of workflow execution. We will use the same data as above (from Eisenberg et al.) to perform a simple workflow:

- Load the demographic and meaningful variables files
- Filter out any non-numeric variables from each data frame
- Join the data frames using their shared index
- Compute the correlation matrix across all variables
- Generate a clustered heatmap for the correlation matrix

I have implemented each of these components as a module [here]().  The simplest possible workflow would be a script that simply imnports and calls each of the methods in turn. For such a simple workflow this would be fine, but we will use the example to show how we might take advantage of more sophisticated workflow management tools.

### Running a simple workflow using GNU make

One of the simplest ways to organize a workflow is using the GNU `make` command, which executes commands defined in a file named `Makefile`.  `make` is a very handy general-purpose tool that every user of UNIX systems should become familiar with.  The Makefile defines a set of labeled commands, like this:

```Makefile

all: step1 step2

step1:
    python step1.py

step2:
    python step2.py
```

In this case, the command `make step1` will run `python step1.py`, `make step2` will run `python step2.py`, and `make all` will run both of those commands. This should already show you why `make` is such a handy tool: Any time there is a command that you run regularly in a particular directory, you can put it into a `Makefile` and then execute it with just a single `make` call.  Here is how we could build a very simple Makefile to run our simple workflow:

```Makefile
# Simple Correlation Workflow using Make
#
# Usage:
#   make all              - Run full workflow
#   make clean            - Remove output directory

# if OUTPUT_DIR isn't already defined, set it to the default
OUTPUT_DIR ?= ./output

# run commands even if files exist with these names
.PHONY: all clean

all:
	mkdir -p $(OUTPUT_DIR)/data $(OUTPUT_DIR)/results $(OUTPUT_DIR)/figures
	python scripts/download_data.py $(OUTPUT_DIR)/data
	python scripts/filter_data.py $(OUTPUT_DIR)/data
	python scripts/join_data.py $(OUTPUT_DIR)/data
	python scripts/compute_correlation.py $(OUTPUT_DIR)/data $(OUTPUT_DIR)/results
	python scripts/generate_heatmap.py $(OUTPUT_DIR)/results $(OUTPUT_DIR)/figures

clean:
	rm -rf $(OUTPUT_DIR)
```

We can run the entire workflow by simply running `make all`.  We could also take advantage of another feature of `make`: it only triggers the action if a file with the name of the action doesn't exist.  Thus, if the command was `make results/output.txt`, then the action would only be triggered if the file does not exist.  This is why we had to put the `.PHONY` command in the makefile above: it's telling `make` that those are not meant to be interpreted as file names, but rather as commands, so that they will be run even if files named "all" or "clean" exist.

For a very simple workflow `make` can be useful, but we will see below why this wouldn't be sufficient for a complex workflow.  For those workflows we could either build our own more complex workflow management system, or we could use an existing software tool that is built to manage workflow execution, known as a *workflow engine*.  Later in the chapter I will show an example of a purpose-built workflow management system, but for this first example we will now turn to a general-purpose workflow engine.

### Using a workflow engine

There is a wide variety of workflow engines available for data analysis workflows, most of which are centered around the concept of an "execution graph".  This is a graph in the sense described by graph theory, which refers to a set of nodes that are connected by lines (known as "edges").  Workflow execution graphs are a particular kind of graph known as a *directed acyclic graph*, or *DAG* for short. Each node in the graph represents a single step in the workflow, and each edge represents the dependency relationships that exist between nodes.  DAGs have two important features.  First, the edges are directed, which means that they move in one direction that is represented graphically as an arrow.  These represent the dependencies within the workflow.  For example, in our workflow step 1 (obtaining the data) must occur before step 2 (filtering the data), so the graph would have an edge from step 1 with an arrow pointing at step 2.  Second, the graph is *acyclic*, which means that it doesn't have any cycles, that is, it never circles back on itself.  Cycles would be problematic, since they could result in workflows that executed in an infinite loop as the cycle repeated itself.  

Most workflow engines provide tools to visualize a workflow as a DAG. #simpleDAG-fig shows our example workflow visualized using the Snakemake tool that we will introduce below:

```{figure} images/simple-DAG.png
:label: simpleDAG-fig
:align: center
:width: 300px

The execution graph for the simple example analysis workflow visualized as a DAG.
```

The use of DAGs to represent workflows provides a number of important benefits:

- The engine can identify independent pathways through the graph, which can then be executed in parallel
- If one node of the graph changes, the engine can identify which downstream nodes need to be rerun
- If a node fails, the engine can continue with executing the nodes that don't depend on the failed node either directly or indirectly

There are a couple of additional benefits to using a workflow engine, which we will discuss in more detail in the context of a more complex workflow. The first is that they generally deal automatically with the storage of intermediate results (known as *checkpointing*), which can help speed up execution when nothing has changed.  The second is that the workflow engine uses the execution graph to optimize the computation, only performing those operations that are actually needed.  This is similar in spirit to the concept of *lazy execution* used by packages like Polars, in which the system optimizes computational efficiency by first analyzing the full computational graph.

### General-purpose versus domain-specific workflow engines

With the growth of data science within industry and research, there has been an explosion of new workflow management systems that aim to solve particular problems; a list of these can be found at [awesome-workflow-engines](https://github.com/meirwah/awesome-workflow-engines). It's also worth noting that there are a number of domain-specific workflow engines that are specialized for particular kinds of data and workflows.  Examples include [Galaxy](https://galaxyproject.org/) which is specialized for bioinformatics and genomics, and [Nipype](https://nipype.readthedocs.io/en/latest/index.html) which is specialized for neuroimaging analysis workflows. If your research community uses one of these then it's worth exploring that engine as your first option, since it will probably be well supported within the community. However, a benefit of using a general-purpose engine is that they will often be better maintained and supported, and AI tools will likely have more examples to work from in generating workflows.

### Workflow management using Snakemake

We will use the Snakemake workflow system for our example, which I chose for several reasons:

- It is a very well-established project that is actively maintained.
- It is Python-based, which makes it easy for Python users to grasp.
- Because of its long history and wide use, AI coding assistants are quite familiar with it and can easily generate the necessary files for complex workflows.

Snakemake is a sort of "make on steroids", designed specifically to manage complex computational workflows.  It uses a Python-like syntax to define the workflow, from which it infers the computational graph and optimizes the computation. The Snakemake workflow is defined using a `Snakefile`, the most important aspect of which is a set of rules that define the different workflow steps in terms of their outputs.  Here is an initial portion of the `Snakefile` for our simple workflow:

```Python
# Load configuration
configfile: "config/config.yaml"

# Global report
report: "report/workflow.rst"

OUTPUT_DIR = Path(config["output_dir"])
DATA_DIR = OUTPUT_DIR / "data"
RESULTS_DIR = OUTPUT_DIR / "results"
FIGURES_DIR = OUTPUT_DIR / "figures"

# Default target
rule all:
    input:
        FIGURES_DIR / "correlation_heatmap.png",
```

What this does is first specify the configuration file, which is a YAML file that defines various parameters for the workflow.  Here are the contents of the config file for our simple example:

```bash
# Data URLs
meaningful_variables_url: "https://raw.githubusercontent.com/IanEisenberg/Self_Regulation_Ontology/refs/heads/master/Data/Complete_02-16-2019/meaningful_variables_clean.csv"
demographics_url: "https://raw.githubusercontent.com/IanEisenberg/Self_Regulation_Ontology/refs/heads/master/Data/Complete_02-16-2019/demographics.csv"

# Correlation settings
correlation_method: "spearman"

# Heatmap settings
heatmap:
  figsize: [12, 10]
  cmap: "coolwarm"
  vmin: -1.0
  vmax: 1.0
```

The only rule shown here is the `all` rule, which takes as its input the correlation figure that is the final output of the workflow.  If snakemake is called and that file already exists, then it won't be rerun (since it's the only requirement for the rule) unless 1) the `--force` flag is included, which forces rerunning the entire workflow, or 2) a rerun is triggered by one of the changes that Snakemake looks for (discussed more below).  If the file doesn't exist, then Snakemake examines the additional rules to determine which steps need to be run in order to generate that output.  In this case, it would start with the rule that generates the correlation figure:

```python
# Step 5: Generate clustered heatmap
rule generate_heatmap:
    input:
        RESULTS_DIR / "correlation_matrix.csv",
    output:
        report(
            FIGURES_DIR / "correlation_heatmap.png",
            caption="report/heatmap.rst",
            category="Results",
        ),
    params:
        figsize=config["heatmap"]["figsize"],
        cmap=config["heatmap"]["cmap"],
        vmin=config["heatmap"]["vmin"],
        vmax=config["heatmap"]["vmax"],
    log:
        OUTPUT_DIR / "logs" / "generate_heatmap.log",
    script:
        "scripts/generate_heatmap.py"
```

This step uses the `generate_heatmap.py` script to generate the correlation figure, and it requires the `correlation_matrix.csv` file as input.  Snakemake would then work backward to identify which step is required to generate that file, which is the following:

```python
# Step 4: Compute correlation matrix
rule compute_correlation:
    input:
        DATA_DIR / "joined_data.csv",
    output:
        RESULTS_DIR / "correlation_matrix.csv",
    params:
        method=config["correlation_method"],
    log:
        OUTPUT_DIR / "logs" / "compute_correlation.log",
    script:
        "scripts/compute_correlation.py"
```

By working backwards this way from the intended output, Snakemake can reconstruct the computational graph that we saw in #simpleDAG-fig.  It then uses this graph to plan the computations that will be performed.  


#### Snakemake scripts

In order for Snakemake to execute each of our modules, we need to wrap those modules in a script that can use the configuration information from the config file.  Here is an example of what the [generate_heatmap.py]() script would looks like:

```python
from pathlib import Path
import pandas as pd
from bettercode.simple_workflow.visualization import (
    generate_clustered_heatmap,
)

def main():
    """Generate and save clustered heatmap."""
    # ruff: noqa: F821
    input_path = Path(snakemake.input[0])
    output_path = Path(snakemake.output[0])
    figsize = tuple(snakemake.params.figsize)
    cmap = snakemake.params.cmap
    vmin = snakemake.params.vmin
    vmax = snakemake.params.vmax

    # Load correlation matrix
    corr_matrix = pd.read_csv(input_path, index_col=0)
    print(f"Loaded correlation matrix: {corr_matrix.shape}")

    # Generate heatmap
    output_path.parent.mkdir(parents=True, exist_ok=True)
    generate_clustered_heatmap(
        corr_matrix,
        output_path=output_path,
        figsize=figsize,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
    )
    print(f"Saved heatmap to {output_path}")

if __name__ == "__main__":
    main()
```

You can see that the code refers to `snakemake` even though we haven't explicitly imported it; this is possible because the script is executed within the Snakemake environment which makes that object available, which contains all of the configuration details.  

- Dry run

```bash
Config file config/config.yaml is extended by additional config specified via the command line.
host: Russells-MacBook-Pro.local
Building DAG of jobs...
Job stats:
job                              count
-----------------------------  -------
all                                  1
compute_correlation                  1
download_demographics                1
download_meaningful_variables        1
filter_demographics                  1
filter_meaningful_variables          1
generate_heatmap                     1
join_datasets                        1
total                                8

... (omitting intermediate output)

Job stats:
job                              count
-----------------------------  -------
all                                  1
compute_correlation                  1
download_demographics                1
download_meaningful_variables        1
filter_demographics                  1
filter_meaningful_variables          1
generate_heatmap                     1
join_datasets                        1
total                                8

Reasons:
    (check individual jobs above for details)
    input files updated by another job:
        all, compute_correlation, filter_demographics, filter_meaningful_variables, generate_heatmap, join_datasets
    output files have to be generated:
        compute_correlation, download_demographics, download_meaningful_variables, filter_demographics, filter_meaningful_variables, generate_heatmap, join_datasets
This was a dry-run (flag -n). The order of jobs does not reflect the order of execution.
```

Once we have confirmed that everything is set up properly, we can then use `snakemake` to run the workflow:

```bash
➤  snakemake --cores 1 --config output_dir=./output
Config file config/config.yaml is extended by additional config specified via the command line.
Assuming unrestricted shared filesystem usage.
host: Russells-MacBook-Pro.local
Building DAG of jobs...
Using shell: /bin/bash
Provided cores: 1 (use --cores to define parallelism)
Rules claiming more threads will be scaled down.
Job stats:
job                              count
-----------------------------  -------
all                                  1
compute_correlation                  1
download_demographics                1
download_meaningful_variables        1
filter_demographics                  1
filter_meaningful_variables          1
generate_heatmap                     1
join_datasets                        1
total                                8

Select jobs to execute...
Execute 1 jobs...

[Wed Dec 24 08:17:57 2025]
localrule download_demographics:
    output: output/data/demographics.csv
    log: output/logs/download_demographics.log
    jobid: 7
    reason: Missing output files: output/data/demographics.csv
    resources: tmpdir=/var/folders/r2/f85nyfr1785fj4257wkdj7480000gn/T
Downloaded 522 rows from https://raw.githubusercontent.com/IanEisenberg/Self_Regulation_Ontology/refs/heads/master/Data/Complete_02-16-2019/demographics.csv
Saved to output/data/demographics.csv
[Wed Dec 24 08:17:58 2025]
Finished jobid: 7 (Rule: download_demographics)
1 of 8 steps (12%) done

... (omitting intermediate output)

8 of 8 steps (100%) done
Complete log(s): .snakemake/log/2025-12-24T081757.266320.snakemake.log
```

One handy feature of snakemake is that, just like `make`, we can give it a specific target file and it will perform only the portions of the workflow that are required to regenerate that specific file. 

#### Best practices for Snakemake workflows

The Snakemake team has published a set of [best practices](https://snakemake.readthedocs.io/en/stable/snakefiles/best_practices.html) for the creation of Snakemake workflows, some of which I will outline here, along with one of my own (the first).

#### Using a working directory- TBD
By default Snakemake looks for a Snakefile in the current directory, so it's tempting to run the workflow from the code repository.  However, Snakemake creates a directory called `.snakemake` to store metadata in the directory where the workflow is run, which one generally doesn't want to mix with the code.  Thus, it's best to create a working directory with its own copy of the config file (to allow local modifications), and then run the command from that directory using the

##### Workflow organization
There is a [standard format](https://snakemake.readthedocs.io/en/stable/snakefiles/deployment.html#distribution-and-reproducibility) for the organization of Snakemake workflow directories, which one should follow when developing new workflows.  

##### Snakefile formatting
Snakemake comes with a set of commands that help ensure that Snakemake files are properly formatted and follow best practices.  First, there is a static analysis tool (i.e a "linter", akin to ruff or flake8 for Python code), which can automatically identify problems with Snakemake rule files.  Unfortunately, this tool assumes that one is using the Conda environment manager (which is increasingly being abandoned in favor of uv) or a container (which comes with substantial overhead), and it raises an issue for any rule that doesn't specify a Conda or container environment. Nonetheless, if those are ignored the linter can be useful in identifying problems. There is also a formatting tool called `snakefmt` (separately installed) that optimally formats Snakemake files in the way that `black` or `blue` format Python code.  These can both be useful tools when developing a new workflow.

##### Configurability
Workflow configuration details should be stored in configuration files, such as the `config.yaml` files that we have used in our workflow examples.  However, these files should not be used for runtime parameters, such as the number of cores or the output directory; those should instead be handled using Snakemake's standard arguments.  The initial workflow generated by Claude did not follow this guidance, and instead custom variables to define runtime details such as the output directory and the number of cores. (TBD - CHECK THIS)

#### Updating the workflow when inputs change

Once the workflow has completed successfully, re-running it will not result in the re-execution of any of the analyses:

```bash
snakemake --cores 1 --config output_dir=/Users/poldrack/data_unsynced/BCBS/simple_workflow/wf_snakemake
Config file config/config.yaml is extended by additional config specified via the command line.
Assuming unrestricted shared filesystem usage.
host: Russells-MacBook-Pro.local
Building DAG of jobs...
Nothing to be done (all requested files are present and up to date).
```

However, Snakemake checks several features of the workflow (by default) when generating its DAG to see if anything relevant has changed.  By default it checks to see if any of the following have changed (configurable using the `-rerun-triggers` flag):

- modification times of input files
- the code specified within the rule
- the input files or parameters for the rule

Snakemake also checks for changes in the details of the software environment, but as of the date of writing this only works for Conda environments.  

As an example, I will first update the modification time of the demographics file from a previous successful run using the `touch` command:

```bash
➤  ls -l data/meaningful_variables.csv
Permissions Size User     Date Modified Name
.rw-r--r--@ 1.2M poldrack 24 Dec 10:11  data/meaningful_variables.csv

➤  touch data/meaningful_variables.csv

➤  ls -l data/meaningful_variables.csv
Permissions Size User     Date Modified Name
.rw-r--r--@ 1.2M poldrack 24 Dec 10:14  data/meaningful_variables.csv
```

You can see that the touch command updated the modification time of the file.  Now let's rerun the `snakemake` command:

```bash
snakemake --cores 1 --config output_dir=/Users/poldrack/data_unsynced/BCBS/simple_workflow/wf_snakemake
Config file config/config.yaml is extended by additional config specified via the command line.
Assuming unrestricted shared filesystem usage.
host: Russells-MacBook-Pro.local
Building DAG of jobs...
Using shell: /bin/bash
Provided cores: 1 (use --cores to define parallelism)
Rules claiming more threads will be scaled down.
Job stats:
job                            count
---------------------------  -------
all                                1
compute_correlation                1
filter_meaningful_variables        1
generate_heatmap                   1
join_datasets                      1
total                              5
```

Similarly, Snakemake will rerun the workflow if any of the scripts used to run the workflow are modified.  However, it's important to note that it will not identify changes in the modules that are imported.  In that case you would need to rerun the workflow in order to re-execute the relevant steps.

## Scaling to a complex workflow

We now turn to a more realistic and complex scientific data analysis workflow. For this example I will use an analysis of single-cell RNA-sequencing data to determine how gene expression in immune system cells changes with age. This analysis will utilize a [large openly available dataset](https://cellxgene.cziscience.com/collections/dde06e0f-ab3b-46be-96a2-a8082383c4a1) that includes data from 982 people comprising about 1.3 million peripheral blood mononuclear cells (i.e. white blood cells) for about 35K transcripts.  I chose this particular example for several reasons:

- It is a realistic example of a workflow that a researcher might actually perform.
- It has a large enough sample size to provide a robust answer to our scientific question.
- The data are large enough to call for a real workflow management scheme, but small enough to be processed on a single laptop (assuming it has decent memory). 
- The workflow has many different steps, some of which can take a significant amount of time (over 30 minutes)
- There is an established Python library ([scanpy](https://scanpy.readthedocs.io/en/stable/)) that implements the necessary workflow components.
- It's an example outside of my own research domain, to help demonstrate the applicability of the book's ideas across a broader set of data types.

I will use this example to show how to move from a monolithic analysis script to a well-structured and usable workflow that meets most of the desired features described above. 

### Starting point: One huge notebook

I developed the initial version of this workflow as many researchers would: by creating a Jupyter notebook that implements the entire workflow, which can be found [here]().  Although I don't usually prefer to do code generation using a chatbot, I did most of the coding for this example using the Google Gemini 3 chatbot, for a couple of reasons.  First, this model seemed particularly knowledgeable about this kind of analysis and the relevant packages.  Second, I found it useful to read the commentary about why particular analysis steps were being selected.  For debugging I used a mixture of the Gemini 3 chatbot and the VSCode Copilot agent, depending on the nature of the problem; for problems specific to the RNA-seq analysis tools I used Gemini, while for standard Python/Pandas issues I used Copilot. The total execution time for this notebook is about two hours on an M3 Max Macbook Pro.  

#### The problem of in-place operations

What I found as I developed the workflow is that I increasingly ran into problems that arose because the state of particular objects had changed.  This occurred for two reasons at different points.  In some cases it occurred because I saved a new version of the object to the same name, resulting in an object with different structure than before.  Second, and more insidiously, it occurred when an object passed into a function is modified by the function internally.  This is known as an *in-place* operation, in which a function modifies an object directly rather than returning a new object that can be assigned to a variable.  

In-place operations can make code particularly difficult to debug in the context of a Jupyter notebook, because it's a case where out-of-order execution can result in very confusing results or errors, since the changes that were made in-place may not be obvious.  For this reason, I generally avoid any kind of in-place operations if possible.  Rather, any functions should immediately create a copy of the object that was passed in, and then do its work on that copy, which is returned at the end of the function for assignment to a new variable.  One can then re-assign it to the same variable name if desired, which is more transparent than an in-place operation but still makes the workflow dependent on the exact state of execution and can lead to confusion when debugging.  Some packages allow a feature called "copy-on-write" which defers actually copying the data in memory until it is actually modified, which can make copying more efficient. 

If one must modify objects in-place, then it is good practice to announce this loudly.  The loudest way to do this would be to put "inplace" in the function name. Another cleaner but less loud way is through conventions regarding function naming; for example, in PyTorch it is a convention that any function that ends with an underscore (e.g. `tensor.mul_(x)`) performs an in-place operation whereas the same function without the underscore (`tensor.mul(x)`) returns a new object. Another way that some packages enable explicit in-place operations is through a function argument (e.g. `inplace=True` in pandas), though this is being phased out from many functions in Pandas because "It is generally seen (at least by several pandas maintainers and educators) as bad practice and often unnecessary" ([PDEP-8](https://pandas.pydata.org/pdeps/0008-inplace-methods-in-pandas.html)). 

One way to prevent in-place operations altogether is to use data types that are *immutable*, meaning that they can't be changed once created.  This is one of the central principles in *functional programming* languages (such as Haskell), where all data types are immutable, such that one is required to create a new object any time data are modified.  Some native data types in Python are immutable (such as tuples and frozensets), and some data science packages also provide immutable data types; in particular, the Polars package (which is meant to be a high-performance alternative to pandas) implements its version of a data frame as an immutable object, and the JAX package (for high-performance numerical computation and machine learning) implements immutable numerical arrays.

#### Converting from Jupyter notebook to a runnable python script

As we discussed in an earlier chapter, converting a Jupyter notebook to a pure Python script is easy using `jupytext`.  This results in a script that can be run from the command line.  However, there can be some commands that will block execution of the script; in particular, plotting commands can open windows that will block execution until they are closed.  To prevent this, and to ensure that the results of the plots are saved for later examination, I replaced all of the `plt.show()` commands that display a figure to the screen with `plt.savefig()` commands that save the figures to a file in the results directory.  (This was an easy job for the Copilot agent to complete.) 

## Decomposing a complex workflow

The first thing we need to do with a large monolithic workflow is to determine how to decompose it into coherent modules.  There are various reasons that one might choose a particular breakpoint between modules.  First and foremost, there are usually different stages that do conceptually different things.  In our example, we can break the workflow into several high-level processes:

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

In addition to a conceptual breakdown, there are also other reasons that one might want to further decompose the workflow:

- There may be points where one might need to restart the computation (e.g. due to computational cost).
- There may be sections where one might wish to swap in a new method or different parameterization.
- There may be points where the output could be reusable elsewhere.

## Stateless workflows

I asked Claude Code to help modularize the monolithic workflow, using a prompt that provided the conceptual breakdown described above.  The resulting code (found at XXX - link to commit 678983e1c337b6a23b0f35cfb974a87587cfd13e) ran correctly, but crashed about two hours into the process due to a resource issue that appeared to be due to asking for too many CPU cores in the differential expression analysis.  This left me in the situation of having to rerun the entire two hours of preliminary workflow simply to get to a point where I could test my fix for the differential expression component, which is not a particularly efficient way of coding.  The problem here is that the workflow execution is *stateful*, in the sense that the previous steps need to be rerun prior to performing the current step in order to establish the required objects in memory.  The solution to this problem is to implement the workflow in a *stateless* way, which doesn't require that earlier steps be rerun if they have already been completed.  One way to do this is by implementing a process called *checkpointing*, in which intermediate results are stored for each step.  These can then be used to start the workflow at any point without having to rerun all of the previous steps.  

Another important feature of a workflow related to statelessness is *idempotency*, which means that a workflow will result in the same answer when run multiple times.  This is related to, but not the same as, the idea of statelessness.  For example, a stateless workflow that saves its outputs to checkpoint files could fail to be idempotent if the results were appended to the output file with each execution, rather than overwriting them.  This would result in different outputs depending on how many times the workflow has been executed.  Thus, when we use checkpointing we should be sure to either reuse the existing file or rewrite it completely with a new version.


I asked Claude Code to help with this:

> I would like to modify the workflow described in src/bettercode/rnaseq/modular_workflow/run_workflow.py to make it execute in a stateless way through the use of checkpointing.  Please analyze the code and suggest the best way to accomplish this.

After analyzing the codebase Claude came up with three proposed solutions to the problem:

- 1. Use a "registry pattern" in which we define each step in terms of its inputs, outputs, and checkpoint file, and then assemble these into a workflow that can be executed in a stateless way, automatically skipping completed steps.  This was its recommended approach.
- 2. Use simple "wrapper" approach in which each module in the workflow is executed via a wrapper function that checks for cached checkpoint values.
- 3. Use a well-established existing workflow engine such as [Prefect](https://www.prefect.io/) or [Luigi](https://github.com/spotify/luigi). While these are powerful, they incur additional dependencies and complexity and may be too heavyweight for our problem.

Here we will examine the first (recommended) option and the third solution; while the second option is easy to implement, it's not as clean as the registry approach.

### A workflow registry with checkpointing

We start with a custom approach in order to get a better view of the details of workflow orchestration. It's important to note that I generally would not recommend building one's one custom workflow manager, at least not before trying a general-purpose workflow engine, but I will show an example of a custom workflow engine in order to provide a better understanding of the detailed process of workflow management.  We start with a prompt:

> let's implement the recommended Stateless Workflow with Checkpointing.  Please generate new code within src/bettercode/rnaseq/stateless_workflow.

The resulting code worked straight out of the box, but it didn't maintain any sort of log of its processing, which can be very useful.  In particular, I wanted to log the time required to execute each step in the workflow, for use in optimization that I will discuss further below.  I asked Claude to add this:

> I would like to log information about execution, including the time required to execute each step along with the details about execution such as parameters passed for each step.  please record these during execution and save to a date-stamped json file within the workflows directory.

After Claude's implementation of this feature, a fresh run of the workflow gives the following summary:

```bash
============================================================
EXECUTION SUMMARY
============================================================
Workflow: immune_aging_scrnaseq
Run ID: 20251221_114458
Status: completed
Total Duration: 7094.5 seconds

Step Details:
------------------------------------------------------------
  ✓ Step 1: data_download                 0.0s [cached]
  ✓ Step 2: filtering                    74.7s
  ✓ Step 3: quality_control             263.3s
  ✓ Step 4: preprocessing                35.9s
  ✓ Step 5: dimensionality_reduction   6565.4s
  ✓ Step 6: clustering                   69.6s
  ✓ Step 7: pseudobulking                11.6s
  ✓ Step 8: differential_expression      19.0s
  ✓ Step 9: gsea                          1.7s
  ✓ Step 10: overrepresentation           13.3s
  ✓ Step 11: predictive_modeling          39.8s
------------------------------------------------------------
```

The associated JSON file contains much more detail regarding each workflow step.  If we run the workflow again, we see that it now uses cached results at each step:

```bash
============================================================
EXECUTION SUMMARY
============================================================
Workflow: immune_aging_scrnaseq
Run ID: 20251221_142225
Status: completed
Total Duration: 17.4 seconds

Step Details:
------------------------------------------------------------
  ✓ Step 1: data_download                 0.0s [cached]
  ✓ Step 2: filtering                     1.9s [cached]
  ✓ Step 3: quality_control               3.0s [cached]
  ✓ Step 4: preprocessing                 3.1s [cached]
  ✓ Step 5: dimensionality_reduction      3.4s [cached]
  ✓ Step 6: clustering                    4.3s [cached]
  ✓ Step 7: pseudobulking                 0.1s [cached]
  ✓ Step 8: differential_expression       1.4s [cached]
  ✓ Step 9: gsea                          0.0s [cached]
  ✓ Step 10: overrepresentation            0.0s [cached]
  ✓ Step 11: predictive_modeling           0.0s [cached]
------------------------------------------------------------
```

Checkpointing thus solved our problem, by allowing each step to be skipped over once it's been completed.

#### Checkpointing and disk usage

One potential drawback of checkpointing is that it can result in substantial disk usage when working with large datasets. In the example above, the checkpoint directory after workflow completion weighs in at a whopping 64 Gigabytes, with numerous very large files:

```bash
➤  du -sh *

7.3G    step02_filtered.h5ad
 13G    step03_qc.h5ad
 13G    step04_preprocessed.h5ad
 14G    step05_dimreduced.h5ad
 14G    step06_clustered.h5ad
380M    step07_pseudobulk.h5ad
 28M    step08_counts.parquet
1.6M    step08_de_results.parquet
1.8G    step08_stat_res.pkl
 13M    step09_gsea.pkl
 44K    step10_enr_down.pkl
 28K    step10_enr_up.pkl
 36K    step11_prediction.pkl
 ```

In particular, in step 3 a copy of the original data was added for reuse in a later step (in a separate variable within the dataset) alongside the results of processing at that step, leading to files that were roughly doubled in size.  However, those raw data were not needed again until step 7.  By changing the workflow to avoid saving those data in the checkpoints and instead loading them directly at step 7, we were able to halve the size of those intermediate checkpoints.

In this implementation a checkpoint file was stored for each step in the workflow.  However, if the goal of checkpointing is primarily to avoid having to rerun expensive computations, then we don't need to checkpoint every step given that some of them take relatively little time.  In this case, we can checkpoint only after a subset of steps.  In this case I chose to checkpoint after steps 2, 3, and 5 since those each take well over a minute to run (with step 5 taking well over an hour).  Another goal of checkpointing is to store files that might be useful for later analyses or QA by the researcher.  In this example workflow, steps 1-7 can be classified as "preprocessing" in the sense that they are preparing the data for analysis, whereas steps 8-11 reflect actual analyses of the data, such that the results could be reported in a publication.  It is thus important to save those outputs for later analyses and for sharing with the final results.

#### Compressing checkpoint files

Another potentially helpful solution is to compress the checkpoint data if they are not already being compressed by default.  In this example, the default in the AnnData package for saving `h5ad` files is to use no compression, so there are substantial savings in disk space to be had by compressing the data: whereas the raw data file was 7.3 GB, a version of the same data saved using compression took up only 2.9 GB.  The tradeoff is that working with compressed files takes longer.  This is particularly the case for saving of files; whereas it took about 3 seconds to save an uncompressed version of the data, it took about 105 seconds to store the compressed version.  Given that the saving of the compressed file will happen in the context of an already long workflow, that doesn't seem like such a concern.  We are more concerned about how the use of compression increases loading times, and here the difference is not quite so dramatic, at 1.3 seconds versus 19.8 seconds.  The decision about whether or not to compress will ultimately come down to the relative cost of time versus disk space, but in this case I decided to go ahead and compress the checkpoint files.

Combining these strategies of reducing data duplication, eliminating some intermediate checkpoints, and compressing the stored data, our final pipeline generates about 13 GB worth of checkpoint data, substantially smaller than the initial 64 GB.  With all checkpoints generated, the entire workflow completes in less than four minutes, with only three time-consuming steps being rerun each time.   The initial execution of the workflow is a few minutes longer due to the extra time needed to read and write compressed checkpoint files, but these few minutes are hardly noticeable for a workflow that takes more than two hours to complete.

The use of a modular architecture for our stateless workflow helps to separate the actual workflow components from the execution logic of the workflow.  One important benefit of this is that it allows us to plug those modules into any other workflow system, and as long as the inputs are correct it should work. We will see that next when we create new versions of this workflow using two common workflow engines.

### Managing a complex workflow with Snakemake

In general I recommend trying a general-purpose workflow engine instead of writing a custom one.  In this example I will focus on the Snakemake workflow engine; in the project repository there is also a parallel workflow developed using the [Prefect] workflow engine (which is integrated directly into the Python code), but I will not discuss it here.
 #rnaseq-DAG-fig shows the DAG generated by Snakemake for the RNA-seq analysis workflow. 

```{figure} images/snakemake-DAG.png
:label: rnaseq-DAG-fig
:align: center
:width: 300px

The execution graph for the RNA-seq analysis workflow visualized as a DAG.
```

The `Snakemake` file is substantially larger for this complex workflow; to keep it from being even longer, we can also move some of the rules into separate rules files using the following syntax within the `Snakemake` file:

```bash
# Include modular rule files
include: "rules/common.smk"
include: "rules/preprocessing.smk"
include: "rules/pseudobulk.smk"
include: "rules/per_cell_type.smk"
```


#### Pipeline optimization

The first time that I ran this workflow using snakemake, I noticed that it was substantially slower than when I ran it using the custom workflow engine.  When I asked Claude about this, it gave me a reasonable answer:

> The Snakemake rules don't specify a threads directive. By default, Snakemake runs each job with 1 thread, which limits parallelization of computationally intensive operations like neighbor computation and UMAP (which use numba internally).

I asked Claude to fix this, and it returned the following change:

>   Fixes applied:
>  1. Added threads: 8 to dimensionality_reduction rule
>  2. Added threads: 8 to quality_control rule (Scrublet)
>  3. Added threads: 4 to preprocess rule
>  4. Set NUMBA_NUM_THREADS and OMP_NUM_THREADS environment variables in dimred.py
>  In contrast, tasks run in the main process have access to all CPUs by default, which is why it was faster.

This solves the problem but it's a brittle soluution: in particular, it will probably fail if there are fewer than 8 threads available on the system and it won't take advantage of more than 8 if they are available. Snakemake actually take a command line argument (`--cores`) to specify the number of cores to use, so I instead asked Claude to have Snakemake use the number of cores specified at the command line rather than an arbitrary number that might not be optimal. We will discuss optimization in much greater detail in a later chapter, but whenever a pipeline takes much longer to run using a workflow manager than one would expect, it's likely that there is optimization to be done.

#### Running snakemake



It's important to know that when snakemake is run, it stores metadata regarding the workflow in a hidden directory called `.snakemake`.  It's generally a good idea to add this to the `.gitignore` file since one probably doesn't want to include detailed workflow metadata in one's git repository.  It's also a best practice to execute the 

#### Report generation

One of the very handy features of Snakemake is its ability to generate reports for workflow execution.  Report generation is as simple as:

```bash
snakemake --report $DATADIR/immune_aging/wf_snakemake/report.html --config datadir=$DATADIR/immune_aging/
```

This command uses the metadata stored in the .snakemake 

#### Tracking provenance

As I discussed in the earlier chapter on data management, it is essential to be able to track the provenance of files in a workflow.  That is, how did the file come to be, and what other files did it depend on?  

#### Parametric sweeps

A common pattern in some computational research domains is the *parametric sweep*, where a workflow is run using a range of values for specific parameters in the workflow.  A key to successful execution of parametric sweeps is proper organization of the outputs so that they can be easily processed by downstream tools.  Snakemake provides the ability to easily implement parametric sweeps simply by specifying a list of parameter values in the configuration file.  For example... TBD


## Testing workflows

- write tests for common edge cases
  - use a small toy dataset for testing
- unit vs integration tests


## Scaling workflows

- maybe leave this to the HPC chapter?

## Choosing a workflow engine



