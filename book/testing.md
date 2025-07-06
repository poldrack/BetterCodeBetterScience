# Software testing

Tests define the expected behavior of code, and detect when the code doesn't match that expected behavior.

One useful analogy for software testing comes from the biosciences.  Think for a moment about the rapid COVID-19 tests that we  all came to know during the pandemic.  These tests had two lines, one of which was a *control* line; if this line didn't show up, then that meant that the test was not functioning as expected.  This is known as a *positive control* because it assesses the test's ability to identify a positive response[^1].  Other tests also include *negative controls*, which ensure that the test returns a negative result when it should.

By analogy, we can think of software tests as being either positive or negative controls for the expected outcome of a software component.  A positive test assesses whether, given a particular valid input, the component returns the correct output.  A negative test assesses whether, in the absence of valid input, the component correctly returns the appropriate error message or null result.  

## Why use software tests?

The most obvious reason to write tests for code is to make sure that the answers that the code gives you are correct.  This becomes increasingly important as AI assistants write more of the code, to the degree that testing is becoming *more important* than code generation as a skill for generating good scientific code.  But creating correct code is far from the only reason for writing tests.

A second reason for testing was highlighted in our earlier discussion of test-driven development.  Tests can provide the coder with a measure of task completion; when the tests pass, the job is done, other than refactoring the code to make it cleaner and more robust.  Writing tests make one think harder about what exactly they want/need the code to do, and to specify those goals in as clear a way as possible.  Focusing on tests can help keep the coder's "eyes on the MVP prize" and prevent generating too much extraneous code ("gold plating").

A third reason to write tests is that they can help drive modularity in the code.  It's much easier to write tests for a simple function that does a single thing than for a complex function with many different roles.  Testing can also help drive modularity by causing you to think more clearly about what a function does when developing the test; the inability to easily write a test for a function can suggest that the function might be overly complex and should be refactored. In this way, writing tests can give us useful insights into the structure of the code.

A final reason to write tests is that they make it much easier to make changes to the code.  Without a robust test suite, one is always left worried that changing some aspect of the code will have unexpected effects on its former behavior (known as a "regression").  Tests can provide you with the comfort you need to make changes, knowing that you will detect any untoward effects your changes might have.  This includes refactoring, where the changes are not meant to modify the function but simply to make the code more robust and readable.


## Types of tests

### Unit tests

Unit tests are the bread and butter of software testing.  They are meant to assess whether individual software components (in the case of Python, functions, classes, and methods) perform as expected.  This includes both assessing whether the component performs as it is supposed to perform given a particular input, but also assessing whether it performs correctly under boundary conditions or problematic conditions, where the correct response is often to raise an exception.  A major goal of unit testing in the latter case is preventing "garbage in, garbage out" behavior.  For example, say that we are testing a function that takes in two matrices, and that the size of these matrices along their first dimension is assumed to match.  In this case, we would want to test to make sure that if the function is provided with two matrices that mismatch in their first dimension, the function will respond by raising an exception rather than by giving back an answer that is incorrect or nonsensical (such as *NaN*, or "not a number").  That is, we want to aim for "garbage in, exception out" behavior.

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

======================= 1 passed in 0.10s =======================
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

Here we add a comment to explain the intention of the statement. Running the tests now will show that the problem is fixed:

```python
❯ pytest src/BetterCodeBetterScience/bug_driven_testing.py
=========================== test session starts ===========================
collected 2 items

src/BetterCodeBetterScience/bug_driven_testing.py ..                [100%]

============================ 2 passed in 0.08s ============================

```

Now we can continue coding with confidence that if we happen to accidentally reintroduce the bug, it will be caught.

## The structure of a good test

A commonly used scheme for writing a test is "given/when/then":

- given some particular situation as background
- when something happens (such as a particular input)
- then something else should happen (such as a particular output or exception)

Importantly, a test should only test one thing at a time.  This doesn't mean that the test should necessarily only test for one specific error at a time; rather, it means that the test should assess a specific situation ("given/when"), and then assess all of the possible outcomes that are necessary to ensure that the component functions properly ("then").  You can see this in the test for zero standard deviation that we generated in the earlier example, which actually tested for two conditions (the intended value being present in the list, and the list having a length of one) that together define the condition that we are interested in testing for.

How do we test that the output of a function is correct given the input?  There are different answers for different situations:

- *commonly known answer*: Sometimes we possess inputs where the output is known.  For example, if we were creating a function that computes the circumference of a circle, then we know that the output for an input radius of 1 should be 2 * pi.  This is generally only the case for very simple functions.  
- *reference implementation*: In other cases we may have a standard implementation of an algorithm that we can compare against.  While in general it's not a good idea to reimplement code that already exists in a standard library, in come cases we may want to extend existing code but also check that the basic version still works as planned. 
- *parallel implementation*: Some times we don't have a reference implementation, but we can code up another parallel implementation to compare our code to.  It's important that this isn't just a copy of the code used in the function; in that case, it's really not a test at all!
- *behavioral test*: Sometimes the best we can do is to run the code repeatedly and ensure that it behaves as expected on average.  For example, if a function outputs a numerical value and we know the expected distribution of that value given a particular input, we can ensure that the result matches that distribution with a high probability.  Such *probabilistic tests* are not optimal in the sense that they can occasionally fail even when the code is correct, but they are sometimes the best we can do.

### Test against the interface, not the implementation

A good test shouldn't know about the internal implementation details of the function that it is testing, and changes in the internal code that do not modify the input-output relationship should not affect the test.  That is, from the standpoint of the test, a function should be a "black box".  

The most common way in which a test can violate this principle is by accessing the internal variables of a class that it is testing.  For example, we might generate a class that performs a scaling operation on a numpy matrix:

```python
class SimpleScaler:
    def __init__(self):
        self.transformed_ = None

    def fit(self, X):
        self.mean_ = X.mean(axis=0)
        self.std_ = X.std(axis=0)

    def transform(self, X):
        self.transformed_ = (X - self.mean_) / self.std_
        return self.transformed_

    def fit_transform(self, X):
        self.fit(X)
        return self.transform(X)
```

We could write a test that checks the values returned by the `fit_transform()` method, treating the the class as a black box:

```python
def test_simple_scaler_interface():
    X = np.array([[1, 2], [3, 4], [5, 6]])
    scaler = SimpleScaler()
    
    # Test the interface without accessing internals
    transformed_X = scaler.fit_transform(X)
    assert np.allclose(transformed_X.mean(axis=0), np.array([0, 0]))
    assert np.allclose(transformed_X.std(axis=0), np.array([1, 1]))
```

Alternatively one might use knowledge of the internals of the class to test the transformed value:

```python
def test_simple_scaler_internals():

    X = np.array([[1, 2], [3, 4], [5, 6]])
    scaler = SimpleScaler()
    _ = scaler.fit_transform(X)
    
    # Test that the transformed data is correct using the internal
    assert np.allclose(scaler.transformed_.mean(axis=0), np.array([0, 0]))
    assert np.allclose(scaler.transformed_.std(axis=0), np.array([1, 1]))

```

Both of these tests pass against the class definition shown above. However, if we were to change the way that the transformation is performed (for example, we decide to use the `StandardScaler` function from `scikit-learn` instead of writing our own), then the implementation-aware tests are likely to fail unless the sample internal variable names are used.  In general we should only interact with a function or class via its explicit interfaces.

### Tests should be independent

In scientific computing it's common to compose many different operations into a workflow.  If we want to test the workflow, then the tests of later steps in the workflow must necessarily rely upon earlier steps.  We could in theory write a set of tests that operate on a shared object, but the tests would fail if executed in an incorrect order, even if the code was correct.  Similarly, a failure on an early test would cause cascading failures in later tests, even if their code was correct.  The use of ordered tests also prevents the parallel execution of tests, which may slow down testing for complex projects.  For these reasons, we should always aim to create tests that can be executed independently.

Here is an example where coupling between tests could cause failures.  First we generate two functions that make changes in place to a data frame:

```python
def split_names(df):
    df['firstname'] = df['name'].apply(lambda x: x.split()[0])
    df['lastname'] = df['name'].apply(lambda x: x.split()[1])

def get_initials(df):
    df['initials'] = df['firstname'].str[0] + df['lastname'].str[0]

```

In this case, the `get_initials()` function relies upon the `split_names()` function having been run, since otherwise the necessary columns won't exist in the data frame. We can then create tests for each of these, and a data frame that they can both use:

```python
people_df = pd.DataFrame({'name': ['Alice Smith', 'Bob Howard', 'Charlie Ashe']}) 

def test_split_names():
    split_names(people_df)
    assert people_df['firstname'].tolist() == ['Alice', 'Bob', 'Charlie']
    assert people_df['lastname'].tolist() == ['Smith', 'Howard', 'Ashe']

def test_get_initials():
    get_initials(people_df)
    assert people_df['initials'].tolist() == ['AS', 'BH', 'CA']
```

These tests run correctly, but the same tests fail if we change their order such that `test_get_intials()` runs first, because the necessary columns (`firstname` and `lastname`) have not yet been created.  

One simple way to deal with this is to set up all of the necessary structure locally within each test:

```python

def get_people_df():
    return pd.DataFrame({'name': ['Alice Smith', 'Bob Howard', 'Charlie Ashe']}) 

def test_split_names_fullsetup():
    local_people_df = get_people_df()
    split_names(local_people_df)
    assert local_people_df['firstname'].tolist() == ['Alice', 'Bob', 'Charlie']
    assert local_people_df['lastname'].tolist() == ['Smith', 'Howard', 'Ashe']

def test_get_initials_fullsetup():
    local_people_df = get_people_df()
    split_names(local_people_df)
    get_initials(local_people_df)
    assert local_people_df['initials'].tolist() == ['AS', 'BH', 'CA']
```

For simple functions like these this would not cause too much computational overhead, but for computationally intensive functions we would like to be able to reuse the results from the first time each function is run.  In a later section we will discuss the use of *fixtures* which allow this kind of reuse across tests while avoiding the ordering problems that we saw above when using a global variable across tests.

## Testing frameworks

One could write tests without the help of any specialized packages, but we generally use a testing framework to help automate the activities of testing.  There are several testing frameworks for Python; we will focus on the popular and flexible `pytest` framework.

We will start with a very simple example: a function that generates the Euclidean distance between two points.  Copilot generates the following for us based on the prompt in the comment:

```python
# generate a function that calculates the distance between two points
# where each point is defined as a tuple of two numbers

import math

def distance(p1, p2):
    """Calculate the distance between two points"""
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
```

Now we would like to generate some tests for this code to make sure that it works properly. If we ask Copilot to generate some tests, it does a seeming decent job:

```python
def test_distance_zero():
    assert distance((0, 0), (0, 0)) == 0

def test_distance_positive_coordinates():
    assert distance((1, 2), (4, 6)) == 5

def test_distance_negative_coordinates():
    assert distance((-1, -2), (-4, -6)) == 5

def test_distance_mixed_coordinates():
    assert distance((1, -2), (-4, 6)) == math.sqrt(125)

def test_distance_same_x():
    assert distance((3, 4), (3, 8)) == 4

def test_distance_same_y():
    assert distance((3, 4), (7, 4)) == 4
```

Now that we have our tests, we can run them using the `pytest` command:

```bash
pytest src/BetterCodeBetterScience/distance_testing
```

This command will cause pytest to search (by default) for any files named `test_*.py` or `*_test.py` in the relevant path, and the select any functions whose name starts with the prefix "test".  Running those tests, we get an error:


```bash
>       assert distance((1, -2), (-4, 6)) == math.sqrt(125)
E       assert 9.433981132056603 == 11.180339887498949
E        +  where 9.433981132056603 = distance((1, -2), (-4, 6))
E        +  and   11.180339887498949 = <built-in function sqrt>(125)
E        +    where <built-in function sqrt> = math.sqrt

```

Here we see that the value returned by our function is different from the one expected by the test; in this case, the test value generated by Copilot is incorrect.  In our research, it was not uncommon for ChatGPT to generate incorrect test values, so these must always be checked by a domain expert.  Once we fix the expected value for that test (the square root of 89), then we can rerun the tests and see that they have passed:

```bash
python -m pytest pytest src/BetterCodeBetterScience/distance_testing
==================== test session starts =====================                                     

src/codingforscience/simple_testing/test_distance.py . [ 16%]
.....                                                  [100%]

===================== 6 passed in 0.06s ======================

```

### Potential problems with AI-generated tests

If we are going to rely upon AI tools to generate our tests, we need to be sure that the tests are correct.  One of my early forays into AI-driven test generation uncovered an interesting example of how this can go wrong. 

In our early project that examined the performance of GPT-4 for coding {cite:p}`Poldrack:2023aa`, one of the analyses that we performed first asked GPT-4 to do was to generate a set of functions related to common problems in several scientific domains, and then to generate tests to make sure that the function performed correctly.  One of the functions that was generated was the escape velocity function shown above, for which GPT-4 generated the [following test](https://github.com/poldrack/ai-coding-experiments/blob/main/data/conceptual_prompting/testdirs/conceptual_prompting06/test_answer.py):


```python
def test_escape_velocity():

    mass_earth = 5.972e24
    radius_earth = 6.371e6
    result = escape_velocity(mass_earth, radius_earth)
    assert pytest.approx(result, rel=1e-3) == 11186.25

    mass_mars = 6.4171e23
    radius_mars = 3.3895e6
    result = escape_velocity(mass_mars, radius_mars)
    assert pytest.approx(result, rel=1e-3) == 5027.34

    mass_jupiter = 1.8982e27
    radius_jupiter = 6.9911e7
    result = escape_velocity(mass_jupiter, radius_jupiter)
    assert pytest.approx(result, rel=1e-3) == 59564.97
```

When we run this test (renaming it `test_escape_velocity_gpt4`), we see that one of the tests fails:

```bash
❯ pytest src/BetterCodeBetterScience/escape_velocity.py::test_escape_velocity_gpt4
==================================== test session starts ====================================
platform darwin -- Python 3.12.0, pytest-8.4.1, pluggy-1.5.0
rootdir: /Users/poldrack/Dropbox/code/BetterCodeBetterScience
configfile: pyproject.toml
plugins: cov-5.0.0, anyio-4.6.0, hypothesis-6.115.3, mock-3.14.0
collected 1 item

src/BetterCodeBetterScience/escape_velocity.py F                                      [100%]

========================================= FAILURES ==========================================
_________________________________ test_escape_velocity_gpt4 _________________________________

    def test_escape_velocity_gpt4():

        mass_earth = 5.972e24
        radius_earth = 6.371e6
        result = escape_velocity(mass_earth, radius_earth)
        assert pytest.approx(result, rel=1e-3) == 11186.25

        mass_mars = 6.4171e23
        radius_mars = 3.3895e6
        result = escape_velocity(mass_mars, radius_mars)
        assert pytest.approx(result, rel=1e-3) == 5027.34

        mass_jupiter = 1.8982e27
        radius_jupiter = 6.9911e7
        result = escape_velocity(mass_jupiter, radius_jupiter)
>       assert pytest.approx(result, rel=1e-3) == 59564.97
E       assert 60202.716344497014 ± 60.2027 == 59564.97
E
E         comparison failed
E         Obtained: 59564.97
E         Expected: 60202.716344497014 ± 60.2027

src/BetterCodeBetterScience/escape_velocity.py:52: AssertionError
================================== short test summary info ==================================
FAILED src/BetterCodeBetterScience/escape_velocity.py::test_escape_velocity_gpt4 - assert 60202.716344497014 ± 60.2027 == 59564.97
===================================== 1 failed in 0.12s =====================================
```
 
It seems that the first two assertions pass but the third one, for Jupiter, fails.  This failure took a bit of digging to fully understand.  In this case, the code and test value are both correct, depending on where you stand on Jupiter! The problem is that planets are *oblate*, meaning that they are slightly flattened such that the radius around the equator is higher than at other points.  NASA’s [Jupiter fact sheet](https://nssdc.gsfc.nasa.gov/planetary/factsheet/jupiterfact.html) claims an escape velocity of 59.5 km/s, which seems to be the source of the test value.  This is correct when computed using the equatorial radius of 71492 km.  However, the radius given for Jupiter in GPT-4's test (69911 km) is the volumetric mean radius rather than the equatorial radius, and the value generated by the code (60.2 km/s) is correct when computed using the volumetric mean radius.  Thus, the test failed not due to any problems with the code itself, but due to a mismatch in assumptions regarding the combination of test values.  This example highlights the importance of understanding and checking the tests that are generated by AI coding tools.

## Test-driven development and AI-assisted coding

Here we will dive into a more realistic example of an application that one might develop using AI assistance, specifically looking at how we could develop the application using a test-driven development (TDD) approach.  We will develop a Python application that takes in a query for the PubMed database and returns a data frame containing the number of database records matching that query for each year. We start by decomposing the problem and sketching out the main set of functions that we will need to develop, with understandable names for each:

- `get_PubmedIDs_for_query`: A function that will search pubmed for a given query and return a list of pubmed IDs
- `get_record_from_PubmedID`: A function that will retrieve the record for a given pubmed ID
- `parse_year_from_Pubmed_record`: A function that will parse a record to extract the year of publication
- A function that will summarize the number of records per year
- The main function that will take in a query and return a data frame with the number of records per year for the query

We start by creating `get_PubmedIDs_for_query`.  We could use the `Biopython.Entrez` module to perform this search, but Biopython is a relatively large module that could introduce technical debt.  Instead, we will directly retrieve the result using the Entrez API and the built-in `requests` module. Note that for all of the code shown here we will not include docstrings, but they are available in the code within the repository.

If we are using the TDD approach, we would first want to develop a set of tests to make sure that our function is working correctly.  The following three tests specify several different outcomes that we might expect. First, we give a query that is known to give a valid result, and test whether it in fact gives such a result:

```python
def test_get_PubmedIDs_for_query_check_valid():
    query = "friston-k AND 'free energy'"
    ids = get_PubmedIDs_for_query(query)

    # make sure that a list is returned
    assert isinstance(ids, list)       
    # make sure the list is not empty
    assert len(ids) > 0                 
```

Second, we give a query with a known empty result, and make sure it returns an empty list:

```python
def test_get_PubmedIDs_for_query_check_empty():
    query = "friston-k AND 'fizzbuzz'"
    ids = get_PubmedIDs_for_query(query)

    # make sure that a list is returned
    assert isinstance(ids, list)   
    # make sure the resulting list is empty
    assert len(ids) == 0
```


With the minimal tests in place, we then move to writing the code for the module.  We first create an empty function to ensure that the tests fail:

```python
def get_PubmedIDs_for_query(query: str, 
                            retmax: int = None,
                            esearch_url: str = None) -> list:
    return None
```

The test result shows that all of the tests fail:

```bash
❯ python -m pytest -v tests/textmining
================================== test session starts ===================================
...
tests/textmining/test_textmining.py::test_get_PubmedIDs_for_query_check_valid FAILED [ 50%]
tests/textmining/test_textmining.py::test_get_PubmedIDs_for_query_check_empty FAILED [100%]

======================================== FAILURES ========================================
________________________ test_get_PubmedIDs_for_query_check_valid ________________________

ids = None

    def test_get_PubmedIDs_for_query_check_valid(ids):
>       assert isinstance(ids, list)
E       assert False
E        +  where False = isinstance(None, list)

tests/textmining/test_textmining.py:32: AssertionError
________________________ test_get_PubmedIDs_for_query_check_empty ________________________

    def test_get_PubmedIDs_for_query_check_empty():
        query = "friston-k AND 'fizzbuzz'"
        ids = get_PubmedIDs_for_query(query)
>       assert len(ids) == 0
               ^^^^^^^^
E       TypeError: object of type 'NoneType' has no len()

tests/textmining/test_textmining.py:39: TypeError
================================ short test summary info =================================
FAILED tests/textmining/test_textmining.py::test_get_PubmedIDs_for_query_check_valid - assert False
FAILED tests/textmining/test_textmining.py::test_get_PubmedIDs_for_query_check_empty - TypeError: object of type 'NoneType' has no len()
=================================== 2 failed in 0.12s ====================================
```

Now we work with Copilot write the code to make the tests pass:

```python
# define the eutils base URL globally for the module
# - not best practice but probably ok here
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def get_PubmedIDs_for_query(
    query: str, retmax: int = None, esearch_url: str = None
) -> list:
    """
    Search database for a given query and return a list of IDs.
    :param query: str, the query to search for
    :param retmax: int, the maximum number of results to return
    :base_url: str, the base url for the pubmed search
    :return: list, a list of pubmed IDs
    """
    # define the base url for the pubmed search
    if esearch_url is None:
        esearch_url = f"{BASE_URL}/esearch.fcgi"

    params = format_pubmed_query_params(query, retmax=retmax)

    response = requests.get(esearch_url, params=params)

    return get_idlist_from_response(response)


def format_pubmed_query_params(query: str, retmax: int = 10000) -> str:
    """
    Format a query for use with the pubmed api.
    :param query: str, the query to format
    :return: dict, the formatted query dict
    """

    # define the parameters for the search
    return {"db": "pubmed", "term": query, "retmode": "json", "retmax": retmax}


def get_idlist_from_response(response: requests.Response) -> list:
    if response.status_code == 200:
        # extract the pubmed IDs from the response
        ids = response.json()["esearchresult"]["idlist"]
        return ids
    else:
        raise ValueError("Bad request")
```

Note that we have split parts of the functionality into separate functions in order to make the code more understandable.  Running the tests, we see that both of them pass.  Assuming that our tests cover all possible outcomes of interest, we can consider our function complete.  We can also add additional tests to cover additional functions that we generated; we won't go into the details here, but you can see them on the Github repo.


## Test coverage

It can be useful to know if there are any portions of our code that are not being exercised by our tests, which is known as *code coverage*.  The `pytest-cov` extension for the `pytest` testing package can provide us with a report of test coverage for these tests:

```bash
---------- coverage: platform darwin, python 3.12.0-final-0 ----------
Name                                                   Stmts   Miss  Cover   Missing
------------------------------------------------------------------------------------
src/BetterCodeBetterScience/textmining/textmining.py      30      1    97%   70
------------------------------------------------------------------------------------
TOTAL                                                     30      1    97%
```

This report shows that of the 30 statements in our code, one of them is not covered by the tests.  When we look at the missing code (denoted as being on line 70), we see that the missing line is this one from `get_idlist_from_response`:

```python
    else:
        # raise an exception if the search didn't return a usable response
        raise ValueError("Bad request")
```

Since none of our test cases caused a bad request to occur, this line never gets executed in the tests. We can address this by adding a test that makes sure that an exception is raised if an invalid base url is provided. To check for an exception, we need to use the `pytest.raises` context manager:

```python
def test_get_PubmedIDs_for_query_check_badurl():
    query = "friston-k AND 'free energy'"
    # bad url
    base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.f'
    
    # make sure that the function raises an exception
    with pytest.raises(Exception):
        ids = get_PubmedIDs_for_query(query, base_url=base_url)
    
```

After adding this test, we see that we now have 100% coverage. It's important not to get too hung up on test coverage; rather than always aspiring to 100% coverage, it's important to make sure that the most likely possible situations are tested.  Just because you have 100% coverage doesn't mean that your code is perfectly tested, since there could always be situations that you haven't checked for. And spending too much time testing for unlikely problems can divert your efforts from other most useful activities.


## Test fixtures

Sometimes we need to use a the same data for multiple tests. Rather than duplicating potentially time-consuming processes across each of the tests, it is often preferable to create a single instance of the object that can be used across multiple tests, which is known as a *test fixture*.  This also helps maintain isolation between tests, since the order of tests shouldn't matter if an appropriate fixture is generated as soon as it's needed.

For our example above, it's likely that we will need to reuse the list of pubmed IDs from the search to perform various tests on the subsequent functions.  We can create a single version of this list of IDs by creating a fixture. In the `pytest` framework we do this using a special Python operator called a *decorator*, which is denoted by the symbol `@` as a prefix. A decorator is function that takes another function as input, modifies its functionality, and returns another function; you don't need to understand in detail how decorators work for this particular usage.  To refactor our tests above, we would first create the fixture by decorating the function that generates the fixture with the `@pytest.fixture` decorator, setting the `scope` variable to "session" so that the fixture is only generated once within the session:

```python
@pytest.fixture(scope="session")
def ids():
    query = "friston-k AND 'free energy'"
    ids = get_PubmedIDs_for_query(query)
    return ids
```

We can then refactor our tests for a valid query to use the fixture by passing it as an argument to the test function:

```python
def test_get_PubmedIDs_for_query_check_valid(ids):
    assert isinstance(ids, list)
    assert len(ids) > 0
```

The result is the same, but we now have a set of ids that we can reuse in subsequent tests, so that we don't have to make repeated queries.  It's important to note while using a session-scoped fixture: If any of the subsequent tests modify the fixture, those modifications will persist, which will break the isolation between tests.  We could prevent this by removing the `scope="session"` argument, which would then default to the standard scope which is within a specific function.  If you wish to use session-scoped fixtures and need to modify them within the test function, then it is best to first create a copy of the fixture object (e.g. `my_ids = ids.copy()`) so that the global fixture object won't be modified.

## Mocking

Sometimes tests require infrastructure that is outside of the control of the tester. In the example above, we are assuming that the Pubmed API is working correctly for our tests to run; if we were to try to run these tests without an internet connection, they would fail.  In other cases, code may rely upon a database system that may or may not exist on a particular system.  In these cases, we can create a mock object that can stand in for and simulate the behavior of the system that the code needs to interact with.

In our example, we want to create a mock response that looks sufficiently like a response from the real API to pass our tests.  Using pytest's *monkeypatch* fixture, we can temporarily replace the real requests.get function with our own fake function that returns a predictable, controlled response.  We first need to create a class that can replace the `requests.get` call in `get_PubmedIDs_for_query`, replacing it with a mock version that outputs a fixed simulacrum of an API response via its `.json()` method.  

```python
class MockPubmedResponse:
    status_code = 200

    def json():
        return {
            'header': {'type': 'esearch', 'version': '0.3'},
            'esearchresult': {
                'count': '2',
                'retmax': '20',
                'retstart': '0',
                'idlist': ['39312494', '39089179']
            }
        }
```

We now insert this mock response for the standard `requests.get` call within the test. In my initial attempt, I created created a fixture based on the mocked response and then tested that fixture:

```python
@pytest.fixture
def ids_mocked(monkeypatch):

    def mock_get(*args, **kwargs):
        return MockPubmedResponse()

    # apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)

    query = "friston-k AND 'free energy'"
    ids = get_PubmedIDs_for_query(query)
    return ids

def test_get_PubmedIDs_for_query_check_valid_mocked(ids_mocked):
    assert isinstance(ids_mocked, list)
    assert len(ids_mocked) == 2

```

Turning off my network connection shows that the mocked test passes, while the tests that require connecting to the actual API fail.  However, my usual code review (using Google's Gemini 2.5 Pro) identified a problem with this fixture: it conflates the setup (creating the mock API) with the execution of the function that uses the mock API.  A better approach (recommended by Gemini) is move the function execution out of the fixture and into the test:

```python
# Fixture ONLY does the setup (the mocking)
@pytest.fixture
def mock_pubmed_api(monkeypatch):

    class MockPubmedResponse:
        status_code = 200
        def json(self):
            return {
                'header': {'type': 'esearch', 'version': '0.3'},
                'esearchresult': {
                    'count': '2',
                    'retmax': '20',
                    'retstart': '0',
                    'idlist': ['39312494', '39089179']
                }
            }

    def mock_get(*args, **kwargs):
        return MockPubmedResponse()

    # Apply the monkeypatch for requests.get to mock_get
    monkeypatch.setattr(requests, "get", mock_get)

# The test requests the setup, then performs the action and assertion.
def test_get_PubmedIDs_for_query_check_valid_mocked(mock_pubmed_api):
    # Action: Call the function under test
    query = "friston-k AND 'free energy'"
    ids = get_PubmedIDs_for_query(query)

    # Assertion: Check the result
    assert isinstance(ids, list)
    assert len(ids) == 2
```

Note that while mocking can be useful for testing specific components by saving time and increasing robustness, integration tests and smoke tests should usually be run without mocking, in order to catch any errors that arise through interaction with the relevant components that are being mocked.  In fact, it's always a good idea to have tests that specifically assess the usage of the external service and the system's response to failures in that service (e.g. by using features of the testing framework that allow one to shut down access to the network).


[^1]: This is slightly inaccurate, because a true positive control would contain the actual virus. It would be more precise to call it a “procedural control” but these seem to be also referred to as “positive controls” so I am sticking with the more understandable terminology here.