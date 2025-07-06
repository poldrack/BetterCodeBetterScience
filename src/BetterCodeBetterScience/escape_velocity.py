import math
import numpy as np
import pytest

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

def test_escape_velocity():
    """
    Test the escape_velocity function with known values.
    """
    mass_earth = 5.972e24  # Earth mass in kg
    radius_earth = 6.371e6  # Earth radius in meters
    ev_expected = 11186.0  # Expected escape velocity for Earth in m/s
    ev_computed = escape_velocity(mass_earth, radius_earth)
    assert np.allclose(ev_expected, ev_computed), "Test failed!"

def test_escape_velocity_negative():
    """
    Make sure the function raises ValueError for negative mass or radius.
    """
    with pytest.raises(ValueError):
        escape_velocity(-5.972e24, 6.371e6)

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
    assert pytest.approx(result, rel=1e-3) == 59564.97
