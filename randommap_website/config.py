import os


class BaseConfig(object):
    DEBUG = False

    REDIS_HOST = os.environ['REDIS_HOST']
    REDIS_PORT = os.environ['REDIS_PORT']
    REDIS_DB = 0

    APP_DIR = os.environ['APP_DIR'] 
    IMAGES_DIR = os.path.join(APP_DIR, 'images')

    IMAGE_EXPIRE_TIME = 60 # seconds


class ProductionConfig(BaseConfig):
    DEBUG = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
