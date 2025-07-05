# generate a function that calculates the distance between two points
# where each point is defined as a tuple of two numbers

import math

def distance(p1, p2):
    """Calculate the distance between two points"""
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


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
