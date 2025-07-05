# Software testing

Tests define the expected behavior of code, and detect when the code doesn't match that expected behavior.

One useful analogy for software testing comes from the biosciences.  Think for a moment about the rapid COVID-19 tests that we  all came to know during the pandemic.  These tests had two lines, one of which was a *control* line; if this line didn't show up, then that meant that the test was not functioning as expected.  This is known as a *positive control* because it assesses the test's ability to identify a positive response.  Other tests also include *negative controls*, which ensure that the test returns a negative result when it should.

By analogy, we can think of software tests as being either positive or negative controls for the expected outcome of a software component.  A positive test assesses whether, given a particular valid input, the component returns the correct output.  A negative test assesses whether, in the absence of valid input, the component correctly returns the appropriate error message or null result.  

## Why use software tests?

The most obvious reason to write tests for code is to make sure that the answers that the code gives you are correct.  This becomes increasingly important as AI assistants write more of the code, to the degree that testing is becoming *more important* than code generation as a skill for generating good scientific code.  But creating correct code is far from the only reason for writing tests.

A second reason for testing was highlighted in our earlier discussion of test-driven development.  Tests can provide the coder with a measure of task completion; when the tests pass, the job is done, other than refactoring the code to make it cleaner and more robust.  Writing tests make one think harder about what exactly they want/need the code to do, and to specify those goals in as clear a way as possible.  Focusing on tests can help keep the coder's "eyes on the MVP prize" and prevent generating too much extraneous code ("gold plating").

A third reason to write tests is that they can help drive modularity in the code.  It's much easier to write tests for a simple function that does a single thing than for a complex function with many different roles.  Testing can also help drive modularity by causing you to think more clearly about what a function does when developing the test; the inability to easily write a test for a function can suggest that the function might be overly complex and should be refactored. In this way, writing tests can give us useful insights into the structure of the code.

A final reason to write tests is that they make it much easier to make changes to the code.  Without a robust test suite, one is always left worried that changing some aspect of the code will have unexpected effects on its former behavior (known as a "regression").  Tests can provide you with the comfort you need to make changes, knowing that you will detect any untoward effects your changes might have.  This includes refactoring, where the changes are not meant to modify the function but simply to make the code more robust and readable.


## Types of tests

### Unit tests

Unit tests are the bread and butter of software testing.  They are meant to assess whether individual software components (in the case of Python, functions, classes, and methods) perform as expected.  This includes both assessing whether the component performs as it is supposed to perform given a particular input, but also assessing whether it performs correctly under boundary conditions or problematic conditions, where the correct response is often to raise an exception.  A major goal of unit testing in the latter case is preventing "garbage in, garbage out" behavior.  For example, say that we are testing a function that takes in two matrices, and that the size of these matrices along their first dimension is assumed to match.  In this case, we would want to test to make sure that if the function is provided with two matrices that mismatch in their first dimension, the function will respond by raising an exception rather than by giving back an answer that is incorrect or nonsensical (such as *NaN*, or "not a number").  

### Integration tests

As the name suggests, an integration test assesses whether the entire application works as it should, integrating all of the components that were tested via unit testing. 

One simple type of integration test is a "smoke test".  This name [apparently](https://learn.microsoft.com/en-us/previous-versions/ms182613(v=vs.80)) derives from the computer hardware industry, where one often performs an initial sanity test on an electronic component by plugging it in and seeing if it smokes.  In coding, a smoke test is a simple sanity check meant to ensure that the entire application runs without crashing.  This is usually accomplished by running a top-level function that exercises the entire application.  Smoke tests are useful for quickly identifying major problems, but they don't actually test whether the application performs its function correctly.  They can be especially useful for large applications, where the full test suite may take hours to run. An initial smoke test can determine whether something is broken downstream, saving lots of wasted testing time. 

Full integration tests assess the function of the entire application; one can think of them as unit tests where the unit is the entire application. Just as with unit tests, we want integration tests that both confirm proper operation under intended conditions, as well as confirming proper behavior (such as exiting with an error message) under improper conditions.

## The anatomy of a test

A test is generally structured as a function that executes without raising an exception as long as the code behaves in an expected way.  Let's say that we want to generate a function that returns the escape velocity of a planet:

```python
import math
import numpy as np

def escape_velocity(mass: float, radius: float, G=6.67430e-11):
    """
    Calculate the escape velocity from a celestial body, given its mass and radius.

    Args:
    mass (float): Mass of the celestial body in kg.
    radius (float): Radius of the celestial body in meters.

    Returns:
    float: Escape velocity in m/s.
    """
    
    return math.sqrt(2 * G * mass / radius)
```

We can then generate a test to determine whether the value returned by our function matches the known value for a given planet:

```python
def test_escape_velocity():
    """
    Test the escape_velocity function with known values.
    """
    mass_earth = 5.972e24  # Earth mass in kg
    radius_earth = 6.371e6  # Earth radius in meters
    ev_expected = 11186.0  # Expected escape velocity for Earth in m/s
    ev_computed = escape_velocity(mass_earth, radius_earth)
    assert np.allclose(ev_expected, ev_computed), "Test failed!"
```

We can run this using `pytest` (more about this later), which tells us that the test passes:

```bash
❯ pytest src/BetterCodeBetterScience/escape_velocity.py
====================== test session starts ======================

src/BetterCodeBetterScience/escape_velocity.py ..          [100%]

======================= 2 passed in 0.10s =======================
```


If the returned value didn't match the known value (within a given level of tolerance, which is handled by `np.allclose()`), then the assertion will fail and raise an exception, causing the test to fail.  For example, if we had mis-specified the expected value as 1186.0, we would have seen an error like this:

```bash
❯ pytest src/BetterCodeBetterScience/escape_velocity.py
====================== test session starts ======================

src/BetterCodeBetterScience/escape_velocity.py F          [100%]

=========================== FAILURES ===========================
_____________________ test_escape_velocity _____________________

    def test_escape_velocity():
        """
        Test the escape_velocity function with known values.
        """
        mass_earth = 5.972e24  # Earth mass in kg
        radius_earth = 6.371e6  # Earth radius in meters
        ev_expected = 1186.0 # 11186.0  # Expected escape velocity for Earth in m/s
        ev_computed = escape_velocity(mass_earth, radius_earth)
>       assert np.allclose(ev_expected, ev_computed), "Test failed!"
E       AssertionError: Test failed!
E       assert False
E        +  where False = <function allclose at 0x101403370>(1186.0, 11185.97789184991)
E        +    where <function allclose at 0x101403370> = np.allclose

src/BetterCodeBetterScience/escape_velocity.py:26: AssertionError
===================== short test summary info =====================
FAILED src/BetterCodeBetterScience/escape_velocity.py::test_escape_velocity - AssertionError: Test failed!
======================== 1 failed in 0.11s ========================
```

It's also important to make sure that an exception is raised whenever it should be.  For example, the version of the `escape_velocity()` function above did not check to make sure that the mass and radius arguments had positive values, which means that it would give nonsensical results when passed a negative mass or radius value.  To address this we should add code to the function that causes it to raise an exception if either of the arguments is negative:

```python
def escape_velocity(mass: float, radius: float, G=6.67430e-11):
    """
    Calculate the escape velocity from a celestial body, given its mass and radius.

    Args:
    mass (float): Mass of the celestial body in kg.
    radius (float): Radius of the celestial body in meters.

    Returns:
    float: Escape velocity in m/s.
    """
    if mass <= 0 or radius <= 0:
        raise ValueError("Mass and radius must be positive values.")
    return math.sqrt(2 * G * mass / radius)

```

We can then specify a test that checks whether the function properly raises an exception when passed a negative value. To do this we can use a feature of the `pytest` package (`pytest.raises`) that passes only if the specified exception is raised:

```python
def test_escape_velocity_negative():
    """
    Make sure the function raises ValueError for negative mass or radius.
    """
    with pytest.raises(ValueError):
        escape_velocity(-5.972e24, 6.371e6)
```


## When to write tests

Too often researchers decide to write tests after they have written an entire codebase.  Having any tests is certainly better than having no tests, but integrating testing into ones development workflow from the start can help improve the development experience and ultimately lead to better and more maintainable software.  In Chapter 1 we mentioned the idea of *test-driven development*, which we outline in more detail below, but we first discuss a simple approach to introducing testing into the development process.  

### Bug-driven testing: Any time you encounter a bug, write a test

An easy way to introduce testing into the development process is to write a new test any time one encounters a bug, which we refer to as *bug-driven testing*.  This makes it easy to then work on fixing the bug, since the test will determine when the bug has been fixed. In addition, the test will detect if future changes reintroduce the bug.  

As an example, take the following function:

```python
def find_outliers(data: List[float], threshold: float = 2.0) -> List[int]:
    """
    Find outliers in a dataset using z-score method.
    
    Parameters
    ----------
    data : List[float]
        List of numerical values.
    threshold : float, default=2.0
        Number of standard deviations from the mean to consider a value as an outlier.
    
    Returns
    -------
    List[int]
        List of indices of outliers in the data.
    """
    
    mean = sum(data) / len(data)
    variance = sum((x - mean) ** 2 for x in data) / len(data)
    std = variance ** 0.5
    
    # Bug: division by zero when std is 0 (all values are identical)
    # This only happens when all data points are the same
    outliers = []
    for i, value in enumerate(data):
        z_score = abs(value - mean) / std 
        if z_score > threshold:
            outliers.append(i)
    
    return outliers
```

This code works to properly identify outliers:

```python
In : data = [1, 2, 3, 1000, 4, 5, 6]

In : find_outliers(data)
Out: [3]
```

However, it fails due to a division by zero if all of the values are equal:

```python
In : data = [1, 1, 1, 1, 1]

In : find_outliers(data)
---------------------------------------------------------------------------
ZeroDivisionError                         Traceback (most recent call last)
Cell In[21], line 1
----> 1 find_outliers(data)

Cell In[9], line 26, in find_outliers(data, threshold)
     24 outliers = []
     25 for i, value in enumerate(data):
---> 26     z_score = abs(value - mean) / std 
     27     if z_score > threshold:
     28         outliers.append(i)

ZeroDivisionError: float division by zero

```

Our intended behavior if all of the values are equal is to return an empty list, since there are by definition no outliers.  But before we do this, let's create a couple of tests to check for the intended behavior and provide useful error messages if the test fails:

```python
def test_find_outliers_normal_case():
    data = [1, 2, 3, 4, 5, 100]  # 100 is clearly an outlier
    outliers = find_outliers(data, threshold=2.0)
    
    # Should find the outlier at index 5
    assert 5 in outliers, f"Failed to detect outlier: {outliers}"
    assert len(outliers) == 1, f'Expected exactly one outlier, got: {len(outliers)}'


def test_find_outliers_identical_values():
    data = [5, 5, 5, 5, 5]  # All identical values
    
    outliers = find_outliers(data, threshold=2.0)
    assert outliers == [], f"Expected no outliers for identical values, got {outliers}"
```

Running this with the original function definition, we see that it fails:

```python
❯ pytest src/BetterCodeBetterScience/bug_driven_testing.py
=========================== test session starts ===========================
collected 2 items

src/BetterCodeBetterScience/bug_driven_testing.py .F                [100%]

================================ FAILURES =================================
___________________ test_find_outliers_identical_values ___________________

    def test_find_outliers_identical_values():
        data = [5, 5, 5, 5, 5]  # All identical values

>       outliers = find_outliers(data, threshold=2.0)

src/BetterCodeBetterScience/bug_driven_testing.py:50:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

data = [5, 5, 5, 5, 5], threshold = 2.0

    def find_outliers(data: List[float], threshold: float = 2.0) -> List[int]:
        """
        Find outliers in a dataset using z-score method.

        Parameters
        ----------
        data : List[float]
            List of numerical values.
        threshold : float, default=2.0
            Number of standard deviations from the mean to consider a value as an outlier.

        Returns
        -------
        List[int]
            List of indices of outliers in the data.
        """

        mean = sum(data) / len(data)
        variance = sum((x - mean) ** 2 for x in data) / len(data)
        std = variance ** 0.5

        # Bug: division by zero when std is 0 (all values are identical)
        # This only happens when all data points are the same
        outliers = []
        for i, value in enumerate(data):
>           z_score = abs(value - mean) / std  # Bug: std can be 0!
E           ZeroDivisionError: float division by zero

src/BetterCodeBetterScience/bug_driven_testing.py:31: ZeroDivisionError
========================= short test summary info =========================
FAILED src/BetterCodeBetterScience/bug_driven_testing.py::test_find_outliers_identical_values
 - ZeroDivisionError: float division by zero
======================= 1 failed, 1 passed in 0.10s =======================
```

We can now fix the code by returning an empty list if zero standard deviation is detected:

```python
    ...
    if std == 0:
        # If standard deviation is zero, all values are identical, so no outliers
        return []
```

Here we add a comment to explain the logic of the test. Running the tests now will show that the problem is fixed:

```python
❯ pytest src/BetterCodeBetterScience/bug_driven_testing.py
=========================== test session starts ===========================
collected 2 items

src/BetterCodeBetterScience/bug_driven_testing.py ..                [100%]

============================ 2 passed in 0.08s ============================

```

Now we can continue coding with confidence that if we happen to accidentally reintroduce the bug, it will be caught.
