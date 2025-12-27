# generate a function that calculates the distance between two points
# where each point is defined as a tuple of two numbers

from bettercode.distance import distance
import math

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
