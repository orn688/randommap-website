from sanic import Sanic, response
from redis import StrictRedis
from mapbox import Static
from datetime import datetime
import random
import os

import config
from geography import choose_coords
from image_context import ImageContext


app = Sanic(__name__)
app.config.from_object(config.DevelopmentConfig()) # TODO
redis = StrictRedis(host=app.config['REDIS_HOST'],
                    port=app.config['REDIS_PORT'],
                    db=app.config['REDIS_DB'],
                    decode_responses=True)
redis.flushdb() # Start with a blank slate
mapbox = Static()
image_context = ImageContext(app, redis, mapbox, choose_coords)


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
