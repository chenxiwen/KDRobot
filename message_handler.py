import time

from util_mongo import MongoUtil
from util_message_client import message_api_client
import datetime
from ender import TimeUtil
import json
import util_message2content
import logging

mongo_db = MongoUtil().__getDB__()
message_col_name = "robot_message"
logging.basicConfig(level=logging.DEBUG)


def save_relay_msg(msg_type, receive_id_type, receive_id, content, sender_id_type, sender_id, create_time):
    msg = {
        "msg_type": msg_type,
        "receive_id_type": receive_id_type,
        "receive_id": receive_id,
        "content": content,
        "sender_id_type": sender_id_type,
        "sender_id": sender_id,
        "sender_time": TimeUtil.parse_time_second(create_time),
        "operate_result": "",
        "msg_status": 0
    }
    col = mongo_db[message_col_name]
    col.insert_one(msg)


def send_no_relay_msg():
    col = mongo_db[message_col_name]
    datas = col.find({'msg_status': 0})
    if datas.count() == 0:
        logging.info("no message need to relay ")
    else:
        for item in datas:
            msg_id = item["_id"]
            receive_id_type = item["receive_id_type"]
            receive_id = item["receive_id"]
            msg_type = item['msg_type']
            content = item['content']
            result = ""
            try:
                result = message_api_client.send(receive_id_type, receive_id, msg_type, json.dumps(content))
                result = "success operate"
            except Exception as e:
                logging.error(e)
                result = "happened exception " + e.__str__()
                message_api_client.send(item["sender_id_type"], item["sender_id"], 'text',
                                        json.dumps(util_message2content.text2content("飞书问卷转发失败，请尽快自行补充转发")))
            finally:
                # item["msg_status"] = 0  # 测试用
                item["msg_status"] = 1
                item["operate_result"] = result
                item["msg_send_time"] = datetime.datetime.now()
                col.update_one({"_id": msg_id}, {"$set": item})
