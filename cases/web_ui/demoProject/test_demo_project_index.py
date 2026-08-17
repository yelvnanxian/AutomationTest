# -*- coding:utf8 -*-
"""作用：定义demoProject index相关的自动化测试用例。"""

import pytest

from base.web_ui.demoProject.web_ui_demo_project_client import WEB_UI_DemoProject_Client
from base.web_ui.demoProject.web_ui_demo_project_read_config import WEB_UI_DemoProject_Read_Config
from page_objects.web_ui.demoProject.pages.page_index import IndexPage
from common.hamcrest.hamcrest import assert_that


pytestmark = pytest.mark.skipif(
    not WEB_UI_DemoProject_Read_Config().config.web_host.rstrip('/').endswith('baidu.com'),
    reason='旧版百度用例仅适用于百度 web_host 配置，当前项目配置为 SauceDemo。',
)


class TestIndex:
    def setup_class(self):
        self.demoProjectClient = WEB_UI_DemoProject_Client()
        self.indexPage=IndexPage(self.demoProjectClient.browserOperator)

    # 用例目的：验证百度首页输入空关键字后仍停留在首页。
    def test_search_empty_kw(self):
        self.indexPage.search_kw('')
        assert_that(self.indexPage.getElements().title.wait_expected_value).is_equal_to(self.demoProjectClient.browserOperator.getTitle())

    # 用例目的：验证百度首页输入关键字后可以进入对应搜索结果页。
    def test_search_kw(self):
        self.indexPage.search_kw('apitest')
        assert_that('apitest_百度搜索').is_equal_to(self.demoProjectClient.browserOperator.getTitle())

    def teardown_class(self):
        self.demoProjectClient.browserOperator.close()
