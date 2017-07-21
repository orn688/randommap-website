from flask import Flask, send_from_directory
from redis import StrictRedis
from . import mapbox
from datetime import datetime, timedelta
import random
import os

CONFIG_NAME_MAPPER = {
    'production': 'config.ProductionConfig',
    'development': 'config.DevelopmentConfig'
}

app = Flask(__name__)
app.config.from_object(CONFIG_NAME_MAPPER['development']) # TODO
redis = FlaskRedis(app)
mapbox = MapboxClient(app) # TODO implement this


# Helpers

def fetch_new_image(lat, lon, zoom, image_file):
    response = mapbox.image('mapbox.satellite', lon=lon, lat=lat, z=zoom,
                            width=1280, height=1280)
    if response.status_code != 200:
        raise
    with open(image_file, 'wb') as f:
        _ = f.write(response.content)


def is_current_image_valid():
    return True
    return redis.exists('current_image')


def is_next_image_valid():
    return True
    return redis.exists('next_image')


def random_coords():
    lat = (random.random() - 0.5) * 160
    lon = (random.random() - 0.5) * 360
    return (lat, lon)


# Routes

@app.route('/')
def index():
    return 'RandomMap Chrome Extension'


@app.route('/image')
def image():
    if not redis.exists('current_lat'):
        lat, lon = random_coords()
        zoom = 7
        redis.set('current_lat', lat, **app.config['IMAGE_EXPIRE_TIME'])
        redis.set('current_lon', lon, **app.config['IMAGE_EXPIRE_TIME'])
        fetch_new_image(lat, lon, zoom,
            os.path.join(app.config['IMAGES_DIR'], 'current_image.png'))
    return send_from_directory(app.config['IMAGES_DIR'], 'current_image.png')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
