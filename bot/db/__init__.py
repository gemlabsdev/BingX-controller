import os
from flask_pymongo import PyMongo
from flask import g
from ..utils.credentials import *

mongo = PyMongo()


def fetch_user_credentials(collection_name):
    user_credentials = get_user_credentials(collection_name)

    if 'user_credentials' not in g:
        g.user_credentials = user_credentials
    return g.user_credentials


def get_user_credentials(collection_name):
    data = mongo.db[collection_name].find({})
    user_credentials = []
    for credential in data:
        if collection_name == 'exchange':
            exchange_credentials = None if not collection_name == 'exchange' else ExchangeCredentials(
                public_key=credential['public_key'],
                private_key=credential['private_key'])
            user_credentials.append(Credentials(name=credential['name'], exchange_credentials=exchange_credentials))
        else:
            broker_credentials = None if not collection_name == 'broker' else BrokerCredentials(
                server=credential['server'],
                account=credential['account'],
                password=credential['password'], )
            user_credentials.append(Credentials(name=credential['name'], broker_credentials=broker_credentials))
    return user_credentials
