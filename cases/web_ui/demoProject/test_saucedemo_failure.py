# -*- coding:utf-8 -*-
"""作用：提供一个需手动运行的SauceDemo失败报告演示用例。"""

import pytest

from page_objects.web_ui.demoProject.pages.page_cart import CartPage
from page_objects.web_ui.demoProject.pages.page_inventory import InventoryPage


@pytest.mark.failure_demo
class TestSauceDemoFailureDemo:
    # 用例目的：演示断言不符合实际结果时，VS Code和Allure中的失败展示效果。
    def test_demo_expected_failure(self, logged_in_client):
        inventory_page = InventoryPage(logged_in_client.browserOperator)
        actual_count = len(inventory_page.get_product_names())

        # 故意使用错误期望值；该用例只用于演示失败报告，不纳入常规回归。
        assert actual_count == 5, '失败演示：预期商品数量为5，实际为%s' % actual_count

    # 用例目的：演示商品价格断言错误时的失败详情。
    def test_demo_price_failure(self, logged_in_client):
        inventory_page = InventoryPage(logged_in_client.browserOperator)
        inventory_page.add_product('sauce-labs-backpack')
        inventory_page.open_cart()

        # 故意使用错误价格，实际价格为29.99美元。
        actual_price = CartPage(logged_in_client.browserOperator).get_item_prices()[0]
        assert actual_price == '$19.99', '失败演示：预期价格为$19.99，实际为%s' % actual_price

    # 用例目的：演示商品排序结果断言错误时的失败详情。
    def test_demo_sorting_failure(self, logged_in_client):
        inventory_page = InventoryPage(logged_in_client.browserOperator)
        inventory_page.sort_products('lohi')
        prices = [float(price.replace('$', '')) for price in inventory_page.get_product_prices()]

        # 故意断言排序后第一件商品价格为错误值。
        assert prices[0] == 99.99, '失败演示：预期最低价为99.99，实际为%s' % prices[0]
