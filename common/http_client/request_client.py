# -*- coding:utf8 -*-
"""作用：提供request client相关的通用工具能力。"""

from common.http_client.diagnostics import record_http_exchange
from pojo.http_response_result import HttpResponseResult
from requests.adapters import HTTPAdapter
import requests
import ujson
class DoRequest(object):
    def __init__(self,url,encoding='utf-8',pool_connections=10,pool_maxsize=10, max_retries=2,timeout=30,verify=True):
        self._url=url
        self._encoding=encoding
        self._headers = {}
        self._cookies = {}
        self._proxies={}
        self._timeout=timeout
        self._verify=verify
        self._session=requests.session()
        httpAdapter=HTTPAdapter(pool_connections=pool_connections,pool_maxsize=pool_maxsize,max_retries=max_retries)
        self._session.mount('http://',httpAdapter)
        self._session.mount('https://', httpAdapter)

    def setHeaders(self, headers):
        self._headers = headers

    def updateHeaders(self, headers):
        self._headers.update(headers)

    def removeHeader(self,key):
        self._headers.pop(key)

    def getHeaders(self):
        return self._headers

    def setCookies(self, cookies):
        self._cookies = cookies

    def updateCookies(self, cookies):
        self._cookies.update(cookies)

    def getCookies(self):
        return self._cookies

    def setTimeout(self,seconds):
        self._timeout=seconds

    def setProxies(self,proxies):
        self._proxies=proxies

    def setVerify(self,verify:bool=True):
        self._verify=verify

    def post_with_form(self,path,params=None,**kwargs):
        r=self._session.post(self._url+path,data=params,headers=self._headers,cookies=self._cookies,timeout=self._timeout,
                        proxies=self._proxies,verify=self._verify,**kwargs)
        return self._dealResponseResult(r)

    def post_with_file(self,path,filePath,params=None,fileKey='file',**kwargs):
        with open(filePath, 'rb') as file_stream:
            files = {fileKey: file_stream}
            r = self._session.post(self._url+path, data=params, files=files,headers=self._headers, cookies=self._cookies,
                              timeout=self._timeout,proxies=self._proxies,verify=self._verify,**kwargs)
        return self._dealResponseResult(r)

    def put(self,path,params=None,**kwargs):
        r=self._session.put(self._url+path,data=params,headers=self._headers,cookies=self._cookies,timeout=self._timeout,
                        proxies=self._proxies,verify=self._verify,**kwargs)
        return self._dealResponseResult(r)

    def get(self,path,params=None,**kwargs):
        r = self._session.get(self._url+path, params=params, headers=self._headers, cookies=self._cookies, timeout=self._timeout,
                          proxies=self._proxies,verify=self._verify,**kwargs)
        return self._dealResponseResult(r)

    def delete(self,path,**kwargs):
        r = self._session.delete(self._url+path,headers=self._headers, cookies=self._cookies, timeout=self._timeout,
                          proxies=self._proxies,verify=self._verify,**kwargs)
        return self._dealResponseResult(r)

    def getFile(self,path,storeFilePath,params=None,**kwargs):
        """
        下载文件
        :param path:
        :param storeFilePath:
        :param params:
        :return:
        """
        kwargs['stream'] = True
        with self._session.get(self._url + path, params=params, headers=self._headers, cookies=self._cookies,
                               timeout=self._timeout, proxies=self._proxies, verify=self._verify, **kwargs) as r:
            httpResponseResult = HttpResponseResult()
            self._populate_response_result(httpResponseResult, r)
            self.updateCookies(self._session.cookies.get_dict())
            httpResponseResult.cookies=ujson.dumps(self.getCookies())
            with open(storeFilePath,"wb") as f:
                for chunk in r.iter_content(chunk_size=64 * 1024):
                    if chunk:
                        f.write(chunk)
        record_http_exchange(httpResponseResult)
        return httpResponseResult

    def _dealResponseResult(self,r):
        """
        将请求结果封装到HttpResponseResult
        :param r: requests请求响应
        :return:
        """
        r.encoding = self._encoding
        httpResponseResult = HttpResponseResult()
        self._populate_response_result(httpResponseResult, r)
        self.updateCookies(self._session.cookies.get_dict())
        httpResponseResult.cookies = ujson.dumps(self.getCookies())
        httpResponseResult.body = r.content.decode(self._encoding)
        record_http_exchange(httpResponseResult)
        return httpResponseResult

    @staticmethod
    def _populate_response_result(http_response_result, response):
        """补充响应状态、耗时以及用于失败诊断的请求摘要。"""
        http_response_result.status_code = response.status_code
        http_response_result.headers = response.headers.__str__()
        http_response_result.headers_dict = dict(response.headers)
        http_response_result.elapsed_ms = round(response.elapsed.total_seconds() * 1000, 2)
        http_response_result.url = response.url
        http_response_result.request_method = response.request.method
        http_response_result.request_headers = dict(response.request.headers)
        http_response_result.request_body = response.request.body

    def changeUrl(self,url):
        self._url=url

    def closeSession(self):
        self._session.close()
