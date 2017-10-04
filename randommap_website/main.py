# pylint: disable=invalid-name
from datetime import datetime
import os
import background
from sanic import Sanic, response
from redis import StrictRedis
from mapbox import Static

import config
from helpers import (
    remove_file_if_exists,
    write_data_to_file,
    choose_coords,
    fetch_map_at_coords,
    MapMetadata,
    RandomMapDatabase,
)


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
mapbox = Static()
app_db = RandomMapDatabase(app, redis)


# High-level helpers

def get_random_map_metadata():
    lat, lon = choose_coords()
    zoom = 7
    timestamp = datetime.now().timestamp()
    filename = map_filename_from_timestamp(timestamp)
    return MapMetadata(lat, lon, zoom, timestamp, filename)


def map_filename_from_timestamp(timestamp):
    return ''.join(('randommap_', str(int(timestamp)), '.png'))


def fetch_new_next_map(db):
    new_map_metadata = get_random_map_metadata()
    raw_map = fetch_map_at_coords(mapbox, new_map_metadata.lat,
        new_map_metadata.lon, new_map_metadata.zoom)
    write_data_to_file(raw_map, path_to_map(new_map_metadata))
    db.set_next_map_metadata(new_map_metadata)


def path_to_map(map_metadata):
    return os.path.join(app.config['MAPS_DIR'], map_metadata.filename)


@background.task
def update_maps(db):
    """Swap next map in for current map, and download a new next map."""
    current_map_metadata = db.get_current_map_metadata()
    if current_map_metadata:
        remove_file_if_exists(path_to_map(current_map_metadata))

    next_map_metadata = db.get_next_map_metadata()
    db.set_current_map_metadata(next_map_metadata)
    db.set_current_map_valid()

    fetch_new_next_map()


# Routes

@app.route('/')
def index(_):
    return response.html('<h1>RandomMap Chrome Extension</h1>')


@app.route('/map')
def get_map(_):
    if app_db.is_current_map_valid():
        map_metadata = app_db.get_current_map_metadata()
    else:
        map_metadata = app_db.get_next_map_metadata()
        if not map_metadata or not os.path.exists(path_to_map(map_metadata)):
            # Need to initialize database.
            set_next_map(app_db)
            map_metadata = app_db.get_next_map_metadata()
        update_maps(app_db)

    response_headers={
        'RandomMap-Latitude': map_metadata.lat,
        'RandomMap-Longitude': map_metadata.lon,
    }
    return response.file(path_to_map(map_metadata), response_headers)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['APP_PORT'])
