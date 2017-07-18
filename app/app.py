import os

from bottle import Bottle, run, static_file
from redis import Redis


app = Bottle()
app_dir = os.environ['APP_DIR']
images_dir = app_dir + '/images'
bottle_port = os.environ['BOTTLE_PORT']
redis = Redis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'])


@app.route('/')
def index():
    # redis.incr('hits')
    return 'RandomMap Chrome Extension'


@app.route('/image')
def current_image():
    return static_file('current_image.png', root=images_dir)


def random_coords():
    lat = (random.random() - 0.5) * 160
    lat = (random.random() - 0.5) * 360
    return (lat, lon)


if __name__ == '__main__':
    run(app, host='localhost', port=bottle_port, debug=True)
