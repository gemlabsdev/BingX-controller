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




def create_app():
    app = Flask(__name__, static_folder='../webapp/dist/')
    CORS(app)
    app.config.from_object(Config)
    app.app_context().push()

    # Initialize MongoDB client
    mongo_client = MongoClient(app.config['MONGO_URI'])

    # Add the MongoDB client to the Flask app context
    g.mongo = mongo_client
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

    # @app.route('/user', methods=['GET'])
    # def get_key_status():
    #     firstTime = Key.public_key == "" or Key.private_key == ""
    #     user = 'NEW_USER' if firstTime else 'CURRENT_USER'
    #     response = make_response(jsonify({'user': user}))
    #     response.headers['Content-Type'] = "application/json"
    #
    #     return response, 200

    # @app.route('/keys', methods=['POST'])
    # def set_keys():
    #     firstTime = Key.public_key == "" or Key.private_key == ""
    #     data = json.loads(request.data)
    #     if not firstTime:
    #         if data['private_current'] != Key.private_key:
    #             response = make_response(jsonify({'status': 'WRONG_PRIVATE_KEY'}))
    #             response.headers['Content-Type'] = "application/json"
    #             logger.info(f'API Keys were not updated. Wrong Private Key.')
    #
    #             return response, 403
    #
    #     Key.public_key = data['public']
    #     Key.private_key = data['private']
    #     # save_keys(Key.public_key, Key.private_key)
    #     logger.info(f'API Keys were successfully {"added" if firstTime else "updated"}')
    #     response = make_response(jsonify({'status': 'SUCCESS'}))
    #     response.headers['Content-Type'] = "application/json"
    #
    #     return response, 200

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

    # @app.route('/perpetual/positions', methods=['POST'])
    # def get_open_positions():
    #     client = get_client()
    #     data = json.loads(request.data)
    #     service = PerpetualService(client=client,
    #                                symbol=data['symbol'])
    #     response = service.get_open_positions_api()
    #     return response

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

    @app.before_request
    def set_attr():
        g.mongo = mongo_client

    return app
