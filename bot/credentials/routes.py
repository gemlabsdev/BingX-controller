import json
import os

from .. import logger
from ..utils.credentials import Credentials
from ..credentials import bp
from flask import g, make_response, jsonify, request, current_app


@bp.route('/credentials/<exchange>/status', methods=['GET'])
def get_credential_status(exchange):
    credentials = get_credentials(exchange)
    firstTime = credentials.public_key == '' and credentials.private_key == ''
    user = 'NEW_USER' if firstTime else 'CURRENT_USER'
    response = make_response(jsonify({'user': user}))
    response.headers['Content-Type'] = "application/json"
    print(response)
    return exchange, 200


@bp.route('/credentials/<exchange>', methods=['POST'])
def post_credentials(exchange):
    credentials = get_credentials(exchange)
    firstTime = credentials.public_key == '' and credentials.private_key == ''
    new_credentials = json.loads(request.data)

    if new_credentials['private_key_current'] != credentials.private_key:
        response = make_response(jsonify({'status': 'WRONG_PRIVATE_KEY'}))
        response.headers['Content-Type'] = "application/json"
        logger.info(f'API Keys were not updated. Wrong Private Key.')

        return response, 403
    # TODO dont forget to change the payload here to send the exchagne
    save_credentials(new_credentials)
    logger.info(f'API Keys were successfully {"added" if firstTime else "updated"}')
    response = make_response(jsonify({'status': 'SUCCESS'}))
    response.headers['Content-Type'] = "application/json"

    return response, 200


def get_credentials(exchange):
    collection = g.mongo['keys_db']['keys']
    if (credentials := collection.find_one({"exchange": exchange})) is not None:
        print(credentials)
        return load_credentials(credentials)
    else:
        return create_new_empty_credentials(exchange, collection)


def load_credentials(credentials):
    _credentials = Credentials(credentials['public_key'],
                       credentials['private_key'],
                       credentials['exchange'])

    return _credentials


def create_new_empty_credentials(exchange):
    _credentials = {"public": '', "private": '', "exchange": exchange}
    save_credentials(_credentials)
    return _credentials


def save_credentials(credentials):
    collection = mongo.db[os.environ['COLLECTION_NAME']]
    new_keys = {"$set": {
        "public": credentials['public_key'] or '',
        "private": credentials['private_key'] or ''
    }}
    collection.update_one({"exchange": credentials.exchange}, new_keys)
