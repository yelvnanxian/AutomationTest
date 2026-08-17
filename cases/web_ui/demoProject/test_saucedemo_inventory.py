# -*- coding:utf-8 -*-
"""作用：定义SauceDemo商品列表和排序相关的自动化测试用例。"""

from page_objects.web_ui.demoProject.pages.page_inventory import InventoryPage
from test_data.web_ui.demoProject.saucedemo_test_data import (
    EXPECTED_LOWEST_PRICE,
    EXPECTED_PRODUCT_COUNT,
)


class TestSauceDemoInventory:
    # 用例目的：验证商品列表默认展示六件商品。
    def test_inventory_displays_six_products(self, logged_in_client):
        inventory_page = InventoryPage(logged_in_client.browserOperator)
        assert len(inventory_page.get_product_names()) == EXPECTED_PRODUCT_COUNT

    # 用例目的：验证商品可以按价格从低到高排序。
    def test_sort_products_by_price_low_to_high(self, logged_in_client):
        inventory_page = InventoryPage(logged_in_client.browserOperator)
        inventory_page.sort_products('lohi')

        prices = [float(price.replace('$', '')) for price in inventory_page.get_product_prices()]
        assert prices == sorted(prices)
        assert prices[0] == EXPECTED_LOWEST_PRICE

    # 用例目的：验证添加和移除商品会同步更新购物车数量。
    def test_add_and_remove_product_updates_cart_count(self, logged_in_client):
        inventory_page = InventoryPage(logged_in_client.browserOperator)
        inventory_page.add_product('sauce-labs-backpack')
        assert inventory_page.get_cart_count() == '1'

        inventory_page.remove_product('sauce-labs-backpack')
        assert not logged_in_client.browserOperator.is_present(
            inventory_page.elements.cart_badge
        )
