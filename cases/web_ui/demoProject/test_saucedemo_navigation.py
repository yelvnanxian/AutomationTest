# -*- coding:utf-8 -*-
"""作用：定义SauceDemo菜单和退出登录相关的自动化测试用例。"""

from page_objects.web_ui.demoProject.pages.page_inventory import InventoryPage
from page_objects.web_ui.demoProject.pages.page_login import LoginPage


class TestSauceDemoNavigation:
    # 用例目的：验证退出登录后会返回登录页并显示登录按钮。
    def test_logout_returns_to_login_page(self, logged_in_client):
        InventoryPage(logged_in_client.browserOperator).logout()

        login_page = LoginPage(logged_in_client.browserOperator)
        assert logged_in_client.browserOperator.get_current_url().endswith('/')
        assert logged_in_client.browserOperator.is_displayed(login_page.elements.login_button)
