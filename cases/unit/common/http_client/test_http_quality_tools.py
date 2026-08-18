"""作用：验证HTTP断言、JSON解析和失败诊断脱敏能力。"""

import json
from datetime import timedelta

import pytest
import requests
from jsonschema.exceptions import ValidationError

from base.api.api_client import APIClient
from base.api.api_client import APIClientCleanupError
from base.api.api_client import APIClientFactory
from common.http_client.diagnostics import build_http_diagnostic
from common.http_client.request_client import DoRequest
from common.http_client.response_assertions import (
    assert_collection_contains,
    assert_header_contains,
    assert_header_equals,
    assert_json_schema,
    assert_json_value,
    assert_mapping_contains,
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

    def test_schema_rejects_invalid_uri_format(self):
        """验证JSON Schema中的format会真正校验URI格式。"""
        response = build_response()
        response.body = '{"url": "not-a-uri"}'
        schema = {
            'type': 'object',
            'required': ['url'],
            'properties': {'url': {'type': 'string', 'format': 'uri'}},
        }

        with pytest.raises(ValidationError, match='not a'):
            assert_json_schema(response, schema)

    def test_validates_headers_json_values_and_business_collections(self):
        """验证Header、JSON关联字段、业务对象和集合可以组合校验。"""
        response = build_response()
        response.body = (
            '{"data":{"order":{"id":"order-1001","status":"PAID"},'
            '"items":[{"id":"item-1"}]}}'
        )
        response.headers_dict = {
            'Content-Type': 'application/json; charset=utf-8',
            'X-Request-ID': 'request-1001',
        }

        assert_header_contains(response, 'content-type', 'application/json')
        assert_header_equals(response, 'x-request-id', 'request-1001')
        assert_json_value(response, 'data.order.id', 'order-1001')
        assert_mapping_contains(
            response.json()['data']['order'],
            {'id': 'order-1001', 'status': 'PAID'},
            mapping_name='订单',
        )
        assert_collection_contains(
            response.json()['data']['items'],
            'item-1',
            key='id',
        )


class TestHttpDiagnostics:
    def test_masks_sensitive_headers_urls_and_bodies(self):
        """验证Allure诊断数据不会泄漏认证信息和密码。"""
        response = build_response()
        response.url = (
            'https://example.test/basic-auth/test_user/secret_password'
            '?token=secret_token&email=user@example.test'
        )
        response.request_headers = {
            'Authorization': 'Basic secret_authorization',
            'X-Test-Source': 'AutomationTest',
        }
        response.request_body = (
            'password=secret_password&phone=13800138000&api_key=secret_api_key'
        )
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
        assert 'user@example.test' not in diagnostic_text
        assert '13800138000' not in diagnostic_text
        assert 'secret_api_key' not in diagnostic_text
        assert '***已脱敏***' in diagnostic_text


class TestDoRequest:
    def test_builds_url_and_merges_request_headers(self, monkeypatch):
        """验证路径拼接和单次请求头不会污染客户端默认请求头。"""
        client = DoRequest('https://example.test/api/')
        client.setHeaders({'X-Default': 'default'})
        captured_request = {}

        def fake_request(**kwargs):
            captured_request.update(kwargs)
            response = requests.Response()
            response.status_code = 200
            response._content = b'{"success": true}'
            response.url = kwargs['url']
            response.headers = {'Content-Type': 'application/json'}
            response.elapsed = timedelta(milliseconds=20)
            response.request = requests.Request(
                kwargs['method'],
                kwargs['url'],
                headers=kwargs['headers'],
                json=kwargs.get('json'),
            ).prepare()
            return response

        monkeypatch.setattr(client._session, 'request', fake_request)

        response = client.post_json(
            '/users',
            {'name': 'tester'},
            headers={'X-Request': 'request'},
        )

        assert captured_request['url'] == 'https://example.test/api/users'
        assert captured_request['headers'] == {
            'X-Default': 'default',
            'X-Request': 'request',
        }
        assert client.getHeaders() == {'X-Default': 'default'}
        assert response.json() == {'success': True}

    def test_header_access_is_safe_and_patch_is_supported(self, monkeypatch):
        """验证外部不能直接修改内部请求头，且PATCH沿用统一请求流程。"""
        client = DoRequest('https://example.test')
        client.setHeaders({'X-Default': 'default'})
        copied_headers = client.getHeaders()
        copied_headers['X-Default'] = 'changed'
        client.removeHeader('X-Missing')
        captured_request = {}

        def fake_request(**kwargs):
            captured_request.update(kwargs)
            response = requests.Response()
            response.status_code = 204
            response._content = b''
            response.url = kwargs['url']
            response.headers = {}
            response.elapsed = timedelta(milliseconds=10)
            response.request = requests.Request(
                kwargs['method'],
                kwargs['url'],
                data=kwargs.get('data'),
            ).prepare()
            return response

        monkeypatch.setattr(client._session, 'request', fake_request)

        client.patch('/users/1', params={'enabled': 'true'})

        assert client.getHeaders() == {'X-Default': 'default'}
        assert captured_request['method'] == 'PATCH'
        assert captured_request['url'] == 'https://example.test/users/1'

    def test_cookie_jar_is_the_only_cookie_state(self):
        """验证服务端或测试清空Cookie Jar后，不会再次发送客户端残留Cookie。"""
        client = DoRequest('https://example.test')
        client.setCookies({'session': 'active-cookie'})
        assert client.getCookies() == {'session': 'active-cookie'}

        client._session.cookies.clear()

        assert client.getCookies() == {}
        client.closeSession()

    def test_temporary_headers_restore_overridden_values(self):
        """验证临时覆盖Authorization后会恢复原Token，即使上下文中发生异常。"""
        client = DoRequest('https://example.test')
        original_headers = {
            'Authorization': 'Bearer original-token',
            'X-Tenant-ID': 'tenant-a',
        }
        client.setHeaders(original_headers)

        with pytest.raises(RuntimeError, match='request failed'):
            with client.temporary_headers(
                {
                    'Authorization': 'Bearer temporary-token',
                    'X-Request-ID': 'request-1',
                }
            ):
                assert client.getHeaders()['Authorization'] == (
                    'Bearer temporary-token'
                )
                raise RuntimeError('request failed')

        assert client.getHeaders() == original_headers
        client.closeSession()

    def test_invalid_response_encoding_raises_by_default(self):
        """验证响应编码损坏时默认失败，不使用替代字符掩盖数据问题。"""
        client = DoRequest('https://example.test', encoding='utf-8')
        response = requests.Response()
        response.status_code = 200
        response._content = b'\xff'
        response.url = 'https://example.test/data'
        response.headers = {}
        response.elapsed = timedelta(milliseconds=1)
        response.request = requests.Request('GET', response.url).prepare()

        with pytest.raises(UnicodeDecodeError):
            client._dealResponseResult(response)
        client.closeSession()

    def test_response_decode_replacement_requires_explicit_configuration(self):
        """验证诊断场景可显式启用replace，但不会成为默认行为。"""
        client = DoRequest(
            'https://example.test',
            encoding='utf-8',
            decode_errors='replace',
        )
        response = requests.Response()
        response.status_code = 200
        response._content = b'\xff'
        response.url = 'https://example.test/data'
        response.headers = {}
        response.elapsed = timedelta(milliseconds=1)
        response.request = requests.Request('GET', response.url).prepare()

        result = client._dealResponseResult(response)

        assert result.body == '\ufffd'
        client.closeSession()


class TestAPIClient:
    def test_loads_optional_http_settings_without_breaking_url_override(
        self,
        tmp_path,
        monkeypatch,
    ):
        """验证API配置可控制超时和TLS，同时环境变量仍可覆盖服务地址。"""
        config_path = tmp_path / 'api_test.conf'
        config_path.write_text(
            '[servers]\n'
            'url=https://config.example.test\n'
            '[http]\n'
            'timeout=12.5\n'
            'verify=false\n'
            'max_retries=1\n'
            'pool_connections=4\n'
            'pool_maxsize=8\n',
            encoding='utf-8',
        )
        monkeypatch.setenv('TEST_API_BASE_URL', 'https://env.example.test/')

        client = APIClient.from_config(
            config_path,
            base_url_env='TEST_API_BASE_URL',
        )

        assert client.request._url == 'https://env.example.test'
        assert client.request._timeout == 12.5
        assert client.request._verify is False
        https_adapter = client.request._session.get_adapter('https://')
        assert https_adapter._pool_connections == 4
        assert https_adapter._pool_maxsize == 8
        client.close()

    def test_factory_creates_isolated_clients_and_closes_all(self, tmp_path):
        """验证不同角色客户端不共享Header、Cookie或Session，并能集中关闭。"""
        config_path = tmp_path / 'api_test.conf'
        config_path.write_text(
            '[servers]\nurl=https://example.test\n',
            encoding='utf-8',
        )
        factory = APIClientFactory(config_path)

        admin_client = factory.create(
            headers={'Authorization': 'Bearer admin-token'},
            cookies={'session': 'admin-session'},
        )
        user_client = factory.create(
            headers={'Authorization': 'Bearer user-token'},
            cookies={'session': 'user-session'},
        )

        assert admin_client.request._session is not user_client.request._session
        assert admin_client.request.getHeaders()['Authorization'] == (
            'Bearer admin-token'
        )
        assert user_client.request.getHeaders()['Authorization'] == (
            'Bearer user-token'
        )
        assert admin_client.request.getCookies() == {'session': 'admin-session'}
        assert user_client.request.getCookies() == {'session': 'user-session'}

        factory.close_all()

        assert factory._clients == []

    def test_factory_continues_closing_after_one_client_fails(self):
        """验证一个客户端关闭失败后，其余客户端仍会按反向顺序释放。"""
        closed_clients = []

        class FakeClient:
            def __init__(self, name, fail=False):
                self.name = name
                self.fail = fail

            def close(self):
                closed_clients.append(self.name)
                if self.fail:
                    raise RuntimeError('%s close failed' % self.name)

        factory = APIClientFactory('unused.conf')
        factory._clients = [
            FakeClient('first'),
            FakeClient('second', fail=True),
            FakeClient('third'),
        ]

        with pytest.raises(APIClientCleanupError, match='second close failed'):
            factory.close_all()

        assert closed_clients == ['third', 'second', 'first']
        assert factory._clients == []

    def test_factory_context_preserves_original_error_when_close_fails(self):
        """验证业务异常和关闭异常同时出现时优先保留原始业务异常。"""
        class FailedClient:
            def close(self):
                raise RuntimeError('close failed')

        with pytest.raises(AssertionError, match='business failed') as error_info:
            with APIClientFactory('unused.conf') as factory:
                factory._clients.append(FailedClient())
                raise AssertionError('business failed')

        assert any('API客户端关闭失败' in note for note in error_info.value.__notes__)
