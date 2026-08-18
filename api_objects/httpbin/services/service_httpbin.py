"""作用：封装httpbin各类HTTP请求的可复用调用。"""

from api_objects.httpbin.endpoints.endpoint_httpbin import HttpbinEndpoints


class HttpbinService:
    """提供GET、POST、状态码、请求头和认证接口调用。"""

    def __init__(self, api_client):
        self._request = api_client.request

    def get_query(self, params):
        """发送带查询参数的GET请求。"""
        return self._request.get(HttpbinEndpoints.GET, params=params)

    def post_form(self, form_data):
        """发送表单格式的POST请求。"""
        return self._request.post_with_form(HttpbinEndpoints.POST, params=form_data)

    def get_status(self, status_code):
        """请求指定HTTP状态码。"""
        path = HttpbinEndpoints.STATUS.format(status_code=status_code)
        return self._request.get(path)

    def get_headers(self, headers):
        """发送自定义请求头并在请求结束后恢复客户端状态。"""
        self._request.updateHeaders(headers)
        try:
            return self._request.get(HttpbinEndpoints.HEADERS)
        finally:
            for header_name in headers:
                self._request.removeHeader(header_name)

    def basic_auth(self, username, password):
        """使用HTTP Basic Auth请求认证接口。"""
        path = HttpbinEndpoints.BASIC_AUTH.format(
            username=username,
            password=password,
        )
        return self._request.get(path, auth=(username, password))

    def basic_auth_with_credentials(self, expected_username, expected_password, username, password):
        """使用指定凭据访问另一组预期凭据的认证接口。"""
        path = HttpbinEndpoints.BASIC_AUTH.format(
            username=expected_username,
            password=expected_password,
        )
        return self._request.get(path, auth=(username, password))
