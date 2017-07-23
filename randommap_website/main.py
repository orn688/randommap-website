from flask import Flask, send_from_directory
from flask_redis import FlaskRedis
from mapbox import Static
from datetime import datetime
import random
import os

from image_context import ImageContext


CONFIG_NAME_MAPPER = {
    'production': 'config.ProductionConfig',
    'development': 'config.DevelopmentConfig'
}

app = Flask(__name__)
app.config.from_object(CONFIG_NAME_MAPPER['development']) # TODO
redis = FlaskRedis(app, decode_responses=True)
mapbox = Static()


# Helpers

def choose_coords():
    max_lat = 80
    min_lat = -80
    max_lon = 180
    min_lon = -180
    # TODO: these aren't right; think about max and min, and distribute evenly
    # over surface of the spherical Earth
    lat = (random.random() - 0.5) * (max_lat - min_lat)
    lon = (random.random() - 0.5) * (max_lon - min_lon)
    return (lat, lon)
    # return (41, -71) # TODO: just for testing


# TODO: find a better place for this
image_context = ImageContext(app, redis, mapbox, choose_coords)


# Routes

@app.route('/')
def index():
    return 'RandomMap Chrome Extension'


@app.route('/image')
def image():
    return send_from_directory(image_context.images_dir,
                               image_context.image.filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
