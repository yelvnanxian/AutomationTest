"""作用：提供httpbin接口测试共用的客户端和服务fixture。"""

import pytest

from api_objects.httpbin.services.service_httpbin import HttpbinService
from base.api.api_client import APIClient
from base.api.api_client import APIClientFactory


@pytest.fixture(scope='session')
def httpbin_service_available():
    """每次测试会话只检查一次公开服务是否可用。"""
    client = APIClient.from_config(
        'config/httpbin/api_httpbin_test.conf',
        base_url_env='HTTPBIN_BASE_URL',
    )
    health_response = client.request.get('/get')
    if health_response.status_code in (502, 503, 504):
        client.close()
        pytest.skip(
            'httpbin外部服务当前不可用，健康检查返回%s'
            % health_response.status_code
        )
    client.close()


@pytest.fixture
def httpbin_client_factory(httpbin_service_available):
    """为每条用例提供可创建多角色独立Session的客户端工厂。"""
    factory = APIClientFactory(
        'config/httpbin/api_httpbin_test.conf',
        base_url_env='HTTPBIN_BASE_URL',
    )
    yield factory
    factory.close_all()


@pytest.fixture
def httpbin_api_client(httpbin_client_factory):
    """为单条用例创建独立Header和Cookie状态的API客户端。"""
    return httpbin_client_factory.create()


@pytest.fixture
def httpbin_service(httpbin_api_client):
    """提供httpbin接口服务对象。"""
    return HttpbinService(httpbin_api_client)
