"""
Helpers for dealing with the filesystem.
"""
import os


__all__ = ['remove_file_if_exists', 'write_data_to_file']


async def remove_file_if_exists(file_path):
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass


async def write_data_to_file(data, file_path):
    """Writes raw bytes to the given file."""
    with open(file_path, 'wb') as data_file:
        _ = data_file.write(data)
