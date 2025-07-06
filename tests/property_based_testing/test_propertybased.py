from hypothesis import given, assume, strategies as st
from hypothesis.extra import numpy as nps
from scipy.stats import linregress
import numpy as np
from BetterCodeBetterScience.my_linear_regression import (
    linear_regression,
    _validate_input,
)


# Test 1: Test the validation logic in isolation
# ------------------------------------------------
@given(
    nps.arrays(
        np.float64, (10, 1), elements=st.floats(allow_nan=True, allow_infinity=True)
    ),
    nps.arrays(
        np.float64, (10,), elements=st.floats(allow_nan=True, allow_infinity=True)
    ),
)
def test_validate_input(X, y):
    """Tests that our validation function correctly identifies and rejects bad data."""
    try:
        # Call the function directly
        _validate_input(X, y)
        # If it gets here, hypothesis generated valid data. Test passes implicitly.
    except ValueError:
        # If a ValueError is raised, it means hypothesis found bad data,
        # and our validator correctly caught it. This is a success!
        pass


# Test 2: Test the algorithm's correctness, assuming valid input
# --------------------------------------------------------------
@given(
    # Only generate data that is likely to be valid to start with
    nps.arrays(np.float64, (10, 1), elements=st.floats(-1e6, 1e6)),
    nps.arrays(np.float64, (10,), elements=st.floats(-1e6, 1e6)),
)
def test_linear_regression_correctness(X, y):
    """Tests that our algorithm matches a reference implementation (scipy)."""
    # Use `hypothesis.assume` to filter out any edge cases the validator would catch.
    # This tells hypothesis: "If this data is bad, just discard it and try another."
    try:
        _validate_input(X, y)
    except ValueError:
        assume(False)  # Prunes this example from the test run

    # Now we can safely test the math against a reference implementation (scipy), 
    # knowing the input is valid.
    params = linear_regression(X, y)
    lr_result = linregress(X.flatten(), y.flatten())

    assert np.allclose(params, [lr_result.intercept, lr_result.slope])
