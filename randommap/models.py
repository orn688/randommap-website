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
