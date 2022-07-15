import datetime
from flask_apscheduler import APScheduler
import message_handler

scheduler = APScheduler()


# @scheduler.task('cron', id='print_msg_1', second="*/2")
# def job():
# print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " -- print msg -- ")


# @scheduler.task('cron', id='print_msg_2', second="*/10")
# def job2():
#     print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " test send info ")
#     message_handler.send_no_relay_msg()


# 发送飞书问卷
@scheduler.task('cron', id='relay_fswj', hour="6", minute="30")
def relay_fswj():
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " begin to relay fswj ")
    message_handler.send_no_relay_msg()
