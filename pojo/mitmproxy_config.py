"""作用：定义或承载mitmproxy config相关的数据结构。"""


class Mitmproxy_Config:
    def __init__(self):
        self.proxy_port=None
        self.ssl_insecure=None
