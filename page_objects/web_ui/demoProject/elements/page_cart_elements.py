# -*- coding:utf-8 -*-
"""作用：定义SauceDemo购物车页面的元素定位信息。"""

from page_objects.create_element import CreateElement
from page_objects.web_ui.locator_type import Locator_Type
from page_objects.web_ui.wait_type import Wait_Type as Wait_By

class CartPageElements:
    def __init__(self):
        self.item_names = CreateElement.create(
            Locator_Type.CSS_SELECTOR,
            '.inventory_item_name',
            wait_type=Wait_By.PRESENCE_OF_ELEMENT_LOCATED,
        )
        self.item_prices = CreateElement.create(
            Locator_Type.CSS_SELECTOR,
            '.inventory_item_price',
            wait_type=Wait_By.PRESENCE_OF_ELEMENT_LOCATED,
        )
        self.checkout_button = CreateElement.create(
            Locator_Type.ID,
            'checkout',
            wait_type=Wait_By.ELEMENT_TO_BE_CLICKABLE,
        )
        self.continue_shopping_button = CreateElement.create(
            Locator_Type.ID,
            'continue-shopping',
            wait_type=Wait_By.ELEMENT_TO_BE_CLICKABLE,
        )

    @staticmethod
    def remove_button(product_slug):
        return CreateElement.create(
            Locator_Type.CSS_SELECTOR,
            '[data-test="remove-%s"]' % product_slug,
            wait_type=Wait_By.ELEMENT_TO_BE_CLICKABLE,
        )
