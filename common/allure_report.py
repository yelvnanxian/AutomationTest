"""作用：提供allure report相关的通用工具能力。"""

import json
import os
import re
import shutil
import shlex
import signal
import socket
import subprocess
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ALLURE_RUNTIME_DIR = PROJECT_ROOT / 'output' / 'runtime' / 'allure'


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


def _is_process_running(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _pid_file(port, runtime_dir=ALLURE_RUNTIME_DIR):
    return Path(runtime_dir) / ('allure_%s.pid' % validate_port(port))


def _read_pid_record(pid_path, expected_port):
    """读取新版JSON或旧版纯PID记录，并验证记录端口。"""
    record_text = pid_path.read_text(encoding='utf-8').strip()
    try:
        record = json.loads(record_text)
    except json.JSONDecodeError:
        record = {'pid': int(record_text), 'port': expected_port}
    if isinstance(record, int):
        record = {'pid': record, 'port': expected_port}
    if not isinstance(record, dict):
        raise ValueError('PID记录格式不正确')

    pid = int(record['pid'])
    record_port = validate_port(record.get('port', expected_port))
    if record_port != expected_port:
        raise ValueError('PID记录端口与目标端口不一致')
    return pid


def _write_pid_record(pid_path, process, port, report_output_path):
    """保存足以校验Allure服务身份的运行信息。"""
    record = {
        'pid': int(process.pid),
        'port': validate_port(port),
        'report_path': str(Path(report_output_path).resolve()),
        'started_at': time.time(),
    }
    pid_path.write_text(
        json.dumps(record, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )


def _get_process_command(pid):
    """跨平台读取进程命令；无法确认身份时返回空字符串。"""
    if os.name == 'nt':
        command = [
            'powershell',
            '-NoProfile',
            '-Command',
            '(Get-CimInstance Win32_Process -Filter "ProcessId=%s").CommandLine' % pid,
        ]
    else:
        command = ['ps', '-p', str(pid), '-o', 'command=']
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return ''
    if result.returncode != 0:
        return ''
    return result.stdout.strip()


def _is_expected_allure_process(process_command, port):
    """同时校验Allure入口、open子命令和目标端口，避免PID复用误杀。"""
    if not process_command:
        return False
    try:
        tokens = shlex.split(process_command, posix=os.name != 'nt')
    except ValueError:
        return False
    normalized_tokens = [token.strip('"\'').lower() for token in tokens]
    has_allure_entry = any(
        token == 'io.qameta.allure.commandline'
        or Path(token).name in {'allure', 'allure.bat', 'allure.cmd'}
        for token in normalized_tokens
    )
    if not has_allure_entry or 'open' not in normalized_tokens:
        return False

    expected_port = str(validate_port(port))
    for index, token in enumerate(normalized_tokens):
        if token in {'-p', '--port'} and index + 1 < len(normalized_tokens):
            return normalized_tokens[index + 1] == expected_port
        if token.startswith(('-p=', '--port=')):
            return token.split('=', 1)[1] == expected_port
    return False


def stop_report_service(port, runtime_dir=ALLURE_RUNTIME_DIR):
    """只停止本项目PID文件记录的Allure服务，避免误杀其他Java进程。"""
    port = validate_port(port)
    pid_path = _pid_file(port, runtime_dir)
    if not pid_path.is_file():
        return False

    try:
        pid = _read_pid_record(pid_path, port)
    except (KeyError, OSError, TypeError, ValueError):
        pid_path.unlink(missing_ok=True)
        return False

    if not _is_process_running(pid):
        pid_path.unlink(missing_ok=True)
        return False

    process_command = _get_process_command(pid)
    if not _is_expected_allure_process(process_command, port):
        pid_path.unlink(missing_ok=True)
        return False

    os.kill(pid, signal.SIGTERM)
    for _ in range(30):
        if not _is_process_running(pid):
            pid_path.unlink(missing_ok=True)
            return True
        time.sleep(0.1)
    return False


def cleanup_report_history(
    report_parent_dir,
    report_name_prefix,
    keep_count,
    protected_paths=None,
):
    """只清理指定前缀的旧报告目录，并返回已删除目录列表。"""
    keep_count = int(keep_count)
    if keep_count < 0:
        raise ValueError('报告保留数量不能小于0')
    if keep_count == 0:
        return []

    report_parent_path = Path(report_parent_dir)
    if not report_parent_path.is_dir():
        return []
    protected = {
        Path(path).resolve()
        for path in (protected_paths or ())
    }
    report_dirs = sorted(
        (
            path for path in report_parent_path.iterdir()
            if path.is_dir() and path.name.startswith(report_name_prefix)
        ),
        key=lambda path: (path.stat().st_mtime_ns, path.name),
        reverse=True,
    )
    removed_dirs = []
    for report_dir in report_dirs[keep_count:]:
        if report_dir.resolve() in protected:
            continue
        shutil.rmtree(report_dir)
        removed_dirs.append(report_dir)
    return removed_dirs


def generate_and_open_report(
    report_data_dir,
    report_output_dir,
    port,
    log_file,
    language='zh',
    history_keep_count=0,
    report_name_prefix=None,
):
    """Generate and serve an Allure report without invoking a shell."""
    port = validate_port(port)
    stop_report_service(port)
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

    if report_name_prefix:
        cleanup_report_history(
            report_output_path.parent,
            report_name_prefix,
            history_keep_count,
            protected_paths=(report_output_path,),
        )

    # Allure根据HTML的lang属性初始化界面语言，生成后设置为配置中的默认语言。
    index_path = report_output_path / 'index.html'
    if index_path.is_file() and language:
        index_html = index_path.read_text(encoding='utf-8')
        index_html = re.sub(
            r'(<html\b[^>]*\blang=")[^"]*(")',
            r'\g<1>%s\2' % language,
            index_html,
            count=1,
        )
        index_path.write_text(index_html, encoding='utf-8')

    creationflags = 0
    popen_kwargs = {'start_new_session': True}
    if os.name == 'nt':
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        popen_kwargs = {'creationflags': creationflags}

    # 同一测试类型和端口只保留最新一次服务日志，避免产生大量时间戳文件。
    with log_path.open('wb') as log_stream:
        process = subprocess.Popen(
            ['allure', 'open', '-p', str(port), str(report_output_path)],
            stdout=log_stream,
            stderr=subprocess.STDOUT,
            **popen_kwargs,
        )
    pid_path = _pid_file(port)
    pid_path.parent.mkdir(parents=True, exist_ok=True)
    _write_pid_record(pid_path, process, port, report_output_path)
    return process.pid
