import randommap_website.routes  # noqa
from randommap_website.application import app

app.run(host='0.0.0.0', port=app.config['PORT'])
