"""作用：提供API状态、性能、结构、Header和业务字段的通用断言。"""

import re

from jsonschema import FormatChecker
from jsonschema import validate

from common.api_test_context import extract_json_value


_SENSITIVE_NAME_PATTERN = re.compile(
    r'(?i)(password|passwd|token|secret|authorization|cookie|session)'
)


def _safe_value(name, value):
    return '***已脱敏***' if _SENSITIVE_NAME_PATTERN.search(name) else repr(value)


def assert_status_code(response, expected_status_code):
    """断言HTTP状态码符合预期。"""
    assert response.status_code == expected_status_code, (
        '预期状态码%s，实际状态码%s，URL:%s'
        % (expected_status_code, response.status_code, response.url)
    )


def assert_response_time(response, max_elapsed_ms):
    """断言接口响应时间不超过指定毫秒数。"""
    assert response.elapsed_ms is not None, '响应中缺少elapsed_ms性能数据'
    assert response.elapsed_ms <= max_elapsed_ms, (
        '接口响应耗时%.2fms，超过限制%sms，URL:%s'
        % (response.elapsed_ms, max_elapsed_ms, response.url)
    )


def assert_json_schema(response, schema):
    """断言响应正文符合JSON Schema，并实际校验URI、日期等format。"""
    validate(
        instance=response.json(),
        schema=schema,
        format_checker=FormatChecker(),
    )


def assert_header_equals(response, header_name, expected_value):
    """不区分Header名称大小写断言响应Header值。"""
    headers = getattr(response, 'headers_dict', {}) or {}
    actual_value = next(
        (
            value for key, value in headers.items()
            if key.lower() == header_name.lower()
        ),
        None,
    )
    assert actual_value == expected_value, (
        '响应Header %s不符合预期，预期:%s，实际:%s，URL:%s'
        % (
            header_name,
            _safe_value(header_name, expected_value),
            _safe_value(header_name, actual_value),
            response.url,
        )
    )


def assert_header_contains(response, header_name, expected_part):
    """断言响应Header包含指定内容，例如Content-Type包含application/json。"""
    headers = getattr(response, 'headers_dict', {}) or {}
    actual_value = next(
        (
            value for key, value in headers.items()
            if key.lower() == header_name.lower()
        ),
        None,
    )
    assert actual_value is not None and expected_part in actual_value, (
        '响应Header %s未包含%s，实际:%s，URL:%s'
        % (
            header_name,
            _safe_value(header_name, expected_part),
            _safe_value(header_name, actual_value),
            response.url,
        )
    )


def assert_json_value(response, path, expected_value):
    """断言JSON路径对应值，适用于跨接口ID和业务状态校验。"""
    actual_value = extract_json_value(response, path)
    assert actual_value == expected_value, (
        'JSON路径%s不符合预期，预期:%s，实际:%s，URL:%s'
        % (
            path,
            _safe_value(path, expected_value),
            _safe_value(path, actual_value),
            response.url,
        )
    )


def assert_mapping_contains(actual_mapping, expected_mapping, mapping_name='数据对象'):
    """只校验关注的业务字段，允许响应或数据库对象包含其他字段。"""
    missing_keys = [key for key in expected_mapping if key not in actual_mapping]
    assert not missing_keys, '%s缺少字段:%s' % (
        mapping_name,
        ', '.join(missing_keys),
    )
    mismatches = {
        key: {
            'expected': _safe_value(key, expected_value),
            'actual': _safe_value(key, actual_mapping[key]),
        }
        for key, expected_value in expected_mapping.items()
        if actual_mapping[key] != expected_value
    }
    assert not mismatches, '%s字段值不一致:%s' % (mapping_name, mismatches)


def assert_collection_contains(collection, expected_item, key=None):
    """断言列表包含指定对象；传key时按该字段值查找。"""
    if key is None:
        found = expected_item in collection
    else:
        found = any(
            isinstance(item, dict) and item.get(key) == expected_item
            for item in collection
        )
    assert found, '集合中未找到%s:%s' % (
        key or '目标值',
        _safe_value(key or 'value', expected_item),
    )
