"""作用：提供allure report相关的通用工具能力。"""

import os
import socket
import subprocess
from pathlib import Path


def validate_port(value):
    """Return a validated TCP port as an integer."""
    try:
        port = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError('端口必须是整数:%s' % value) from exc
    if not 1 <= port <= 65535:
        raise ValueError('端口必须在1到65535之间:%s' % value)
    return port


def ensure_port_available(port):
    """Fail without terminating an unrelated process when a port is occupied."""
    port = validate_port(port)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(('0.0.0.0', port))
        except OSError as exc:
            raise RuntimeError('端口%s已被占用，请指定其他端口' % port) from exc


def generate_and_open_report(report_data_dir, report_output_dir, port, log_file):
    """Generate and serve an Allure report without invoking a shell."""
    port = validate_port(port)
    ensure_port_available(port)

    report_data_path = Path(report_data_dir)
    report_output_path = Path(report_output_dir)
    log_path = Path(log_file)
    if not report_data_path.is_dir():
        raise FileNotFoundError('测试报告数据目录不存在:%s' % report_data_path)

    report_output_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ['allure', 'generate', str(report_data_path), '-o', str(report_output_path)],
        check=True,
    )

    creationflags = 0
    popen_kwargs = {'start_new_session': True}
    if os.name == 'nt':
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        popen_kwargs = {'creationflags': creationflags}

    with log_path.open('ab') as log_stream:
        process = subprocess.Popen(
            ['allure', 'open', '-p', str(port), str(report_output_path)],
            stdout=log_stream,
            stderr=subprocess.STDOUT,
            **popen_kwargs,
        )
    return process.pid
