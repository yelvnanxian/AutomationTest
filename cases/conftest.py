"""作用：提供所有测试类型共用的失败诊断和报告钩子。"""

import json

import allure
import pytest

from common.http_client.diagnostics import (
    build_http_diagnostic,
    get_http_exchanges,
    reset_http_exchanges,
)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """把pytest各阶段结果保存到测试节点，供fixture判断是否失败。"""
    outcome = yield
    report = outcome.get_result()
    setattr(item, 'report_%s' % report.when, report)


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
