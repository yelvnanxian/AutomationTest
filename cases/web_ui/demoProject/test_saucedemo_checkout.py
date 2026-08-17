# -*- coding:utf-8 -*-
"""作用：定义SauceDemo结算和订单完成相关的自动化测试用例。"""

from page_objects.web_ui.demoProject.pages.page_cart import CartPage
from page_objects.web_ui.demoProject.pages.page_checkout import CheckoutPage
from page_objects.web_ui.demoProject.pages.page_inventory import InventoryPage
from test_data.web_ui.demoProject.saucedemo_test_data import CHECKOUT_CUSTOMER


class TestSauceDemoCheckout:
    # 用例目的：验证用户填写完整信息后可以成功提交订单。
    def test_checkout_completes_order(self, logged_in_client):
        inventory_page = InventoryPage(logged_in_client.browserOperator)
        inventory_page.add_product('sauce-labs-backpack')
        inventory_page.open_cart()
        CartPage(logged_in_client.browserOperator).checkout()
        checkout_page = CheckoutPage(logged_in_client.browserOperator)

        checkout_page.fill_customer_information(**CHECKOUT_CUSTOMER)
        checkout_page.continue_to_overview()
        assert checkout_page.get_total().startswith('Total: $')

        checkout_page.finish_order()
        assert checkout_page.get_confirmation() == 'Thank you for your order!'

    # 用例目的：验证结算时未填写名会显示必填项错误。
    def test_checkout_requires_first_name(self, logged_in_client):
        inventory_page = InventoryPage(logged_in_client.browserOperator)
        inventory_page.add_product('sauce-labs-backpack')
        inventory_page.open_cart()
        CartPage(logged_in_client.browserOperator).checkout()
        checkout_page = CheckoutPage(logged_in_client.browserOperator)

        checkout_page.fill_customer_information('', 'User', '10001')
        checkout_page.continue_to_overview()

        assert 'Error: First Name is required' in checkout_page.get_error_message()

    # 用例目的：验证结算时未填写姓会显示必填项错误。
    def test_checkout_requires_last_name(self, logged_in_client):
        inventory_page = InventoryPage(logged_in_client.browserOperator)
        inventory_page.add_product('sauce-labs-backpack')
        inventory_page.open_cart()
        CartPage(logged_in_client.browserOperator).checkout()
        checkout_page = CheckoutPage(logged_in_client.browserOperator)

        checkout_page.fill_customer_information('Test', '', '10001')
        checkout_page.continue_to_overview()

        assert 'Error: Last Name is required' in checkout_page.get_error_message()

    # 用例目的：验证结算时未填写邮编会显示必填项错误。
    def test_checkout_requires_postal_code(self, logged_in_client):
        inventory_page = InventoryPage(logged_in_client.browserOperator)
        inventory_page.add_product('sauce-labs-backpack')
        inventory_page.open_cart()
        CartPage(logged_in_client.browserOperator).checkout()
        checkout_page = CheckoutPage(logged_in_client.browserOperator)

        checkout_page.fill_customer_information('Test', 'User', '')
        checkout_page.continue_to_overview()

        assert 'Error: Postal Code is required' in checkout_page.get_error_message()
