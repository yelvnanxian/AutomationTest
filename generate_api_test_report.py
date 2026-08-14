# -*- coding:utf-8 -*-
"""作用：生成并启动api test report对应的Allure测试报告。"""

import argparse
import sys

from base.read_report_config import Read_Report_Config
from common.allure_report import generate_and_open_report, validate_port
from common.dateTimeTool import DateTimeTool
from common.network import Network


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', help='生成报告使用的端口', type=int)
    args = parser.parse_args()

    configured_port = Read_Report_Config().report_config.api_port
    port = validate_port(args.port if args.port is not None else configured_port)
    test_time = DateTimeTool.getNowTime('%Y_%m_%d_%H_%M_%S_%f')
    report_output_dir = 'output/api/report/api_report_%s' % test_time
    log_file = 'logs/generate_api_test_report_%s.log' % test_time

    print('%s生成报告,使用端口%s' % (DateTimeTool.getNowTime(), port))
    process_id = generate_and_open_report(
        'output/api/report_data', report_output_dir, port, log_file
    )
    print('%s报告地址:http://%s:%s/' % (DateTimeTool.getNowTime(), Network.get_local_ip(), port))
    print('%sAllure服务进程id:%s' % (DateTimeTool.getNowTime(), process_id))
    return 0


if __name__ == '__main__':
    sys.exit(main())
