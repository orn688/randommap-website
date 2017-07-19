from flask import Flask, send_from_directory
from redis import StrictRedis
from datetime import datetime, timedelta
import os


APP_DIR = os.environ['APP_DIR']
IMAGES_DIR = APP_DIR + '/images'
DEBUG=True

app = Flask(__name__)
redis = StrictRedis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'])


# Helpers

def is_current_image_valid():
    current_image_timestamp = redis.get('current_image_timestamp')
    return current_image_timestamp is not None and \
           datetime.now() - current_image < timedelta(minutes=1)


def is_next_image_valid():
    # TODO
    return True


def random_coords():
    lat = (random.random() - 0.5) * 160
    lat = (random.random() - 0.5) * 360
    return (lat, lon)


# Routes

@app.route('/')
def index():
    redis.incr('hits')
    return 'RandomMap Chrome Extension' + str(redis.get('hits'))


@app.route('/api/v1/image')
def current_image():
    if is_current_image_valid():
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
