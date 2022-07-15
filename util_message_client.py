import os
from api import MessageApiClient
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")
LARK_HOST = os.getenv("LARK_HOST")
message_api_client = MessageApiClient(APP_ID, APP_SECRET, LARK_HOST)
