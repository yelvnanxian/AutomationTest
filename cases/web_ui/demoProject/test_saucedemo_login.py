# -*- coding:utf-8 -*-
"""作用：定义saucedemo login相关的自动化测试用例。"""

from base.web_ui.demoProject.web_ui_demo_project_client import WEB_UI_DemoProject_Client
from page_objects.web_ui.demoProject.pages.login_page import LoginPage


class TestSauceDemoLogin:
    def setup_method(self):
        self.client = WEB_UI_DemoProject_Client()
        self.login_page = LoginPage(self.client.browserOperator)

    def teardown_method(self):
        self.client.browserOperator.close()

    def test_standard_user_login_success(self):
        self.login_page.login('standard_user', 'secret_sauce')

        current_url = self.client.browserOperator.get_current_url()
        assert current_url.endswith('/inventory.html')

    def test_locked_out_user_login_failed(self):
        self.login_page.login('locked_out_user', 'secret_sauce')

        error_message = self.login_page.get_error_message()
        assert 'Sorry, this user has been locked out' in error_message
