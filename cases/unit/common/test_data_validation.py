"""作用：验证API与数据库字段标准化、映射比较和最终一致性轮询。"""

from datetime import datetime
from datetime import timedelta
from datetime import timezone
from decimal import Decimal

import pytest

from common.data_validation import assert_api_database_match
from common.data_validation import normalize_decimal
from common.data_validation import normalize_value
from common.data_validation import poll_until


pytestmark = pytest.mark.unit


def test_normalizes_decimal_datetime_bytes_and_nested_values():
    """验证常见数据库类型可以转换为稳定的API可比较形式。"""
    source = {
        'amount': Decimal('10.00'),
        'created_at': datetime(
            2026,
            8,
            18,
            16,
            0,
            tzinfo=timezone(timedelta(hours=8)),
        ),
        'name': b'order',
        'items': [Decimal('1.50')],
    }

    assert normalize_value(source) == {
        'amount': '10',
        'created_at': '2026-08-18T08:00:00+00:00',
        'name': 'order',
        'items': ['1.5'],
    }


def test_compares_api_and_database_records_with_field_mapping():
    """验证API字段名和数据库列名不同也能比较关键业务数据。"""
    api_record = {
        'id': 'order-1001',
        'total_amount': '99.00',
        'status': 'PAID',
    }
    database_record = {
        'order_no': 'order-1001',
        'amount': Decimal('99.0'),
        'order_status': 'PAID',
        'internal_version': 3,
    }

    assert_api_database_match(
        api_record,
        database_record,
        field_mapping={
            'id': 'order_no',
            'total_amount': 'amount',
            'status': 'order_status',
        },
        normalizers={'total_amount': normalize_decimal},
    )


def test_database_comparison_masks_sensitive_mismatch():
    """验证数据库比对失败时不会在断言消息中泄漏Token。"""
    with pytest.raises(AssertionError) as error_info:
        assert_api_database_match(
            {'access_token': 'api-secret-token'},
            {'token_value': 'database-secret-token'},
            field_mapping={'access_token': 'token_value'},
        )

    error_message = str(error_info.value)
    assert 'api-secret-token' not in error_message
    assert 'database-secret-token' not in error_message
    assert '***已脱敏***' in error_message


def test_poll_until_returns_when_database_reaches_expected_state():
    """验证轮询会在数据库状态达到预期时立即返回。"""
    query_results = iter([None, {'status': 'CREATED'}, {'status': 'PAID'}])
    current_time = [0.0]

    def fake_clock():
        return current_time[0]

    def fake_sleep(seconds):
        current_time[0] += seconds

    result = poll_until(
        query=lambda: next(query_results),
        condition=lambda row: row and row['status'] == 'PAID',
        timeout=5,
        interval=0.5,
        description='订单状态变为PAID',
        clock=fake_clock,
        sleeper=fake_sleep,
    )

    assert result == {'status': 'PAID'}
    assert current_time[0] == 1.0


def test_poll_until_times_out_with_clear_message():
    """验证数据始终未落库时产生包含超时和尝试次数的错误。"""
    current_time = [0.0]

    def fake_clock():
        return current_time[0]

    def fake_sleep(seconds):
        current_time[0] += seconds

    with pytest.raises(TimeoutError, match='订单记录出现.*尝试次数=3'):
        poll_until(
            query=lambda: None,
            condition=bool,
            timeout=1,
            interval=0.5,
            description='订单记录出现',
            clock=fake_clock,
            sleeper=fake_sleep,
        )
