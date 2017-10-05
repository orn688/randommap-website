import random
import mapbox
from datetime import datetime


class SatMap:
    """Contains metadata and the actual image for a satellite map."""
    def __init__(self, lat, lon, zoom, timestamp, image):
        self.lat = lat
        self.lon = lon
        self.zoom = zoom
        self.timestamp = timestamp
        self.image = image

    @property
    def metadata(self):
        return {
            'lat': self.lat,
            'lon': self.lon,
            'zoom': self.zoom,
            'timestamp': self.timestamp
        }


class RandomMapModel:
    CURR_MAP_KEY = "CURR_MAP_KEY"
    NEXT_MAP_KEY = "NEXT_MAP_KEY"

    @staticmethod
    def choose_coords():
        """
        Choose a random latitude and longitude within certain ranges.
        Returns: tuple(float, float)
        """
        max_lat = 80
        min_lat = -80
        max_lon = 180
        min_lon = -180
        # TODO: these aren't right; think about max and min, and distribute
        # evenly over surface of the spherical Earth
        lat = (random.random() - 0.5) * (max_lat - min_lat)
        lon = (random.random() - 0.5) * (max_lon - min_lon)

        return (lat, lon)

    @staticmethod
    def fetch_image_at_coords(lat, lon, zoom):
        """
        Loads a map image file at the requested coords and zoom from Mapbox.
        """
        client = mapbox.Static()
        response = client.image('mapbox.satellite', lon=lon, lat=lat,
                                z=zoom, width=1280, height=1280)
        if response.status_code == 200:
            return response.content
        else:
            # TODO: is this the error that should be raised? Think about what
            # the user will see
            raise RuntimeError('Failed to fetch map image from Mapbox')

    @staticmethod
    def new_sat_map():
        lat, lon = RandomMapModel.choose_coords()
        zoom = 7
        timestamp = str(int(datetime.now().timestamp()))
        image = RandomMapModel.fetch_image_at_coords(lat, lon, zoom)
        return SatMap(lat, lon, zoom, timestamp, image)

    @staticmethod
    def image_key(key):
        return '{}_IMAGE'.format(key)

    def __init__(self, redis, map_ttl):
        self.redis = redis
        self.map_ttl = map_ttl

    def set_map(self, map_key, sat_map, expire=False):
        self.redis.hmset(map_key, sat_map.metadata)
        self.redis.set(self.image_key(map_key), sat_map.image)
        if expire:
            self.redis.expire(map_key, self.map_ttl)
            self.redis.expire(self.image_key(map_key), self.map_ttl)

    def get_map(self, map_key):
        map_dict = self.redis.hgetall(map_key)
        if map_dict:
            map_dict['image'] = self.redis.get(self.image_key(map_key))
            if map_dict['image'] is None:
                raise RuntimeError('image is None')
            return SatMap(**map_dict)
        else:
            return None

    def update_maps(self):
        """
        Replace the current map with the next map, downloading a new next
        map if one does not already exist.
        """
        next_map = self.get_map(self.NEXT_MAP_KEY)
        if not next_map:
            curr_map = self.new_sat_map()
            self.set_map(self.CURR_MAP_KEY, curr_map)
            next_map = self.new_sat_map()
            self.set_map(self.NEXT_MAP_KEY, next_map)
        else:
            self.set_map(self.CURR_MAP_KEY, next_map, expire=True)
            self.set_map(self.NEXT_MAP_KEY, self.new_sat_map())

    def request_map(self):
        curr_map = self.get_map(self.CURR_MAP_KEY)
        if curr_map is None:
            old_next_map = self.get_map(self.NEXT_MAP_KEY)
            self.update_maps()
            if old_next_map is None:
                curr_map = self.get_map(self.CURR_MAP_KEY)
            else:
                curr_map = old_next_map
        return curr_map
