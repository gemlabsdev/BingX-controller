import logging
from logging.handlers import RotatingFileHandler
from flask_socketio import emit

logger = logging.getLogger('BingXBot')
logger.propagate = False
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

file_handler = RotatingFileHandler('logs.log', maxBytes=5 * 1024 * 1024, backupCount=1)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


