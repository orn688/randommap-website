import base64
import logging
from datetime import datetime

import background
import mapbox
from redis import StrictRedis

from . import application
from .geography import is_land, random_coords
from .models import SatMap

__all__ = ["get_current_map"]

logger = logging.getLogger("root")
redis = StrictRedis.from_url(application.config["REDIS_URL"], decode_responses=True)

CURR_MAP_KEY = "CURR_MAP"
NEXT_MAP_KEY = "NEXT_MAP"
MAP_TTL = application.config["MAP_TTL"]
ZOOM = application.config["ZOOM"]


async def get_current_map():
    curr_map = await get_map_from_db(CURR_MAP_KEY)
    if curr_map:
        return curr_map

    else:
        logger.info("Current map expired, fetching new map")
        old_next_map = await get_map_from_db(NEXT_MAP_KEY)
        await update_maps()
        if old_next_map:
            return old_next_map

        return await get_map_from_db(CURR_MAP_KEY)


def image_key(key):
    return "{}_IMAGE".format(key)


async def update_maps():
    """
    Replace the current map with the next map, downloading a new next map
    if one does not already exist.
    """
    next_map = await get_map_from_db(NEXT_MAP_KEY)
    if next_map:
        save_map_to_db(CURR_MAP_KEY, next_map, expire=True)
    else:
        curr_map = fetch_new_sat_map()
        save_map_to_db(CURR_MAP_KEY, curr_map, expire=True)
    await fetch_new_map_bg(NEXT_MAP_KEY, expire=False)


def save_map_to_db(map_key, sat_map, expire):
    redis.hmset(map_key, sat_map.metadata)
    encoded_image = base64.encodestring(sat_map.image).decode("utf-8")
    redis.set(image_key(map_key), encoded_image)

    if expire:
        redis.expire(map_key, MAP_TTL)
        redis.expire(image_key(map_key), MAP_TTL)


async def fetch_new_map_bg(map_key, expire):
    """Download and save a map in the background (non-blocking)."""

    @background.task
    def do_fetch_new_map():
        new_map = fetch_new_sat_map()
        save_map_to_db(map_key, new_map, expire)

    do_fetch_new_map()


async def get_map_from_db(map_key):
    map_dict = redis.hgetall(map_key)
    if map_dict:
        encoded_image = redis.get(image_key(map_key))
        if encoded_image:
            map_dict["image"] = base64.decodestring(encoded_image.encode("utf-8"))
            return SatMap(**map_dict)

    return None


def fetch_new_sat_map():
    lat, lon = choose_coords()
    timestamp = int(datetime.now().timestamp())
    image = fetch_image_at_coords(lat, lon, ZOOM, application.config["RETINA_IMAGES"])
    return SatMap(lat, lon, ZOOM, timestamp, image)


def choose_coords():
    """
    Choose a random latitude and longitude within certain ranges.
    Returns: tuple(float, float)
    """
    for i in range(25):
        lat, lon = random_coords()
        if is_land(lat, lon, ZOOM):
            logger.info(
                f"Took {i + 1} attempt(s) to find land ({round(lat, 2)}, {round(lon, 2)})"
            )
            return (lat, lon)

    return (41.5300122, -70.6861865)


def fetch_image_at_coords(lat, lon, zoom, retina=True):
    """
    Loads a map image file at the requested coords and zoom from Mapbox.
    """
    client = mapbox.Static()
    response = client.image(
        "mapbox.satellite",
        lon=lon,
        lat=lat,
        z=zoom,
        width=1280,
        height=1280,
        retina=retina,
    )
    assert response.status_code == 200, "Failed to fetch map image from Mapbox"
    return response.content
