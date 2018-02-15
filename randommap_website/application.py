# pylint: disable=invalid-name
import os

from flask import Flask, make_response, send_file
from redis import StrictRedis

from randommap_website import config
from randommap_website.randommap_model import RandomMapModel

CONFIG = {
    'production': config.ProductionConfig,
    'development': config.DevelopmentConfig,
}

app = Flask(__name__)
app.config.from_object(CONFIG[os.environ['APP_CONFIG']])

redis = StrictRedis.from_url(app.config['REDIS_URL'], decode_responses=True)
model = RandomMapModel(redis, app.config['MAP_TTL'])


# Routes

@app.route('/')
def index():
    return '<h1>RandomMap Chrome Extension</h1>'


@app.route('/favicon.ico')
def favicon():
    return send_file(os.path.join('static', 'images', 'favicon.ico'))


@app.route('/map')
def get_map():
    sat_map = model.request_map()

    headers = {
        'Randommap-Latitude': sat_map.lat,
        'Randommap-Longitude': sat_map.lon,
        'Randommap-Zoom': sat_map.zoom,
    }
    # Allow client-side JavaScript to access custom headers
    headers['Access-Control-Expose-Headers'] = ', '.join(h for h in headers)
    headers['Content-Type'] = 'image/png'

    return make_response(sat_map.image, headers)
