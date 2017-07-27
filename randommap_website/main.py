from sanic import Sanic, response
from redis import StrictRedis
from mapbox import Static
from datetime import datetime
import random
import os

import config
from helpers import *


app = Sanic(__name__)
app.config.from_object(config.DevelopmentConfig()) # TODO
redis = StrictRedis(host=app.config['REDIS_HOST'],
                    port=app.config['REDIS_PORT'],
                    db=app.config['REDIS_DB'],
                    decode_responses=True)
mapbox = Static()
redis_wrapper = RedisWrapper(app, redis, mapbox, choose_coords)


# High-level helpers

async def random_image_metadata():
    lat, lon = choose_coords()
    zoom = 7
    timestamp = datetime.now().timestamp(),
    return SatelliteImage(lat, lon, zoom, timestamp,
                          filename=str(int(timestamp)) + '.png')


async def update_image():
    current_image = redis_wrapper.get_current_image()
    await remove_file_if_exists(os.path.join(app.config['IMAGE_DIR'] \
                                + current_image.filename))
    await redis_wrapper.swap_in_next_image()
    await redis_wrapper.set_current_image_valid()

    new_image = random_image_metadata() 
    write_data_to_file(
        image_at_coords(mapbox, new_image.lat, new_image.lon, new_image.zoom),
        os.path.join(app.config['IMAGES_DIR'], new_image.filename))
    await


# Routes 

@app.route('/')
async def index(request):
    return response.html('<h1>RandomMap Chrome Extension</h1>')


@app.route('/image')
async def image(request):
    return_image = await image_context.get_image()
    image_path = os.path.join(image_context.images_dir, return_image.filename)
    return await response.file(image_path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['APP_PORT'])
