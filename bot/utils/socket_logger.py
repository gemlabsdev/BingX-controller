import logging
from flask_socketio import SocketIO

from .socket_io_handler import SocketIOHandler
from flask import current_app

socketio = SocketIO(current_app, cors_allowed_origins="*")


def init_socket_logger():
    logger = logging.getLogger('BingXBot')
    socketio_handler = SocketIOHandler(socketio)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    socketio_handler.setFormatter(formatter)
    socketio_handler.setLevel(logging.INFO)
    logger.addHandler(socketio_handler)
