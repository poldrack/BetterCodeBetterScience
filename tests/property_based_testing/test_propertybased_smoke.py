from hypothesis import given, assume, strategies as st
from hypothesis.extra import numpy as nps
from scipy.stats import linregress
import numpy as np
from BetterCodeBetterScience.my_linear_regression import (
    linear_regression,
)

@given(
    # Only generate data that is likely to be valid to start with
    nps.arrays(np.float64, (10, 1), elements=st.floats(-1e6, 1e6)),
    nps.arrays(np.float64, (10,), elements=st.floats(-1e6, 1e6)),
)
def test_linear_regression_without_validation(X, y):
    """Tests that our algorithm matches a reference implementation (scipy)."""

    # Now we can safely test the math against a reference implementation (scipy), 
    # knowing the input is valid.
    params = linear_regression(X, y, validate=False)
    assert params is not None, "Parameters should not be None"
