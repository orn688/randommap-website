"""
Helper functions to acess the Mapbox API.
"""


__all__ = ['fetch_map_at_coords']


def fetch_map_at_coords(mapbox_client, lat, lon, zoom):
    """Loads a map image file at the requested coords and zoom from Mapbox.

    Args:
        lat, lon: Desired float coordinates for map.
        zoom: Integer zoom level for map from range [0, 19].
    Returns:
        The raw data for the requested map image.
    """
    response = mapbox_client.image('mapbox.satellite', lon=lon, lat=lat,
                                   z=zoom, width=1280, height=1280)
    if response.status_code == 200:
        return response.content
    else:
        # TODO: is this the error that should be raised? Think about what the
        # user will see
        raise RuntimeError('Failed to fetch map image from Mapbox')
