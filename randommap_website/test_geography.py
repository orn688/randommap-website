from .geography import is_land


def test_is_land():
    assert is_land(36, -117, 12) is True
    assert is_land(8, -127, 12) is False
