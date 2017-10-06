import random
import base64
import mapbox
import background
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
    """
    Representation of a Redis-backed model for RandomMap, with metadata and
    images for current and next satellite maps.
    """
    CURR_MAP_KEY = 'CURR_MAP'
    NEXT_MAP_KEY = 'NEXT_MAP'

    def __init__(self, redis, map_ttl):
        self.redis = redis
        self.map_ttl = map_ttl

    def request_map(self):
        curr_map = self._get_map(self.CURR_MAP_KEY)
        if curr_map is None:
            old_next_map = self._get_map(self.NEXT_MAP_KEY)
            self._update_maps()
            if old_next_map is None:
                curr_map = self._get_map(self.CURR_MAP_KEY)
            else:
                curr_map = old_next_map
        return curr_map

    def _update_maps(self):
        """
        Replace the current map with the next map, downloading a new next map
        if one does not already exist.
        """
        next_map = self._get_map(self.NEXT_MAP_KEY)
        if next_map:
            self._set_map(self.CURR_MAP_KEY, next_map, expire=True)
        else:
            curr_map = self._new_sat_map()
            self._set_map(self.CURR_MAP_KEY, curr_map, expire=True)
        self._set_new_map_bg(self.NEXT_MAP_KEY, expire=False)

    def _set_map(self, map_key, sat_map, expire):
        self.redis.hmset(map_key, sat_map.metadata)
        encoded_image = base64.encodestring(sat_map.image).decode('utf-8')
        self.redis.set(self._image_key(map_key), encoded_image)

        if expire:
            self.redis.expire(map_key, self.map_ttl)
            self.redis.expire(self._image_key(map_key), self.map_ttl)

    def _set_new_map_bg(self, map_key, expire):
        """Download and save a map in the background (non-blocking)."""
        @background.task
        def do_set_map():
            new_map = self._new_sat_map()
            self._set_map(map_key, new_map, expire)

        do_set_map()

    def _get_map(self, map_key):
        map_dict = self.redis.hgetall(map_key)
        if map_dict:
            encoded_image = self.redis.get(self._image_key(map_key))
            if encoded_image:
                map_dict['image'] = base64.decodestring(
                        encoded_image.encode('utf-8'))
                return SatMap(**map_dict)
        return None

    @staticmethod
    def _image_key(key):
        return '{}_IMAGE'.format(key)

    @staticmethod
    def _new_sat_map():
        lat, lon = RandomMapModel._choose_coords()
        zoom = 7
        timestamp = int(datetime.now().timestamp())
        image = RandomMapModel._fetch_image_at_coords(lat, lon, zoom)
        return SatMap(lat, lon, zoom, timestamp, image)

    @staticmethod
    def _choose_coords():
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
    def _fetch_image_at_coords(lat, lon, zoom):
        """
        Loads a map image file at the requested coords and zoom from Mapbox.
        """
        client = mapbox.Static()
        response = client.image('mapbox.satellite', lon=lon, lat=lat,
                                z=zoom, width=1280, height=1280)
        if response.status_code == 200:
            return response.content
        else:
            # TODO: is this the error that should be raised?
            raise RuntimeError('Failed to fetch map image from Mapbox')
