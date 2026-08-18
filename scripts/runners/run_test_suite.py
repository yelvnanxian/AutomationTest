# -*- coding:utf-8 -*-
"""作用：统一执行指定demo和测试用例，并按需生成Allure报告。"""

import argparse
import os
import signal
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CASES_ROOT = PROJECT_ROOT / 'cases'

DEMO_ALIASES = {
    'saucedemo': Path('web_ui/demoProject'),
    'demoproject': Path('web_ui/demoProject'),
    'web_ui': Path('web_ui'),
    'httpbin': Path('api/httpbin'),
    'api': Path('api'),
}

REPORT_SPECS = {
    'web_ui': {
        'data_dir': PROJECT_ROOT / 'output' / 'web_ui' / 'chrome' / 'report_data',
        'default_port': 9527,
        'module': 'scripts.reports.generate_web_ui_test_report',
        'port_arg': '--chrome_port',
    },
    'api': {
        'data_dir': PROJECT_ROOT / 'output' / 'api' / 'report_data',
        'default_port': 9080,
        'module': 'scripts.reports.generate_api_test_report',
        'port_arg': '--port',
    },
}


def parse_args():
    parser = argparse.ArgumentParser(
        description='统一执行AutomationTest测试用例并生成Allure报告。'
    )
    parser.add_argument(
        '--demo',
        default='saucedemo',
        help='选择demo目录或别名，例如：saucedemo、httpbin、web_ui、api。',
    )
    parser.add_argument(
        '--tests',
        default='all',
        help='选择测试用例：all表示全部，也可传逗号分隔的文件名或测试关键字。',
    )
    parser.add_argument(
        '--include-failure-demo',
        action='store_true',
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        '--port',
        type=int,
        default=None,
        help='Allure报告端口，默认Web UI为9527、API为9080。',
    )
    parser.add_argument(
        '--no-report',
        action='store_true',
        help='只执行测试，不生成Allure报告。',
    )
    parser.add_argument(
        '--keep-report-data',
        action='store_true',
        help='保留已有Allure原始数据，不在执行前清理。',
    )
    return parser.parse_args()


def resolve_demo_path(demo):
    demo_path = DEMO_ALIASES.get(demo, Path(demo))
    resolved_path = (CASES_ROOT / demo_path).resolve()
    if not resolved_path.is_dir() or CASES_ROOT not in resolved_path.parents:
        raise ValueError('找不到demo目录：%s（应位于cases目录下）' % demo)
    return resolved_path


def build_test_args(demo, tests):
    demo_path = resolve_demo_path(demo)
    if demo == 'saucedemo':
        test_files = sorted(demo_path.glob('test_saucedemo_*.py'))
    else:
        test_files = sorted(demo_path.rglob('test_*.py'))

    test_tokens = [token.strip() for token in tests.split(',') if token.strip()]
    if tests.lower() == 'all' or not test_tokens:
        selected_files = test_files
        keyword_expression = None
    else:
        file_tokens = {
            token.lower()
            for token in test_tokens
            if any(token.lower() in path.stem.lower() for path in test_files)
        }
        selected_files = [
            path for path in test_files
            if any(token in path.stem.lower() for token in file_tokens)
        ]
        keyword_tokens = [token for token in test_tokens if token.lower() not in file_tokens]
        keyword_expression = ' or '.join(keyword_tokens) if keyword_tokens else None
        if not selected_files:
            selected_files = test_files

    test_args = [str(path.relative_to(PROJECT_ROOT)) for path in selected_files]
    if keyword_expression and selected_files:
        test_args.extend(['-k', keyword_expression])

    return test_args


def resolve_test_type(demo_path):
    """根据cases下的一级目录识别测试类型。"""
    relative_path = demo_path.relative_to(CASES_ROOT)
    test_type = relative_path.parts[0]
    if test_type not in REPORT_SPECS:
        raise ValueError('统一入口暂不支持%s类型的报告生成' % test_type)
    return test_type


def clean_report_data(report_data_dir):
    if report_data_dir.exists():
        shutil.rmtree(report_data_dir)
    report_data_dir.mkdir(parents=True, exist_ok=True)
    print('已清理Allure原始数据：%s' % report_data_dir, flush=True)


def release_allure_port(port):
    """只停止本项目启动的Allure服务，避免固定端口重复运行冲突。"""
    try:
        listener_result = subprocess.run(
            ['lsof', '-tiTCP:%s' % port, '-sTCP:LISTEN'],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return

    for pid_text in listener_result.stdout.split():
        pid = int(pid_text)
        process_result = subprocess.run(
            ['ps', '-p', str(pid), '-o', 'command='],
            capture_output=True,
            text=True,
            check=False,
        )
        process_command = process_result.stdout.strip()
        expected_command = 'io.qameta.allure.CommandLine open -p %s' % port
        if expected_command not in process_command:
            raise RuntimeError('端口%s已被其他进程占用:%s' % (port, pid))
        os.kill(pid, signal.SIGTERM)


def run():
    args = parse_args()

    try:
        demo_path = resolve_demo_path(args.demo)
        test_type = resolve_test_type(demo_path)
        test_args = build_test_args(args.demo, args.tests)
    except ValueError as error:
        print('参数错误：%s' % error)
        return 2
    if not test_args:
        print('未找到可执行的测试文件。')
        return 2

    report_spec = REPORT_SPECS[test_type]
    report_data_dir = report_spec['data_dir']
    report_port = args.port or report_spec['default_port']
    if not args.keep_report_data:
        clean_report_data(report_data_dir)

    pytest_command = [
        sys.executable,
        '-m',
        'pytest',
        '-c',
        'config/pytest.ini',
        '-v',
        '-s',
        '--alluredir=%s' % report_data_dir,
    ] + test_args
    print('执行命令：%s' % ' '.join(pytest_command), flush=True)
    test_result = subprocess.run(pytest_command, cwd=PROJECT_ROOT).returncode

    report_result = 0
    if not args.no_report:
        release_allure_port(report_port)
        report_command = [
            sys.executable,
            '-m',
            report_spec['module'],
            report_spec['port_arg'],
            str(report_port),
        ]
        print('生成报告命令：%s' % ' '.join(report_command), flush=True)
        report_result = subprocess.run(report_command, cwd=PROJECT_ROOT).returncode

    return test_result if test_result != 0 else report_result


if __name__ == '__main__':
    sys.exit(run())
