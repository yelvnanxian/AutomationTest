#-*- coding:utf8 -*-
"""作用：定义或承载httpResponseResult相关的数据结构。"""

# 创建时间 2018/01/19 22:36
class HttpResponseResult:
    def __init__(self):
        self.status_code=None
        self.body=None
        self.cookies=None
        self.headers=None
