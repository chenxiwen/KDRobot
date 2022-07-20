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
user_col_name = "chat_users"
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


def send_msg_notify_with_at(users, chat_id, msg, url, url_text):
    user_list = []
    if users is not None:
        user_list = json.loads(users)
    user_employees = [user["employee"] for user in user_list]
    col = mongo_db[message_col_name]
    datas = col.find({'employee': {"$in": user_employees}})
    mongo_datas = []
    for item in datas:
        mongo_datas.append(item)
    for user in user_list:
        user["open_id"] = ""
        for item in mongo_datas:
            if user["employee"] == item["employee"]:
                user["open_id"] = item["open_id"]
                user["name"] = item["name"]

    print(json.dumps(util_message2content.url2contentWithAt(user_list, msg, url, url_text)))
    message_api_client.send("chat_id", chat_id, "post",
                            json.dumps(util_message2content.url2contentWithAt(user_list, msg, url, url_text)))


# 将群组中的用户信息保存
def initChatUsers(chat_id):
    logging.info("begin to init chat user ")
    page_token = ""
    try:
        user_id_list = []
        user_list = []
        user_save_list = []
        while True:
            resp = message_api_client.get_group_member_list(chat_id, page_token)
            if resp.status_code != 200:
                resp.raise_for_status()
            response_dict = resp.json()
            code = response_dict.get("code", -1)
            if code != 0:
                logging.warn("failed get chat member list")
            data = response_dict["data"]
            page_token = data["page_token"]
            users = data["items"]
            for user in users:
                user_id_list.append(user["member_id"])
            if page_token == "":
                logging.info("no more user for query")
                break
        for open_id in user_id_list:
            resp = message_api_client.get_user_by_open_id(open_id)
            if resp.status_code != 200:
                resp.raise_for_status()
            response_dict = resp.json()
            code = response_dict.get("code", -1)
            if code != 0:
                logging.warn("failed get chat member list")
            user = response_dict["data"]["user"]
            user_info = {
                "open_id": open_id,
                "name": user["name"],
                "employee": user["employee_no"]
            }
            user_list.append(user_info)

        col = mongo_db[message_col_name]
        datas = col.find()
        mongo_datas = []
        for item in datas:
            mongo_datas.append(item)
        for user in user_list:
            find = False
            for item in mongo_datas:
                if item["open_id"] == user["open_id"]:
                    find = True
            if find is not True:
                user_save_list.append(user)
        if user_save_list.__len__() != 0:
            col.insert_many(user_save_list)
        else:
            logging.info("no chat user need to save")
        # print(json.dumps(util_message2content.url2contentWithAt(user_list, "xxx", "http://www.baidu.com", "xxxaaa")))
    except Exception as e:
        logging.error(e)
        print(e)
        raise e
