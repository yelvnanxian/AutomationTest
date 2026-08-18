"""作用：提供所有测试类型共用的失败诊断和报告钩子。"""

import json
import logging
import os
from pathlib import Path

import allure
import pytest

from common.api_test_context import ApiTestContext
from common.cleanup_registry import CleanupRegistry
from common.http_client.diagnostics import (
    build_http_diagnostic,
    get_http_exchanges,
    reset_http_exchanges,
)
from common.selenium.diagnostics import (
    attach_web_driver_diagnostics,
    find_web_drivers,
)


LOGGER = logging.getLogger('automation_test')
PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def api_context():
    """为单条API用例提供独立关联上下文。"""
    context = ApiTestContext()
    yield context
    context.clear()


@pytest.fixture
def cleanup_registry():
    """登记API或数据库测试创建的数据，并在用例结束后反向清理。"""
    registry = CleanupRegistry()
    yield registry
    registry.run_or_raise()


def get_worker_id():
    """返回xdist worker编号，串行执行时返回main。"""
    return os.getenv('PYTEST_XDIST_WORKER', 'main')


@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    """设置串行或并行测试对应的规范化日志文件路径。"""
    logging_plugin = config.pluginmanager.get_plugin('logging-plugin')
    if logging_plugin is None:
        return

    worker_id = get_worker_id()
    log_name = 'test.log' if worker_id == 'main' else 'test_%s.log' % worker_id
    log_path = PROJECT_ROOT / 'logs' / log_name
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging_plugin.set_log_path(str(log_path))


def pytest_sessionstart(session):
    """记录测试会话开始。"""
    LOGGER.info('测试会话开始 worker=%s', get_worker_id())


def pytest_sessionfinish(session, exitstatus):
    """记录测试会话结束及pytest退出状态码。"""
    LOGGER.info(
        '测试会话结束 worker=%s exit_status=%s',
        get_worker_id(),
        exitstatus,
    )


def pytest_runtest_logstart(nodeid, location):
    """记录单条测试开始。"""
    LOGGER.info('测试开始 worker=%s case=%s', get_worker_id(), nodeid)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """把pytest各阶段结果保存到测试节点，供fixture判断是否失败。"""
    outcome = yield
    report = outcome.get_result()
    setattr(item, 'report_%s' % report.when, report)

    should_log = report.when == 'call' or (
        report.when in ('setup', 'teardown') and report.outcome != 'passed'
    )
    if should_log:
        LOGGER.info(
            '测试结果 worker=%s case=%s stage=%s result=%s duration=%.3fs',
            get_worker_id(),
            report.nodeid,
            report.when,
            report.outcome,
            report.duration,
        )

    if report.failed and report.when in ('setup', 'call'):
        drivers = find_web_drivers(item.funcargs.values())
        for index, driver in enumerate(drivers, start=1):
            errors = attach_web_driver_diagnostics(
                driver,
                attachment_prefix='Web UI失败诊断-%s' % index,
            )
            if errors:
                LOGGER.warning(
                    'Web UI失败诊断部分收集失败 case=%s errors=%s',
                    report.nodeid,
                    '; '.join(errors),
                )


@pytest.fixture(autouse=True)
def attach_http_diagnostics_on_failure(request):
    """测试失败时自动将本用例的HTTP请求响应附加到Allure。"""
    reset_http_exchanges()
    yield

    setup_report = getattr(request.node, 'report_setup', None)
    call_report = getattr(request.node, 'report_call', None)
    if not any(report and report.failed for report in (setup_report, call_report)):
        return

    for index, response in enumerate(get_http_exchanges(), start=1):
        diagnostic = build_http_diagnostic(response)
        allure.attach(
            json.dumps(diagnostic, ensure_ascii=False, indent=2),
            name='HTTP请求响应-%s' % index,
            attachment_type=allure.attachment_type.JSON,
        )
