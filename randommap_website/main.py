from flask import Flask, send_from_directory
from redis import StrictRedis
from mapbox import Static
from datetime import datetime
import random
import os

from geography import choose_coords
from image_context import ImageContext


CONFIG_NAME_MAPPER = {
    'production': 'config.ProductionConfig',
    'development': 'config.DevelopmentConfig'
}

app = Flask(__name__)
app.config.from_object(CONFIG_NAME_MAPPER['development']) # TODO
redis = StrictRedis(host=app.config['REDIS_HOST'],
                    port=app.config['REDIS_PORT'],
                    db=app.config['REDIS_DB'],
                    decode_responses=True)
redis.flushdb() # Start with a blank slate
mapbox = Static()
image_context = ImageContext(app, redis, mapbox, choose_coords)


# Routes 

@app.route('/')
def index():
    return 'RandomMap Chrome Extension'


@app.route('/image')
def image():
    return send_from_directory(image_context.images_dir,
                               image_context.get_image().filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
