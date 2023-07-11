from flask import Blueprint, current_app
from flask_socketio import SocketIO

bp = Blueprint('socketio_bp', __name__)

socketio = SocketIO(cors_allowed_origins="*")
socketio.init_app(current_app)

from ..utils.socket_logger import init_socket_logger
init_socket_logger()

from . import routes

