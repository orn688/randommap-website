from bottle import route, static_file

@route('/')
def index():
    # redis.incr('hits')
    return 'RandomMap Chrome Extension'


@route('/api/v1/image')
def current_image():
    return static_file('current_image.png', root=images_dir)


def random_coords():
    lat = (random.random() - 0.5) * 160
    lat = (random.random() - 0.5) * 360
    return (lat, lon)


