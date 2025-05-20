# Essential tools and techniques

## The tools and why we use them

We hope that the principles and strategies outlined in this book will transcend any particular software platform or programming language, but for the purposes of explication we will focus on a particular language (Python) and a particular set of tools for software development/engineering and AI coding assistance.  Here we briefly outline our motivation for these particular tools.  

### Why Python?

For the coding examples in this book we will use the Python programming language.  We have chosen Python first and foremost because it is a language that we know well, as well as being one of the most popular languages today in science.  Python is a relatively high level programming language, which means that it can be understandable (if written correctly) even by someone with relatively little experience.  It also free and open source, which means that anyone with a computer can download it and run it at no cost.
In addition, Python is a language that has exceptionally good support from AI coding assistants such as Github Copilot, which has been trained on a huge corpus of Python code (along with code from many other languages as well).  
Python also has a large and growing ecosystem of packages and tools that make it possible to solve many different problems easily.  If you are interested in working on machine learning or AI, the tools in Python are especially good.

Across many different domains of science there are specialized Python packages to solve domain-specific problems: Examples include [astropy](https://www.astropy.org/) (astronomy), [geopandas](https://geopandas.org/en/stable/getting_started/introduction.html) (geospatial sciences), [quantecon](https://quantecon.org/) (economics), [sunpy](https://sunpy.org/) (solar physics), and [psychopy](https://www.psychopy.org/), just to name a few. We should note that different scientific communities have often converged on particular high-level languages. The above are some examples of Python packages, but in some fields the ecosystem is much more elaborated in R, Julia, Perl or Matlab.  We hope that most of the lessons in this book will be relevant to these other languages as well.

If you don't already know Python, then we suggest that you try to follow along with the examples anyway; our aim is to write them in a way that anyone with a general knowledge of programming should be able to read and understand them. In some cases we may use programming constructs that are specific to Python; if you are coming from another language and you see something you don't understand, then we would recommend asking an AI assistant to explain it to you, since current AI tools are very good at explaining the intent of Python code!  As we discuss in Chapter XXX, learning a new programming language is a great way to expand your programming skills, and Python is currently a great language to learn.


## Version control

Scientists in many fields have traditionally kept a *lab notebook* to record their experimentation. This is still the case in domains such as biology where the work often involves manual experimentation at a lab bench. Many such labs have moved to using electronic lab notebooks, making it much easier to search and find relevant information.  However, an increasing amount of scientific work is now computational, and for this work it would seem somewhat inefficient to record information about the software development process separately from the code that is being written.  There is in fact a tool that can provide the computational researcher with an integrated way to record the history their work, known as *version control.*  While there are many tools that can be used to perform version control, [git](https://git-scm.com/) has become by far the most prevalent within the scientific computing ecosystem, largely due to the popularity of the [Github](http://github.com) web site that enables the hosting and sharing of git repositories.  

In this section we will assume that the researcher has a basic knowledge of the `git` software tool; for researchers looking to learn `git`, there are numerous resources online, which we will not duplicate; see the suggested resources at the end of this chapter. Here we will focus on the ways in which version control tools like `git` can serve as important tools to improve scientific coding.  While there are numerous graphical user interfaces (GUIs) for git (including those offered by various IDEs), we will focus on its use via the command line interface (CLI).  Every researcher should have a basic knowledge of the `git` CLI, since there are some operations (such as fixing merge conflicts) that are best done using the CLI.

### How version control works

The goal of a version control system is to provide an annotated history of all changes that occur to the tracked files.  Here we will provide a brief overview of the conceptual structure of version control, using the `git` system as our example.

The general workflow for version control using `git` is as follows:

- Initial check-in: A file is added to the database.
- The file is *modified* by the user, but the changes are not added to the database.
- The file is *added* to the staging area, which tracks the changes in the file and marks the new version to be added to the database.
- The file is *committed*, which stores it in the base along with a *commit message* that describes the changes.

**TODO**: Provide visualizations for git/github concepts?


Here is an example using `git`.  We will create a test directory (outside of our current git repository) and initialize it as a git repository:

```bash
> cd /tmp
> mkdir git-test
> cd git-test
> git init
> echo "test file" > test_file.txt
❯ git status
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	test_file.txt

nothing added to commit but untracked files present (use "git add" to track)

```

So far our new file is not being tracked, but we can add it to the database:

```bash
❯ git add test_file.txt
❯ git status
On branch main

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
	new file:   test_file.txt


```

It's now in the staging area, but hasn't yet been committed to the database, as we can see if we print the log:

```bash
❯ git log
fatal: your current branch 'main' does not have any commits yet

```

We can commit the items in the staging area (in this case, just our single added file) to the database and provide a message that labels the commit:

```bash
❯ git commit -m"initial add"
[main (root-commit) 752ca80] initial add
 1 file changed, 1 insertion(+)
 create mode 100644 test_file.txt
❯ git status
On branch main
nothing to commit, working tree clean
```

Now that all changes have been committed, we are "clean", meaning that the files in the directory match exactly to those in the database.  We can see the commit in the git log:

```bash
> git log
commit 752ca809cd662f846434dcb2c81f3000db640b4e (HEAD -> main)
Author: Russell Poldrack <poldrack@gmail.com>
Date:   Mon Feb 17 07:42:35 2025 -0800

    initial add

```

The long string (starting with "752") is the *hash* for this commit.  This is a value (generated by a cryptographic algorithm called SHA-1) that uniquely represents all of the changes that were made in this commit.  For example, if we had used a different commit message then the hash would be different. The commit hash is the way that we refer to commits - for example, if we wanted to change the state of our repository back to an earlier commit we would use the hash of that earlier commit.  We usually don't need to use the entire hash; the first ~8 letters are usually sufficient.

The most important role for version control is to track changes in a file, along with notes about those changes.  That is, it can serve as a digital version of a lab notebook!  Let's make a change to the file to see this in action:

```bash
❯ echo "another line" >> test_file.txt # add another line of text
> git diff test_file.txt
diff --git a/test_file.txt b/test_file.txt
index 16b14f5..0db3737 100644
--- a/test_file.txt
+++ b/test_file.txt
@@ -1 +1,2 @@
 test file
+another line

```

This provides us with a (somewhat cryptic) description of the changes to the file; the line starting with a "+" denotes the content that was added (in the console this would also be color-coded in green).  We can then add and commit the file and then view the new commit in the log:

```bash
❯ git add test_file.txt
❯ git commit -m"added a second line"
[main 5e8c41a] added a second line
 1 file changed, 1 insertion(+)
❯ git log

commit 5e8c41a075b2ab2d954d59cab6530d924c5e3e6a (HEAD -> main)
Author: Russell Poldrack <poldrack@gmail.com>
Date:   Mon Feb 17 07:56:09 2025 -0800

    added a second line

commit 752ca809cd662f846434dcb2c81f3000db640b4e
Author: Russell Poldrack <poldrack@gmail.com>
Date:   Mon Feb 17 07:42:35 2025 -0800

    initial add
```

Now we can see our latest commit at the top of the list.  If we were to push our repository to GitHub, then we could also see a much more user-friendly graphical view of commit history and the changes that occurred in each commit.  Most IDEs also have an interface to work directly with `git`; for example, within VSCode there is a *Source Control* panel that would allow one to do everything that we did above using the command line.

### Version control as a lab notebook

It is essential for a researcher to keep track of their work as it proceeds, and traditionally this has been done using a written lab notebook.  This has several drawbacks; it's impossible to search easily, and for researchers with terrible handwriting (like author RP) it can often be impossible to later decipher what the notes actually mean.  

:::{figure-md} LabNotebook-fig
<img src="images/lab_notebook_scan.png" alt="Scan of a page from Russ's lab notebook circa 2000." width="400px">

Scan of a page from Russ's lab notebook circa 2000.
:::


### Version control best practices

Version control systems like `git` can serve as an outstanding alternative to a written lab notebook for the computational researcher, but only if it used well.  Here are a few best practices for ensuring good record-keeping:

#### Use a consistent standard format for commit messages

Using a particular format consistently will make it much easier to understand and search your history later on. Here is one simple format that one might use for commit messages:

```
<type>: <summary>

<optional longer description>
```

The *type* tag describes the type of change, which could include tags like *feature*, *bugfix*, *refactor*, *doc*, *test*, and *cleanup*.  

The *summary* should include a brief summary (usually less than 72 characters) that summarizes what was done.  You should avoid using generic or vague summaries such as "update" or "fix bug".  

By `git` convention, commit messages should be written in imperative mood, as if one is giving a command. For example, the message might say "add test for infinite edge case" rather than "added test for infinite edge case".  

Here is a example:

```
refactor: Make crossvalidation function cleaner

The previous function was written in a way that was not clean, using badly named variables and confusing programming constructs.  The new code fixes these issues while still passing all tests.
```

#### Explain intent rather than code

A good commit message should explain what problem was being solved and why the change was necessary, rather than detailing the specific code changes.  The code changes are already evident from the change log, so the message should focus instead on details that are not evident from looking at the code itself.  For example:

```
feature: Enable use of multiple APIs

Previously the function only worked with the OpenAI API.  This change generalizes it to allow any endpoint that follows the OpenAI API conventions.
```


#### A single commit should reflect solution of a particular problem

One of the tricky aspects of learning to use version control is learning when to commit.  One rule of thumb is that a commit should reflect a group of changes that solve a particular problem.  For example, say that we have modified three source files to add the multiple API functionality listed above.  We could on the one hand add and commit the changes from each file separately, leading to three separate commits. This is too granular; if we later decide that we want to roll back those changes (which could be difficult depending on commit messages and our memory), we have to identify the three separate commits and then roll back each one separately.  At the other extreme, it's not uncommon for users to check in all of the work that was done in a day, with a commit message like "all work from Tuesday".  If one were to later decide that part of the work from that day needed to be rolled back, it would require a lot of extra work to isolate just those changes.  The sweet spot for committing is to commit changes that represent a functional bundle, or that solve a particular problem.  Thinking about the commit message can be helpful in considering when to commit; if it's difficult to give a concise functional description to the specific set of changes being committed, then the commit may be either too narrow or too broad. 

#### Avoid blanket add/commit operations

Another common `git` "anti-pattern" (i.e. a commonly used but bad solution to a common problem) is to simply add all files using `git add .` (which adds all files in the current directory, including those that have not been added) or `git add -A` (which does the similar thing recursively for the entire directory tree).  This kind of "blanket add/commit" is problematic for at least two reasons. First, there are often files that we don't want to add to version control, such as files containing credentials or files with details about the local system configuration. While we would usually want to add these files to our `.gitignore` file (which prevents them from being added), it's best practice to explicitly add files that we are working on. A second reason to avoid blanket add/commit is that if we are working on more than one problem at a time, the resulting commit will bundle together files that address different problems and thus prevent writing a clean commit message as well as prevent a clean reversion of that code later. It would also require knowing exactly which files have been added in order to create an accurate commit message. The only time that we can imagine a blanket add/commit being reasonable is when one is initially creating a repository using a large number of files.

A better practice is to explicitly name all files being added, which forces one to think about exactly what problem the commit is solving.  If one is certain that they know exactly which code files have been changed, then a useful alternative can be to only add modified files (using `git add -u`), which can save a bit of time if there are numerous files being added. However, it's important to make sure that the commit message always faithfully reflects the totality of the changes.

### Version control as developer productivity tool

So far we have discussed version control primarily as a way to record the history of software development.  But an arguably even more powerful aspect of version control is the way that it enables developer productivity by allowing one to try our new changes and easily revert to a previous version.  It's useful to first examine how this might be done without version control.  Suppose a developer has a codebase and wants to try out a major change, such as changing the database backend used in the project.  They would usually save a copy of all of the source files (perhaps with a timestamped label), and then start working on the problem.  If at some point they wish to completely abandon the new project, they can always go back to the copy of the original.  But what if they want to abandon the latest part (e.g. a specific database) without necessarily abandoning the rest of the work that it took to get there?  Unless they are saving copies at every step (which quickly becomes a bookkeeping nightmare), this will be very challenging to pull off.  On the other hand, with a solid version control workflow these problems are trivial to solve, because these systems are built exactly in order to solve this bookkeeping problem.


#### Falling back on previous commits

We will start first with a simple example that only involves the `main` branch of the repository; if you don't know what a "branch" is, this would be a good time to seek out your favorite `git` resource and learn about that concept.  Later we will suggest that working directly in the main branch is not optimal, but it's common for many research projects with a single developer so we will start there, fitting with our mantra that we should never let the perfect be the enemy of the good.

Let's say that we wish to try changing out the database backend for our project, which will require changes to several of the source files. Starting with a clean working tree (i.e. no uncommitted changes or untracked files not included in `.gitignore`), we would first create a new tag so that we can easily find the last commit in case we decide that we want to revert back to it:

```bash
git tag v0.2-pre-db-change
```

We then start developing on the new code, committing as usual.  Let's say that we make a few commits on the new code, but then go down a road that we decide to abandon.  It's easy to get back to the last commit simply by typing `git reset --hard HEAD`, which takes the code back to the state it was in at the last commit (known as "HEAD").  In the case that we decide to abandon the entire project and want to go back to the state of the code when we started (which is denoted by the tag we created), we simply need to find the hash for that commit and then check out that version of the repository:

```bash
> git show v0.2-pre-db-change
commit 5e8c41a075b2ab2d954d59cab6530d924c5e3e6a (HEAD -> main, tag: v0.2-pre-db-change, tag: v0.2)
> git checkout 5e8c41a07 .
> git commit -m"""
cleanup: Revert attempted database backend switch

We tried to replace the database backend but realized after some
development that this would not solve our problem, so we are reverting
back to the original code."""

On branch main
nothing to commit, working tree clean
```

A look at the `git log` will now show that the HEAD matches the hash for the tagged commit.

#### Using branches

All `git` repositories start with a single default branch, usually called "main" (or sometimes the previous convention, "master").  While it's possible to develop completely within the main branch of a repository, we generally prefer to use *development branches*, which can be thought of as different versions of the repository.   In our preferred workflow, whenever we want to modify code we first create and then check out a new branch, in which we will do that work.  One great benefit of this is that if the main branch was working when we created the development branch, it will remain in a working state even as we make our changes in the new branch. This provides much greater freedom to try out changes with no concern about breaking existing code, and also allows development to proceed without interfering with production code.

It's important to name branches in way that makes clear what their purpose is.  It is customary to use a prefix that states the general purpose of the branch; common prefixes including "feature/" (for new features), "bugfix/" (for bug fixes), "release/" (for a new package release), "docs/" (for documentation changes), and "test/" (for testing-related changes).  The prefix should be followed by a description of the purpose of the branch.  For example, for our example above we might use "feature/swap-db-backend". 

We can create a new branch and check it out (making it the current branch) using `git checkout`:

```bash
> git branch
* main
❯ git checkout -b feature/swap-db-backend
Switched to a new branch 'feature/swap-db-backend'
> git branch
* feature/swap-db-backend
  main
```

We can now go about our development work, committing as usual to the branch.  If we were to later decide to abandon the new branch, we simply check out the main branch, and we are right back where we left off before creating the new branch.  We could either delete the feature branch (to keep the repository clean), or keep it around in case we wish to go back later and look at it again.

### Collaborative development using Github

While git is very useful for the individual developer, it becomes even more powerful when used for collaborative development amongst a group of developers.  For `git` users this is enabled by the popular [Github](http://github.com) web platform for version control.  We will assume a basic familiarity with the use of Github: see the Suggested Resources at the end of the chapter for resources to learn how to use Github.

Collaborative development requires choosing a workflow that the team will adhere to; a commonly used workflow for Github users is the [Github flow](https://docs.github.com/en/get-started/using-github/github-flow), which goes as follows.  Let's say that we have two developers on our team, and one of them wants to attempt the database backend project that we described above.  The process would be:

1. The developer creates a branch within the repo, giving it a a clear and expressive name such as "feature/swap-db-backend". They develop their code within this branch.  
2. If the user doesn't have write access to the repo, they first create a *fork* of the repo, which copies it to their own account and thus allows write access.
3. Once the feature is complete, they commit and push all of their changes to the repository on Github.  
4. They then create a *pull request*, which requests that the code in their branch be merged into the main branch of the primary repository.
5. Another developer on the team reviews the pull request, and provides comments suggesting changes to the code.
6. Once the reviewer's comments are addressed, the code from the branch is merged into the main branch, so that the changes are now incorporated there.
7. After merging, the branch is deleted to keep the repository clean.

This type of collaborative development process powers many of the large open source projects that are commonly used today, but can be equally transformative for small groups such as a individual research lab.

