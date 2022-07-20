#! /usr/bin/env python3.8
import json
import os
import logging
import requests

APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")

# const
TENANT_ACCESS_TOKEN_URI = "/open-apis/auth/v3/tenant_access_token/internal"
MESSAGE_URI = "/open-apis/im/v1/messages"
GROUP_MEMBER_LIST = "/open-apis/im/v1/chats/{}/members"
USER_INFO = "/open-apis/contact/v3/users/{}"

proxies = {
    "http": "http://11.8.32.43:404",
    "https": "http://11.8.32.43:404"
}


class MessageApiClient(object):
    def __init__(self, app_id, app_secret, lark_host):
        self._app_id = app_id
        self._app_secret = app_secret
        self._lark_host = lark_host
        self._tenant_access_token = ""

    @property
    def tenant_access_token(self):
        return self._tenant_access_token

    def send_text_with_open_id(self, open_id, content):
        self.send("open_id", open_id, "text", content)

    def send_text_with_chat_id(self, chat_id, content):
        self.send("chat_id", chat_id, "text", content)

    def send(self, receive_id_type, receive_id, msg_type, content):
        # send message to user, implemented based on Feishu open api capability. doc link: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/create
        self._authorize_tenant_access_token()
        url = "{}{}?receive_id_type={}".format(
            self._lark_host, MESSAGE_URI, receive_id_type
        )
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": "Bearer " + self.tenant_access_token,
        }
        req_body = {
            "receive_id": receive_id,
            "content": content,
            "msg_type": msg_type,
        }
        print(url, headers, req_body)
        resp = requests.post(url=url, headers=headers, json=req_body)
        MessageApiClient._check_error_response(resp)
        return resp

    def _authorize_tenant_access_token(self):
        # get tenant_access_token and set, implemented based on Feishu open api capability. doc link: https://open.feishu.cn/document/ukTMukTMukTM/ukDNz4SO0MjL5QzM/auth-v3/auth/tenant_access_token_internal
        url = "{}{}".format(self._lark_host, TENANT_ACCESS_TOKEN_URI)
        req_body = {"app_id": self._app_id, "app_secret": self._app_secret}
        response = requests.post(url, req_body)
        MessageApiClient._check_error_response(response)
        self._tenant_access_token = response.json().get("tenant_access_token")

    def get_group_chat_list(self):
        self._authorize_tenant_access_token()
        url = "https://open.feishu.cn/open-apis/im/v1/chats"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.tenant_access_token,
        }
        resp = requests.get(url=url, headers=headers)
        MessageApiClient._check_error_response(resp)
        print(resp.json())
        return resp.json()

    def get_group_member_list(self, chat_id, page_token):
        self._authorize_tenant_access_token()
        url = (self._lark_host + GROUP_MEMBER_LIST).format(chat_id)
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.tenant_access_token,
        }
        params = {
            "member_id_type": "open_id",
            "page_token": page_token,
            "page_size": 100
        }
        resp = requests.get(url=url, headers=headers, params=params)
        MessageApiClient._check_error_response(resp)
        return resp

    def get_user_by_open_id(self, open_id):
        self._authorize_tenant_access_token()
        url = (self._lark_host + USER_INFO).format(open_id)
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.tenant_access_token,
        }
        params = {
            "user_id_type": "open_id"
        }
        resp = requests.get(url=url, headers=headers, params=params)
        MessageApiClient._check_error_response(resp)
        return resp

    @staticmethod
    def _check_error_response(resp):
        # check if the response contains error information
        if resp.status_code != 200:
            resp.raise_for_status()
        response_dict = resp.json()
        code = response_dict.get("code", -1)
        if code != 0:
            logging.error(response_dict)
            raise LarkException(code=code, msg=response_dict.get("msg"))


class LarkException(Exception):
    def __init__(self, code=0, msg=None):
        self.code = code
        self.msg = msg

    def __str__(self) -> str:
        return "{}:{}".format(self.code, self.msg)

    __repr__ = __str__
