from bottle import Bottle, run, debug
from redis import Redis
import os

import routes
import config

app_dir = os.environ['APP_DIR']
images_dir = app_dir + '/images'
bottle_port = os.environ['BOTTLE_PORT']
# redis = Redis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'])

DEBUG = True

debug(DEBUG)
run(host='localhost', port=config.bottle_port, reloader=DEBUG)
