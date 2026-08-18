"""作用：统一API与数据库数据格式，并轮询验证最终一致性结果。"""

import re
import time
from datetime import date
from datetime import datetime
from datetime import timezone
from decimal import Decimal


_SENSITIVE_NAME_PATTERN = re.compile(
    r'(?i)(password|passwd|token|secret|authorization|cookie|session)'
)


def normalize_value(value, default_timezone=timezone.utc):
    """递归标准化Decimal、日期时间、bytes及嵌套数据结构。"""
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, Decimal):
        normalized_decimal = value.normalize()
        return format(normalized_decimal, 'f')
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=default_timezone)
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')
    if isinstance(value, dict):
        return {
            key: normalize_value(item, default_timezone)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [normalize_value(item, default_timezone) for item in value]
    return value


def normalize_decimal(value):
    """把API字符串、数字和数据库Decimal统一为无多余零的十进制字符串。"""
    if value is None:
        return None
    return format(Decimal(str(value)).normalize(), 'f')


def normalize_datetime(value, default_timezone=timezone.utc):
    """把ISO字符串或datetime统一转换为UTC ISO格式。"""
    if value is None:
        return None
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace('Z', '+00:00'))
    return normalize_value(value, default_timezone)


def normalize_boolean(value):
    """统一API布尔值和数据库0/1，但拒绝含义不明确的其他值。"""
    if isinstance(value, bool):
        return value
    if value in (0, 1, '0', '1'):
        return bool(int(value))
    raise ValueError('无法标准化为布尔值:%s' % value)


def _safe_value(field_name, value):
    return '***已脱敏***' if _SENSITIVE_NAME_PATTERN.search(field_name) else repr(value)


def assert_api_database_match(
    api_record,
    database_record,
    field_mapping=None,
    normalizers=None,
):
    """根据字段映射比较API和数据库记录，只校验明确指定的业务字段。"""
    field_mapping = field_mapping or {
        field_name: field_name for field_name in api_record
    }
    normalizers = normalizers or {}
    missing_fields = []
    mismatches = {}

    for api_field, database_field in field_mapping.items():
        if api_field not in api_record or database_field not in database_record:
            missing_fields.append('%s->%s' % (api_field, database_field))
            continue
        api_value = api_record[api_field]
        database_value = database_record[database_field]
        normalizer = normalizers.get(api_field, normalize_value)
        normalized_api_value = normalizer(api_value)
        normalized_database_value = normalizer(database_value)
        if normalized_api_value != normalized_database_value:
            mismatches[api_field] = {
                'database_field': database_field,
                'api': _safe_value(api_field, normalized_api_value),
                'database': _safe_value(api_field, normalized_database_value),
            }

    assert not missing_fields, 'API或数据库缺少关联字段:%s' % ', '.join(missing_fields)
    assert not mismatches, 'API与数据库字段不一致:%s' % mismatches


def poll_until(
    query,
    condition,
    timeout=10,
    interval=0.5,
    description='数据达到预期状态',
    ignored_exceptions=(),
    clock=time.monotonic,
    sleeper=time.sleep,
):
    """轮询查询直到条件满足，避免使用固定sleep等待异步数据落库。"""
    if timeout < 0:
        raise ValueError('timeout不能小于0')
    if interval < 0:
        raise ValueError('interval不能小于0')

    deadline = clock() + timeout
    attempt_count = 0
    while True:
        attempt_count += 1
        try:
            result = query()
        except ignored_exceptions:
            result = None
        if condition(result):
            return result
        remaining_time = deadline - clock()
        if remaining_time <= 0:
            raise TimeoutError(
                '等待%s超时，timeout=%ss，尝试次数=%s'
                % (description, timeout, attempt_count)
            )
        sleeper(min(interval, remaining_time))


def wait_for_database_record(
    query,
    timeout=10,
    interval=0.5,
    description='数据库记录出现',
):
    """等待数据库查询返回首条非空记录。"""
    return poll_until(
        query=query,
        condition=lambda result: bool(result),
        timeout=timeout,
        interval=interval,
        description=description,
    )
