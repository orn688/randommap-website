import math
import os
import random

import requests
from PIL import Image


def random_coords(min_lat=-75, max_lat=75, min_lon=-180, max_lon=180):
    """
    Produces a random lat/lon pair within the given bounds.
    """
    if (min_lat < -90 or max_lat > 90 or min_lon < -180 or max_lon > 180
            or min_lat >= max_lat or min_lon >= max_lon):
        raise ValueError('Bad coordinate bounds arguments.')

    # Source: https://www.jasondavies.com/maps/random-points/
    min_x = 0.5 * (1 - math.sin(math.pi * min_lat / 180))
    max_x = 0.5 * (1 - math.sin(math.pi * max_lat / 180))
    lat = (180 / math.pi)*math.acos(2*random.uniform(min_x, max_x) - 1) - 90
    lon = random.uniform(min_lon, max_lon)

    return (lat, lon)


def rgb2hex(r, g, b):
    return '0x{:02x}{:02x}{:02x}'.format(r, g, b)


def is_land(lat, lon, zoom):
    """
    Determines if a given lat/lon is land (specifically, whether
    a birds-eye view of that position is less than 98% water)
    by querying the Google Maps API for a static map with land
    and water having different colors.
    """
    # Parameters for Google Maps static image query
    height = 100
    width = 100
    google_logo_height = 20
    water_color = (0, 0, 255)
    land_color = (0, 255, 0)
    gmaps_api_key = os.environ['GOOGLE_MAPS_API_KEY']

    gmaps_url = ('http://maps.googleapis.com/maps/api/staticmap'
                 f'?center={lat},{lon}'
                 f'&zoom={zoom}'
                 f'&size={width}x{height + 2*google_logo_height}'
                 f'&style=feature:landscape|color:{rgb2hex(*land_color)}'
                 f'&style=feature:water|color:{rgb2hex(*water_color)}'
                 '&style=feature:transit|visibility:off'
                 '&style=feature:poi|visibility:off'
                 '&style=feature:road|visibility:off'
                 '&style=feature:administrative|visibility:off'
                 '&style=element:labels|visibility:off'
                 f'&key={gmaps_api_key}')

    img = Image.open(requests.get(gmaps_url, stream=True).raw).convert('RGB')
    img = img.crop((0, google_logo_height, width, height - google_logo_height))

    total_pixel_count = sum(count for count, color in img.getcolors())
    water_pixel_count = sum(count for count, color in img.getcolors()
                            if all(abs(color[i] - water_color[i]) < 2
                                   for i in range(3)))

    water_ratio = float(water_pixel_count) / total_pixel_count
    return water_ratio < 0.98
