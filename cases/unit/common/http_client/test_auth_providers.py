"""作用：验证Bearer Token刷新、Cookie和CSRF认证信息能够安全关联到请求。"""

from datetime import timedelta

import pytest
import requests

from common.http_client.auth import AuthenticationExpiredError
from common.http_client.auth import BearerTokenProvider
from common.http_client.auth import CompositeAuthProvider
from common.http_client.auth import CookieAuthProvider
from common.http_client.auth import CsrfTokenProvider
from common.http_client.request_client import DoRequest


pytestmark = pytest.mark.unit


def build_fake_response(kwargs):
    """根据发送参数构造不访问网络的requests响应。"""
    response = requests.Response()
    response.status_code = 200
    response._content = b'{"success": true}'
    response.url = kwargs['url']
    response.headers = {'Content-Type': 'application/json'}
    response.elapsed = timedelta(milliseconds=10)
    response.request = requests.Request(
        kwargs['method'],
        kwargs['url'],
        headers=kwargs['headers'],
        cookies=kwargs['cookies'],
    ).prepare()
    return response


def test_bearer_provider_injects_token_without_changing_default_headers(monkeypatch):
    """验证Bearer Token仅在发送时注入，不污染客户端默认Header。"""
    client = DoRequest('https://example.test')
    client.setHeaders({'X-Tenant-ID': 'tenant-a'})
    client.set_auth_provider(BearerTokenProvider('access-token'))
    captured_request = {}

    def fake_request(**kwargs):
        captured_request.update(kwargs)
        return build_fake_response(kwargs)

    monkeypatch.setattr(client._session, 'request', fake_request)

    client.get('/users')

    assert captured_request['headers']['Authorization'] == 'Bearer access-token'
    assert client.getHeaders() == {'X-Tenant-ID': 'tenant-a'}
    client.closeSession()


def test_expired_bearer_token_refreshes_before_request(monkeypatch):
    """验证过期Token在请求发送前刷新，不依赖401后重放业务请求。"""
    refresh_calls = []

    def refresh_token(refresh_token):
        refresh_calls.append(refresh_token)
        return {
            'access_token': 'new-access-token',
            'refresh_token': 'new-refresh-token',
            'expires_in': 3600,
        }

    provider = BearerTokenProvider(
        'expired-token',
        refresh_token='old-refresh-token',
        expires_in=0,
        refresh_callback=refresh_token,
        refresh_margin_seconds=0,
    )
    headers = {}

    provider.apply(headers, {})

    assert headers['Authorization'] == 'Bearer new-access-token'
    assert refresh_calls == ['old-refresh-token']


def test_expired_token_without_refresh_callback_fails_before_request():
    """验证无法刷新的过期Token会快速失败，不发送未认证请求。"""
    provider = BearerTokenProvider(
        'expired-token',
        expires_in=0,
        refresh_margin_seconds=0,
    )

    with pytest.raises(AuthenticationExpiredError, match='未配置刷新回调'):
        provider.apply({}, {})


def test_cookie_and_csrf_providers_can_be_composed(monkeypatch):
    """验证Session Cookie和CSRF Header可以组合并允许单次请求覆盖。"""
    client = DoRequest('https://example.test')
    client.set_auth_provider(
        CompositeAuthProvider(
            CookieAuthProvider({'session': 'session-cookie'}),
            CsrfTokenProvider(
                'csrf-token',
                cookie_name='XSRF-TOKEN',
            ),
        )
    )
    captured_request = {}

    def fake_request(**kwargs):
        captured_request.update(kwargs)
        return build_fake_response(kwargs)

    monkeypatch.setattr(client._session, 'request', fake_request)

    client.post_json('/orders', {'product_id': 1})

    assert captured_request['headers']['X-CSRF-Token'] == 'csrf-token'
    assert captured_request['cookies'] == {
        'session': 'session-cookie',
        'XSRF-TOKEN': 'csrf-token',
    }
    client.closeSession()
