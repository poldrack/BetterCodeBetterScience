# this is for a demo of parallel testing

import pytest
import time

@pytest.mark.parametrize("x", range(10))
def test_parallel(x):
    assert x in range(10), f"Value {x} is not in the expected list."
    time.sleep(1)