# -*- coding:utf-8 -*-
"""作用：封装SauceDemo结算页面的用户操作和状态读取。"""

from page_objects.web_ui.demoProject.elements.page_checkout_elements import CheckoutPageElements


class CheckoutPage:
    def __init__(self, browser_operator):
        self.browser = browser_operator
        self.elements = CheckoutPageElements()

    def fill_customer_information(self, first_name, last_name, postal_code):
        self.browser.sendText(self.elements.first_name, first_name)
        self.browser.sendText(self.elements.last_name, last_name)
        self.browser.sendText(self.elements.postal_code, postal_code)

    def continue_to_overview(self):
        self.browser.click_by_javascript(self.elements.continue_button)

    def get_total(self):
        return self.browser.getText(self.elements.summary_total)

    def finish_order(self):
        self.browser.click_by_javascript(self.elements.finish_button)

    def get_confirmation(self):
        return self.browser.getText(self.elements.complete_header)

    def get_error_message(self):
        return self.browser.getText(self.elements.error_message)
