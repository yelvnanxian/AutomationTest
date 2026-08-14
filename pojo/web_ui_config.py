# -*- coding:utf-8 -*-
"""作用：定义或承载web ui config相关的数据结构。"""

# 创建时间 2018/01/19 22:36
class WEB_UI_Config:
    def __init__(self):
        self.selenium_hub=None
        self.test_workers=None
        self.test_browsers=[]
        self.current_browser=None
        self.download_dir = None
        self.is_chrome_headless = None
        self.is_firefox_headless = None
