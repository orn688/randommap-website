from sanic import Sanic

__all__ = ['app']

app = Sanic(__name__)

from .config import *  # noqa
from .routes import *  # noqa
