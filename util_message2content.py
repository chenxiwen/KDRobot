import datetime


def fswj_url2content(txt):
    content = {
        "zh_cn": {
            "content": [
                [{
                    "tag": "a",
                    "href": txt,
                    "text": (datetime.datetime.now() + datetime.timedelta(days=1)).strftime(
                        "%m月%d日") + "平台技术部信息统计（全员填写）"
                }]
            ]
        }
    }
    return content


def url2content(txt, url, url_text):
    content = {}
    if url is None or len(url) == 0:
        content = {
            "zh_cn": {
                "content": [
                    [
                        {
                            "tag": "text",
                            "text": txt,
                        }
                    ]
                ]
            }
        }
    else:
        content = {
            "zh_cn": {
                "content": [
                    [
                        {
                            "tag": "text",
                            "text": txt,
                        }
                    ],
                    [{
                        "tag": "a",
                        "href": url,
                        "text": url_text
                    }]
                ]
            }
        }
    return content


def url2contentWithAt(users, txt, url, url_text):
    notify_msg = []
    if len(users) != 0:
        for user in users:
            at_info = {}
            if user["open_id"] == "":
                at_info = {
                    "tag": "at",
                    "user_id": "",
                    "user_name": user["name"],
                }
            else:
                at_info = {
                    "tag": "at",
                    "user_id": user["open_id"],
                    "user_name": user["name"],
                }
            notify_msg.append(at_info)
    notify_msg.append({
        "tag": "text",
        "text": txt,
    })

    content = {}
    if url is None or len(url) == 0:
        content = {
            "zh_cn": {
                "content": notify_msg
            }
        }
    else:
        content = {
            "zh_cn": {
                "content": [
                    notify_msg,
                    [{
                        "tag": "a",
                        "href": url,
                        "text": url_text
                    }]
                ]
            }
        }
    return content


def text2content(txt):
    content = {
        "text": txt
    }
    return content
