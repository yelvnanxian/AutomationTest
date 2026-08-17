# -*- coding:utf-8 -*-
"""作用：提供demoProject Web UI测试的通用浏览器和登录fixture。"""

import pytest

from base.web_ui.demoProject.web_ui_demo_project_client import WEB_UI_DemoProject_Client
from page_objects.web_ui.demoProject.pages.page_login import LoginPage
from test_data.web_ui.demoProject.saucedemo_test_data import STANDARD_USER


@pytest.fixture
def web_ui_client():
    """创建浏览器客户端，并在测试结束后释放浏览器资源。"""
    client = WEB_UI_DemoProject_Client()
    yield client
    client.browserOperator.close()


@pytest.fixture
def logged_in_client(web_ui_client):
    """创建已使用标准用户登录的浏览器客户端。"""
    LoginPage(web_ui_client.browserOperator).login(
        STANDARD_USER['username'],
        STANDARD_USER['password'],
    )
    return web_ui_client
