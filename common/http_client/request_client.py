# -*- coding:utf-8 -*-
"""作用：提供支持连接复用、统一配置和失败诊断的HTTP请求客户端。"""

import codecs
from contextlib import contextmanager
from urllib.parse import urljoin

import requests
import ujson
from requests.adapters import HTTPAdapter

from common.http_client.diagnostics import record_http_exchange
from pojo.http_response_result import HttpResponseResult


class DoRequest(object):
    """封装requests.Session，并兼容框架原有请求方法。"""

    def __init__(
        self,
        url,
        encoding='utf-8',
        pool_connections=10,
        pool_maxsize=10,
        max_retries=2,
        timeout=30,
        verify=True,
        decode_errors='strict',
    ):
        codecs.lookup_error(decode_errors)
        self._url = url
        self._encoding = encoding
        self._decode_errors = decode_errors
        self._headers = {}
        self._auth_provider = None
        self._proxies = {}
        self._timeout = timeout
        self._verify = verify
        self._session = requests.Session()
        http_adapter = HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=max_retries,
        )
        self._session.mount('http://', http_adapter)
        self._session.mount('https://', http_adapter)

    def _build_url(self, path=''):
        """安全拼接基础地址和请求路径，同时保留空路径形式的Webhook地址。"""
        if not path:
            return self._url
        if path.startswith(('http://', 'https://')):
            return path
        return urljoin(self._url.rstrip('/') + '/', path.lstrip('/'))

    def _send(self, method, path='', **kwargs):
        """合并客户端默认配置和单次请求配置并发送原始请求。"""
        request_headers = self.getHeaders()
        request_cookies = {}
        if self._auth_provider is not None:
            self._auth_provider.apply(request_headers, request_cookies)
        request_headers.update(kwargs.pop('headers', {}) or {})
        request_cookies.update(kwargs.pop('cookies', {}) or {})

        return self._session.request(
            method=method,
            url=self._build_url(path),
            headers=request_headers,
            cookies=request_cookies or None,
            timeout=kwargs.pop('timeout', self._timeout),
            proxies=kwargs.pop('proxies', self._proxies),
            verify=kwargs.pop('verify', self._verify),
            **kwargs,
        )

    def request(self, method, path='', **kwargs):
        """发送任意HTTP方法请求并返回框架统一响应对象。"""
        response = self._send(method.upper(), path, **kwargs)
        return self._dealResponseResult(response)

    def setHeaders(self, headers):
        self._headers = dict(headers or {})

    def updateHeaders(self, headers):
        self._headers.update(headers or {})

    def removeHeader(self, key):
        self._headers.pop(key, None)

    def clearHeaders(self):
        self._headers.clear()

    def getHeaders(self):
        return self._headers.copy()

    def set_auth_provider(self, auth_provider):
        self._auth_provider = auth_provider

    def setAuthProvider(self, auth_provider):
        """兼容历史命名，请优先使用set_auth_provider。"""
        self.set_auth_provider(auth_provider)

    def clear_auth_provider(self):
        if self._auth_provider is not None:
            self._auth_provider.clear()
        self._auth_provider = None

    def setCookies(self, cookies):
        self.clearCookies()
        self.updateCookies(cookies)

    def updateCookies(self, cookies):
        self._session.cookies.update(cookies or {})

    def clearCookies(self):
        self._session.cookies.clear()

    def getCookies(self):
        return self._session.cookies.get_dict()

    @contextmanager
    def temporary_headers(self, headers):
        """临时覆盖默认Header，退出上下文后完整恢复原状态。"""
        original_headers = self.getHeaders()
        self.updateHeaders(headers)
        try:
            yield self
        finally:
            self.setHeaders(original_headers)

    def setTimeout(self, seconds):
        self._timeout = seconds

    def setProxies(self, proxies):
        self._proxies = dict(proxies or {})

    def setVerify(self, verify=True):
        self._verify = verify

    def post_with_form(self, path, params=None, **kwargs):
        """兼容原有表单POST方法。"""
        kwargs.setdefault('data', params)
        return self.request('POST', path, **kwargs)

    def post_json(self, path, payload=None, **kwargs):
        """发送JSON格式POST请求。"""
        kwargs.setdefault('json', payload)
        return self.request('POST', path, **kwargs)

    def post_with_file(self, path, filePath, params=None, fileKey='file', **kwargs):
        with open(filePath, 'rb') as file_stream:
            files = {fileKey: file_stream}
            kwargs.setdefault('data', params)
            kwargs['files'] = files
            return self.request('POST', path, **kwargs)

    def put(self, path, params=None, **kwargs):
        """兼容原有表单PUT方法，也允许调用方通过json参数发送JSON。"""
        if 'json' not in kwargs:
            kwargs.setdefault('data', params)
        return self.request('PUT', path, **kwargs)

    def patch(self, path, params=None, **kwargs):
        """发送PATCH请求，默认使用表单数据，也支持json参数。"""
        if 'json' not in kwargs:
            kwargs.setdefault('data', params)
        return self.request('PATCH', path, **kwargs)

    def get(self, path, params=None, **kwargs):
        kwargs.setdefault('params', params)
        return self.request('GET', path, **kwargs)

    def delete(self, path, params=None, **kwargs):
        kwargs.setdefault('params', params)
        return self.request('DELETE', path, **kwargs)

    def getFile(self, path, storeFilePath, params=None, **kwargs):
        """下载文件并返回不包含响应正文的统一响应对象。"""
        kwargs['stream'] = True
        kwargs.setdefault('params', params)
        with self._send('GET', path, **kwargs) as response:
            http_response_result = HttpResponseResult()
            self._populate_response_result(http_response_result, response)
            http_response_result.cookies = ujson.dumps(self.getCookies())
            with open(storeFilePath, 'wb') as file_stream:
                for chunk in response.iter_content(chunk_size=64 * 1024):
                    if chunk:
                        file_stream.write(chunk)
        record_http_exchange(http_response_result)
        return http_response_result

    def _dealResponseResult(self, response):
        """将requests响应封装为HttpResponseResult。"""
        if self._encoding:
            response.encoding = self._encoding
        http_response_result = HttpResponseResult()
        self._populate_response_result(http_response_result, response)
        http_response_result.cookies = ujson.dumps(self.getCookies())
        http_response_result.body = response.content.decode(
            self._encoding or response.encoding or 'utf-8',
            errors=self._decode_errors,
        )
        record_http_exchange(http_response_result)
        return http_response_result

    @staticmethod
    def _populate_response_result(http_response_result, response):
        """补充响应状态、耗时以及用于失败诊断的请求摘要。"""
        http_response_result.status_code = response.status_code
        http_response_result.headers = str(response.headers)
        http_response_result.headers_dict = dict(response.headers)
        http_response_result.elapsed_ms = round(response.elapsed.total_seconds() * 1000, 2)
        http_response_result.url = response.url
        http_response_result.request_method = response.request.method
        http_response_result.request_headers = dict(response.request.headers)
        http_response_result.request_body = response.request.body

    def changeUrl(self, url):
        self._url = url

    def closeSession(self):
        self._session.close()
