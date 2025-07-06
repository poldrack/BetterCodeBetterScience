# generate a function that calculates the distance between two points
# where each point is defined as a tuple of two numbers

import math

def distance(p1, p2):
    """Calculate the distance between two points"""
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

