## for Intro

- discuss Naur, "Programming as theory building"

## for essentials

- discuss databases - e.g. sqlite example


## from AI-assisted coding chapter

## github spec kit

## More on MCP?

## AI-human pair programming

We often view AI coding agents as autonomous 

## Leveraging LLM coding for reproducibility

LLM-based chatbots can be very useful for solving many problems beyond coding.  For example, we recently worked on a paper with more than 100 authors, and needed to harmonize the affiliation listings across authors.  This would have been immensely tedious for a human, but working with an LLM we were able to solve the problem with only a few manual changes needed.  Other examples where we have used LLMs in the research process include data reformatting and summarization of text for meta-analyses.  However, as noted above, the use of chatbots in scientific research is challenging from the standpoint of reproducibility, since it is generally impossible to guarantee the ability to reproduce an LLM output; even if the random seed is fixed, the commercial models change regularly, without the ability to go back to a specific model version.  

The ability to LLMs to write code to solve problems provides a solution to the reproducibility challenge: instead of simply using a chatbot to solve a problem, ask the chatbot to generate code to solve the problem, which makes the result testable and reproducible.  This is also a way to solve problems with information that you don't want to submit to the LLM for privacy reasons.

For example, ...

# Project structure


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

### Creating a Python module using uv

