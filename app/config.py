app_dir = os.environ['APP_DIR']
images_dir = app_dir + '/images'
bottle_port = os.environ['BOTTLE_PORT']
redis = Redis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'])
