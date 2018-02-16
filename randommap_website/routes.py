import os

from sanic import response

from .application import app
from .randommap_model import model


@app.route('/')
def index(_):
    return response.html('<h1>RandomMap Chrome Extension</h1>')


@app.route('/favicon.ico')
def favicon(_):
    return response.file(os.path.join('randommap_website', 'static', 'images',
                                      'favicon.ico'))


@app.route('/map')
def get_map(_):
    sat_map = model.request_map()

    headers = {
        'Randommap-Latitude': sat_map.lat,
        'Randommap-Longitude': sat_map.lon,
        'Randommap-Zoom': sat_map.zoom,
    }
    # Allow client-side JavaScript to access custom headers
    headers['Access-Control-Expose-Headers'] = ', '.join(h for h in headers)

    return response.raw(sat_map.image, headers=headers,
                        content_type='image/png')
