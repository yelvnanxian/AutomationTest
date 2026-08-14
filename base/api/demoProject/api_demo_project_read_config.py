"""作用：读取并解析api demoProject config所需的配置。"""

from common.file_tool import FileTool
from pojo.api.demoProject.demo_project_config import DemoProjectConfig
import configparser as ConfigParser
import os

class API_DemoProject_Read_Config(object):
    __instance=None
    __inited=None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance=object.__new__(cls)
        return cls.__instance


    def __init__(self,config_file_path:str=None,env:str=None):
        """优先取传参配置文件，再取传参环境，最后去运行指定的环境

        Args:
            config_file_path (str, optional): 如果指定该参数，env参数被忽略. Defaults to None.
            env (str, optional): _description_. Defaults to None.
        """
        if self.__inited is None:
            if config_file_path is None:
                if env is None:
                    if os.path.exists('config/tmp/env.json'):
                        env_info=FileTool.readJsonFromFile('config/tmp/env.json')
                        env=env_info['env']
                    else:
                        env='test'
                if env.lower()=='test':
                    config_file_path='config/demoProject/api_demo_project_test.conf'
                elif env.lower()=='release':
                    config_file_path='config/demoProject/api_demo_project_release.conf'
                else:
                    raise ValueError('不支持的环境:%s，仅支持test或release' % env)
            if not os.path.isfile(config_file_path):
                raise FileNotFoundError('API配置文件不存在:%s' % config_file_path)
            self.config=self._readConfig(config_file_path)
            self.env=env

            self.__inited=True

    def _readConfig(self,configFile):
        config = ConfigParser.ConfigParser()
        loaded_files = config.read(configFile,encoding='utf-8')
        if not loaded_files:
            raise FileNotFoundError('API配置文件无法读取:%s' % configFile)
        demo_project_config=DemoProjectConfig()
        demo_project_config.url=config.get('servers','url')
        demo_project_config.init=config.get('isInit','init')
        return demo_project_config
