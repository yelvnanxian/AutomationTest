"""作用：定义或承载report config相关的数据结构。"""


class Report_Config:
    def __init__(self):
        self.api_port = None
        self.app_ui_start_port = None
        self.web_ui_ie_port = None
        self.web_ui_firefox_port = None
        self.web_ui_chrome_port = None
