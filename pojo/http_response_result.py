#-*- coding:utf8 -*-
"""作用：定义或承载http response result相关的数据结构。"""

class HttpResponseResult:
    def __init__(self):
        self.status_code=None
        self.body=None
        self.cookies=None
        self.headers=None
