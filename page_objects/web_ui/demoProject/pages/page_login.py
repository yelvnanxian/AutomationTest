# -*- coding:utf-8 -*-
"""作用：封装SauceDemo登录页面的用户操作和状态读取。"""

from page_objects.web_ui.demoProject.elements.page_login_elements import LoginPageElements


class LoginPage:
    def __init__(self, browser_operator):
        self.browser = browser_operator
        self.elements = LoginPageElements()

    def login(self, username, password):
        self.browser.sendText(self.elements.username, username)
        self.browser.sendText(self.elements.password, password)
        self.browser.click(self.elements.login_button)

    def get_error_message(self):
        return self.browser.getText(self.elements.error_message)
