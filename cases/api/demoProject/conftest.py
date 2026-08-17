"""作用：提供demoProject接口测试共用的客户端和服务fixture。"""

import pytest

from api_objects.demoProject.services.service_search import SearchService
from base.api.demoProject.api_demo_project_client import API_DemoProject_Client


@pytest.fixture(scope='session')
def api_client():
    """创建并在测试结束后关闭demoProject接口客户端。"""
    client = API_DemoProject_Client()
    yield client
    client.doRequest.closeSession()


@pytest.fixture(scope='session')
def search_service(api_client):
    """提供搜索模块的接口服务对象。"""
    return SearchService(api_client)
