#!/usr/bin/env python3.8

import os
import logging
import requests
from api import MessageApiClient
from event import MessageReceiveEvent, UrlVerificationEvent, EventManager, MessageReadEvent
from flask import Flask, jsonify
from dotenv import load_dotenv, find_dotenv

# load env parameters form file named .env
load_dotenv(find_dotenv())

app = Flask(__name__)

# load from env
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")
VERIFICATION_TOKEN = os.getenv("VERIFICATION_TOKEN")
ENCRYPT_KEY = os.getenv("ENCRYPT_KEY")
LARK_HOST = os.getenv("LARK_HOST")

# init service
message_api_client = MessageApiClient(APP_ID, APP_SECRET, LARK_HOST)
event_manager = EventManager()


@event_manager.register("url_verification")
def request_url_verify_handler(req_data: UrlVerificationEvent):
    # url verification, just need return challenge
    if req_data.event.token != VERIFICATION_TOKEN:
        raise Exception("VERIFICATION_TOKEN is invalid")
    return jsonify({"challenge": req_data.event.challenge})


@event_manager.register("im.message.receive_v1")
def message_receive_event_handler(req_data: MessageReceiveEvent):
    sender_id = req_data.event.sender.sender_id
    message = req_data.event.message
    if message.message_type != "text":
        logging.warn("Other types of messages have not been processed yet")
        return jsonify()
        # get open_id and text_content
    open_id = sender_id.open_id
    text_content = message.content
    print("MessageReceiveEvent:\n\topen_id="+open_id+"\n\tmessage_id="+message.message_id+"\n\tmessage_type="+message.message_type+"\n\tmessage_content="+text_content)
    # echo text message
    message_api_client.send_text_with_open_id(open_id, text_content)
    return jsonify()


@event_manager.register("im.message.message_read_v1")
def message_read_event_handler(req_data: MessageReadEvent):
    message_id_list = req_data.event.message_id_list
    read_time = req_data.event.reader.read_time
    reader_id = req_data.event.reader.reader_id
    open_id = reader_id.open_id
    print("MessageReadEvent:\n\topen_id="+open_id+"\n\tmessage_id_list="+str(message_id_list)+"\n\tread_time="+read_time)
    return jsonify()



@app.errorhandler
def msg_error_handler(ex):
    logging.error(ex)
    response = jsonify(message=str(ex))
    response.status_code = (
        ex.response.status_code if isinstance(ex, requests.HTTPError) else 500
    )
    return response


@app.route("/", methods=["POST"])
def callback_event_handler():
    # init callback instance and handle
    event_handler, event = event_manager.get_handler_with_event(VERIFICATION_TOKEN, ENCRYPT_KEY)

    return event_handler(event)

@app.route("/sendMsg/<open_id>/<msg>", methods=["POST", "GET"])
def sendMsg2Openid(open_id, msg):
    print(open_id, msg)
    message_api_client.send_text_with_open_id(open_id, '{"text":"'+msg+'"}')
    return jsonify()

@app.route("/sendGroupMsg/<chat_id>/<msg>", methods=["POST", "GET"])
def sendMsg2Chatid(chat_id, msg):
    print(chat_id, msg)
    message_api_client.send_text_with_chat_id(chat_id, '{"text":"'+msg+'"}')
    return jsonify()

@app.route("/getGroupChatList", methods=["GET"])
def getGroupChatList():
    resp = message_api_client.get_group_chat_list()
    return resp


if __name__ == "__main__":
    # init()
    app.run(host="0.0.0.0", port=44444, debug=True)
