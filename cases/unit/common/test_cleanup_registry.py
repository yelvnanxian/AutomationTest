"""作用：验证测试数据清理能够反向执行、继续处理异常并避免重复清理。"""

import pytest

from common.cleanup_registry import CleanupError
from common.cleanup_registry import CleanupRegistry


pytestmark = pytest.mark.unit


def test_cleanup_runs_in_reverse_creation_order():
    """验证订单明细、订单、用户按照资源创建的反方向清理。"""
    cleaned_resources = []
    registry = CleanupRegistry()
    registry.add(cleaned_resources.append, 'user', name='删除用户')
    registry.add(cleaned_resources.append, 'order', name='删除订单')
    registry.add(cleaned_resources.append, 'item', name='删除订单明细')

    registry.run_or_raise()

    assert cleaned_resources == ['item', 'order', 'user']


def test_cleanup_continues_after_failure_and_reports_all_errors():
    """验证一项清理失败不会阻止其他资源清理，结束后统一报告异常。"""
    cleaned_resources = []
    registry = CleanupRegistry()

    def failed_cleanup():
        raise RuntimeError('service unavailable')

    registry.add(cleaned_resources.append, 'user', name='删除用户')
    registry.add(failed_cleanup, name='删除订单')
    registry.add(cleaned_resources.append, 'item', name='删除订单明细')

    with pytest.raises(CleanupError, match='删除订单:service unavailable'):
        registry.run_or_raise()

    assert cleaned_resources == ['item', 'user']
    assert registry.run() == []


def test_cleanup_action_can_be_cancelled_after_business_delete():
    """验证业务流程主动删除资源后，可以取消兜底清理避免重复请求。"""
    cleaned_resources = []
    registry = CleanupRegistry()
    action = registry.add(cleaned_resources.append, 'order', name='删除订单')

    assert registry.cancel(action) is True
    registry.run_or_raise()

    assert cleaned_resources == []


def test_context_manager_preserves_original_test_error():
    """验证业务断言和清理同时失败时，原始业务异常不会被清理异常覆盖。"""
    def failed_cleanup():
        raise RuntimeError('cleanup failed')

    with pytest.raises(AssertionError, match='business failed') as error_info:
        with CleanupRegistry() as registry:
            registry.add(failed_cleanup, name='删除订单')
            raise AssertionError('business failed')

    assert any('测试数据清理失败' in note for note in error_info.value.__notes__)
