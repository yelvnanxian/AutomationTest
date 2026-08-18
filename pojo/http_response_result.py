# -*- coding:utf-8 -*-
"""作用：统一承载HTTP响应、请求摘要和性能数据。"""

import json


class HttpResponseResult:
    def __init__(self):
        self.status_code = None
        self.body = None
        self.cookies = None
        self.headers = None
        self.headers_dict = {}
        self.elapsed_ms = None
        self.url = None
        self.request_method = None
        self.request_headers = {}
        self.request_body = None

    def json(self):
        """将响应正文解析为JSON，解析失败时保留标准JSON异常。"""
        return json.loads(self.body)
