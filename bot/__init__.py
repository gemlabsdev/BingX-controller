from flask_cors import CORS
from flask import Flask
from bingX.perpetual.v1 import Perpetual

from .config import Config
from .utils.cache import Cache
from .utils.logger import logger
from .utils.credentials import Credentials
from .utils.service import PerpetualService
from .utils.socket_io_handler import SocketIOHandler
from .db import mongo, store_user_credentials


def create_app():
    app = Flask(__name__, static_folder='../webapp/dist/')
    CORS(app)
    app.config.from_object(Config)

    with app.app_context():

        mongo.init_app(app)

        # Blueprint registration
        from .socketio import bp as socketio_bp
        app.register_blueprint(socketio_bp)

        from .main import bp as main_bp
        app.register_blueprint(main_bp)

        from .credentials import bp as credentials_bp
        app.register_blueprint(credentials_bp)

        from .logs import bp as logs_bp
        app.register_blueprint(logs_bp)



    return app
