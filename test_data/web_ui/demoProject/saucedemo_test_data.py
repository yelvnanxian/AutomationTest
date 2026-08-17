# -*- coding:utf-8 -*-
"""作用：集中维护SauceDemo测试账号、结算信息和业务期望值。"""


STANDARD_USER = {
    'username': 'standard_user',
    'password': 'secret_sauce',
}

LOCKED_OUT_USER = {
    'username': 'locked_out_user',
    'password': 'secret_sauce',
}

INVALID_PASSWORD = 'wrong_password'

CHECKOUT_CUSTOMER = {
    'first_name': 'Test',
    'last_name': 'User',
    'postal_code': '10001',
}

EXPECTED_PRODUCT_COUNT = 6
EXPECTED_LOWEST_PRICE = 7.99
