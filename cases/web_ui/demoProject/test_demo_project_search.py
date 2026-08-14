# -*- coding:utf8 -*-
"""作用：定义demoProject search相关的自动化测试用例。"""

from base.web_ui.demoProject.web_ui_demo_project_client import WEB_UI_DemoProject_Client
from page_objects.web_ui.demoProject.pages.index_page import IndexPage
from common.hamcrest.hamcrest import assert_that
class TestIndex:
    def setup_class(self):
        self.demoProjectClient = WEB_UI_DemoProject_Client()
        self.searchPage=IndexPage(self.demoProjectClient.browserOperator).search_kw('apitest')

    def test_search_kw(self):
        self.searchPage.search_kw('apitest12')
        assert_that('apitest12_百度搜索').is_equal_to(self.demoProjectClient.browserOperator.getTitle())

    def teardown_class(self):
        self.demoProjectClient.browserOperator.close()
