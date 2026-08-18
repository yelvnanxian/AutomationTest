"""作用：为单条API用例保存Token、业务ID和其他跨接口动态关联数据。"""

import json
import re


_MISSING = object()
_SENSITIVE_KEY_PATTERN = re.compile(
    r'(?i)(password|passwd|token|secret|authorization|cookie|session)'
)
_PATH_TOKEN_PATTERN = re.compile(r'([^.\[\]]+)|\[(\d+)\]')
_VALID_PATH_PATTERN = re.compile(
    r'^[^.\[\]]+(?:(?:\.[^.\[\]]+)|(?:\[\d+\]))*$'
)


def _sanitize_context_value(key, value):
    if _SENSITIVE_KEY_PATTERN.search(str(key)):
        return '***已脱敏***'
    if isinstance(value, dict):
        return {
            nested_key: _sanitize_context_value(nested_key, nested_value)
            for nested_key, nested_value in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_sanitize_context_value(key, item) for item in value]
    return value


class ApiTestContext:
    """用例级关联上下文，不使用模块全局变量或磁盘临时文件。"""

    def __init__(self):
        self._values = {}

    def set(self, key, value):
        if not isinstance(key, str) or not key.strip():
            raise ValueError('关联数据key不能为空')
        self._values[key] = value
        return value

    def get(self, key, default=_MISSING):
        if key in self._values:
            return self._values[key]
        if default is not _MISSING:
            return default
        available_keys = ', '.join(sorted(self._values)) or '无'
        raise KeyError('缺少关联数据:%s，当前可用key:%s' % (key, available_keys))

    def require(self, *keys):
        """一次读取多个必需字段，返回顺序与传入key一致。"""
        return tuple(self.get(key) for key in keys)

    def pop(self, key, default=_MISSING):
        if key in self._values:
            return self._values.pop(key)
        if default is not _MISSING:
            return default
        raise KeyError('缺少关联数据:%s' % key)

    def clear(self):
        self._values.clear()

    def describe(self):
        """返回可安全写入日志的关联数据摘要，敏感值统一脱敏。"""
        return {
            key: _sanitize_context_value(key, value)
            for key, value in self._values.items()
        }

    def capture_json(self, response_or_data, path, key=None):
        value = extract_json_value(response_or_data, path)
        return self.set(key or path, value)

    def capture_header(self, response, header_name, key=None):
        value = extract_header_value(response, header_name)
        return self.set(key or header_name, value)

    def capture_cookie(self, response, cookie_name, key=None):
        value = extract_cookie_value(response, cookie_name)
        return self.set(key or cookie_name, value)


def _response_json(response_or_data):
    if hasattr(response_or_data, 'json') and callable(response_or_data.json):
        return response_or_data.json()
    return response_or_data


def extract_json_value(response_or_data, path):
    """从JSON对象提取如data.order.id或data.items[0].id的字段。"""
    current_value = _response_json(response_or_data)
    if not path:
        raise ValueError('JSON关联路径不能为空')
    if not _VALID_PATH_PATTERN.fullmatch(path):
        raise ValueError('JSON关联路径格式无效:%s' % path)
    path_tokens = list(_PATH_TOKEN_PATTERN.finditer(path))

    for match in path_tokens:
        object_key, list_index = match.groups()
        try:
            if object_key is not None:
                current_value = current_value[object_key]
            else:
                current_value = current_value[int(list_index)]
        except (KeyError, IndexError, TypeError) as exc:
            raise KeyError('无法从JSON路径%s提取到%s' % (path, match.group(0))) from exc
    return current_value


def extract_header_value(response, header_name):
    """不区分大小写提取响应Header。"""
    headers = getattr(response, 'headers_dict', {}) or {}
    for key, value in headers.items():
        if key.lower() == header_name.lower():
            return value
    raise KeyError('响应中缺少Header:%s' % header_name)


def extract_cookie_value(response, cookie_name):
    """从统一响应对象序列化的Cookie中提取指定值。"""
    cookies = getattr(response, 'cookies', None)
    if isinstance(cookies, str):
        cookies = json.loads(cookies or '{}')
    cookies = cookies or {}
    if cookie_name not in cookies:
        raise KeyError('响应中缺少Cookie:%s' % cookie_name)
    return cookies[cookie_name]
