# pylint: disable=too-few-public-methods
"""
Configuration variables for different environments
"""
import os


class BaseConfig(object):
    DEBUG = False

    REDIS_HOST = os.environ['REDIS_HOST']
    REDIS_PORT = os.environ['REDIS_PORT']
    REDIS_DB = 0

    PORT = os.environ['PORT']

    MAP_TTL = 1 # seconds

class ProductionConfig(BaseConfig):
    DEBUG = False

class DevelopmentConfig(BaseConfig):
    DEBUG = True
