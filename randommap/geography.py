import io
import math
import random

import mapbox
from PIL import Image


def random_coords(min_lat=-75, max_lat=75, min_lon=-180, max_lon=180):
    """
    Produces a random lat/lon pair within the given bounds.
    """
    lats_ok = -90 < min_lat <= max_lat < 90
    lons_ok = -180 <= min_lon <= max_lon <= 180
    assert lats_ok and lons_ok, "Bad coordinate bounds arguments"

    # Source: https://www.jasondavies.com/maps/random-points/
    min_x = 0.5 * (1 - math.sin(math.pi * min_lat / 180))
    max_x = 0.5 * (1 - math.sin(math.pi * max_lat / 180))
    lat = (180 / math.pi) * math.acos(2 * random.uniform(min_x, max_x) - 1) - 90
    lon = random.uniform(min_lon, max_lon)

    return (lat, lon)


def is_roughly_water_color(color):
    """Water is black, land is white."""
    r, g, b, *_ = color
    average_pixel_value = (r + g + b) / 3
    return average_pixel_value <= 128


def is_land(lat, lon, zoom):
    """
    Determines if a given lat/lon is land (specifically, whether a birds-eye
    view of that position is less than 98% water) by querying Mapbox for a
    static map with land and water having different colors.
    """
    client = mapbox.StaticStyle()
    dimension = 100
    # Mapbox static maps include a logo in the bottom left, so we request a
    # slightly taller than desired image and then crop out the top and bottom
    # (so the resulting image is still square).
    logo_size = 20

    response = client.image(
        username="orn688",
        style_id="cjqlx253r2wcl2sms5lxw13rh",
        lat=lat,
        lon=lon,
        zoom=zoom,
        height=dimension + 2 * logo_size,
        width=dimension,
    )
    if response.status_code != 200:
        raise Exception("Failed to fetch map image from Mapbox for detecting land")

    img = Image.open(io.BytesIO(response.content)).convert("RGBA")
    width, height = img.size
    diff = (height - width) / 2
    img = img.crop((0, diff, width, height - diff))
    total_pixel_count = width ** 2

    water_pixel_count = sum(
        count for count, color in img.getcolors() if is_roughly_water_color(color)
    )

    water_ratio = water_pixel_count / total_pixel_count
    return water_ratio < 0.98
