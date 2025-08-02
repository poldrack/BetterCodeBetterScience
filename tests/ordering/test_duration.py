import pytest
from time import sleep


@pytest.mark.order(2)
def test_duration_3():
    sleep(3)
    assert True

@pytest.mark.order(3)
def test_duration_5():
    sleep(5)
    assert True

@pytest.mark.order(1)
def test_duration_1():
    sleep(1)
    assert True