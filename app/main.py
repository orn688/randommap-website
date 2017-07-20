from flask import Flask, send_from_directory
from redis import StrictRedis
from mapbox import Static
from datetime import datetime, timedelta
import os


DEBUG=True

APP_DIR = os.environ['APP_DIR']
IMAGES_DIR = APP_DIR + '/images'

app = Flask(__name__)
redis = StrictRedis(host=os.environ['REDIS_HOST'],
                    port=os.environ['REDIS_PORT'])
mapbox = Static() # Must have MAPBOX_ACCESS_TOKEN set


# Helpers
def fetch_new_image(lat, lon):
    response = mapbox.image('mapbox.satellite', lon=lon, lat=lat, z=12)
    if response.status_code != 200:
        raise
    # TODO: 


def is_current_image_valid():
    return redis.exists('current_image')


def is_next_image_valid():
    return redis.exists('next_image')


def random_coords():
    lat = (random.random() - 0.5) * 160
    lat = (random.random() - 0.5) * 360
    return (lat, lon)


# Routes

@app.route('/')
def index():
    redis.incr('hits')
    return 'RandomMap Chrome Extension' + str(redis.get('hits'))


@app.route('/image')
def current_image():
    if is_current_image_valid():
        # TODO: return current image
        return send_from_directory(IMAGES_DIR, 'current_image.png')
    elif is_next_image_valid():
        # TODO: asynchronously copy next_image to current_image, and download a
        # new next_image
        return send_from_directory(IMAGES_DIR, 'next_image.png')
    else:
        # TODO: Gotta start somewhere
        pass


if __name__ == '__main__':
    app.run(debug=DEBUG, host='0.0.0.0')
