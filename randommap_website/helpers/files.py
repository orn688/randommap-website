"""
Helpers for dealing with the filesystem.
"""
import os


__all__ = ['remove_file_if_exists', 'write_data_to_file']


async def remove_file_if_exists(file_path):
    """Try to remove the given file."""
    try:
        os.remove(file_path)
    except FileNotFoundError:
        return False
    else:
        return True


async def write_data_to_file(data, file_path):
    """Writes raw image data to a file."""
    with open(file_path, 'wb') as f:
        _ = f.write(data)
