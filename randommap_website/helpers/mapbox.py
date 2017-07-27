"""
Helper functions to acess the Mapbox API.
"""


__all__ = ['image_at_coords']


async def image_at_coords(mapbox_client, lat, lon, zoom):
    """Gets the image file at the requested coords and zoom from Mapbox.

    Args:
        lat, lon: Desired float coordinates for image.
        zoom: Integer zoom level for image from range [0, 19].
    Returns:
        The raw data for the requested image.
    """
    response = mapbox_client.image('mapbox.satellite', lon=lon, lat=lat,
                                    z=zoom, width=1280, height=1280)
    if response.status_code == 200:
        return response.content
    else:
        raise RuntimeError() # TODO
