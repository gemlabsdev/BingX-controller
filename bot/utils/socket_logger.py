import logging

from .socket_io_handler import SocketIOHandler


def init_logger(socket):
    logger = logging.getLogger('BingXBot')
    socketio_handler = SocketIOHandler(socket)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    socketio_handler.setFormatter(formatter)
    socketio_handler.setLevel(logging.INFO)
    logger.addHandler(socketio_handler)
