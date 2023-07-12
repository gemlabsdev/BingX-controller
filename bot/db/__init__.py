import os
from flask_pymongo import PyMongo
from flask import g
from ..utils.credentials import Credentials

mongo = PyMongo()


def store_user_credentials():
    user_credentials = get_user_credentials()

    if 'user_credentials' not in g:
        g.user_credentials = user_credentials
        print(f"added {user_credentials} to global {g}")
    return g.user_credentials


def get_user_credentials():
    data = mongo.db[os.environ['COLLECTION_NAME']].find({})
    user_credentials = []
    for credential in data:
        user_credentials.append(Credentials(credential['public_key'],
                                            credential['private_key'],
                                            credential['exchange']))
    return user_credentials

