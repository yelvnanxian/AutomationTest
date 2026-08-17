# -*- coding:utf-8 -*-
"""作用：定义SauceDemo商品列表页面的元素定位信息。"""

from page_objects.create_element import CreateElement
from page_objects.web_ui.locator_type import Locator_Type
from page_objects.web_ui.wait_type import Wait_Type as Wait_By


class InventoryPageElements:
    def __init__(self):
        self.product_sort = CreateElement.create(
            Locator_Type.CLASS_NAME,
            'product_sort_container',
            wait_type=Wait_By.ELEMENT_TO_BE_CLICKABLE,
        )
        self.product_names = CreateElement.create(
            Locator_Type.CSS_SELECTOR,
            '.inventory_item_name',
            wait_type=Wait_By.PRESENCE_OF_ELEMENT_LOCATED,
        )
        self.product_prices = CreateElement.create(
            Locator_Type.CSS_SELECTOR,
            '.inventory_item_price',
            wait_type=Wait_By.PRESENCE_OF_ELEMENT_LOCATED,
        )
        self.cart_link = CreateElement.create(
            Locator_Type.CSS_SELECTOR,
            '.shopping_cart_link',
            wait_type=Wait_By.ELEMENT_TO_BE_CLICKABLE,
        )
        self.cart_badge = CreateElement.create(
            Locator_Type.CSS_SELECTOR,
            '.shopping_cart_badge',
            wait_type=Wait_By.PRESENCE_OF_ELEMENT_LOCATED,
        )
        self.menu_button = CreateElement.create(
            Locator_Type.ID,
            'react-burger-menu-btn',
            wait_type=Wait_By.ELEMENT_TO_BE_CLICKABLE,
        )
        self.logout_link = CreateElement.create(
            Locator_Type.ID,
            'logout_sidebar_link',
            wait_type=Wait_By.ELEMENT_TO_BE_CLICKABLE,
        )

    @staticmethod
    def product_button(product_slug, action='add'):
        data_test_action = 'add-to-cart' if action == 'add' else 'remove'
        return CreateElement.create(
            Locator_Type.CSS_SELECTOR,
            '[data-test="%s-%s"]' % (data_test_action, product_slug),
            wait_type=Wait_By.ELEMENT_TO_BE_CLICKABLE,
        )
