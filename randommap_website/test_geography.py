from . import geography


def test_is_land():
    assert geography.is_land(40.924292, -71.4047197, 7) is True
