import json
import os

from dotenv import load_dotenv
from flask_cors import CORS
from flask import Flask, request, make_response, jsonify, g
from bingX.perpetual.v1 import Perpetual
from pymongo import MongoClient

from .config import Config
from .utils.cache import Cache
from .utils.logger import logger
from .utils.credentials import Credentials
from .utils.service import PerpetualService
from .utils.socket_io_handler import SocketIOHandler
from .db import mongo

def create_app():
    app = Flask(__name__, static_folder='../webapp/dist/')
    CORS(app)
    app.config.from_object(Config)
    app.app_context().push()
    # Add the MongoDB client to the Flask app context
    mongo.init_app(app)

    # Blueprint registration
    from .socketio import bp as socketio_bp
    app.register_blueprint(socketio_bp)

    from .main import bp as main_bp
    app.register_blueprint(main_bp)

    from .credentials import bp as credentials_bp
    app.register_blueprint(credentials_bp)

    # def get_client():
    #     if 'client' not in g:
    #         # g.client = Perpetual(Key.public_key, Key.private_key)
    #
    #     return g.client

    @app.route('/perpetual/trade', methods=['POST'])
    def perpetual_order():
        client = get_client()
        data = json.loads(request.data)
        service = PerpetualService(client=client,
                                   symbol=data['symbol'],
                                   side=data['side'],
                                   action=data['action'],
                                   quantity=data['quantity'],
                                   trade_type=data['trade_type'],
                                   leverage=data['leverage'] if 'leverage' in data else 1)
        if data['action'] == 'Open':
            return service.open_trade()
        if data['action'] == 'Close':
            return service.close_trade()

    @app.route('/perpetual/dump', methods=['POST'])
    def clear_cache():
        Cache.clear_cache()
        return 'CACHE CLEARED'

    @app.route('/logs', methods=['GET'])
    def get_logs():
        with open('logs.log', 'r') as f:
            logs = f.read()
        return logs

    @app.route('/logs', methods=['DELETE'])
    def delete_logs():
        with open('logs.log', 'w') as f:
            f.close()
        return {'status': 'DELETED'}

    return app
