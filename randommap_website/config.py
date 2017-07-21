import os


class BaseConfig(object):
    DEBUG = False

    REDIS_HOST = os.environ['REDIS_HOST']
    REDIS_PORT = os.environ['REDIS_PORT']
    REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'

    APP_DIR = os.environ['APP_DIR'] 
    IMAGES_DIR = os.path.join(APP_DIR, 'images')

    IMAGE_EXPIRE_TIME={'ex': 60} # For passing to Redis.set()


class ProductionConfig(BaseConfig):
    DEBUG = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
