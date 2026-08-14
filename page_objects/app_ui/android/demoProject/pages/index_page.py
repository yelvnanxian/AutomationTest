#-*- coding:utf-8 -*-
"""作用：封装indexPage页面的用户操作和状态读取。"""

from page_objects.app_ui.android.demoProject.elements.index_page_elements import IndexPageElements

class IndexPage:
    def __init__(self,appOperator):
        self.appOperator=appOperator
        self._indexPageElement=IndexPageElements()


    def index_left_slide(self):
        self.appOperator.touch_left_slide()

    def index_right_slide(self):
        self.appOperator.touch_right_slide()

    def index_up_slide(self):
        self.appOperator.touch_up_slide()

    def index_down_slide(self):
        self.appOperator.touch_down_slide()
