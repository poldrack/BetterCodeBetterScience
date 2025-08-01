import pytest

@pytest.mark.unit
def test_unit1():
    """This is a unit test."""
    assert True

@pytest.mark.unit
def test_unit2():
    """This is a unit test."""
    assert True

@pytest.mark.integration
def test_integration():
    """This is an integration test."""
    assert True
