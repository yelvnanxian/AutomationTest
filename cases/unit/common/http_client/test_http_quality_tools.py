"""作用：验证HTTP断言、JSON解析和失败诊断脱敏能力。"""

import json

import pytest

from common.http_client.diagnostics import build_http_diagnostic
from common.http_client.response_assertions import (
    assert_json_schema,
    assert_response_time,
    assert_status_code,
)
from pojo.http_response_result import HttpResponseResult


pytestmark = pytest.mark.unit


def build_response():
    """构造不依赖网络的HTTP响应测试对象。"""
    response = HttpResponseResult()
    response.status_code = 200
    response.body = '{"success": true, "name": "AutomationTest"}'
    response.elapsed_ms = 125.5
    response.url = 'https://example.test/get'
    response.request_method = 'GET'
    return response


class TestHttpResponseAssertions:
    def test_parses_json_and_validates_response_quality(self):
        """验证响应可以进行状态、耗时、JSON解析和结构校验。"""
        response = build_response()
        schema = {
            'type': 'object',
            'required': ['success', 'name'],
            'properties': {
                'success': {'const': True},
                'name': {'type': 'string'},
            },
        }

        assert_status_code(response, 200)
        assert_response_time(response, 500)
        assert_json_schema(response, schema)
        assert response.json()['name'] == 'AutomationTest'

    def test_response_time_assertion_rejects_slow_response(self):
        """验证响应超过性能阈值时会产生清晰的断言失败。"""
        response = build_response()

        with pytest.raises(AssertionError, match='超过限制'):
            assert_response_time(response, 100)


class TestHttpDiagnostics:
    def test_masks_sensitive_headers_urls_and_bodies(self):
        """验证Allure诊断数据不会泄漏认证信息和密码。"""
        response = build_response()
        response.url = (
            'https://example.test/basic-auth/test_user/secret_password'
            '?token=secret_token'
        )
        response.request_headers = {
            'Authorization': 'Basic secret_authorization',
            'X-Test-Source': 'AutomationTest',
        }
        response.request_body = 'password=secret_password'
        response.headers_dict = {'Set-Cookie': 'session=secret_cookie'}
        response.body = '{"token":"secret_token"}'

        diagnostic_text = json.dumps(
            build_http_diagnostic(response),
            ensure_ascii=False,
        )

        assert 'secret_password' not in diagnostic_text
        assert 'secret_token' not in diagnostic_text
        assert 'secret_authorization' not in diagnostic_text
        assert 'secret_cookie' not in diagnostic_text
        assert '***已脱敏***' in diagnostic_text
