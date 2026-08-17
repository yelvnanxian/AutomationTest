# -*- coding:utf-8 -*-
"""作用：封装SauceDemo商品列表页面的用户操作和状态读取。"""

from page_objects.web_ui.demoProject.elements.page_inventory_elements import InventoryPageElements


class InventoryPage:
    def __init__(self, browser_operator):
        self.browser = browser_operator
        self.elements = InventoryPageElements()

    def get_product_names(self):
        return [element.text for element in self.browser.getElements(self.elements.product_names)]

    def get_product_prices(self):
        return [element.text for element in self.browser.getElements(self.elements.product_prices)]

    def sort_products(self, sort_value):
        self.browser.select_dropDownBox_by_value(self.elements.product_sort, sort_value)

    def add_product(self, product_slug):
        self.browser.click(self.elements.product_button(product_slug, 'add'))

    def remove_product(self, product_slug):
        self.browser.click(self.elements.product_button(product_slug, 'remove'))

    def get_cart_count(self):
        return self.browser.getText(self.elements.cart_badge)

    def open_cart(self):
        self.browser.click(self.elements.cart_link)

    def logout(self):
        self.browser.click(self.elements.menu_button)
        self.browser.click_by_javascript(self.elements.logout_link)
