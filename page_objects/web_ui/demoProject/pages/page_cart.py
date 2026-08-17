# -*- coding:utf-8 -*-
"""作用：封装SauceDemo购物车页面的用户操作和状态读取。"""

from page_objects.web_ui.demoProject.elements.page_cart_elements import CartPageElements


class CartPage:
    def __init__(self, browser_operator):
        self.browser = browser_operator
        self.elements = CartPageElements()

    def get_item_names(self):
        return [element.text for element in self.browser.getElements(self.elements.item_names)]

    def get_item_prices(self):
        return [element.text for element in self.browser.getElements(self.elements.item_prices)]

    def remove_product(self, product_slug):
        self.browser.click(self.elements.remove_button(product_slug))

    def checkout(self):
        self.browser.click_by_javascript(self.elements.checkout_button)
