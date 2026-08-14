#-*- coding:utf8 -*-
"""作用：定义start page elements页面或界面的元素定位信息。"""

from page_objects.create_element import CreateElement
from page_objects.app_ui.wait_type import Wait_Type as Wait_By
from page_objects.app_ui.locator_type import Locator_Type
class StartPageElements:
    def __init__(self):
        self.start_btn = CreateElement.create(Locator_Type.ID, 'com.moji.mjweather:id/zc', wait_type=Wait_By.VISIBILITY_OF)
        self.search_city = CreateElement.create(Locator_Type.ID, 'com.moji.mjweather:id/d', wait_type=Wait_By.VISIBILITY_OF)
        self.city_btns = CreateElement.create(Locator_Type.ID,'com.moji.mjweather:id/abk',wait_type=Wait_By.VISIBILITY_OF)
