"""作用：在Web UI测试失败时安全收集浏览器截图、页面信息和控制台日志。"""

import json
import re

import allure


_SENSITIVE_PATTERN = re.compile(
    r'(?i)(password|passwd|token|secret|authorization|cookie|'
    r'api[_-]?key|access[_-]?key|client[_-]?secret|email|e-mail|'
    r'phone|mobile|id[_-]?card)'
    r'(["\'\s:=]+)([^&\s"\',}<]+)'
)
_SENSITIVE_INPUT_PATTERN = re.compile(
    r'(?is)(<input\b(?=[^>]*(?:name|id|type)=["\']'
    r'(?:password|passwd|token|secret|api[_-]?key|access[_-]?key|'
    r'client[_-]?secret|email|e-mail|phone|mobile|id[_-]?card)'
    r'["\'])[^>]*\bvalue=["\'])'
    r'[^"\']*'
)
_MAX_PAGE_SOURCE_LENGTH = 1_000_000


def _sanitize_text(value):
    """对常见凭据和个人信息字段进行基础文本脱敏。"""
    if value is None:
        return ''
    sanitized_value = _SENSITIVE_INPUT_PATTERN.sub(
        r'\1***已脱敏***',
        str(value),
    )
    return _SENSITIVE_PATTERN.sub(r'\1\2***已脱敏***', sanitized_value)


def find_web_drivers(fixture_values):
    """从测试fixture对象中识别Selenium WebDriver，并去除重复对象。"""
    drivers = []
    driver_ids = set()
    for value in fixture_values:
        candidates = [
            getattr(value, 'driver', None),
            getattr(value, '_driver', None),
        ]
        browser_operator = getattr(value, 'browserOperator', None)
        if browser_operator is not None:
            candidates.append(getattr(browser_operator, '_driver', None))

        for driver in candidates:
            if driver is None or not hasattr(driver, 'get_screenshot_as_png'):
                continue
            if id(driver) not in driver_ids:
                driver_ids.add(id(driver))
                drivers.append(driver)
    return drivers


def attach_web_driver_diagnostics(driver, attachment_prefix='Web UI失败诊断'):
    """尽最大可能附加浏览器诊断，单个附件失败不会覆盖原始测试异常。"""
    errors = []

    try:
        allure.attach(
            driver.get_screenshot_as_png(),
            name='%s-截图' % attachment_prefix,
            attachment_type=allure.attachment_type.PNG,
        )
    except Exception as exc:
        errors.append('截图:%s' % exc)

    try:
        page_info = {
            'title': _sanitize_text(driver.title),
            'url': _sanitize_text(driver.current_url),
        }
        allure.attach(
            json.dumps(page_info, ensure_ascii=False, indent=2),
            name='%s-页面信息' % attachment_prefix,
            attachment_type=allure.attachment_type.JSON,
        )
    except Exception as exc:
        errors.append('页面信息:%s' % exc)

    try:
        page_source = _sanitize_text(driver.page_source)
        if len(page_source) > _MAX_PAGE_SOURCE_LENGTH:
            page_source = (
                page_source[:_MAX_PAGE_SOURCE_LENGTH]
                + '\n<!-- 页面源码已截断 -->'
            )
        allure.attach(
            page_source,
            name='%s-页面源码' % attachment_prefix,
            attachment_type=allure.attachment_type.HTML,
        )
    except Exception as exc:
        errors.append('页面源码:%s' % exc)

    try:
        browser_logs = driver.get_log('browser')
        if browser_logs:
            allure.attach(
                _sanitize_text(json.dumps(browser_logs, ensure_ascii=False, indent=2)),
                name='%s-浏览器控制台' % attachment_prefix,
                attachment_type=allure.attachment_type.JSON,
            )
    except Exception as exc:
        errors.append('浏览器控制台:%s' % exc)

    return errors
