"""
Helper functions for dealing with geography.
"""
import random


def choose_coords():
    """
    Choose a random latitude and longitude within certain ranges.
    Returns: tuple(float, float)
    """
    max_lat = 80
    min_lat = -80
    max_lon = 180
    min_lon = -180
    # TODO: these aren't right; think about max and min, and distribute evenly
    # over surface of the spherical Earth
    lat = (random.random() - 0.5) * (max_lat - min_lat)
    lon = (random.random() - 0.5) * (max_lon - min_lon)

    return (lat, lon)
