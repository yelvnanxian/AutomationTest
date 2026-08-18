"""作用：验证httpbin常用HTTP请求、响应结构、性能和认证行为。"""

import pytest

from common.http_client.response_assertions import (
    assert_json_schema,
    assert_response_time,
    assert_status_code,
)
from test_data.api.httpbin.httpbin_response_schemas import (
    AUTH_RESPONSE_SCHEMA,
    GET_RESPONSE_SCHEMA,
    HEADERS_RESPONSE_SCHEMA,
    POST_RESPONSE_SCHEMA,
)
from test_data.api.httpbin.httpbin_test_data import (
    BASIC_AUTH,
    CUSTOM_HEADERS,
    FORM_DATA,
    INVALID_AUTH_PASSWORD,
    MAX_RESPONSE_TIME_MS,
    QUERY_PARAMS,
    STATUS_CODES,
)


pytestmark = pytest.mark.api


def normalize_echo_values(values):
    """兼容httpbin字符串回显和兼容服务的单元素数组回显。"""
    return {
        key: value[0] if isinstance(value, list) and len(value) == 1 else value
        for key, value in values.items()
    }


class TestHttpbinRequests:
    def test_get_echoes_query_parameters(self, httpbin_service):
        """验证GET接口能够原样返回查询参数。"""
        response = httpbin_service.get_query(QUERY_PARAMS)

        assert_status_code(response, 200)
        response_data = response.json()
        assert_response_time(response, MAX_RESPONSE_TIME_MS)
        assert_json_schema(response, GET_RESPONSE_SCHEMA)
        assert normalize_echo_values(response_data['args']) == QUERY_PARAMS

    def test_post_echoes_form_data(self, httpbin_service):
        """验证POST接口能够原样返回表单数据。"""
        response = httpbin_service.post_form(FORM_DATA)

        assert_status_code(response, 200)
        response_data = response.json()
        assert_response_time(response, MAX_RESPONSE_TIME_MS)
        assert_json_schema(response, POST_RESPONSE_SCHEMA)
        assert normalize_echo_values(response_data['form']) == FORM_DATA

    @pytest.mark.parametrize('status_code', STATUS_CODES)
    def test_returns_requested_status_code(self, httpbin_service, status_code):
        """验证状态码接口能够返回指定的成功或异常状态码。"""
        response = httpbin_service.get_status(status_code)

        assert_status_code(response, status_code)

    def test_echoes_custom_request_header(self, httpbin_service):
        """验证服务端能够接收并返回自定义请求头。"""
        response = httpbin_service.get_headers(CUSTOM_HEADERS)

        assert_status_code(response, 200)
        response_data = response.json()
        assert_json_schema(response, HEADERS_RESPONSE_SCHEMA)
        echoed_headers = normalize_echo_values(response_data['headers'])
        assert echoed_headers['X-Test-Source'] == CUSTOM_HEADERS['X-Test-Source']

    def test_basic_auth_succeeds_with_valid_credentials(self, httpbin_service):
        """验证正确的Basic Auth账号密码可以通过认证。"""
        response = httpbin_service.basic_auth(**BASIC_AUTH)

        assert_status_code(response, 200)
        response_data = response.json()
        assert_json_schema(response, AUTH_RESPONSE_SCHEMA)
        assert response_data['authenticated'] is True
        assert response_data['user'] == BASIC_AUTH['username']

    def test_basic_auth_rejects_invalid_password(self, httpbin_service):
        """验证错误的Basic Auth密码会返回401。"""
        response = httpbin_service.basic_auth_with_credentials(
            BASIC_AUTH['username'],
            BASIC_AUTH['password'],
            BASIC_AUTH['username'],
            INVALID_AUTH_PASSWORD,
        )

        assert_status_code(response, 401)
