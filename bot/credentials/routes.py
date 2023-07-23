import json
import os

from .. import logger
from ..utils.credentials import Credentials, ExchangeCredentials, BrokerCredentials
from ..credentials import bp
from flask import make_response, jsonify, request, g
from ..db import mongo, fetch_user_credentials

db = mongo.db


# @bp.before_request
# def find_user_credentials():
#     fetch_user_credentials()

def extract_new_credentials(data: object, intermediary: str):
    new_credentials = None
    if intermediary == 'exchange':
        exchange_credentials = ExchangeCredentials(public_key=data['public_key'],
                                                   private_key=data['private_key'])

        new_credentials = Credentials(exchange_credentials=exchange_credentials, name=data['agent'])
        print(new_credentials.exchange_credentials.private_key)
    elif intermediary == 'broker':
        broker_credentials = BrokerCredentials(server=data['server'],
                                               account=data['account'],
                                               password=data['password'], )
        new_credentials = Credentials(broker_credentials=broker_credentials, name=data['agent'])
    return new_credentials


@bp.route('/credentials/<exchange>/status', methods=['GET'])
def get_credential_status(exchange: str):
    fetch_user_credentials()
    credentials = get_credentials(exchange)
    is_first_login = credentials.public_key == '' and credentials.private_key == ''
    user = 'NEW_USER' if is_first_login else 'CURRENT_USER'
    response = jsonify({'user': user})
    response.status_code = 200

    return response


@bp.route('/credentials/<intermediary>/<agent>', methods=['POST'])
def post_credentials(intermediary: str, agent: str):
    fetch_user_credentials(intermediary)
    data = json.loads(request.data)
    new_credentials = extract_new_credentials(data, intermediary)
    existing_credentials = get_credentials(intermediary, agent)
    print(existing_credentials)
    if existing_credentials is None:
        create_credentials(new_credentials, intermediary)
        return 'SUCCESS'
    # is_first_login = credentials.public_key == '' and credentials.private_key == '' and credentials.access_token == ''
    # is_wrong_private_key = data['private_key_current'] != credentials.private_key
    # is_blank_credential = credentials.public_key == '' or credentials.private_key == ''
    #
    # if is_wrong_private_key and not is_first_login:
    #     response = make_response(jsonify({'status': 'WRONG_PRIVATE_KEY'}))
    #     response.headers['Content-Type'] = "application/json"
    #     logger.info(f'API Keys were not updated. Wrong Private Key.')
    #
    #     return response, 403
    #
    # if is_blank_credential and not is_first_login:
    #     response = make_response(jsonify({'status': 'NO_EMPTY_KEYS'}))
    #     response.headers['Content-Type'] = "application/json"
    #     logger.info(f'API Keys were not updated. Empty keys are not allowed.')
    #
    #     return response, 403

    update_credentials(new_credentials, intermediary)
    # logger.info(f'API Keys were successfully {"added" if is_first_login else "updated"}')
    response = make_response(jsonify({'status': 'SUCCESS'}))
    response.headers['Content-Type'] = "application/json"

    return response, 200


def get_credentials(intermediary: str, agent: str):
    credentials = next((credential for credential in g.user_credentials if credential.name == agent), None)
    if credentials is not None:
        return credentials
    else:
        return None


def update_credentials(credentials: Credentials, collection: str):
    new_keys = {"$set": {}}
    if collection == 'exchange':
        new_keys = {"$set": {
            "public_key": credentials.exchange_credentials.public_key,
            "private_key": credentials.exchange_credentials.private_key,
        }}
    elif collection == 'broker':
        new_keys = {"$set": {
            "server": credentials.broker_credentials.server,
            "account": credentials.broker_credentials.account,
            "password": credentials.broker_credentials.password
        }}
    else:
        return
    db[collection].update_one({"name": credentials.name}, new_keys)


def create_credentials(credentials: Credentials, collection: str):
    if collection == 'exchange':
        db[collection].insert_one({"name": credentials.name,
                                   "public_key": credentials.exchange_credentials.public_key,
                                   "private_key": credentials.exchange_credentials.private_key,
                                   })
    if collection == 'broker':
        db[collection].insert_one({"name": credentials.name,
                                   "server": credentials.broker_credentials.server,
                                   "account": credentials.broker_credentials.account,
                                   "password": credentials.broker_credentials.password
                                   })
    return
