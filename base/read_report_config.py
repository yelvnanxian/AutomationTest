"""作用：读取并解析report config所需的配置。"""

import configparser as ConfigParser
from pathlib import Path

from pojo.report_config import Report_Config


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT_CONFIG = PROJECT_ROOT / 'config' / 'report.conf'


class Read_Report_Config(object):
    __instance = None
    __inited = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        if self.__inited is None:
            self.report_config = self._readConfig(DEFAULT_REPORT_CONFIG)
            self.__inited = True

    def _readConfig(self, configFile):
        config_path = Path(configFile)
        if not config_path.is_file():
            raise FileNotFoundError('报告配置文件不存在:%s' % config_path)
        configParser = ConfigParser.ConfigParser()
        loaded_files = configParser.read(config_path, encoding='utf-8')
        if not loaded_files:
            raise FileNotFoundError('报告配置文件无法读取:%s' % config_path)
        report_config = Report_Config()
        report_config.history_keep_count = configParser.getint(
            'common', 'history_keep_count', fallback=0
        )
        report_config.language = configParser.get('web_ui', 'language', fallback='zh')
        report_config.api_port = configParser.get('api', 'api_port')
        report_config.app_ui_start_port = configParser.get(
            'app_ui', 'app_ui_start_port'
        )
        report_config.web_ui_ie_port = configParser.get('web_ui', 'web_ui_ie_port')
        report_config.web_ui_firefox_port = configParser.get(
            'web_ui', 'web_ui_firefox_port'
        )
        report_config.web_ui_chrome_port = configParser.get(
            'web_ui', 'web_ui_chrome_port'
        )
        return report_config
