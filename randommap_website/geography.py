import random


def choose_coords():
    """
    Function to choose a random latitude and longitude.
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
