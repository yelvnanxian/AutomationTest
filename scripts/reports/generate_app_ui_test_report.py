# -*- coding:utf-8 -*-
"""作用：生成并启动app ui test report对应的Allure测试报告。"""

import argparse
import sys
from pathlib import Path

from base.read_report_config import Read_Report_Config
from common.allure_report import generate_and_open_report, validate_port
from common.datetime_tool import DateTimeTool
from common.network import Network


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-sp', '--start_port', help='生成报告使用的开始端口，多份报告每次加1', type=int)
    args = parser.parse_args()

    report_config = Read_Report_Config().report_config
    configured_port = report_config.app_ui_start_port
    start_port = validate_port(args.start_port if args.start_port is not None else configured_port)
    report_data_dirs = sorted(Path('output/app_ui').glob('*/*/report_data'))
    if not report_data_dirs:
        print('%s没有找到可生成的App UI报告数据' % DateTimeTool.getNowTime())
        return 1
    if start_port + len(report_data_dirs) - 1 > 65535:
        raise ValueError('报告数量超过起始端口可用范围')

    test_time = DateTimeTool.getNowTime('%Y_%m_%d_%H_%M_%S_%f')
    for index, report_data_dir in enumerate(report_data_dirs):
        port = start_port + index
        report_dir = report_data_dir.parent
        report_output_dir = report_dir / 'report' / ('app_ui_report_%s' % test_time)
        log_file = Path('logs') / ('allure_app_ui_%s_%s.log' % (index, port))
        print('%s生成报告%s,使用端口%s' % (DateTimeTool.getNowTime(), report_output_dir, port))
        process_id = generate_and_open_report(
            report_data_dir,
            report_output_dir,
            port,
            log_file,
            report_config.language,
            report_config.history_keep_count,
            'app_ui_report_',
        )
        print('%s报告地址:http://%s:%s/，进程id:%s' % (
            DateTimeTool.getNowTime(), Network.get_local_ip(), port, process_id
        ))
    return 0


if __name__ == '__main__':
    sys.exit(main())
