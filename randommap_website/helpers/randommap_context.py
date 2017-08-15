from collections import namedtuple


__all__ = ['MapMetadata', 'RandomMapContext']


# Satellite map metadata class.
MapMetadata = namedtuple('MapMetadata',
                         ['lat', 'lon', 'zoom', 'filename', 'timestamp'])


class RandomMapContext:
    """
    Helper class to manage the Redis connection and map metadata.
    """
    def __init__(self, app, redis, **kwargs):
        self.app = app
        self.redis = redis

        self.current_map_key = kwargs.get('current_map_key', 'current_map')
        self.next_map_key = kwargs.get('next_map_key', 'next_map')
        self.current_map_valid_key = kwargs.get('current_map_valid_key',
                                                'current_map_valid')

        self.expire_time = self.app.config['MAP_EXPIRE_TIME']

    async def get_current_map_metadata(self):
        return await self.get_map_metadata_by_key(self.current_map_key)

    async def get_next_map_metadata(self):
        return await self.get_map_metadata_by_key(self.next_map_key)

    async def get_map_metadata_by_key(self, map_key):
        map_metadata_dict = self.redis.hgetall(map_key)
        return MapMetadata(**map_metadata_dict) if map_metadata_dict else None

    async def is_current_map_valid(self):
        return bool(self.redis.get(self.current_map_valid_key))

    async def set_current_map_valid(self, valid=True):
        self.redis.set(self.current_map_valid_key, valid,
                       ex=self.expire_time)

    async def set_current_map_metadata(self, map_metadata):
        await self.set_map_metadata_by_key(self.current_map_key, map_metadata)

    async def set_next_map_metadata(self, map_metadata):
        await self.set_map_metadata_by_key(self.next_map_key, map_metadata)

    async def set_map_metadata_by_key(self, map_key, map_metadata):
        self.redis.hmset(map_key, map_metadata._asdict())
