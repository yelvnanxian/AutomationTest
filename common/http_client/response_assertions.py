"""作用：提供API响应状态、耗时和JSON结构的通用断言。"""

from jsonschema import validate


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
    """断言响应正文符合指定JSON Schema。"""
    validate(instance=response.json(), schema=schema)
