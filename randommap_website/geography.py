import os
import random

import requests
from PIL import Image


def random_coords(min_lat=-75, max_lat=75, min_lon=-180, max_lon=180):
    if (min_lat < -90 or max_lat > 90 or min_lon < -180 or max_lon > 180
            or min_lat >= max_lat or min_lon >= max_lon):
        raise ValueError('Bad coordinate bounds arguments.')

    # TODO: these aren't right; think about max and min, and distribute
    # evenly over surface of the spherical Earth
    # TODO: if max and min don't have the same absolute value, this won't work
    lat = (random.random() - 0.5) * (max_lat - min_lat)
    lon = (random.random() - 0.5) * (max_lon - min_lon)

    return (lat, lon)


def is_land(lat, lon, zoom):
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
                 f'&style=feature:landscape|color:{_rgb_to_hex(*land_color)}'
                 f'&style=feature:water|color:{_rgb_to_hex(*water_color)}'
                 '&style=feature:transit|visibility:off'
                 '&style=feature:poi|visibility:off'
                 '&style=feature:road|visibility:off'
                 '&style=feature:administrative|visibility:off'
                 '&style=element:labels|visibility:off'
                 f'&key={gmaps_api_key}')

    img = Image.open(requests.get(gmaps_url, stream=True).raw).convert('RGB')
    img = img.crop((0, google_logo_height, width, height - google_logo_height))

    total_pixel_count = sum(color[0] for color in img.getcolors())
    water_pixel_count = sum(color[0] for color in img.getcolors()
                            if all(abs(color[1][i] - water_color[i]) < 2
                                   for i in range(3)))

    water_ratio = float(water_pixel_count) / total_pixel_count
    return water_ratio < 0.98


def _rgb_to_hex(r, g, b):
    return '0x{:02x}{:02x}{:02x}'.format(r, g, b)
