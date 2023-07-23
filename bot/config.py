import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()


class Config:
    MONGO_URI = f"mongodb+srv://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}@{os.environ['DB_HOST']}.mongodb.net/credentials_db?retryWrites=true&w=majority"


