"""作用：提供httpbin接口测试共用的客户端和服务fixture。"""

import pytest

from api_objects.httpbin.services.service_httpbin import HttpbinService
from base.api.api_client import APIClient


@pytest.fixture(scope='session')
def httpbin_api_client():
    """按httpbin测试配置创建并关闭通用API客户端。"""
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
    yield client
    client.close()


@pytest.fixture(scope='session')
def httpbin_service(httpbin_api_client):
    """提供httpbin接口服务对象。"""
    return HttpbinService(httpbin_api_client)
