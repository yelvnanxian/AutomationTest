#!/usr/bin/env python3
"""作用：提供static check模块相关功能。"""

import ast
import importlib.util
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {'.git', '.venv', '.appium', 'node_modules'}
REPORT_SCRIPTS = (
    ROOT / 'scripts' / 'reports' / 'generate_api_test_report.py',
    ROOT / 'scripts' / 'reports' / 'generate_web_ui_test_report.py',
    ROOT / 'scripts' / 'reports' / 'generate_app_ui_test_report.py',
    ROOT / 'common' / 'allure_report.py',
)
REQUIRED_PATHS = (
    ROOT / 'config' / 'pytest.ini',
    ROOT / 'config' / 'demoProject' / 'api_demo_project_release.conf',
    ROOT / 'scripts' / 'runners' / 'run_api_test.py',
    ROOT / 'scripts' / 'runners' / 'run_web_ui_test.py',
    ROOT / 'scripts' / 'runners' / 'run_app_ui_test.py',
    ROOT / 'scripts' / 'reports' / 'generate_api_test_report.py',
    ROOT / 'scripts' / 'reports' / 'generate_web_ui_test_report.py',
    ROOT / 'scripts' / 'reports' / 'generate_app_ui_test_report.py',
    ROOT / 'scripts' / 'services' / 'start_selenium.sh',
    ROOT / 'scripts' / 'test_env.sh',
    ROOT / 'requirements' / 'web.txt',
    ROOT / 'requirements' / 'mobile.txt',
    ROOT / 'requirements' / 'performance.txt',
    ROOT / 'requirements' / 'database.txt',
    ROOT / 'requirements' / 'dev.txt',
    ROOT / 'config' / 'ruff.toml',
)
ALLOWED_ROOT_FILES = {
    '.gitignore',
    'README.md',
    'package-lock.json',
    'package.json',
    'requirements.txt',
}


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


def check_python_file_names(errors):
    for path in ROOT.rglob('*.py'):
        if EXCLUDED_DIRS.intersection(path.relative_to(ROOT).parts):
            continue
        if path.name != path.name.lower():
            errors.append('%s Python文件名应使用snake_case小写格式' % path.relative_to(ROOT))


def check_root_layout(errors):
    output = subprocess.check_output(['git', 'ls-files'], cwd=ROOT, text=True)
    tracked_root_files = {
        path for path in output.splitlines()
        if path and '/' not in path
    }
    unexpected_files = sorted(tracked_root_files - ALLOWED_ROOT_FILES)
    for path in unexpected_files:
        errors.append('%s 应移动到职责明确的子目录' % path)


def check_ruff(errors):
    """使用Ruff检查会直接导致运行失败的高风险Python错误。"""
    if importlib.util.find_spec('ruff') is None:
        return False
    result = subprocess.run(
        [
            sys.executable,
            '-m',
            'ruff',
            'check',
            '--config',
            'config/ruff.toml',
            '.',
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        errors.append('Ruff高风险规则检查失败:\n%s' % result.stdout.strip())
    return True


def main():
    errors = []
    python_file_count = check_python_syntax(errors)
    check_report_shell_usage(errors)
    check_required_paths(errors)
    check_python_file_names(errors)
    check_root_layout(errors)
    ruff_enabled = check_ruff(errors)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    ruff_status = '已执行Ruff高风险规则' if ruff_enabled else '未安装Ruff，已跳过Ruff规则'
    print('静态检查通过：%s个Python文件，%s' % (python_file_count, ruff_status))
    return 0


if __name__ == '__main__':
    sys.exit(main())
