import pytest

@pytest.mark.order(2)
def test_second():
    """This is the second test."""
    assert True

@pytest.mark.order(1)
def test_first():
    """This is the first test."""
    assert True