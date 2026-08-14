# -*- coding:utf-8 -*-
"""作用：生成并启动web ui test report对应的Allure测试报告。"""

import argparse
import sys
from pathlib import Path

from base.read_report_config import Read_Report_Config
from common.allure_report import generate_and_open_report, validate_port
from common.dateTimeTool import DateTimeTool
from common.network import Network


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', '--ie_port', help='ie生成报告使用的端口', type=int)
    parser.add_argument('-cp', '--chrome_port', help='chrome生成报告使用的端口', type=int)
    parser.add_argument('-fp', '--firefox_port', help='firefox生成报告使用的端口', type=int)
    args = parser.parse_args()

    report_config = Read_Report_Config().report_config
    browser_reports = [
        ('ie', args.ie_port, report_config.web_ui_ie_port),
        ('chrome', args.chrome_port, report_config.web_ui_chrome_port),
        ('firefox', args.firefox_port, report_config.web_ui_firefox_port),
    ]
    test_time = DateTimeTool.getNowTime('%Y_%m_%d_%H_%M_%S_%f')
    generated_count = 0

    for browser, requested_port, configured_port in browser_reports:
        report_data_dir = Path('output/web_ui') / browser / 'report_data'
        if not report_data_dir.is_dir():
            print('%s跳过%s报告，未找到测试数据目录:%s' % (
                DateTimeTool.getNowTime(), browser, report_data_dir
            ))
            continue
        port = validate_port(requested_port if requested_port is not None else configured_port)
        report_output_dir = Path('output/web_ui') / browser / 'report' / ('web_ui_report_%s' % test_time)
        log_file = Path('logs') / ('generate_web_ui_test_%s_report_%s.log' % (browser, test_time))
        print('%s生成%s报告,使用端口%s' % (DateTimeTool.getNowTime(), browser, port))
        process_id = generate_and_open_report(report_data_dir, report_output_dir, port, log_file)
        print('%s%s报告地址:http://%s:%s/，进程id:%s' % (
            DateTimeTool.getNowTime(), browser, Network.get_local_ip(), port, process_id
        ))
        generated_count += 1

    if generated_count == 0:
        print('%s没有找到可生成的Web UI报告数据' % DateTimeTool.getNowTime())
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
