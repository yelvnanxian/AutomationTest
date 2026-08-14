# -*- coding:utf-8 -*-
"""作用：封装web ui demoProject client客户端的连接和访问能力。"""

from base.web_ui.demoProject.web_ui_demo_project_read_config import WEB_UI_DemoProject_Read_Config
from base.read_web_ui_config import Read_WEB_UI_Config
from common.selenium.browser_operator import BrowserOperator
from common.selenium.driver_tool import DriverTool
class WEB_UI_DemoProject_Client:
    def __init__(self):
        self.config=Read_WEB_UI_Config().web_ui_config
        self.demo_project_config=WEB_UI_DemoProject_Read_Config().config

        self.driver = DriverTool.get_driver(self.config.selenium_hub, self.config.current_browser)
        self.driver.get(self.demo_project_config.web_host + '/')
        self.browserOperator = BrowserOperator(self.driver)
