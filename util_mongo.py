import pymongo
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = os.getenv("MONGO_PORT")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PWD = os.getenv("MONGO_PWD")


class MongoUtil:
    def __init__(self):
        self.client = pymongo.MongoClient(host=MONGO_HOST, port=int(MONGO_PORT))

    def __getDB__(self):
        db = self.client[MONGO_DB]
        if MONGO_USER or MONGO_PWD:
            db.authenticate(name=MONGO_USER, password=MONGO_PWD)
        return db

    def __close__(self):
        self.client.close()
