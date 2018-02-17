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
    RETINA_IMAGES = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    MAP_TTL = 1
    RETINA_IMAGES = False


app.config.from_object({
    'production': ProductionConfig,
    'development': DevelopmentConfig,
}.get(os.environ['APP_CONFIG'], DevelopmentConfig))
