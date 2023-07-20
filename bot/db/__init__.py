import os
from flask_pymongo import PyMongo
from flask import g
from ..utils.credentials import *

mongo = PyMongo()


def store_user_credentials():
    user_credentials = get_user_credentials()

    if 'user_credentials' not in g:
        g.user_credentials = user_credentials
    return g.user_credentials


def get_user_credentials():
    data = mongo.db[os.environ['COLLECTION_NAME']].find({})
    user_credentials = []
    for credential in data:
        exchange_credentials = ExchangeCredentials(public_key=credential['exchange']['public_key'],
                                                   private_key=credential['exchange']['private_key'])
        broker_credentials = BrokerCredentials(server=credential['broker']['server'],
                                               account=credential['broker']['account'],
                                               password=credential['broker']['password'],)
        user_credentials.append(Credentials(name=credential['name'],
                                            exchange_credentials=exchange_credentials,
                                            broker_credentials=broker_credentials))
    return user_credentials
