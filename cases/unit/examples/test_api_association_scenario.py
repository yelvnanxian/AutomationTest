"""作用：以可执行示例展示登录、Token/Cookie关联、数据校验和资源清理流程。"""

import json
from decimal import Decimal

import pytest

from common.data_validation import assert_api_database_match
from common.data_validation import normalize_decimal
from common.data_validation import poll_until
from common.http_client.auth import BearerTokenProvider
from common.http_client.auth import CompositeAuthProvider
from common.http_client.auth import CookieAuthProvider
from common.http_client.auth import CsrfTokenProvider
from common.http_client.response_assertions import assert_json_value
from pojo.http_response_result import HttpResponseResult


pytestmark = pytest.mark.unit


class FakeOrderService:
    """模拟真实项目Service层，示例不访问外部网络或数据库。"""

    def __init__(self):
        self.deleted_order_ids = []

    def login(self):
        return build_response(
            {
                'data': {
                    'access_token': 'example-access-token',
                    'refresh_token': 'example-refresh-token',
                    'expires_in': 3600,
                    'csrf_token': 'example-csrf-token',
                }
            },
            cookies={'session': 'example-session-cookie'},
        )

    def create_order(self):
        return build_response(
            {
                'data': {
                    'id': 'order-1001',
                    'total_amount': '99.00',
                    'status': 'PAID',
                }
            }
        )

    def delete_order(self, order_id):
        self.deleted_order_ids.append(order_id)


def build_response(body, cookies=None):
    response = HttpResponseResult()
    response.status_code = 200
    response.body = json.dumps(body)
    response.cookies = json.dumps(cookies or {})
    response.headers_dict = {'Content-Type': 'application/json'}
    response.url = 'https://example.test/api'
    return response


def test_complete_api_association_flow(api_context, cleanup_registry):
    """验证完整场景不依赖用例顺序，并在失败时具备兜底清理能力。"""
    service = FakeOrderService()

    login_response = service.login()
    access_token = api_context.capture_json(
        login_response,
        'data.access_token',
        'access_token',
    )
    csrf_token = api_context.capture_json(
        login_response,
        'data.csrf_token',
        'csrf_token',
    )
    session_cookie = api_context.capture_cookie(
        login_response,
        'session',
        'session_cookie',
    )
    auth_provider = CompositeAuthProvider(
        BearerTokenProvider(access_token),
        CookieAuthProvider({'session': session_cookie}),
        CsrfTokenProvider(csrf_token),
    )
    request_headers = {}
    request_cookies = {}
    auth_provider.apply(request_headers, request_cookies)

    create_response = service.create_order()
    order_id = api_context.capture_json(create_response, 'data.id', 'order_id')
    cleanup_action = cleanup_registry.add(
        service.delete_order,
        order_id,
        name='删除示例订单',
    )

    database_results = iter(
        [
            None,
            {
                'order_no': order_id,
                'amount': Decimal('99.0'),
                'order_status': 'PAID',
            },
        ]
    )
    database_record = poll_until(
        query=lambda: next(database_results),
        condition=bool,
        timeout=1,
        interval=0,
        description='示例订单写入数据库',
    )

    assert request_headers['Authorization'] == 'Bearer example-access-token'
    assert request_headers['X-CSRF-Token'] == 'example-csrf-token'
    assert request_cookies == {'session': 'example-session-cookie'}
    assert_json_value(create_response, 'data.id', order_id)
    assert_api_database_match(
        create_response.json()['data'],
        database_record,
        field_mapping={
            'id': 'order_no',
            'total_amount': 'amount',
            'status': 'order_status',
        },
        normalizers={'total_amount': normalize_decimal},
    )

    service.delete_order(order_id)
    cleanup_registry.cancel(cleanup_action)

    assert service.deleted_order_ids == ['order-1001']
