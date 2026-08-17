# -*- coding:utf-8 -*-
"""作用：定义saucedemo login相关的自动化测试用例。"""

from page_objects.web_ui.demoProject.pages.page_login import LoginPage
from test_data.web_ui.demoProject.saucedemo_test_data import (
    INVALID_PASSWORD,
    LOCKED_OUT_USER,
    STANDARD_USER,
)


class TestSauceDemoLogin:
    # 用例目的：验证标准用户可以使用正确凭据登录商品列表页。
    def test_standard_user_login_success(self, web_ui_client):
        login_page = LoginPage(web_ui_client.browserOperator)
        login_page.login(**STANDARD_USER)

        current_url = web_ui_client.browserOperator.get_current_url()
        assert current_url.endswith('/inventory.html')

    # 用例目的：验证被锁定用户登录时会显示锁定提示。
    def test_locked_out_user_login_failed(self, web_ui_client):
        login_page = LoginPage(web_ui_client.browserOperator)
        login_page.login(**LOCKED_OUT_USER)

        error_message = login_page.get_error_message()
        assert 'Sorry, this user has been locked out' in error_message

    # 用例目的：验证用户名或密码错误时会显示凭据错误提示。
    def test_invalid_credentials_login_failed(self, web_ui_client):
        login_page = LoginPage(web_ui_client.browserOperator)
        login_page.login(STANDARD_USER['username'], INVALID_PASSWORD)

        error_message = login_page.get_error_message()
        assert 'Username and password do not match' in error_message

    # 用例目的：验证未填写用户名时会显示用户名必填提示。
    def test_login_requires_username(self, web_ui_client):
        login_page = LoginPage(web_ui_client.browserOperator)
        login_page.login('', STANDARD_USER['password'])

        error_message = login_page.get_error_message()
        assert 'Username is required' in error_message
