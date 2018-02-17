"""
Configuration variables for different environments.
"""
import os

from . import app


class BaseConfig(object):
    DEBUG = False

    REDIS_URL = os.environ['REDIS_URL']
    PORT = int(os.environ['PORT'])

    ZOOM = 9
    MAP_TTL = 60  # seconds
    RETINA_IMAGES = True


class ProductionConfig(BaseConfig):
    DEBUG = False
    ZOOM = int(os.environ.get('ZOOM', 9))
    MAP_TTL = int(os.environ.get('MAP_TTL', 60))
    RETINA_IMAGES = bool(os.environ.get('RETINA_IMAGES', True))


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    MAP_TTL = 1
    RETINA_IMAGES = False


app.config.from_object({
    'production': ProductionConfig,
    'development': DevelopmentConfig,
}.get(os.environ['APP_CONFIG'], DevelopmentConfig))
