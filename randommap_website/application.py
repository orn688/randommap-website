import os

from redis import StrictRedis
from sanic import Sanic

from . import config   # isort:skip

CONFIG = {
    'production': config.ProductionConfig,
    'development': config.DevelopmentConfig,
}.get(os.environ['APP_CONFIG'], config.DevelopmentConfig)

app = Sanic(__name__)
app.config.from_object(CONFIG)

redis = StrictRedis.from_url(app.config['REDIS_URL'], decode_responses=True)
