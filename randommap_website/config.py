# pylint: disable=too-few-public-methods
"""
Configuration variables for different environments
"""
import os


class BaseConfig(object):
    DEBUG = False

    REDIS_URL = os.environ['REDIS_URL']
    PORT = os.environ['PORT']

    MAP_TTL = 0 # seconds

class ProductionConfig(BaseConfig):
    DEBUG = False

class DevelopmentConfig(BaseConfig):
    DEBUG = True
