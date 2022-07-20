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


def text2content(txt):
    content = {
        "text": txt
    }
    return content
