"""作用：记录HTTP请求响应，并在测试失败时生成脱敏诊断信息。"""

import re
from contextvars import ContextVar


_HTTP_EXCHANGES = ContextVar('http_exchanges', default=None)
_SENSITIVE_HEADERS = {
    'authorization',
    'cookie',
    'proxy-authorization',
    'set-cookie',
    'x-api-key',
}
_SENSITIVE_VALUE_PATTERN = re.compile(
    r'(?i)(password|passwd|token|secret|authorization)(["\s:=]+)([^&\s",}]+)'
)
_SENSITIVE_QUERY_PATTERN = re.compile(
    r'(?i)([?&](?:password|passwd|token|secret|api_key|access_key)=)[^&#]*'
)
_BASIC_AUTH_PATH_PATTERN = re.compile(r'(/basic-auth/[^/]+/)[^/?#]+')
_MAX_BODY_LENGTH = 20000


def reset_http_exchanges():
    """为当前测试重置HTTP请求响应记录。"""
    _HTTP_EXCHANGES.set([])


def record_http_exchange(response):
    """记录当前上下文中的一次HTTP请求响应。"""
    exchanges = _HTTP_EXCHANGES.get()
    if exchanges is None:
        exchanges = []
        _HTTP_EXCHANGES.set(exchanges)
    exchanges.append(response)


def get_http_exchanges():
    """返回当前测试记录的HTTP请求响应。"""
    return tuple(_HTTP_EXCHANGES.get() or ())


def _sanitize_headers(headers):
    return {
        key: '***已脱敏***' if key.lower() in _SENSITIVE_HEADERS else value
        for key, value in (headers or {}).items()
    }


def _sanitize_body(body):
    if body is None:
        return None
    if isinstance(body, bytes):
        body = body.decode('utf-8', errors='replace')
    body_text = str(body)
    body_text = _SENSITIVE_VALUE_PATTERN.sub(r'\1\2***已脱敏***', body_text)
    if len(body_text) > _MAX_BODY_LENGTH:
        return body_text[:_MAX_BODY_LENGTH] + '\n...正文已截断...'
    return body_text


def _sanitize_url(url):
    if not url:
        return url
    sanitized_url = _SENSITIVE_QUERY_PATTERN.sub(r'\1***已脱敏***', url)
    return _BASIC_AUTH_PATH_PATTERN.sub(r'\1***已脱敏***', sanitized_url)


def build_http_diagnostic(response):
    """把响应对象转换成适合Allure附件的脱敏字典。"""
    return {
        'request': {
            'method': response.request_method,
            'url': _sanitize_url(response.url),
            'headers': _sanitize_headers(response.request_headers),
            'body': _sanitize_body(response.request_body),
        },
        'response': {
            'status_code': response.status_code,
            'elapsed_ms': response.elapsed_ms,
            'headers': _sanitize_headers(response.headers_dict),
            'body': _sanitize_body(response.body),
        },
    }
