# pylint: disable=invalid-name
from collections import namedtuple
import os
from sanic import Sanic, response
from redis import StrictRedis

from randommap_model import RandomMapModel
import config


CONFIG = {
    'production': config.ProductionConfig,
    'development': config.DevelopmentConfig,
}


app = Sanic(__name__)
app.config.from_object(CONFIG[os.environ['APP_CONFIG']])

redis = StrictRedis.from_url(app.config['REDIS_URL'], decode_responses=True)
model = RandomMapModel(redis, app.config['MAP_TTL'])


# Routes

@app.route('/')
def index(_):
    return response.html('<h1>RandomMap Chrome Extension</h1>')


@app.route('/favicon.ico')
def favicon(_):
    return response.file('static/images/favicon.ico')


@app.route('/map')
def get_map(_):
    sat_map = model.request_map()
    randommap_headers = {
        'Randommap-Latitude': sat_map.lat,
        'Randommap-Longitude': sat_map.lon,
        'Randommap-Zoom': sat_map.zoom
    }
    return response.raw(sat_map.image, headers=randommap_headers,
                        content_type='image/png')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['PORT'])
