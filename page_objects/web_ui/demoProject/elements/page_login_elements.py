# -*- coding:utf-8 -*-
"""作用：定义SauceDemo登录页面的元素定位信息。"""

from page_objects.create_element import CreateElement
from page_objects.web_ui.locator_type import Locator_Type
from page_objects.web_ui.wait_type import Wait_Type as Wait_By


class LoginPageElements:
    def __init__(self):
        self.username = CreateElement.create(
            Locator_Type.ID,
            'user-name',
            wait_type=Wait_By.PRESENCE_OF_ELEMENT_LOCATED,
        )
        self.password = CreateElement.create(
            Locator_Type.ID,
            'password',
            wait_type=Wait_By.PRESENCE_OF_ELEMENT_LOCATED,
        )
        self.login_button = CreateElement.create(
            Locator_Type.ID,
            'login-button',
            wait_type=Wait_By.ELEMENT_TO_BE_CLICKABLE,
        )
        self.error_message = CreateElement.create(
            Locator_Type.CSS_SELECTOR,
            '[data-test="error"]',
            wait_type=Wait_By.PRESENCE_OF_ELEMENT_LOCATED,
        )
