from sanic import Sanic

app = Sanic(__name__)

from .config import *  # noqa
from .routes import *  # noqa
