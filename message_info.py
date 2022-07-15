import datetime

mongo_col_name = "robot_message"


class RobotMessage:
    def __init__(self, msg_type, receive_id_type, receive_id, content, sender_id_type, sender_id):
        self.msg_type = ""
        self.receive_id_type = ""
        self.receive_id = ""
        self.content = ""
        self.sender_id_type = ""
        self.sender_id = ""
        self.sender_time = datetime.datetime.now()
        self.operate_result = ""
        self.msg_status = 0
