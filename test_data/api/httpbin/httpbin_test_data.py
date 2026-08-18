"""作用：集中维护httpbin接口的请求输入和预期结果。"""


QUERY_PARAMS = {
    'source': 'AutomationTest',
    'language': 'zh-CN',
}

FORM_DATA = {
    'username': 'test_user',
    'action': 'submit',
}

CUSTOM_HEADERS = {
    'X-Test-Source': 'AutomationTest',
}

BASIC_AUTH = {
    'username': 'automation_user',
    'password': 'httpbin_demo_password',
}

INVALID_AUTH_PASSWORD = 'wrong_password'
STATUS_CODES = (200, 404, 500)
MAX_RESPONSE_TIME_MS = 5000
