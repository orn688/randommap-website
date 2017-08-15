# pylint: disable=invalid-name
from datetime import datetime
import os
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
    RandomMapContext,
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
app_ctx = RandomMapContext(app, redis)


# High-level helpers

def get_random_map_metadata():
    lat, lon = choose_coords()
    zoom = 7
    timestamp = datetime.now().timestamp()
    filename = map_filename_from_timestamp(timestamp)
    return MapMetadata(lat, lon, zoom, timestamp, filename)


def get_map_filename_from_timestamp(timestamp):
    return ''.join('randommap_', str(int(timestamp)), '.png')


async def set_next_map():
    new_map_metadata = get_random_map_metadata()
    await write_data_to_file(
        await fetch_map_at_coords(mapbox, new_map_metadata.lat,
                                  new_map_metadata.lon, new_map_metadata.zoom),
        path_to_map(new_map_metadata))
    await app_ctx.set_next_map_metadata(new_map_metadata)


async def update_maps():
    current_map_metadata = await app_ctx.get_current_map_metadata()
    if current_map_metadata:
        await remove_file_if_exists(path_to_map(current_map_metadata))

    next_map_metadata = await app_ctx.get_next_map_metadata()
    await app_ctx.set_current_map_metadata(next_map_metadata)
    await app_ctx.set_current_map_valid()

    await set_next_map()


def path_to_map(map_metadata):
    return os.path.join(app.config['MAPS_DIR'], map_metadata.filename)


# Routes

@app.route('/')
async def index(_):
    return response.html('<h1>RandomMap Chrome Extension</h1>')


@app.route('/map')
async def get_map(_):
    if await app_ctx.is_current_map_valid():
        map_metadata = await app_ctx.get_current_map_metadata()
    else:
        map_metadata = await app_ctx.get_next_map_metadata()
        if not map_metadata or not os.path.exists(path_to_map(map_metadata)):
            # Need to initialize app context
            await set_next_map()
            map_metadata = await app_ctx.get_next_map_metadata()
        await update_maps() # TODO: do this asynchronously
    return await response.file(path_to_map(map_metadata))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['APP_PORT'])
