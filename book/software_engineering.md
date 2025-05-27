# Principles of software engineering

Just as mechanical engineering is the science of building physical things like airports or engines, software engineering is the science of building software.  Its goal is to identify the principles and practices that allow building of software that is robust, efficient, and maintainable.  Just as a person can build a table at home without any formal knowledge of mechanical engineering, one can build software without knowing any of the principles of software engineering. However, this software is likely to suffer from exactly the same kinds of instability and poor functionality as the average homemade table.  Knowing a few basic ideas from software engineering can help scientists build software more effectively and generate outputs that will be more robust and maintainable over time.

We have already talked about some of the basic tools of software engineering, such as version control. In this chapter we will focus on some of the "big ideas" from software engineering, highlighting how their adoption can improve the life of nearly anyone who develops software.  

## Why software engineering matters in the age of AI-assisted coding

One might ask why we are spending an entire chapter talking about software engineering; when it's likely that AI tools going to write much of the code in our projects going forward.  First, think back to the point we made in Chapter 1: Programming is not equivalent to writing code.  Even if the AI system can write computer code (e.g. in Python), a human needs to describe the problem(s) that the software is meant to solve, and to iterate with the code to debug any failures to solve the problem.  This requires that a human write the specification that tells the computer how to solve the problem: we may have traded Python for English as the programming language of choice, but nonetheless the human needs to precisely specify the goals of the software.  Thus, an understanding of the software development process will remain essential even as AI assistants write an increasing amount of code.  

Software development processes may be less important for small one-off projects written by a single developer, but they become essential once a project becomes large and involves multiple developers.  Coordination costs can quickly eat into the added benefit of more developers on a project, particularly if there is not a strong development process in place.  And writing good, clean code is essential to help bring new developers into a project; otherwise, the startup costs for a developer to get their head around a poorly engineering codebase can just be too large.  Similarly, poorly written code can result in a high "bus factor" (i.e., what happens if your lead developer gets hit by a bus?), which can be major risk for groups that rely heavily upon a particular software project for their work.


## Agile development processes

When I was in graduate school, I spent countless hours developing a tool for analyzing data that was general enough to process not just the data that I needed to analyze for his project, but also nearly any other kind of data that one might envision from similar experiments.  How many of those other kinds of data did I ever actually analyze?  You guessed it: Zilch.  There is an admirable tendency amongst some scientists to want to solve a problem in a maximally general way, but this problem is not limited to scientists. In fact, it has a name within software circles: "gold plating".  Unfortunately, humans are generally bad at predicting what is actually needed to solve a problem, and the extra work spent adding gold plating might be fun for the developer but rarely pays off in the longer term.  Software engineers love acronyms, and a commonly used acronym that targets this kind of overengineering is YAGNI: "You Aren't Gonna Need It".  

Within commercial software engineering, it was once common to develop a detailed requirements document before one ever started writing code, and then move on to code writing using those fixed requirements.  This is known as the "waterfall" method for project management; it can work well in some domains (like physical construction, where the plans can't change halfway through building, and the materials need to be on hand before construction starts), but in software development it often led to long delays that occurred once the initial plan ran into challenges at the coding phase.  Instead, most software development projects now use methods generally referred to as *Agile*, in which there are much faster cycles between planning and development. One of the most important [principles](https://agilemanifesto.org/principles.html) of the Agile movement is that "Working software is the primary measure of progress.".  It's worth noting that a lot of dogma has grown up around Agile and related software development methodologies (such as *Scrum* and *Kanban*), most of which is overkill for scientists producing code for research.  But there are nonetheless some very useful concepts and processes that we can take from these methodologies to help us build scientific software better and faster.

In our laboratory, we focus heavily on the idea of the "minimum viable product" (MVP) that grows out of the Agile philosophy.  We shoot for code that solves the scientific or technical problem at hand: no more, and no less.  We try to write that code as cleanly as possible (as described in the next section), but we realize that the code will never be perfect, and that's ok.  If it's code that will be reused in the future, then we will likely spend some additional time refactoring it to improve its clarity and robustness and providing additional documentation.  This philosophy is the rationale for the "test-driven development" approach that we outline later in this chapter.

## Designing software through user stories

It's important to think through the ways that a piece of software will be used, and one useful way to address this is through *user stories*.  Understanding specific use cases for the software from the standpoint of users can be very useful in helping to ensure that the software is actually solving real problems, rather than solving problems that might theoretically exist but that no user will ever engage with.  We often see this with the development of visualization tools, where the developer thinks that a visualization feature would be "cool" but it doesn't actually solve a real scientific problem for a user of the software.

A user story is often framed in the following way: "As a [type of user], I want [a particular functionality] so that [what problem the functionality will solve]". 
As an example, say that a researcher wanted to develop a tool to convert between different genomic data formats. A couple of potential user stories for this software could be:

- "As a user of the ABC123 sequencer, I want to convert my raw data to the current version of the SuperMegaFormat, so that I can submit my data to the OmniData Repository."
- "As a user of software that that requires my data to be in a specific version of the SuperMegaFormat, I want to validate that my data have been properly converted to comply with that version of the format so that I can ensure that my data can be analyzed."

These two stories already point to several functions that need to be implemented:

- The code needs to be able to access specific versions of the SuperMegaFormat, including the current version and older versions.
- The code needs to be able to read data from the ABC123 sequencer.
- The code needs to be able to validate that a dataset meets any particular version of the SuperMegaFormat.

User stories are also useful for thinking through the potential impact of new features that are envisioned by the coder.  Perhaps the most common example of violations of YAGNI comes about in the development of visualization tools.  In this example, the developer might decide to create an visualizer to show how the original dataset is being converted into the new format, with interactive features that would allow the user to view features of individual files.  The question that you should always ask yourself is: What user stories would this feature address?  If it's difficult to come up with stories that make clear how the feature would help solve particular problems for users, then the feature is probably not needed. "If you build it, they will come" might work in baseball, but it rarely works in scientific software. This is the reason that one of us (RP) regularly tells his trainees to post a note in their workspace with one simple mantra: "MVP".


## Refactoring code

Throughout our discussion we will regularly mention the concept of *refactoring* (as we just did in the previous section), so we should introduce it here.  When we refactor a piece of code, we modify it in a way that doesn't change its external behavior. The idea long existed in software development but was made prominent by Martin Fowler in his book *Refactoring: Improving the Design of Existing Code*.  As the title suggests, the goal of refactoring is to improve existing code rather than adding features or fixing bugs - but why would we spend time modifying code once it's working, unless our goal is to add something new or fix something that is broken?    

In fact, the idea of refactoring is closely aligned with the Agile development philosophy mentioned above.  Rather than designing a software product in detail before coding, we can instead design as we go, understanding that this is just a first pass.  As Fowler says:

> "With refactoring, we can take a bad, even chaotic, design and rework it into well-structured code. Each step is simple — even simplistic. I move a field from one class to another, pull some code out of a method to make it into its own method, or push some code up or down a hierarchy. Yet the cumulative effect of these small changes can radically improve the design." - Fowler (p. xiv)

There are several reasons why we might want to refactor existing code.  Most importantly, we may want to make the code *easier to maintain*.  This in turn often implies making it easier to read and understand, as we discuss further below in the context of *clean coding*.  For example, we might want to break a large function out into several smaller functions so that the logical structure of the code is clearer from the code itself. Making code easier to understand and maintain also helps make it easier to add features to in the future. There are many other ways in which one can improve code, which are the focus of Fowler's book; we will outline more of them below when we turn later to the problem of "code smells".

It is increasingly possible to use AI tools to refactor code. As long as one has a solid testing program in place, this can help save time and also help learn how to refactor code more effectively. This suggests that testing needs to be a central part of our coding process, which is why we will devote an entire chapter to it later in the book.


## Test-driven development

Let's say that you have a software project you want to undertake, and you have in mind what the Minimum Viable Product would be: A script that takes in a dataset and transforms the data into a standardized format that can be uploaded to a particular data repository.  How would you get started?  And how would you know when you are done?  

After decomposing the problem into its components, many coders would simply start writing code to implement each of the components.  For example, one might start by creating a script with comments that describe each of the needed components:

```
# Step 1: index the data files

# Step 2: load the files

# Step 3: reformat the metadata to match the repository standard

# Step 4: combine the data and metadata

# Step 5: save the data to the required format
```

A sensible way to get started would be march through the steps and write a function to accomplish each one, and then test the entire package once all of the functions are created.  However, this approach has a couple of drawbacks.  First, since you can't run the application until all of the code is written, you can't know whether each component is working properly until the entire package is built.  Second, it's easy to end up writing code that will end up not needing, since you haven't specified exactly what the inputs and outputs are for each component.  Finally, once you start integrating all of the components, you won't have a way to know if you have introduced a bug.  

One answer to these problems is to start the process by creating a set of *tests*, which tell us whether the code has solved our intended problems.  The process of writing tests before writing code to solve the problem is known as *test-driven development* (TDD), and we think that it is a very useful framework to use when writing scientific code, especially if one plans to use LLMs for code generation.  Test-driven development is somewhat controversial within the software engineering field, in part because many people take it too far and become obsessive with testing, such that the tests come to be the tail that wags the dog; in particular we would caution against using the amount of test coverage as a metric for success. But we think that when it is used in a thoughtful way, TDD can be a powerful way to increase the effectiveness and accuracy of one's code.

We will dive deeply into testing in a later chapter; here we will simply outline a simple test-driven development workflow for the data transformation problem described above.  The TDD workflow can be summarized in a cycle involving three steps:

- *Red*: Create a test that initially fails for the intended function.
- *Green*: Create a function that passes the test.
- *Refactor*: Modify the code to make it more maintainable, readable, and robust

These processes are then repeated until the software solves the intended problem. This process helps prevent the developer from writing code to solve problems that don't exist yet, since the only aim is to create code that passes the specific test in question.  


## Clean coding

> "Any fool can write code that a computer can understand. Good programmers write code that humans can understand."  Fowler (p. 10)

Another idea that has emerged from the Agile community is *clean coding*, which is the idea that code should be simple, readable, and easily maintainable.  This idea was codified in the book titled *Clean Code: A Handbook of Agile Software Craftsmanship*, published in 2008 by Robert C. Martin (known in the community as "Uncle Bob"). One of the best ways to describe clean code is that it is *simple*.  Kent Beck, another Agile founder who developed the idea of "Extreme Programming", laid out a set of rules for simple code:

1. The code has tests and all of the tests run.
2. The code contains no duplication.
3. The code makes the design of the system clear
4. The code minimizes the number of entities (such as functions or classes).

Another way to think about clean code is that it makes it as easy as possible for another programmer to come in later and change it.  And it's essential to remember that this "other programmer" is mostly like to refer to future you!  When we look back at code that we wrote more than a few months ago, we are likely to remember very little of it, meaning that we need to rediscover the design and structure of the code.

There are many different interpretations of the concept of clean code. Here we will lay out the principles that we think are most important for the creation of code in the context of scientific research (as opposed to commercial software development).  Fortunately, the code generated by AI coding assistants is often quite clean, as we found in our analyses of code generated by GPT-4 {cite:p}`Poldrack:2023aa`.  But as we work alongside these assistants, it's important to develop a mindset of continuous improvement, always seeking to make the code cleaner and simpler whenever we can.

### Readability

An excellent test for whether code is clean is whether it is *readable*.  In fact, one of the 19 guiding principles of the Python language, enshrined in [The Zen of Python](https://peps.python.org/pep-0020/), is "Readability counts", reflecting the judgment by Python founder Guido van Rossum that ["code is read much more often than it is written"](https://peps.python.org/pep-0008/).  

#### Naming things well

The book ["Naming Things"](https://leanpub.com/naming-things) by Tom Benner is subtitled "The Hardest Problem in Software Engineering", which might sound hyperbolic but really can turn out to be true once you start trying to come up with good names as you program. Benner provides a summary on his blog of what he calls ["The 7 principles of naming"](https://www.namingthings.co/naming-things-principles), a subset of which we detail here. However, we highly recommend the book for much more detail on how to follow each of the principles.  It's particularly important to point out that these different principles may sometimes clash with one another, requiring the judgment of the developer to determine the best name to use.

##### Consistency

> "Each concept should be represented by a single, unique name."

The use of different names for the same concept can lead the reader to assume that there are two different concepts at play, often known as a "[jangle fallacy](https://en.wikipedia.org/wiki/Jingle-jangle_fallacies)".  This might occur when a similar concept appears across multiple functions, but is named differently; for example, a variable referring to a specific model is called `modelname` in one function and `llm_label` in another.  

Conversely, using the same name to represent two different concepts can lead the reader to think that they are referring to the same thing, which is called a "jingle fallacy." For example, if one were to use the variable name `model` to refer to a model class within one function but to a string containing the model name in another function.  This fallacy is particularly likely to occur when one uses names that are too simple (see below).

##### Understandability

> "A name should describe the concept it represents."

The reader should be able to accurately infer from the name what is being represented.  This implies the common proscription against single-letter variable names, except in cases where the context makes very clear what its function is (e.g. as a counter in a compact loop).  More generally, when creating a variable name it's worth thinking about what kind of confusion might occur, and also who the intended audiences are. For example, it can be particularly useful to select terms that are common within the relevant scientific domain when available.  Other important guidelines for understandability are using the right pluralization (e.g. a variable with a pluralized name should contain more than one thing, and vice versa for variables with a single name) and the right part of speech (for example, functions should generally use verbs while variables and classes should generally use nouns). 

##### Specificity

> "A name shouldn’t be overly vague or overly specific."

One should avoid very generic names such as "object" or "request".  In addition, the name of a function should highlight its intended use, rather than details about the implementation.  For example, say that we develop a function that uses a fast Fourier transform to perform bandpass filtering a timeseries.  A name like `filter_timeseries_bandpass` focuses on the intended use, whereas a name like `fft_timeseries` would highlight the implementation details without specifying what the function is meant to do.

##### Brevity

> "A name should be neither overly short nor overly long."

Most coders tend to err on the side of variables names that are too short, with single-letter names being epitome of this.  One useful concept from Martin's *Clean Code* is that the length of a variable name should be related to the scope of the variable.  When a single-letter variable name is used in the context of a very compact loop, its meaning will be immediately obvious.  However, as a variable is used across a broader scope, using a more detailed name will allow the reader to understand the variable without having to look back at where it was previously used to understand its meaning. We would generally suggest to err on the side of using names that are too long versus too short, since the cost to typing longer names is reduced by the autocompletion features present in modern IDEs.

##### Pronounceability

> "A name should be easy to use in common speech."

Pronounceability is primarily important for cognitive reasons: We are much more likely to remember things that are meaningful to us compared to things that don't have obvious meaning.  In addition, an unpronounceable name makes communicating about the object with others (e.g. in a code review) very difficult.  So while `bfufftots` might seem like a clever acronym for "bandpass filter using FFT on time series", `filter_timeseries_bandpass` is probably more effective and will certainly be clearer to readers.

##### Austerity

> "A name should not be clever or rely on temporary concepts."

Programmers often like to use humorous or clever object names.  For example, a function that marks a directory for later deletion might be called `terminator()` (riffing on Schwarzenegger's "I'll be back".)  As clever as this might seem, it's not useful for anyone who doesn't have the same cultural context.  Object names should be boring and matter-of-fact to ensure that they are as widely understandable as possible.

#### Using empty space properly

Another important aspect of readability is the judicious use of empty space.  While users of other languages sometimes revolt at the fact that empty space plays a syntactic role in Python, we actually view this is a very useful feature of the language, because it enhances the readability of code.  For example, the following code is perfectly legitimate in R, but inferring its structure from a quick glance is difficult:

```R
trans_levels <- list(); for (gene in genes) {snps <- get_snps(gene, 
  .001)
  trans_levels[[gene]] <- 
get_transcript_level(gene, snps)}; phenotype <- get_phen(gene, trans_levels[[gene]])
```

On the other hand, the syntactic role of horizontal empty space in Python enforces much clearer visual structure:

```python
trans_levels = {}
for gene in genes:
    snps = get_snps(gene, .001)
    trans_levels[gene] = get_transcript_level(gene, snps)
phenotype <- get_phen(gene, trans_levels[gene])
```

It is also important to use vertical empty space to separate conceptually distinct sections of code.  In this case, this helps make more visually apparent the fact that there is likely an error in the code, with the `gene` variable that indexes the loop being used outside of the loop.  

Vertical empty space also plays a role in readability, by helping to distinguish conceptually or logically related section of code. At the same time, it's important to not overuse vertical white space; our ability to understand code that we can see at once is much better than understanding code that spreads across multiple screen pages (which requires holding information in working memory), so it's important to use vertical empty space judiciously. 

#### Commenting code

There are few topics where the common understanding differs so much from expert consensus as in the use of comments within code.  For many programmers, the term "documentation" is largely synonymous with code comments, and it is common to hear novice programmers complaining about the need to add comments to their code before releasing it.  On the other hand, one of the most consistent messages from the software engineering literature is that comments are far too often used as a "magic balm" over bad code:

- "Don’t comment bad code — rewrite it" (Kernighan & Plaugher)
- "Clear and expressive code with few comments is far superior to cluttered and complex code with lots of comments"”" (Robert Martin, Clean Code)
- "comments aren’t a bad smell; indeed they are a sweet smell. The reason we mention comments here is that comments are often used as a deodorant. It’s surprising how often you look at thickly commented code and notice that the comments are there because the code is bad." (Fowler, Refactoring)

The overall goal of code comments should be to help the reader know as much as the writer knows about the code.  We will start by outlining the kinds of things that do *not* warrant comments, and then turn to the legitimate uses of comments.

##### What not to comment

###### Ugly or indecipherable code

Rather that adding comments, one should instead refactor so that the code is understandable.

```python
# function to create a random normal variate
# takes mean and SD as arguments
def crv(a=0, b=1):
    u = [random.random() for i in range(2)]
    z = math.sqrt(-2 * math.log(u[0])) * \
        math.cos(2 * math.pi * u[1])
    return a + b * z
```

• instead, use understandable names:

```python
def random_normal_variate(mean=0, stddev=1):
    unif = [random.random() for i in range(2)]
    box_mueller_z0 = math.sqrt(-2 * math.log(unif[0])) * \
        math.cos(2 * math.pi * unif[1])
    return mean + stddev * box_mueller_z0
```

In this case, we don't need a comment to explain the function because its name and the names of its arguments make clear what its function is and how to use it.  By using the variable name `box_mueller_z0` we also make clear what algorithm this computation reflects (the Box-Mueller transform).

###### The obvious

Anything that is clear from the structure of the code or the names of the variables doesn't need to be commented.  Here are some examples of unnecessary comments:

```python
# looping over states
for state_index, state in enumerate(states):
    ...

# function to create a random normal variate
def create_random_normal_variate(mean, sd):
    ...
```

In general one should assume that the reader of code has a good understanding of the language, such that they could understand that first example involves a loop over states.  An exception to this rule is when one is writing code for educational purposes; in that case, one might want to include comments that are more didactic even though they would cause clutter for an experienced programmer.


###### Historical information

Rather than including historical notes about the code:

```python
# RP changed on 2/22/2025 to include sd argument
def random_normal_variate(mean=0, stddev=1):
    ...
```

One should instead use a version control to track changes.

```bash
git commit -m"feature: added std dev argument to random_normal_variate"
```

It's then possible to see who is responsible for each line in a particular source file using the `git blame` function:

```bash
> git blame random_numbers.py
^e14a07d (Russell Poldrack 2025-02-22 07:54:37 -0800 1) import random
^e14a07d (Russell Poldrack 2025-02-22 07:54:37 -0800 2) import math
^e14a07d (Russell Poldrack 2025-02-22 07:54:37 -0800 3)
73cee79c (Russell Poldrack 2025-02-22 07:55:19 -0800 4) def random_normal_variate(mean=0, stddev=1):
^e14a07d (Russell Poldrack 2025-02-22 07:54:37 -0800 5)     unif = [random.random() for i in range(2)]
^e14a07d (Russell Poldrack 2025-02-22 07:54:37 -0800 6)     box_mueller_z0 = math.sqrt(-2 * math.log(unif[0])) * \
^e14a07d (Russell Poldrack 2025-02-22 07:54:37 -0800 7)         math.cos(2 * math.pi * unif[1])
73cee79c (Russell Poldrack 2025-02-22 07:55:19 -0800 8)     return mean +  stddev * box_mueller_z0
```

##### What to comment

###### Intention (aka “Director's Commentary”)

Comments should help the reader understand important design choices that would not be evident from simply reading the code.  For example:

```python
# using a numpy array here rather than
# a pandas DataFrame for performance reasons
```

**TODO**: More examples here

###### Known flaws or TODO items

It's often the case that there are remaining known issues with code that the developer has not yet had the time to address.  These should be noted with a consistent heading (e.g. "TODO") so that they can be easily searched for.  For example:

```python
# TODO: Current algorithm is very inefficient
# - should parallelize to improve performance
```

###### Comments on constant values

When including constant values, it can be useful to describe the motivation for the specific value chosen.

```python
# Using 500 bootstrap replicates based on recommendation 
# from Efron & Tibshirani 1993
n_replicates = 500
```


### Avoiding "code smells" and "anti-patterns"

There are two related concepts that are used to describe the appearance of potentially problematic code  The “anti-pattern” is a riff on the concept of a *design pattern*, which is a recommended solution (i.e. a "best practice") for a common programming problem {cite:p}`Gamma:1995aa`.  An anti-pattern is conversely a commonly used but bad solution (i.e. a "worst practice") for a common programming problem. In the Python world these are well known from the [The Little Book of Python Anti-Patterns](https://docs.quantifiedcode.com/python-anti-patterns/), which lays out many different anti-patterns common in Python coding.  The second idea, that of the "code smell", has been popularized by Martin Fowler in his well-known book *Refactoring: Improving The Design of Existing Code*{cite:p}`Fowler:1999aa`. Just as a bad smell from food can give us an intuitive sense that the good might be spoiled, code smells are intuitive reactions to code that suggest that there might be a problem that could be a target for refactoring.  

Here we outline several bad smells and anti-patterns commonly found in our experience with scientific code.

#### Duplicated code

One of the most common smells in scientific code is the use of repeated blocks of duplicated code with only minor changes.  For example:

```python
# Compute mean response time separately for each test (bad practice)
mean_rt_1 = stroop_data['ResponseTime'].mean()
mean_rt_2 = flanker_data['RT'].mean()
mean_rt_3 = nback_data['RespTime'].mean()
grand_mean_rt = np.mean([mean_rt_1, mean_rt_2, mean_rt_3])
```

This code might work, but it violates the commonly stated principle of "Don't Repeat Yourself" (DRY), and is problematic for several reasons.  First, any changes to the intended operation (in this case computing the mean of the 'ResponseTime' variable in the data frame) would require making changes on multiple lines. In this example the lines are close to one another so it would be easy to see that they all need to be changed, but if they were separated by many other others then one would need to be sure to make the change in each place.  Second, imagine that we wanted to include an additional task in the dataset; we would need to add a new line to compute the mean for the added condition, and also would need to remember to add it to the computation of the grand mean.  Third, an especially strong code smell is the use of numbers as part of variable names, rather than using a data structure such as a dictionary or data frame that inherently represents the data within a single iterable object.  Let's say that we decided to remove the flanker task from our dataset; we would then need to remember to remove `mean_rt_2` from the grand mean computation, which would require working memory if those two lines were to become separated by other code.

Here is a refactored version of the code that:

- extracts the task names and associated data frame column names for the response time variable for each into a dictionary
- creates a function that returns the mean of a given column in the data frame.  Its naming as "get_mean_response_time" will help the reader understand that "rt" refers to "response time" in the rest of the code (which is obvious to domain experts but not necessarily to others reading the code).
- loops through the dictionary elements and applies the function to the relevant column, saving them to a dictionary
- computes the grand mean using the values from the dictionary created from each dataset

```python
    rt_column_names = {
        'stroop': 'ResponseTime',
        'flanker': 'RT',
        'nback': 'RespTime'
    }

    def get_mean_response_time(testdata, column_name):
        return testdata[column_name].mean()

    mean_rt = {}
    for test, column_name in rt_column_names.items():
        mean_rt[test] = get_mean_response_time(
            data[test],
            column_name)

    grand_mean_rt = np.mean(list(mean_rt.values()))
```

This refactoring has more lines of code than the original, but it will be much easier to understand, to maintain, and to modify.  Also note the use of vertical empty space to highlight the distinct logical components of the code.

#### Magic numbers

A *magic number* is a number that is included in code directly rather than via assignment to a variable  For example:

```python
def proportion_significant(data):
    return np.mean(data > 3.09)
```

What does "3.09" refer to? A statistically literate reader might infer that this was meant to refer to the 99.9th percentile of the standard normal (Z) distribution, but couldn't be certain without talking to the developer. Another particular problem with floating point magic numbers is that they often are rounded (i.e. 3.09 rather than 3.090232306167813), which could lead to imprecision in the results in some contexts.   An additional problem with this particular function is that the value can't be changed by the user of the function.  It would be better compute the value formally based on an explicit input of the probability, and then assign it to a named variable that makes clear what it means:

```python
def proportion_exceeding_threshold(data, p_threshold=.001):
    z_cutoff = scipy.stats.norm.ppf(1 - p_threshold)
    return np.mean(data > z_cutoff)
```

#### Long parameter lists

A long list of parameters in a function definition can be confusing for users. One way that Python coders sometimes get around specifying long parameter lists is the use of the `**kwargs` argument, which allows the specification of arbitrary keyword arguments to a function, placing them within a dictionary.  For example:

```python
In [36]: def myfunc(**kwargs):
            print(kwargs)

In [37]: myfunc(myarg=1, mybool=True)
{'myarg': 1, 'mybool': True}
```

This can be useful in specific cases, but in general should be avoided if possible, as it makes the code less clear and allows for potential type errors.

A useful solution when one needs to pass a large number of named parameters is to create a *configuration object* that contains all of these parameters. This can be easily accomplished using *dataclasses* within Python, which are specialized classes meant to easily store data.  Here is an example of a function call with a number of parameters:

```python

def run_llm_prompt(prompt, model='gpt4', random_seed=None, stream=True,
                   temperature=0.7, max_tokens=256, verbose=False,
                   system_prompt=None, max_response_length=None):
    ...

```

We could instead first create a configuration class that allows us to define all of the optional parameters:

*TODO*: DO WE ACTUALLY WANT TO USE TYPE HINTS THROUGHOUT?  IF SO, WE PROBABLY NEED TO INTRODUCE THEM EARLIER

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class LLMConfig:
    model: str = 'gpt4'
    random_seed: Optional[int] = None
    stream: bool = True
    temperature: float = 0.7
    max_tokens: int = 256
    verbose: bool = False
    system_prompt: Optional[str] = None
    max_response_length: Optional[int] = None

def run_llm_prompt(prompt, config):
    ...

# we could then use it like this, first setting any optional 
config = LLMConfig(
    temperature=0.8,
)
run_llm_prompt(config)
```

#### Loops

- Loops aren't always a bad smell, but in the context of data processing, one can almost always use a vectorized operation.


#### Wild-card imports

This is a Python-specific anti-pattern that is commonly seen in software written by researchers.  

