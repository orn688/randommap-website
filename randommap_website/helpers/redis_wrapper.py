from collections import namedtuple
import os


__all__ = ['SatelliteImage', 'RedisWrapper']


# Satellite image metadata class.
SatelliteImage = namedtuple('SatelliteImage', ['lat', 'lon', 'zoom',
                                               'filename', 'timestamp'])


class RedisWrapper:
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
        """Fetches the metadata (coords, filename, etc.) for the current image.

        If the current image does not exist or has expired, returns the next
        image and downloads a new next image.
        NOTE: To be called externally; calls only top-level internal methods
        without itself accessing Redis.

        Returns:
            A SatelliteImage containing the metadata for the currently valid
            image.
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

    async def swap_in_next_image(self):
        await self.set_current_image(await self.get_next_image())

    async def update_image(self):
        """
        Swaps the current image's metadata with the next image's metadata in
        Redis, downloads a new next image, and sets its metadata in Redis.
        """
        # Remove the old image file if it exists, and swap in the next image's
        # metadata
        current_image = await self.get_current_image()
        os.remove(os.path.join(self.images_dir, current_image.filename))
        await self.set_current_image_valid()

        new_image = await self.fetch_new_image()
        await self.set_next_image(new_image)

    async def fetch_new_image(self):
        """Downloads a new image from Mapbox and return its metadata.

        Returns:
            A SatelliteImage containing the metadata for the newly downloaded
            image.
        """
        # Assemble metadata for new image
        lat, lon = self.choose_coords()
        zoom = 7 # TODO
        timestamp = datetime.now().timestamp()
        filename = str(int(timestamp)) + '.png'
        new_image = SatelliteImage(lat, lon, zoom, filename, timestamp)

        # Download new image
        new_image_path = os.path.join(self.images_dir, new_image.filename)
        image_data = await self.image_at_coords(lat, lon, zoom)
        await write_data_to_file(image_data, new_image_path)

        return new_image
