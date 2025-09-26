# Project structure and management

```{contents}
```

One of the keys to efficient software development is good project organization.  Above all else, using a consistent organizational scheme makes development easier because it allows one to rely upon defaults rather than making decisions, and to rely upon assumptions rather than asking questions. In this chapter we will talk about various aspects of project organization and management.  In particular, we will discuss the use of computational notebooks and ways to make them more amenable to a reproducible computational workflow, as well as when and how to move beyond notebooks.

## The goals of a scientific software project

### It needs to work

This might seem like an obvious point: In order for a software project to be useful, the software first and foremost needs to be written and to run successfully.  However, the point may not be as obvious as it seems: In particular, may researchers can get stuck trying to plan and generate code that is as perfect as possible, and never actually generate code that runs well enough to solve their problem.  Remember the Agile software development idea that we discussed in Chapter 1, which stresses the importance of "working software" over clean, well-documented code. This is not to say that we don't want clean, well-documented code in the end; rather, it implies that we should first get something working that solves our problem (the "minimum viable product"), and once we have that we can then clean up, refactor, and document the code to help address the next goals.

### It needs to work accurately

Once it runs, our main goal is to make sure that our scientific code solves the intended problem accurately.  There are many ways in which inaccuracy can creep into scientific code:

- *The wrong algorithm may be chosen to solve the problem.* For example, you might be analyzing count data that have a high prevalence of zeros, but use a statistical model like linear regression that assumes normality of the model errors.  The data thus violate the assumptions of the selected algorithm.
- *The right algorithm may be implemented incorrectly.*  For example, you might implement the hurdle regression model for zero-inflated count data, but use an incorrect implementation (like the one that is often recommended by AI coding tools, as discussed in an earlier chapter).
- *The algorithm may not perform properly.* For example, one might use a linear mixed effects model that is estimated using a maximum likelihood method, but the estimation procedure doesn't converge for the particular dataset and model specification, leading to potentially invalid parameter estimates.  Similarly, an estimation procedure may return parameter estimates that are located at the boundaries of the procedure, suggesting that these estimates are not valid.  
- *The assumptions about the data may be incorrect.*  For example, a variable label in the data may suggest that the variable means one thing, when in fact it means different things for different observations depending on their experimental condition.  

These are just a few examples of how code that runs may return answers that are incorrect, each of which could lead to invalid scientific claims if they are not caught.


### It needs to be understandable

As we discussed in our earlier sections on clean coding, one of the most important features of good code is *readability*.  If the code is not readable, then it will be difficult for you or someone else to understand it in the future.  Even language models benefit greatly from readable code, making it much easier for them to infer the original intent and goals of the code (even if they can often do this even with unreadable code).  

### It needs to be portable

It's rare for one to perform analyses that are only meant to run on one specific computer system.  Coding portably (as discussed in Chapter 3) makes it easy to run the code on other machines.  This can be useful, for example, when one replaces one's laptop, or when one needs to scale their code to run on a high-performance computing system.  It also helps ensure that the code can be tested using automated testing tools, like those discussed in Chapter 4.  


## Computational notebooks

The advent of the Jupyter notebook has fundamentally changed the way that many scientists do their computational work.  By allowing the mixing together of code, text, and graphics, Project Jupyter has taken Donald Knuth's vision of "literate programming"{cite:p}`Knuth:1992aa` and made it available in a powerful way to users of [many supported languages](https://github.com/jupyter/jupyter/wiki/Jupyter-kernels), including Python, R, Julia, and more.  Many scientists now do the majority of their computing within these notebooks or similar literate programming frameworks (such as RMarkdown or Quarto notebooks). Given its popularity and flexibility we will focus on Jupyter, but many of the points raised below extend to other frameworks as well.

The exploding prevalence of Jupyter notebooks is unsurprising, given their many useful features. They match the way that many scientists interactively work to explore and process their data, and provide a way to visualize results next to the code and text that generates them. They also provide an easy way to share results with other researchers. At the same time, they come with some particular software development challenges, which we discuss further below.

### What is a Jupyter notebook?



### Workflows for Jupyter notebook development


### Mixing languages using Jupyter magic


### Using Jupyter notebooks with IDEs

Many users of Jupyter notebooks edit them via the default Jupyter Lab interface within the a web browser. However, other editors (including VSCode and PyCharm) provide support for the editing and execution of Jupyter notebooks.  The main reason that we generally use a standalone editor is that these editors allow seamless integration of AI coding assistants.  While there are tools that attempt to integrate these assistants within the native Jupyter interface, they are at present nowhere near the level of the commercial IDEs like VSCode.  In addition, these IDEs provide easy access to many other essential coding features, such as code formatting and automated linting. 

### Extracting functions from Jupyter notebooks into modules

It's common for users of Jupyter notebooks to define functions within their notebook in order to modularize their code. This is of course a good practice, but suggest that these functions be moved to a module outside of jupyter and imported, rather than being defined within the Jupyter notebook. The reason has to do with the fact that the variables defined in all of the cells within a Jupyter notebook have a global scope.  As we discussed in Chapter Three, global variables are generally frowned upon because they can make it very difficult to debug problems.  In the case of Jupyter notebooks, we have on more than one occasioned been flummoxed by a difficult debugging problem, only to realize that it was due to our use of a global variable within a function.  If a function is defined within the notebook then variables within the global scope are accessible within the function, whereas if a function is imported from another module those global variables are not accessible within the function.  As an example, if we execute the following code within a Jupyter notebook cell:

```
x = 1
def myfunc():
    print(x)

myfunc()
```

the output is 1; this is because the `x` variable is global, and thus is accessible within the function without being passed.  If we instead create a separate python file called 'myfunc2.py' containing the following:

```
def myfunc2():
    print(x)
```

and then import this within our Jupyter notebook:

```
from myfunc2 import myfunc2
x = 1
myfunc2()
```

We will get an error reflecting the fact that x doesn't exist within the scope of the imported function:

```
---------------------------------------------------------------------------
NameError                                 Traceback (most recent call last)
Cell In[9], line 3
      1 from myfunc2 import myfunc2
      2 x = 1
----> 3 myfunc2()

File ~/Dropbox/code/coding_for_science/src/codingforscience/jupyter/myfunc2.py:2, in myfunc2()
      1 def myfunc2():
----> 2     print(x)

NameError: name 'x' is not defined
```

Extracting functions from notebooks into a Python module not only helps prevent problems due to the inadvertent use of global variables; it also makes those functions easier to test.  And as we learned in Chapter XXX, testing is the best way to keep our code base working and to make it easy to change when we need to.  Extracting functions also helps keep the notebook clean and readable, abstracting away the details of the functions and showing primarily the results.

#### Why I avoid autoreload in notebooks


### Version control with Jupyter notebooks

While notebooks have understandably gained wide traction, they also have some important limitations.  Foremost, the structure of the `.ipynb` file makes them problematic for use in version control systems like git. The file itself is stored as a JSON (JavaScript Object Notation) object, which in Python translates into a dictionary.  As an example, we created a very simple notebook and saved it to our computer.  We can open it as a json file, where we see the following contents:

```
{'cells': [{'cell_type': 'markdown',
   'metadata': {},
   'source': ['# Example notebook']},
  {'cell_type': 'code',
   'execution_count': 3,
   'metadata': {},
   'outputs': [],
   'source': ['import numpy as np\n', '\n', 'x = np.random.randn(1)']}],
 'metadata': {'language_info': {'name': 'python'}},
 'nbformat': 4,
 'nbformat_minor': 2}
 ```
 
 You can see that the file includes a section for cells, that in this case can contain either Markdown or Python code. In addition, it contains various metadata elements about the file. One thing you should notice is that each code cell contains an `execution_count` variable, which stores the number of times the cell has been executed.  If we rerun the code in that cell without making any changes and then save the notebook, we will see that the execution count has incremented by one.  We can see this by running `git diff` on this new file after having checked in the previous version:

```
-   "execution_count": 3,
+   "execution_count": 4,
```

This is one of the reasons why we say that notebook files don't work well with version control: simply executing the file without any actual changes will still result in a difference according to git, and these differences can litter the git history, making it very difficult to discern true code differences.  

Another challenge with using Jupyter notebooks alongside version control occurs when the notebook includes images, such as output from plotting commands.  Images in Jupyter notebooks are stored in a serialized text-based format; you can see this by perusing the text of a notebook that includes images, where you will see large sections of seemingly random text, which represent the content of the image converted into text.  If the images change then the `git diff` will be littered with huge sections of this gibberish text.  One could filter these out when viewing the diffs (e.g. using `grep`) but another challenge is that very large images can cause the version control system to become slow and bloated if there are many notebooks with images that change over time.

### Converting notebooks to pure Python

One alternative that we like is to convert our notebooks to pure Python files using the `jupytext` tool.  Jupytext supports several formats that can encode the metadata from a notebook into comments within a python file, allowing direct conversion in both directions between a Jupyter notebook and a pure Python file. We like the `py:percent` format, which places a specific marker (`# %%`) above each cell:

```
# %% [markdown]
# ### Example notebook
#
# This is just a simple example

# %%
import numpy as np
import matplotlib.pyplot as plt
```

These cells can then be version-controlled just as one would with any Python file. To convert a Jupyter notebook to Python, use the jupytext command:

```
❯ jupytext --to py:percent ExampleNotebook1.ipynb
[jupytext] Reading ExampleNotebook1.ipynb in format ipynb
[jupytext] Writing ExampleNotebook1.py in format py:percent

```

which will create a new Python version of the file.  Then set the metadata of the Python file to include ipynb as one of its formats, as this will allow syncing of the files:

```
❯ jupytext --set-formats "py:percent,ipynb" ExampleNotebook1.py
[jupytext] Reading ExampleNotebook1.py in format py
[jupytext] Updating notebook metadata with '{"jupytext": {"formats": "py:percent,ipynb"}}'
[jupytext] Loading ExampleNotebook1.ipynb
[jupytext] Updating ExampleNotebook1.ipynb
[jupytext] Updating ExampleNotebook1.py
```

Then, one can synchronize the Jupyter notebook and Python versions using the command:

```
jupytext --sync notebook.ipynb
```

#### Using jupytext as a pre-commit hook

If one wants to edit code using Jupyter notebooks while still maintaining the advantages of the pure Python format for version control (assuming one is using Git), one option is to apply Jupytext as part of a `pre-commit hook`, which is a git feature that allows commands to be executed automatically prior to the execution of a commit.  This takes advantage of the syncing function described above.  Automatic syncing can be enabled within a git repository by creating a file called `.pre-commit-config.yaml` within the main repository directory, with the [following contents](https://github.com/mwouts/jupytext/blob/v1.9.1/docs/using-pre-commit.md):

```
repos:
  -
    repo: local
    hooks:
      -
        id: jupytext
        name: jupytext
        entry: jupytext --from ipynb --to py:percent --pre-commit
        pass_filenames: false
        language: python
      -
        id: unstage-ipynb
        name: unstage-ipynb
        entry: git reset HEAD **/*.ipynb
        pass_filenames: false
        language: system
```

The first section will automatically run jupytext and generate a pure Python version of the notebook before the commit is completed.  The second section will unstage the `ipynb` files before committing, so that they will not be committed to the git repository (only the Python files will). This will keep the Python and Jupyter notebook files synced while only committing the Python files to the git repository.  


## Python modules

While Python has native access to a small number of functions, much of the functionality of Python comes from *modules*, which provide access to objects defined in separate files that can be imported into a Python session.  All Python users will be familiar with importing functions from standard libraries (such as `os` or `math`) or external packages (such as `numpy` or `pytorch`). It's also possible to create one's own modules simply by putting functions into a file.

Let's say that we have a set of functions that do specific operations on text, saved to a file called `textfuncs.py` in our working directory:

```
def reverse(text):
    return text[::-1]

def capitalize(text):
    return text.capitalize()

def lowercase(text):
    return text.lower()
```

If we wish to use those functions within another script ('mytext.py'), we can simply import the module and then run them:

```
import textfuncs

def main():
    mytext = "Hello World"
    print(mytext)
    print(textfuncs.reverse(mytext))
    print(textfuncs.capitalize(mytext))
    print(textfuncs.lowercase(mytext))

if __name__ == "__main__":
    main()
```

Giving the results:

```
❯ python mytext.py
Hello World
dlroW olleH
Hello world
hello world
```

```{admonition} Antipattern
It's not uncommon to see Python programmers use *wildcard imports*, such as `from mytext import *`.  This practice is an antipattern and should be avoided, because it can make it very difficult to debug problems with imported functions, particularly if there is a wildcard import from more than one module.  It can also result in collisions if two modules have a function with the same name, and can prevent linters from properly analyzing the code.  It's better practice to explicitly import all objects from a module, or to use fully specified paths within the module.

R users might notice that this antipattern is built into the way that library functions are usually imported in R: In general, when one imports a library the functions are made available directly in the global namespace.  For example, if we load the `dplyr` library we will see several errors regarding objects being masked:

````
> library(dplyr)

Attaching package: ‘dplyr’

The following objects are masked from ‘package:stats’:

    filter, lag

The following objects are masked from ‘package:base’:

    intersect, setdiff, setequal, union
````

This means that if we call `filter()` it will now refer to `dplyr::filter()` rather than the default reference to `stats::filter()`.  This can cause major problems when one adds library imports during the development process, since those later additions can mask functions that had worked without disambiguation before.  For this reason, when coding in R it's always good to use the full disambiguated function call for any functions with generic names like "select" or "filter".

```



## Python packages

One of the most attractive features of Python is the immense ecosystem of *packages* that have grown up around it.  For nearly any field of scientific research one can find packages that provide access to specialized functions for that field.  *EXAMPLES?*

### What is a Python package?

### Creating a new Python package

### Submitting a package to PYPI

### Editable packages for local development

- workflow for developing a package using editable package + autoreload



## Containers

- Donoho quote


## Logging

*NOTE:* Not sure where this should actually go but we should talk about it somewhere.  Leaving as a placeholder here for now.