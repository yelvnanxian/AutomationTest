#!/usr/bin/env python3
"""作用：提供static check模块相关功能。"""

import ast
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {'.git', '.venv', '.appium', 'node_modules'}
REPORT_SCRIPTS = (
    ROOT / 'generate_api_test_report.py',
    ROOT / 'generate_web_ui_test_report.py',
    ROOT / 'generate_app_ui_test_report.py',
    ROOT / 'common' / 'allure_report.py',
)
REQUIRED_PATHS = (
    ROOT / 'config' / 'demoProject' / 'api_demoProject_release.conf',
    ROOT / 'generate_api_test_report.py',
    ROOT / 'generate_web_ui_test_report.py',
    ROOT / 'generate_app_ui_test_report.py',
)


def check_python_syntax(errors):
    python_files = sorted(
        path for path in ROOT.rglob('*.py')
        if not EXCLUDED_DIRS.intersection(path.relative_to(ROOT).parts)
    )
    for path in python_files:
        try:
            compile(path.read_bytes(), str(path), 'exec')
        except Exception as exc:
            errors.append('%s: %s' % (path.relative_to(ROOT), exc))
    return len(python_files)


def check_report_shell_usage(errors):
    for path in REPORT_SCRIPTS:
        tree = ast.parse(path.read_bytes(), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            for keyword in node.keywords:
                if keyword.arg == 'shell' and isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                    errors.append('%s:%s 禁止在报告脚本中使用shell=True' % (
                        path.relative_to(ROOT), node.lineno
                    ))


def check_required_paths(errors):
    for path in REQUIRED_PATHS:
        if not path.is_file():
            errors.append('缺少必要文件:%s' % path.relative_to(ROOT))


def main():
    errors = []
    python_file_count = check_python_syntax(errors)
    check_report_shell_usage(errors)
    check_required_paths(errors)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print('静态检查通过：%s个Python文件' % python_file_count)
    return 0


if __name__ == '__main__':
    sys.exit(main())
