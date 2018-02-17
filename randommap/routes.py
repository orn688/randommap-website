from sanic import response

from . import app
from .db import get_current_map


app.static('/favicon.ico', './randommap/static/images/favicon.ico')


@app.route('/')
async def index(_):
    return response.html('<h1>RandomMap Chrome Extension</h1>')


@app.route('/map')
async def map(_):
    sat_map = await get_current_map()

    headers = {
        'Randommap-Latitude': sat_map.lat,
        'Randommap-Longitude': sat_map.lon,
        'Randommap-Zoom': sat_map.zoom,
    }
    # Allow client-side JavaScript to access custom headers
    headers['Access-Control-Expose-Headers'] = ', '.join(h for h in headers)
    headers['Cache-Control'] = 'max-age={}'.format(app.config['MAP_TTL'])

    return response.raw(sat_map.image, headers=headers,
                        content_type='image/png')
