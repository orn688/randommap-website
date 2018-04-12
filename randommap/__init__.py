from sanic import Sanic

__all__ = ["application"]

application = Sanic(__name__)

from .config import *  # noqa
from .routes import *  # noqa
