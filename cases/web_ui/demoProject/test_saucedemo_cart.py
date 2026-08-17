# -*- coding:utf-8 -*-
"""作用：定义SauceDemo购物车相关的自动化测试用例。"""

from page_objects.web_ui.demoProject.pages.page_cart import CartPage
from page_objects.web_ui.demoProject.pages.page_inventory import InventoryPage


class TestSauceDemoCart:
    # 用例目的：验证加入多个商品后，购物车展示正确的商品名称和价格。
    def test_cart_contains_added_products(self, logged_in_client):
        inventory_page = InventoryPage(logged_in_client.browserOperator)
        inventory_page.add_product('sauce-labs-backpack')
        inventory_page.add_product('sauce-labs-bike-light')
        inventory_page.open_cart()
        cart_page = CartPage(logged_in_client.browserOperator)

        assert cart_page.get_item_names() == ['Sauce Labs Backpack', 'Sauce Labs Bike Light']
        assert cart_page.get_item_prices() == ['$29.99', '$9.99']

    # 用例目的：验证从购物车移除商品后，商品条目会立即消失。
    def test_remove_product_from_cart(self, logged_in_client):
        inventory_page = InventoryPage(logged_in_client.browserOperator)
        inventory_page.add_product('sauce-labs-backpack')
        inventory_page.open_cart()
        cart_page = CartPage(logged_in_client.browserOperator)

        cart_page.remove_product('sauce-labs-backpack')
        assert not logged_in_client.browserOperator.is_present(cart_page.elements.item_names)
