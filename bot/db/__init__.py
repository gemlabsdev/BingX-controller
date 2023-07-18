import os
from flask_pymongo import PyMongo
from flask import g
from ..utils.credentials import Credentials

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
        user_credentials.append(Credentials(public_key=credential['public_key'] or None,
                                            private_key=credential['private_key'] or None,
                                            access_token=credential['access_token'] or None,
                                            account_id=credential['account_id'] or None,
                                            exchange=credential['exchange'] or None))
        print(user_credentials[0].account_id)
        print(user_credentials[0].access_token)
    return user_credentials
