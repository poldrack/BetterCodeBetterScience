# Workflow Management

In most parts of science today, data processing and analysis comprises many different steps.  We will refer to such a set of steps as a computational *workflow* (or, interchangeably, *pipeline*). If you have been doing science for very long, you have very likely encountered a *mega-script* that implements such a workflow. Usually written in a scripting language like *Bash*, this is a script that may be hundreds or even thousands of lines long that runs a single workflow from start to end.  Often these scripts are handed down to new trainees over generations, such that users become afraid to make any changes lest the entire house of cards comes crashing down.  I think that most of us can agree that this is not an optimal workflow, and in this chapter I will discuss in detail how to move from a mega-script to a workflow that will meet all of the requirements that are required to provide robust and reliable answers to our scientific questions.

## What do we want from a scientific workflow?

First let's ask: What do we want from a computational scientific workflow?  Here are some of the factors that I think are important.  First, we care about the *correctness* of the workflow, which includes the following factors:

- *Verifiability*:  The workflow includes validation procedures to ensure against known problems or edge cases.
- *Reproducibility*:  The workflow can be rerun from scratch on the same data and get the same answer, at least within the limits of uncontrollable factors such as floating point imprecision.
- *Robustness*: When there is a problem, the workflow fails quickly with explicit error messages, or degrades gracefully when possible.

Second, we care about the *usability* of the workflow. Factors related to usability include:

- *Configurability*: The workflow uses smart defaults, but allows the user to easily change the configuration in a way that is traceable.
- *Parameterizability*: Multiple runs of the workflow can be executed with different parameters, and the separate outputs can be tracked.
- *Standards compliance*:  The workflow leverages common standards to easily read in data and generates output using community standards for file formats and organization when available.

Third, we care about the *engineering quality* of the code, which includes:

- *Maintainability*: The workflow is structured and documented so that others (including your future self) can easily maintain, update, and extend it in the future.
- *Modularity*: The workflow is composed of a set of independently testable modules, which can be swapped in or out relatively easily.
- *Idempotency*: This term from computer science means that running the workflow multiple times gives the same result as running it once, which allows safely rerunning the workflow when there is a failure.
- *Traceability*:  All operations are logged, and provenance information is stored for outputs.

Finally, we care about the *efficiency* of the workflow implementation. This includes:

- *Incremental execution*: The workflow only reruns a module if necessary, such as when an input changes.
- *Amortized computation*: The workflow pre-computes and reuses results from expensive operations when possible.

It's worth noting that these different desiderata will sometimes conflict with one another (such as configurability versus maintainability), and that no workflow will be perfect.  

## An example workflow

In this chapter I will use a running example to show how to move from a monolithic analysis script to a well-structured and usable workflow that meets most of the desired features outlined above.  


## Breaking a workflow into stages

good breakpoints between workflow modules include:

- conceptual logic - different stages do different things 
- points where one might need to restart the computation (e.g. due to computational cost)
- sections where one might wish to swap in a new method or different parameterization
- points where the output could be reusable elsewhere

the workflow should be stateless when possible

- allows each state to be run independently

but sometimes state is required

- e.g. training a neural network, one needs to know where you are in the process



## Modularity and reusability

- separate analysis logic from workflow orchestration
- analysis modules should be tested (e.g. with synthetic data)



## Idempotency

- running it multiple time should give same answer as running it once
- 

- somewhere talk about in-place operations and their challenges

- local mutation - never change an object that is passed in as an argument
    - always copy
    - if the package uses copy-on-write then this is cheap (only copied metadata)
    - this is not default in pandas 1.x but coming in 2.x
        - google says it's possible using pd.options.mode.copy_on_write = True - need to confirm
    - need to check for other frameworks

- lazy frames (polars)

- any function that must mutate in place should do so clearly
    - e.g. normalize_(x) (apparently pytorch style for mutating functions?)
    - or using "inplace" in the function name


- can encode state in type (e.g. a lightweight class that tracks state ,e.g. "NormalizedArray")
- or track stage explicitly (e.g. Dataset(stage='normalized', data=array))

- use zarr to save each pipeline step as a new group:

dataset.zarr/
├── raw/
│   └── signal
├── zscored/
│   └── signal
├── filtered/
│   └── signal

- can also store parameters as attrs in zarr
- e.g. z.attrs.update({
    "stage": "zscore",
    "mean_method": "time",
    "std_ddof": 1,
})


also look at arrow for columnar data - look into arrow immutability


## Deferred execution

- dask, xarray

## Checkpointing

- pipeline state should be files on disk, not in memory
- functions don't pass large objects in memory, they simply pass file names
- for modern formats like parquet (others?) reading is very fast so the penalty is minimal

## Precomputing expensive/common operations


## Tracking provenance



### Configuration management

- how to configure a workflow

    - configuration files
    - command line arguments
    - defaults

- interaction with provenance

- discuss fit-transform model somewhere

https://workflowhub.eu/


 - use narps as the working example 


## Error handling and robustness

- Fail fast
- Gracefully handle missing data
- Checkpointing for long-running workflows
- write tests for common edge cases
  - use a small toy dataset for testing
- unit vs integration tests


## Logging


## Report generation


 
## Simple workflow management with Makefiles



## Python workflow management with checkpoints



## Workflow management systems for complex workflows

- introduce DAGs

- general purpose vs domain specific
    - overview various engines




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

    

