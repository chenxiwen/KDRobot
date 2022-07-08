import time

class TimeUtil(object):
    @staticmethod
    def local_time_struct(timeStr) -> time:
        return time.localtime(int(timeStr)/1000)

    @staticmethod
    def format_time_second(timeStr) -> str:
        return time.strftime("%Y-%m-%d %H:%M:%S", TimeUtil.local_time_struct(timeStr))

    @staticmethod
    def format_time_milsecond(timeStr) -> str:
        milsecond = timeStr[-3:]
        return TimeUtil.format_time_second(timeStr)+":"+milsecond