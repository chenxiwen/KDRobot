#!/usr/bin/env python3.8

import os
import logging
import requests
from event import MessageReceiveEvent, UrlVerificationEvent, EventManager, MessageReadEvent, RobotAddedEvent, \
    RobotDeletedEvent
from flask import Flask, jsonify, request
from dotenv import load_dotenv, find_dotenv
from ender import TimeUtil
from robot_scheduler import scheduler
import util_message2content, message_handler
from util_message_client import message_api_client
import json
from Result import Result

# load env parameters form file named .env
load_dotenv(find_dotenv())

app = Flask(__name__)

# load from env

VERIFICATION_TOKEN = os.getenv("VERIFICATION_TOKEN")
ENCRYPT_KEY = os.getenv("ENCRYPT_KEY")

ROBOT_YXO_OPEN_ID = os.getenv("ROBOT_YXO_OPEN_ID")
ROBOT_YXO_RELAY_PREFIX = os.getenv("ROBOT_YXO_RELAY_PREFIX")
ROBOT_PTJSB_CHAT_ID = os.getenv("ROBOT_PTJSB_CHAT_ID")

# init handler

event_manager = EventManager()


@event_manager.register("url_verification")
def request_url_verify_handler(req_data: UrlVerificationEvent):
    # url verification, just need return challenge
    if req_data.event.token != VERIFICATION_TOKEN:
        raise Exception("VERIFICATION_TOKEN is invalid")
    return jsonify({"challenge": req_data.event.challenge})


@event_manager.register("im.message.receive_v1")
def message_receive_event_handler(req_data: MessageReceiveEvent):
    # print(req_data)
    sender_id = req_data.event.sender.sender_id
    message = req_data.event.message
    if message.message_type != "text":
        logging.warn("Other types of messages have not been processed yet")
        return jsonify()
    if message.chat_type != "p2p":
        logging.warn("only p2p messages have been processed yet")
        return jsonify()
    # get open_id and text_content
    message_time = TimeUtil.format_time_milsecond(message.create_time)
    open_id = sender_id.open_id
    text_content = message.content
    create_time = message.create_time
    print(
        "MessageReceiveEvent:\n\topen_id=" + open_id + "\n\tmessage_id=" + message.message_id + "\n\tmessage_type=" + message.message_type + "\n\tmessage_content=" + text_content + "\n\tmessage_time=" + message_time)
    # echo text message

    text_content = json.loads(text_content)["text"]

    # create relay msg
    if open_id == ROBOT_YXO_OPEN_ID and text_content.startswith(ROBOT_YXO_RELAY_PREFIX):
        # create relay msg
        fswj_url = text_content[text_content.index(
            ROBOT_YXO_RELAY_PREFIX) + len(ROBOT_YXO_RELAY_PREFIX):]
        message_handler.save_relay_msg('post', 'chat_id', ROBOT_PTJSB_CHAT_ID,
                                       util_message2content.fswj_url2content(fswj_url),
                                       'open_id', open_id, create_time)
        message_api_client.send_text_with_open_id(open_id,
                                                  json.dumps(
                                                      util_message2content.text2content("问卷预计于明日6点30转发至平台技术部群组")))
    else:
        message_api_client.send_text_with_open_id(open_id, json.dumps(
            util_message2content.text2content("个人回复暂未开放")))
    return jsonify()


@event_manager.register("im.message.message_read_v1")
def message_read_event_handler(req_data: MessageReadEvent):
    message_id_list = req_data.event.message_id_list
    read_time = TimeUtil.format_time_milsecond(req_data.event.reader.read_time)
    reader_id = req_data.event.reader.reader_id
    open_id = reader_id.open_id
    print("MessageReadEvent:\n\topen_id=" + open_id + "\n\tmessage_id_list=" + str(
        message_id_list) + "\n\tread_time=" + read_time)
    return jsonify()


@event_manager.register("im.chat.member.bot.added_v1")
def robot_added_event_handler(req_data: RobotAddedEvent):
    header = req_data.header
    event_time = TimeUtil.format_time_milsecond(header.create_time)
    group_chat_id = req_data.event.chat_id
    operator_id = req_data.event.operator_id
    print(
        "RobotAddedEvent:\n\tevent_time=" + event_time + "\n\tgroup_chat_id=" + group_chat_id + "\n\tuser_id=" + operator_id.user_id + "\n\tunion_id=" + operator_id.union_id + "\n\topen_id=" + operator_id.open_id)
    return jsonify()


@event_manager.register("im.chat.member.bot.deleted_v1")
def robot_deleted_event_handler(req_data: RobotDeletedEvent):
    header = req_data.header
    event_time = TimeUtil.format_time_milsecond(header.create_time)
    group_chat_id = req_data.event.chat_id
    operator_id = req_data.event.operator_id
    print(
        "RobotDeletedEvent:\n\tevent_time=" + event_time + "\n\tgroup_chat_id=" + group_chat_id + "\n\tuser_id=" + operator_id.user_id + "\n\tunion_id=" + operator_id.union_id + "\n\topen_id=" + operator_id.open_id)
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


@app.route("/sendMsg/<open_id>/<msg>",
           methods=["POST", "GET"])  # http://39.96.51.65:44444/sendMsg/ou_53721b31602889f3d7cb4a9cb5ff5928/ender123
def sendMsg2Openid(open_id, msg):
    print(open_id, msg)
    message_api_client.send_text_with_open_id(open_id, '{"text":"' + msg + '"}')
    return jsonify()


@app.route("/sendGroupMsg/<chat_id>/<msg>", methods=["POST",
                                                     "GET"])  # http://39.96.51.65:44444/sendGroupMsg/oc_b2a4730ae0221061bad7e67f3b71e4ca/%E6%B5%8B%E8%AF%95%E5%B7%B2%E8%AF%BB%E5%9B%9E%E8%B0%83
def sendMsg2Chatid(chat_id, msg):
    print(chat_id, msg)
    message_api_client.send_text_with_chat_id(chat_id, '{"text":"' + msg + '"}')
    return jsonify()


@app.route("/getGroupChatList", methods=["GET"])  # http://39.96.51.65:44444/getGroupChatList
def getGroupChatList():
    resp = message_api_client.get_group_chat_list()
    return resp


@app.route("/message/group/notify", methods=["POST"])
def sendGroupMsg():
    authHeader = request.headers.get("KD_ROBOT")
    if authHeader is None or len(authHeader) == 0 or authHeader != 'KD_ROBOT_KD':
        logging.warn("no permission to access")
        return Result(-1, "need auth").standard_format()
    chat_id = request.values.get("chat_id")
    msg = request.values.get("msg")
    url = request.values.get("url")
    url_text = request.values.get("url_text")
    try:
        message_api_client.send("chat_id", chat_id, "post",
                                json.dumps(util_message2content.url2content(msg, url, url_text)))
    except Exception as e:
        logging.error(e)
        return Result(-2, e.__str__()).standard_format()
    return Result(0, "success").standard_format()


@app.route("/message/user/notify", methods=["POST"])
def sendEpidemicMsg2User():
    # 测试给lt
    authHeader = request.headers.get("KD_ROBOT")
    if authHeader is None or len(authHeader) == 0 or authHeader != 'KD_ROBOT_KD':
        logging.warn("no permission to access")
        return Result(-1, "need auth").standard_format()
    open_id = request.values.get("open_id")
    msg = request.values.get("msg")
    url = request.values.get("url")
    url_text = request.values.get("url_text")
    try:
        message_api_client.send("open_id", open_id, "post",
                                json.dumps(util_message2content.url2content(msg, url, url_text)))
    except Exception as e:
        logging.error(e)
        return Result(-2, e.__str__()).standard_format()
    return Result(0, "success").standard_format()


if __name__ == "__main__":
    # init()

    # 注册定时器
    scheduler.init_app(app)
    scheduler.start()

    app.run(host="0.0.0.0", port=8888, debug=True, use_reloader=False)
