#-*- coding:utf8 -*-
"""作用：定义示例项目搜索结果页面的元素定位信息。"""

from page_objects.web_ui.locator_type import Locator_Type
from page_objects.create_element import CreateElement
from page_objects.web_ui.wait_type import Wait_Type as Wait_By
class SearchPageElements:
    def __init__(self):
        self.path = '/'
        self.title = CreateElement.create(None,None,None,Wait_By.TITLE_IS)
        self.search_input = CreateElement.create(Locator_Type.ID,'kw',wait_type=Wait_By.PRESENCE_OF_ELEMENT_LOCATED)
        self.search_button =  CreateElement.create(Locator_Type.ID,'su',wait_type=Wait_By.PRESENCE_OF_ELEMENT_LOCATED)
