"""
Configuration variables for different environments
"""
import os


class BaseConfig(object):
    DEBUG = False

    REDIS_URL = os.environ['REDIS_URL']
    PORT = int(os.environ['PORT'])

    MAP_TTL = 60  # seconds


class ProductionConfig(BaseConfig):
    DEBUG = False
    MAP_TTL = 60


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    MAP_TTL = 1
