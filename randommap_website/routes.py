import os

from flask import make_response, send_file

from .application import app
from .randommap_model import model


@app.route('/')
def index():
    return '<h1>RandomMap Chrome Extension</h1>'


@app.route('/favicon.ico')
def favicon():
    return send_file(os.path.join('static', 'images', 'favicon.ico'))


@app.route('/map')
def get_map():
    sat_map = model.request_map()

    headers = {
        'Randommap-Latitude': sat_map.lat,
        'Randommap-Longitude': sat_map.lon,
        'Randommap-Zoom': sat_map.zoom,
    }
    # Allow client-side JavaScript to access custom headers
    headers['Access-Control-Expose-Headers'] = ', '.join(h for h in headers)
    headers['Content-Type'] = 'image/png'

    return make_response(sat_map.image, headers)
