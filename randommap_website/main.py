# pylint: disable=invalid-name
from datetime import datetime
from collections import namedtuple
import os
import random
import background
from sanic import Sanic, response
from redis import StrictRedis

import config


# Redis keys
CURR_MAP = 'curr_map'
NEXT_MAP = 'next_map'
CURR_METADATA = 'curr_metadata'
NEXT_METADATA = 'next_metadata'
CURR_VALID = 'curr_map_valid'
NEXT_VALID = 'next_map_valid'

CONFIG = {
    'production': config.ProductionConfig,
    'development': config.DevelopmentConfig,
}


app = Sanic(__name__)
app.config.from_object(CONFIG[os.environ['APP_CONFIG']])

redis = StrictRedis(host=app.config['REDIS_HOST'],
                    port=app.config['REDIS_PORT'],
                    db=app.config['REDIS_DB'],
                    decode_responses=True)


# Satellite map metadata class.

MapMetadata = namedtuple('MapMetadata', ['lat', 'lon', 'zoom', 'timestamp'])


# Redis helpers

def set_metadata(redis_client, key, metadata):
    redis_client.hmset(key, metadata._asdict())


def get_metadata(redis_client, key):
    metadata_dict = redis_client.hgetall(key)
    return MapMetadata(**metadata_dict) if metadata_dict else None


# Map helpers

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


def fetch_map_at_coords(app, lat, lon, zoom):
    """Loads a map image file at the requested coords and zoom from Mapbox."""
    client = mapbox.Static()
    response = client.image('mapbox.satellite', lon=lon, lat=lat,
                                   z=zoom, width=1280, height=1280)
    if response.status_code == 200:
        return response.content
    else:
        # TODO: is this the error that should be raised? Think about what the
        # user will see
        raise RuntimeError('Failed to fetch map image from Mapbox')


def get_random_metadata():
    lat, lon = choose_coords()
    zoom = 7
    timestamp = datetime.now().timestamp()
    return MapMetadata(lat, lon, zoom, timestamp)


# General high-level helpers

def fetch_new_next_map(redis):
    new_metadata = get_random_metadata()
    raw_map = fetch_map_at_coords(mapbox, new_metadata.lat,
                                  new_metadata.lon, new_metadata.zoom)
    set_metadata(redis, NEXT_METADATA, new_metadata)
    set_map_image(redis, NEXT_MAP, raw_map)


def update_maps(redis_client, mapbox_client):
    """Swap next map in for current map, and download a new next map."""
    @background.task
    def do_update():
        if not redis_client.get(NEXT_VALID):
            next_metadata = get_random_metadata()
            set_metadata(redis_client, NEXT_METADATA, next_metadata)

            ex = app.config['MAP_EXPIRE_TIME']
            redis_client.set(NEXT_VALID, True, ex=ex)

            next_image = redis.
        
    do_update()


# Routes

@app.route('/')
def index(_):
    return response.html('<h1>RandomMap Chrome Extension</h1>')


@app.route('/map')
def get_map(_):
    if redis.get(CURR_VALID):
        metadata = get_metadata(redis, CURR_METADATA)
    else:
        metadata = get_metadata(redis, NEXT_METADATA)
        update_maps(redis, mapbox)

    response_headers = {
        'RandomMap-Latitude': metadata.lat,
        'RandomMap-Longitude': metadata.lon,
    }
    return response.file("TODO", response_headers)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['APP_PORT'])
