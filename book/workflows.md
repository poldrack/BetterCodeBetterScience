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
- *Idempotency*: This term from computer science means that the result of the workflow does not change after its first successful run, which allows safely rerunning the workflow when there is a failure.
- *Traceability*:  All operations are logged, and provenance information is stored for outputs.

Finally, we care about the *efficiency* of the workflow implementation. This includes:

- *Incremental execution*: The workflow only reruns a module if necessary, such as when an input changes.
- *Cached computation*: The workflow pre-computes and reuses results from expensive operations when possible.

It's worth noting that these different desiderata will sometimes conflict with one another (such as configurability versus maintainability), and that no workflow will be perfect.  For example, a highly configurable workflow will often be more difficult to maintain.

## Pipelines versus workflows

The terms *workflow* and *pipeline* are sometimes used interchangeably, but in this chapter I will use them to refer to different kinds of applications. I will use *workflow* as the more general term to refer to any set of analysis procedures that are implemented as separate modules.  I will use the term *pipeline* to refer more specifically to a data analysis workflow where several operations are combined into a single command through the use of *pipes*, which are a syntactic construct that feed the output of one process directly into the next process as input.  Some readers may be familiar with pipes from the UNIX command line, where they are represented by the vertical bar "|".  For example, let's say that we had a log file that contains the following entries:

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


## An example of a complex workflow

In this chapter we will focus primarily on complex workflows that have many stages. I will use a running example to show how to move from a monolithic analysis script to a well-structured and usable workflow that meets most of the desired features described earlier.  For this example I will use an analysis of single-cell RNA-sequencing data to determine how gene expression in immune system cells changes with age. This analysis will utilize a [large openly available dataset](https://cellxgene.cziscience.com/collections/dde06e0f-ab3b-46be-96a2-a8082383c4a1) that includes data from about 1.3 million immune system cells for about 35K transcripts.  I chose this particular example for several reasons:

- It is a realistic example of a workflow that a researcher might actually perform.
- The data are large enough to call for a real workflow management scheme, but small enough to be processed on a single laptop (assuming it has decent memory). 
- The workflow has many different steps, some of which can take a significant amount of time (over 30 minutes)
- There is an established Python library ([scanpy](https://scanpy.readthedocs.io/en/stable/)) that implements the necessary workflow components.
- It's an example outside of my own research domain, to help demonstrate the applicability of the book's ideas across a broader set of data types.

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

> I would like to modify the workflow described in src/BetterCodeBetterScience/rnaseq/modular_workflow/run_workflow.py to make it execute in a stateless way through the use of checkpointing.  Please analyze the code and suggest the best way to accomplish this.

After analyzing the codebase Claude came up with three proposed solutions to the problem:

- 1. Use a "registry pattern" in which we define each step in terms of its inputs, outputs, and checkpoint file, and then assemble these into a workflow that can be executed in a stateless way, automatically skipping completed steps.  This was its recommended approach.
- 2. Use simple "wrapper" approach in which each module in the workflow is executed via a wrapper function that checks for cached checkpoint values.
- 3. Use a well-established existing workflow engine such as [Prefect](https://www.prefect.io/) or [Luigi](https://github.com/spotify/luigi). While these are powerful, they incur additional dependencies and complexity and may be too heavyweight for our problem.

Here we will examine the first (recommended) option and the third solution; while the second option is easy to implement, it's not as clean as the registry approach.

### A workflow registry with checkpointing

We start with a custom approach in order to get a better view of the details of workflow orchestration.   

> let's implement the recommended Stateless Workflow with Checkpointing.  Please generate new code within src/BetterCodeBetterScience/rnaseq/stateless_workflow.

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

### Using a workflow engine

There is a wide variety of workflow engines available for data analysis workflows, most of which are centered around the concept of an "execution graph."  This is a graph in the sense described by graph theory, which refers to a set of nodes that are connected by lines (known as "edges").  Workflow execution graphs are a particular kind of graph known as a *directed acyclic graph*, or *DAG* for short. Each node in the graph represents a single step in the workflow, and each edge represents the dependency relationships that exist between nodes.  DAGs have two important features.  First, the edges are directed, which means that they move in one direction that is represented graphically as an arrow.  These represent the dependencies within the workflow.  For example, in our workflow step 1 (obtaining the data) must occur before step 2 (filtering the data), so the graph would have an edge from step 1 with an arrow pointing at step 2.  Second, the graph is *acyclic*, which means that it doesn't have any cycles, that is, it never circles back on itself.  Cycles would be problematic, since they could result in workflows that executed in an infinite loop as the cycle repeated itself.  

Most workflow engines provide tools to visualize a workflow as a DAG. #DAG-fig shows our example workflow visualized using the Snakemake tool that we will introduce below:

```{figure} images/snakemake-DAG.png
:label: DAG-fig
:align: center
:width: 300px

The execution graph for the RNA-seq analysis workflow visualized as a DAG.
```

The use of DAGs to represent workflows provides a number of important benefits:

- The engine can identify independent pathways through the graph, which can then be executed in parallel
- If one node of the graph changes, the engine can identify which downstream nodes need to be rerun
- If a node fails, the engine can continue with executing the nodes that don't depend on the failed node either directly or indirectly

There are a couple of additional benefits to using a workflow engine. The first is that they generally deal automatically with checkpointing and caching of intermediate results.  The second is that the workflow engine uses the execution graph to optimize the computation, only performing those operations that are actually needed.  This is similar in spirit to the concept of *lazy execution* used by packages like Polars, in which the system optimizes computational efficiency by first analyzing the full computational graph.

#### General-purpose versus domain-specific workflow engines

With the growth of data science within industry and research, there has been an explosion of new workflow management systems that aim to solve particular problems; a list of these can be found at [awesome-workflow-engines](https://github.com/meirwah/awesome-workflow-engines).  One important distinction between engines is the degree to which the workflow definition is built into the code, or whether it is defined in a *domain-specific language* (DSL).  We will look at two examples below, one of which (Prefect) builds the workflow details in the code, and the other (Snakemake) uses a specialized syntax built on Python to define the workflow.

It's also worth noting that there are a number of domain-specific workflow engines that are specialized for particular kinds of data and workflows.  Examples include [Galaxy](https://galaxyproject.org/) which is specialized for bioinformatics and genomics, and [Nipype](https://nipype.readthedocs.io/en/latest/index.html) which is specialized for neuroimaging analysis workflows. If your research community uses one of these then it's worth exploring that engine as your first option, since it will probably be well supported within the community. However, a benefit of using a general-purpose engine is that they will often be better maintained and supported, and AI tools will likely have more examples to work from in generating workflows.

### A language-specific workflow management example: Prefect


#### Configuration management

The initial version of the Prefect workflow generated by Claude had the default parameter settings for each workflow hard-coded into the task definitions in Python.  This is not a great practice, since it means that any changes in parameter settings require changes in the code, making it difficult to easily test different parameter settings.  A better practice is to put the parameter settings into a human-editable configuration file, which can be specified upon execution of the workflow.  YAML is a common markup language for configuration files, which is used in both this workflow and the following one.



### A general-purpose workflow management example: Snakemake


#### Pipeline optimization

The first time that I ran my workflow using snakemake, I noticed that it was substantially slower than when I ran it with Prefect.  When I asked Claude about this, it gave me a reasonable answer:

> The Snakemake rules don't specify a threads directive. By default, Snakemake runs each job with 1 thread, which limits parallelization of computationally intensive operations like neighbor computation and UMAP (which use numba internally).

I asked Claude to fix this, and it returned the following change:


>   Fixes applied:
>  1. Added threads: 8 to dimensionality_reduction rule
>  2. Added threads: 8 to quality_control rule (Scrublet)
>  3. Added threads: 4 to preprocess rule
>  4. Set NUMBA_NUM_THREADS and OMP_NUM_THREADS environment variables in dimred.py
>   In contrast, Prefect tasks run in the main process with access to all CPUs by default, which is why it was faster.

This solves the problem but it's an odd choice: in particular, it will probably fail if there are fewer than 8 threads available on the system. Snakemake actually take a command line argument (`--cores`) to specify the number of cores to use, so I instead asked Claude to have Snakemake use the number of cores specified at the command line rather than an arbitrary number that might fail if the requested number of cores are not available. We will discuss optimization in much greater detail in a later chapter.




## Tracking provenance



### Configuration management

- how to configure a workflow

    - configuration files
    - command line arguments
    - defaults

- interaction with provenance

- discuss fit-transform model somewhere

https://workflowhub.eu/



## Error handling and robustness

- Fail fast
- Gracefully handle missing data
- Checkpointing for long-running workflows
- write tests for common edge cases
  - use a small toy dataset for testing
- unit vs integration tests


## Logging


## Report generation


 



## Scaling workflows

- maybe leave this to the HPC chapter?


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

    

