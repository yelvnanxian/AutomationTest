#-*- coding:utf8 -*-
"""作用：定义或承载element info相关的数据结构。"""

class ElementInfo:
    def __init__(self):
        self.locator_type=None
        self.locator_value=None
        self.expected_value=None
        self.wait_type=None
        self.wait_seconds=None
        self.wait_expected_value=None
