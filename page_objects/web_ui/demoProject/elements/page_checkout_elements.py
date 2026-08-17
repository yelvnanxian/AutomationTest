# -*- coding:utf-8 -*-
"""作用：定义SauceDemo结算页面的元素定位信息。"""

from page_objects.create_element import CreateElement
from page_objects.web_ui.locator_type import Locator_Type
from page_objects.web_ui.wait_type import Wait_Type as Wait_By


class CheckoutPageElements:
    def __init__(self):
        self.first_name = CreateElement.create(
            Locator_Type.ID,
            'first-name',
            wait_type=Wait_By.PRESENCE_OF_ELEMENT_LOCATED,
        )
        self.last_name = CreateElement.create(
            Locator_Type.ID,
            'last-name',
            wait_type=Wait_By.PRESENCE_OF_ELEMENT_LOCATED,
        )
        self.postal_code = CreateElement.create(
            Locator_Type.ID,
            'postal-code',
            wait_type=Wait_By.PRESENCE_OF_ELEMENT_LOCATED,
        )
        self.continue_button = CreateElement.create(
            Locator_Type.ID,
            'continue',
            wait_type=Wait_By.ELEMENT_TO_BE_CLICKABLE,
        )
        self.finish_button = CreateElement.create(
            Locator_Type.ID,
            'finish',
            wait_type=Wait_By.ELEMENT_TO_BE_CLICKABLE,
        )
        self.summary_total = CreateElement.create(
            Locator_Type.CSS_SELECTOR,
            '.summary_total_label',
            wait_type=Wait_By.PRESENCE_OF_ELEMENT_LOCATED,
        )
        self.complete_header = CreateElement.create(
            Locator_Type.CSS_SELECTOR,
            '[data-test="complete-header"]',
            wait_type=Wait_By.PRESENCE_OF_ELEMENT_LOCATED,
        )
        self.error_message = CreateElement.create(
            Locator_Type.CSS_SELECTOR,
            '[data-test="error"]',
            wait_type=Wait_By.PRESENCE_OF_ELEMENT_LOCATED,
        )
