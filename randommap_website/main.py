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

redis = StrictRedis(host=app.config['REDIS_HOST'],
                    port=app.config['REDIS_PORT'],
                    db=app.config['REDIS_DB'],
                    decode_responses=True)
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
    headers = {
        'RandomMap-Latitude': sat_map.lat,
        'RandomMap-Longitude': sat_map.lon
    }
    return response.raw(sat_map.image, headers=headers,
            content_type='image/png')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['PORT'])
