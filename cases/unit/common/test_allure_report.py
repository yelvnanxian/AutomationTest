"""作用：验证Allure报告历史清理和PID进程管理不会误删或误杀。"""

import json
import signal

import pytest

from common.allure_report import cleanup_report_history
from common.allure_report import stop_report_service


pytestmark = pytest.mark.unit


def test_cleanup_report_history_only_removes_matching_old_directories(tmp_path):
    """验证只保留指定前缀的最新报告，不影响其他目录和文件。"""
    first = tmp_path / 'web_ui_report_001'
    second = tmp_path / 'web_ui_report_002'
    third = tmp_path / 'web_ui_report_003'
    unrelated = tmp_path / 'manual_backup'
    for path in (first, second, third, unrelated):
        path.mkdir()
    (tmp_path / 'README.txt').write_text('keep', encoding='utf-8')
    first.touch()
    second.touch()
    third.touch()

    removed = cleanup_report_history(tmp_path, 'web_ui_report_', 2)

    assert len(removed) == 1
    assert sum(path.is_dir() for path in (first, second, third)) == 2
    assert unrelated.is_dir()
    assert (tmp_path / 'README.txt').is_file()


def test_cleanup_report_history_never_removes_protected_current_report(tmp_path):
    """验证当前报告即使时间较旧，也不会被历史清理误删。"""
    current_report = tmp_path / 'web_ui_report_current'
    newer_report = tmp_path / 'web_ui_report_newer'
    current_report.mkdir()
    newer_report.mkdir()

    removed = cleanup_report_history(
        tmp_path,
        'web_ui_report_',
        1,
        protected_paths=(current_report,),
    )

    assert current_report.is_dir()
    assert removed == []


def test_stop_report_service_only_terminates_verified_allure_process(
    tmp_path,
    monkeypatch,
):
    """验证PID对应命令确为Allure服务时才发送终止信号。"""
    pid_path = tmp_path / 'allure_9527.pid'
    pid_path.write_text('12345', encoding='utf-8')
    running_states = iter([True, False])
    killed_processes = []

    monkeypatch.setattr(
        'common.allure_report._is_process_running',
        lambda pid: next(running_states),
    )
    monkeypatch.setattr(
        'common.allure_report._get_process_command',
        lambda pid: 'java io.qameta.allure.CommandLine open -p 9527',
    )
    monkeypatch.setattr(
        'common.allure_report.os.kill',
        lambda pid, signal_number: killed_processes.append((pid, signal_number)),
    )

    stopped = stop_report_service(9527, runtime_dir=tmp_path)

    assert stopped is True
    assert killed_processes == [(12345, signal.SIGTERM)]
    assert not pid_path.exists()


def test_stop_report_service_does_not_kill_unrelated_process(tmp_path, monkeypatch):
    """验证PID复用为其他程序时只清理过期记录，不终止该进程。"""
    pid_path = tmp_path / 'allure_9527.pid'
    pid_path.write_text('12345', encoding='utf-8')
    killed_processes = []

    monkeypatch.setattr(
        'common.allure_report._is_process_running',
        lambda pid: True,
    )
    monkeypatch.setattr(
        'common.allure_report._get_process_command',
        lambda pid: 'python local_server.py',
    )
    monkeypatch.setattr(
        'common.allure_report.os.kill',
        lambda pid, signal_number: killed_processes.append((pid, signal_number)),
    )

    stopped = stop_report_service(9527, runtime_dir=tmp_path)

    assert stopped is False
    assert killed_processes == []
    assert not pid_path.exists()


def test_stop_report_service_does_not_kill_allure_on_another_port(
    tmp_path,
    monkeypatch,
):
    """验证PID复用为其他端口的Allure服务时不会误杀。"""
    pid_path = tmp_path / 'allure_9527.pid'
    pid_path.write_text(
        json.dumps({'pid': 12345, 'port': 9527}),
        encoding='utf-8',
    )
    killed_processes = []
    monkeypatch.setattr('common.allure_report._is_process_running', lambda pid: True)
    monkeypatch.setattr(
        'common.allure_report._get_process_command',
        lambda pid: 'java io.qameta.allure.CommandLine open -p 9080',
    )
    monkeypatch.setattr(
        'common.allure_report.os.kill',
        lambda pid, signal_number: killed_processes.append((pid, signal_number)),
    )

    stopped = stop_report_service(9527, runtime_dir=tmp_path)

    assert stopped is False
    assert killed_processes == []
    assert not pid_path.exists()


def test_stop_report_service_keeps_pid_record_when_process_does_not_stop(
    tmp_path,
    monkeypatch,
):
    """验证进程未退出时返回失败并保留记录，避免错误报告成功。"""
    pid_path = tmp_path / 'allure_9527.pid'
    pid_path.write_text('12345', encoding='utf-8')
    monkeypatch.setattr('common.allure_report._is_process_running', lambda pid: True)
    monkeypatch.setattr(
        'common.allure_report._get_process_command',
        lambda pid: 'java io.qameta.allure.CommandLine open -p 9527',
    )
    monkeypatch.setattr('common.allure_report.os.kill', lambda *args: None)
    monkeypatch.setattr('common.allure_report.time.sleep', lambda seconds: None)

    stopped = stop_report_service(9527, runtime_dir=tmp_path)

    assert stopped is False
    assert pid_path.is_file()
