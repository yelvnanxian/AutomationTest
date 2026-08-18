"""作用：验证API关联上下文可提取JSON、Header、Cookie并保护敏感数据。"""

import json

import pytest

from common.api_test_context import ApiTestContext
from common.api_test_context import extract_json_value
from pojo.http_response_result import HttpResponseResult


pytestmark = pytest.mark.unit


def build_response():
    response = HttpResponseResult()
    response.body = json.dumps(
        {
            'data': {
                'order': {'id': 'order-1001'},
                'items': [{'id': 'item-1'}, {'id': 'item-2'}],
                'access_token': 'secret-access-token',
            }
        }
    )
    response.headers_dict = {'X-Request-ID': 'request-1001'}
    response.cookies = json.dumps({'session': 'session-cookie'})
    return response


def test_captures_cross_request_values_from_response():
    """验证业务ID、列表字段、Header和Cookie可保存并供后续接口使用。"""
    context = ApiTestContext()
    response = build_response()

    context.capture_json(response, 'data.order.id', 'order_id')
    context.capture_json(response, 'data.items[1].id', 'item_id')
    context.capture_header(response, 'x-request-id', 'request_id')
    context.capture_cookie(response, 'session', 'session_cookie')

    assert context.require('order_id', 'item_id') == ('order-1001', 'item-2')
    assert context.get('request_id') == 'request-1001'
    assert context.get('session_cookie') == 'session-cookie'


def test_context_description_masks_sensitive_values():
    """验证Token、Cookie、密码等关联值不会进入安全摘要。"""
    context = ApiTestContext()
    context.set('access_token', 'secret-access-token')
    context.set('session_cookie', 'secret-session')
    context.set('order_id', 'order-1001')
    context.set(
        'login_response',
        {
            'user': 'tester',
            'data': {'refresh_token': 'secret-refresh-token'},
        },
    )

    description = context.describe()

    assert description == {
        'access_token': '***已脱敏***',
        'session_cookie': '***已脱敏***',
        'order_id': 'order-1001',
        'login_response': {
            'user': 'tester',
            'data': {'refresh_token': '***已脱敏***'},
        },
    }


def test_missing_path_and_context_key_have_clear_errors():
    """验证关联路径或key错误时快速失败，并显示可用key而不输出敏感值。"""
    context = ApiTestContext()
    context.set('order_id', 'order-1001')

    with pytest.raises(KeyError, match='data.missing.id'):
        extract_json_value(build_response(), 'data.missing.id')

    with pytest.raises(KeyError, match='当前可用key:order_id'):
        context.get('user_id')

    with pytest.raises(ValueError, match='路径格式无效'):
        extract_json_value(build_response(), 'data..order.id')
