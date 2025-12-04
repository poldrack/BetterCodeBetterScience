# Optimizing performance

## Avoiding premature optimization

> The real problem is that programmers have spent far too much time worrying about efficiency in the wrong places and at the wrong times; premature optimization is the root of all evil (or at least most of it) in programming. - Donald Knuth

- often it takes less time to throw more compute at the problem than it does to optimize the code.  

## Tradeoffs in code optimization

In their book *The Elements of Programming Style*, {cite:t}`Kernighan:1978aa` proposed a set of organizing principles for optimization of existing code, which highlight the tradeoffs involved in optimization:

- "Make it right before you make it faster"
- "Make it clear before you make it faster"
- "Keep it right when you make it faster"

That is, there is a tradeoff between accuracy, clarity, and speed that one must navigate when optimizing code.  

## A brief introduction to computational complexity


## Code profiling

- execution profiling
    -line_profiler

- Memory management
    - memory profiling

## Common sources of slow code execution

### Slow algorithm

A common source of slow execution is use of an inefficient algorithm.  Let's say that we want to find duplicate elements within a list.  A simple way to implement this could be perform nested loops to compare each item to each other.  This has computational complexity of *O(n^2)*.  

```python
import random
def create_random_list(n):
    return [random.randint(1, n) for i in range(n)]

def find_duplicates_slow(lst):
    duplicates = []
    for i in range(len(lst)):
        for j in range(i+1, len(lst)):
            if lst[i] == lst[j] and lst[i] not in duplicates:
                duplicates.append(lst[i])
    return duplicates

lst = create_random_list(10000)

%timeit find_duplicates_slow(lst)

833 ms ± 5.85 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
```

We can speed this up substantially by using a dictionary and keeping track of how many times each item appears.  This only requires a single loop, giving it a time complexity of O(n).

```python
def find_duplicates_fast(lst):
    seen = {}
    duplicates = []
    for item in lst:
        if item in seen:
            if seen[item] == 1:
                duplicates.append(item)
            seen[item] += 1
        else:
            seen[item] = 1
    return duplicates

%timeit find_duplicates_fast(lst)

446 μs ± 1.06 μs per loop (mean ± std. dev. of 7 runs, 1,000 loops each)
```

Notice that the first results are reported in milliseconds and the second in microseconds: That's a speedup of almost 1900X for our better algorithm!  We could do even better by using the built-in Python `Counter` object:

```python
from collections import Counter

def find_duplicates_counter(lst):
    duplicates = [item for item, count in Counter(lst).items() if count > 1]
    return duplicates

%timeit find_duplicates_counter(lst)

327 μs ± 2 μs per loop (mean ± std. dev. of 7 runs, 1,000 loops each)

```

That's about a 36% speedup, which is much less than we got moving from our poor algorithm to the better one, but it could be signficant if working with big data, and it also makes for cleaner code.  In general, built-in functions will be faster than hand-written ones as well as being better-tested, so it's always a good idea to use an existing solution if it exists.  Fortunately AI assistants are quite good at recommending optimized versions of code.


### Slow operations in Pandas

Many researchers use Pandas because of its powerful data manipulation methods, but some of its operations are notoriously slow.  Here we show an example of how incrementally inserting data into an existing data frame can be remarkably slower than using standard python objects and then converting them to a Pandas data frame in a single step:

```python
import pandas as pd 
import numpy as np
import timeit

# generate some random data
nrows, ncolumns = 1000, 100
rng = np.random.default_rng(seed=42)
random_data = rng.random((nrows, ncolumns))

# slow way to fill the data frame
def fill_df_slow(random_data):
    nrows, ncolumns = random_data.shape
    columns = ['column_' + str(i) for i in range(ncolumns)]
    df = pd.DataFrame(columns=columns)

    for i in range(nrows):
        df.loc[i] = random_data[i, :]
    return df

%timeit fill_df_slow(random_data)

121 ms ± 418 μs per loop (mean ± std. dev. of 7 runs, 10 loops each)
```

We can compare this to a function that also loops through each row of data, but instead of adding the data to a data frame it adds them to a dictionary, and then converts the dictionary to a data frame:

```python
# fill df by creating a dictionary using a dict comprehension and then converting it to a data frame
def fill_df_fast(random_data):
    nrows, ncolumns = random_data.shape
    columns = ['column_' + str(i) for i in range(ncolumns)]
    df = pd.DataFrame({columns[j]: random_data[:, j] for j in range(ncolumns)})
    return df

%timeit fill_df_fast(random_data)

255 μs ± 885 ns per loop (mean ± std. dev. of 7 runs, 1,000 loops each)
```

Again notice the difference in units between the two measurement.  This method gives us an almost 500X speedup!  We can make it even faster by directly passing the numpy array into pandas:

```python
# fill df by creating a dictionary and then converting it to a data frame
def fill_df_superfast(random_data):
    nrows, ncolumns = random_data.shape
    columns = ['column_' + str(i) for i in range(ncolumns)]
    df = pd.DataFrame(random_data, columns=columns)
    return df

%timeit fill_df_superfast(random_data)

18.7 μs ± 279 ns per loop (mean ± std. dev. of 7 runs, 100,000 loops each)
```

This gives more than 10X speedup compared to the previous solution. In general, one should avoid any operations with data frames that involve looping, and also avoid building data frames incrementally, preferring instead to generate a dict or Numpy array and then convert it into a data frame in one step.

### Use of suboptimal object types

Different types of objects in Python may perform better or worse for different types of operation.  For example, while we saw that some operations using Pandas data frames may be slow, it can be quite fast for other operations.  As an example we can look at searching for an item within a list of items. We can compare four different ways of doing this, using the `in` operator with a Python dict, Python list, Pandas Series, or numpy array.  Here are the average execution times for each of these searching over 100,000 values computed using `timeit`:

| Object Type    | Execution Time (µs) |
|----------------|---------------------|
| dict           | 0.0282              |
| Pandas series  | 0.845               |
| Numpy array    | 10.0                |
| list           | 287.0               |
|----------------|---------------------|

Here we see that dictionaries are by far the fastest objects for searching, with lists being the absolute worst.  When timing matters, it's usually useful to do some prototype testing across different types of objects to find the most performant.

### Unnecessary looping

Any time one is working with numpy or Pandas objects, the presence of a loop in the code should count as a bad smell.  These packages have highly optimized vectorized operations, so the use of loops will almost always be orders of magnitude slower.  For example, we can compute the dot product of two arrays using a list comprehension (whicih is effectively a loop):

```python
def dotprod_by_hand(a, b):
    return sum([a[i]*b[i] for i in range(len(a))])

npts = 1000
a = np.random.rand(npts)
b = np.random.rand(npts)

%timeit dotprod_by_hand(a, b)

109 μs ± 610 ns per loop (mean ± std. dev. of 7 runs, 10,000 loops each)
```

Compare this to the result using the built-in dot product operator in Numpy, which gives a speedup of more than 150X compared to our hand-built code:

```python
%timeit np.dot(a, b)

614 ns ± 1.61 ns per loop (mean ± std. dev. of 7 runs, 1,000,000 loops each)
```

### Suboptimal API usage

- e.g. individual vs batch fetching with pubmed API

### Slow I/O

For data-intensive workflows, especially when the data are too large to fit completely in memory, a substantial amount of execution time may be spent waiting for data to be read and/or written to a filesystem or database.


## Just-in-time compilation with Numba


## Using Einstein operators


## A brief introduction to parallelism and multithreading


## Writing paralellized code

