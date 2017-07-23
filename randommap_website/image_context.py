from flask import current_app
from datetime import datetime
import os


class SatelliteImage:
    def __init__(self, lat, lon, zoom, filename, timestamp):
        self.lat = lat
        self.lon = lon
        self.zoom = zoom
        self.filename = filename
        self.timestamp = timestamp

    def __str__(self):
        return self.filename

    def __repr__(self):
        return 'SatelliteImage({})'.format(
            ', '.join(f'{attr}={val}' for attr, val in self.__dict__.items()))


class ImageContext:
    """
    Helper class to manage the Redis connection and the image files for the
    RandomMap website.
    """
    def __init__(self, app, redis, mapbox, choose_coords_func,
                 current_image_key='current_image',
                 next_image_key='next_image',
                 current_image_valid_key='current_image_valid'):
        self.app = app
        self.init_app(app)
        self.images_dir = app.config['IMAGES_DIR']

        self.redis = redis
        self.mapbox = mapbox
        self.choose_coords = choose_coords_func

        self.current_image_key = current_image_key
        self.next_image_key = next_image_key
        self.current_image_valid_key = current_image_valid_key
        self.expire_time = {'ex': 60} # TODO

    def init_app(self, app):
        pass

    @property
    def image(self):
        """
        To be called externally; calls only top-level internal methods without
        itself accessing Redis.
        """
        if self.is_current_image_valid():
            return_image = self.get_current_image()
        else:
            # Current image is expired; return the next image (downloading it
            # first, if necessary), and throw away the old one while
            # downloading a new next image.
            return_image = self.get_next_image()
            if not return_image:
                return_image = self.fetch_new_image()
                self.set_next_image(return_image)
            self.update_image() # TODO: do this asynchronously
        return return_image

    def get_current_image(self):
        return self.get_image(self.current_image_key)

    def get_next_image(self):
        return self.get_image(self.next_image_key)

    def get_image(self, image_key):
        image_dict = self.redis.hgetall(image_key)
        return SatelliteImage(**image_dict) if image_dict else None

    def is_current_image_valid(self):
        return bool(self.redis.get(self.current_image_valid_key))

    def set_current_image_valid(self, valid=True):
        self.redis.set(self.current_image_valid_key, valid, **self.expire_time)

    def set_next_image(self, image):
        self.redis.hmset(self.next_image_key, image.__dict__)

    def update_image(self):
        """
        Swap 
        """
        # Remove the old image if it exists, and swap in the next image's data
        current_image = self.get_current_image()
        if current_image:
            os.remove(os.path.join(self.images_dir, current_image.filename))
        self.redis.hmset(self.current_image_key,
                         self.get_next_image().__dict__)
        self.set_current_image_valid()

        new_image = self.fetch_new_image()
        self.set_next_image(new_image)

    def fetch_new_image(self):
        # Assemble metadata for new image
        lat, lon = self.choose_coords()
        zoom = 7 # TODO
        timestamp=datetime.now().timestamp()
        filename = str(int(timestamp)) + '.png'
        new_image = SatelliteImage(lat, lon, zoom, filename, timestamp)

        # Download new image
        new_image_path = os.path.join(self.images_dir, new_image.filename)
        image_data = self.image_at_coords(lat, lon, zoom)
        self.write_data_to_file(image_data, new_image_path)

        return new_image

    def write_data_to_file(self, data, filename):
        with open(filename, 'wb') as f:
            _ = f.write(data)

    def image_at_coords(self, lat, lon, zoom):
        response = self.mapbox.image('mapbox.satellite', lon=lon, lat=lat,
                                     z=zoom, width=1280, height=1280)
        if response.status_code == 200:
            return response.content
        else:
            raise RuntimeError() # TODO
