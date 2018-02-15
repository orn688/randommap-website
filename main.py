from randommap_website.application import app


app.run(host='0.0.0.0', port=app.config['PORT'], access_log=True)
