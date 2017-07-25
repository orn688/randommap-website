# pylint: disable=too-few-public-methods
"""
Configuration variables for different environments
"""
import os


class BaseConfig(object):
    """Default configuration variables."""
    DEBUG = False

    REDIS_HOST = os.environ['REDIS_HOST']
    REDIS_PORT = os.environ['REDIS_PORT']
    REDIS_DB = 0

    APP_PORT = os.environ['APP_PORT']
    APP_DIR = os.environ['APP_DIR']
    IMAGES_DIR = os.path.join(APP_DIR, 'images')

    IMAGE_EXPIRE_TIME = 60 # seconds


class ProductionConfig(BaseConfig):
    """Production configuration variables."""
    DEBUG = False


class DevelopmentConfig(BaseConfig):
    """Development configuration variables."""
    DEBUG = True
