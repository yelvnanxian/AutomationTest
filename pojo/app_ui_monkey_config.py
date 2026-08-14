"""作用：定义或承载app ui monkey config相关的数据结构。"""

#
# app_ui_monkey_config.py
# @description
# @created 2021-05-18T20:39:30.852Z+08:00
# @last-modified 2021-05-20T18:04:35.360Z+08:00

class APP_UI_Monkey_Config:
    def __init__(self) -> None:
        self.udid=None
        self.phone_ip=None
        self.phone_port=None
        self.package=None
        self.throttle=None
        self.event_times=None
