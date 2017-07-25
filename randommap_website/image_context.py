from collections import namedtuple
from datetime import datetime
from random import random
import os


SatelliteImage = namedtuple('SatelliteImage', ['lat', 'lon', 'zoom',
                                               'filename', 'timestamp'])

async def write_data_to_file(data, filename):
    with open(filename, 'wb') as f:
        _ = f.write(data)


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
        self.expire_time = app.config['IMAGE_EXPIRE_TIME']

    def init_app(self, app):
        pass

    async def get_image(self):
        """
        To be called externally; calls only top-level internal methods without
        itself accessing Redis.
        """
        if await self.is_current_image_valid():
            return_image = await self.get_current_image()
        else:
            # Current image is expired; return the next image (downloading it
            # first, if necessary), and throw away the old one while
            # downloading a new next image.
            return_image = await self.get_next_image()
            if not return_image:
                return_image = await self.fetch_new_image()
                await self.set_next_image(return_image)
            await self.update_image()
        return return_image

    async def get_current_image(self):
        return await self.get_image_by_key(self.current_image_key)

    async def get_next_image(self):
        return await self.get_image_by_key(self.next_image_key)

    async def get_image_by_key(self, image_key):
        image_dict = self.redis.hgetall(image_key)
        return SatelliteImage(**image_dict) if image_dict else None

    async def is_current_image_valid(self):
        return bool(self.redis.get(self.current_image_valid_key))

    async def set_current_image_valid(self, valid=True):
        self.redis.set(self.current_image_valid_key, valid,
                       ex=self.expire_time)

    async def set_current_image(self, image):
        await self.set_image_by_key(self.current_image_key, image)

    async def set_next_image(self, image):
        await self.set_image_by_key(self.next_image_key, image)

    async def set_image_by_key(self, image_key, image):
        self.redis.hmset(image_key, image._asdict())

    async def update_image(self):
        """
        Swap 
        """
        # Remove the old image if it exists, and swap in the next image's data
        current_image = await self.get_current_image()
        if current_image:
            os.remove(os.path.join(self.images_dir, current_image.filename))
        await self.set_current_image(await self.get_next_image())
        await self.set_current_image_valid()

        new_image = await self.fetch_new_image()
        await self.set_next_image(new_image)

    async def fetch_new_image(self):
        # Assemble metadata for new image
        lat, lon = self.choose_coords()
        zoom = 7 # TODO
        timestamp=datetime.now().timestamp()
        filename = str(int(timestamp)) + '.png'
        new_image = SatelliteImage(lat, lon, zoom, filename, timestamp)

        # Download new image
        new_image_path = os.path.join(self.images_dir, new_image.filename)
        image_data = await self.image_at_coords(lat, lon, zoom)
        await write_data_to_file(image_data, new_image_path)

        return new_image

    async def image_at_coords(self, lat, lon, zoom):
        response = self.mapbox.image('mapbox.satellite', lon=lon, lat=lat,
                                     z=zoom, width=1280, height=1280)
        if response.status_code == 200:
            return response.content
        else:
            raise RuntimeError() # TODO
