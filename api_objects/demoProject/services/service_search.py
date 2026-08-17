"""作用：封装demoProject搜索接口的请求动作。"""

from api_objects.demoProject.endpoints.endpoint_search import SearchEndpoints


class SearchService:
    """提供搜索模块可复用的接口调用能力。"""

    def __init__(self, api_client):
        self._request = api_client.doRequest

    def open_index(self):
        """请求站点首页。"""
        return self._request.get(SearchEndpoints.INDEX)

    def search(self, keyword):
        """按关键字请求搜索接口。"""
        return self._request.get(
            SearchEndpoints.SEARCH,
            params={'wd': keyword},
        )
