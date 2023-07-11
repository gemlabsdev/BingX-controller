import os
from flask import g
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv()
uri = f"mongodb+srv://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}@{os.environ['DB_HOST']}.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))

def get_db():
    if 'db' not in g:
        g.db = client[os.environ['DB_NAME']]


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    get_db()
    print('connected')


def init_db_connection(app):
    app.teardown_appcontext(close_db)
    init_db()
