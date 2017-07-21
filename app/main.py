from flask import Flask, send_from_directory
from redis import StrictRedis
from mapbox import Static
from datetime import datetime, timedelta
import random
import os


app = Flask(__name__)
redis = StrictRedis(host=os.environ['REDIS_HOST'],
                    port=os.environ['REDIS_PORT'])
mapbox = Static() if 'MAPBOX_ACCESS_TOKEN' in os.environ else None

app.config['DEBUG']=os.environ['DEBUG']
app.config['APP_DIR'] = os.environ['APP_DIR']
app.config['IMAGES_DIR'] = APP_DIR + '/images'
app.config['IMAGE_EXPIRE_TIME'] = {'ex': 60}


# Helpers
class RandomMapRedis(StrictRedis):
    # TODO
    pass


def fetch_new_image(lat, lon, image_file):
    response = mapbox.image('mapbox.satellite', lon=lon, lat=lat, z=12,
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
        redis.set('current_lat', lat, ex=60)
        redis.set('current_lon', lon, ex=60)
        fetch_new_image(lat, lon, app.config['IMAGES_DIR'] + '/current_image.png')
    return send_from_directory(app.config['IMAGES_DIR'], 'current_image.png')


if __name__ == '__main__':
    app.run(debug=DEBUG, host='0.0.0.0')
