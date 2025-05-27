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
