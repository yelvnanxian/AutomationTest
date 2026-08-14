# -*- coding:utf-8 -*-
"""作用：读取并解析web ui demoProject config所需的配置。"""

from pojo.web_ui.demoProject.demo_project_config import DemoProjectConfig
import configparser as ConfigParser

class WEB_UI_DemoProject_Read_Config(object):
    __instance=None
    __inited=None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance=object.__new__(cls)
        return cls.__instance

    def __init__(self):
        if self.__inited is None:
            self.config=self._readConfig('config/demoProject/web_ui_demo_project.conf')
            self.__inited=True

    def _readConfig(self, configFile):
        config = ConfigParser.ConfigParser()
        config.read(configFile,encoding='utf-8')
        demo_project_config = DemoProjectConfig()
        demo_project_config.web_host = config.get('servers','web_host')
        demo_project_config.init=config.get('isInit','init')
        return demo_project_config
