"""作用：验证Web UI失败诊断的驱动识别、附件生成和敏感信息脱敏。"""

import json

import pytest

from common.selenium.diagnostics import (
    attach_web_driver_diagnostics,
    find_web_drivers,
)


pytestmark = pytest.mark.unit


class FakeDriver:
    title = '失败页面'
    current_url = (
        'https://example.test/page?token=secret_token&email=user@example.test'
    )
    page_source = (
        '<input name="password" value="secret_password">'
        '<input name="phone" value="13800138000">'
        '<input name="api_key" value="secret_api_key">'
    )

    def get_screenshot_as_png(self):
        return b'png-data'

    def get_log(self, log_type):
        assert log_type == 'browser'
        return [{'level': 'SEVERE', 'message': 'token=secret_console_token'}]


class FakeBrowserOperator:
    def __init__(self, driver):
        self._driver = driver


class FakeClient:
    def __init__(self, driver):
        self.driver = driver
        self.browserOperator = FakeBrowserOperator(driver)


def test_finds_each_web_driver_only_once():
    """验证同一驱动从client和browserOperator暴露时不会重复附加。"""
    driver = FakeDriver()

    drivers = find_web_drivers([FakeClient(driver), FakeBrowserOperator(driver)])

    assert drivers == [driver]


def test_attaches_diagnostics_and_masks_sensitive_values(monkeypatch):
    """验证失败附件完整生成，URL、源码和控制台中的Token或密码被脱敏。"""
    attachments = []

    def fake_attach(body, name, attachment_type):
        attachments.append(
            {'body': body, 'name': name, 'attachment_type': attachment_type}
        )

    monkeypatch.setattr('common.selenium.diagnostics.allure.attach', fake_attach)

    errors = attach_web_driver_diagnostics(FakeDriver())

    assert errors == []
    assert len(attachments) == 4
    diagnostic_text = json.dumps(attachments, ensure_ascii=False, default=str)
    assert 'secret_token' not in diagnostic_text
    assert 'secret_password' not in diagnostic_text
    assert 'secret_console_token' not in diagnostic_text
    assert 'user@example.test' not in diagnostic_text
    assert '13800138000' not in diagnostic_text
    assert 'secret_api_key' not in diagnostic_text
    assert '***已脱敏***' in diagnostic_text
