# -*- coding:utf8 -*-
"""作用：封装api demoProject client客户端的连接和访问能力。"""

from base.api.demoProject.api_demo_project_read_config import API_DemoProject_Read_Config
from base.api.demoProject.api_demo_project_db_clients import API_DemoProject_DB_Clients
from common.http_client.request_client import DoRequest

class API_DemoProject_Client(object):
    __instance=None
    __inited=None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance=object.__new__(cls)
        return cls.__instance

    def __init__(self,config_file_path:str=None,env:str=None):
        if self.__inited is None:
            self.demo_project_config=API_DemoProject_Read_Config(config_file_path,env).config
            self.demoProjectDBClients=API_DemoProject_DB_Clients()
            self.doRequest=DoRequest(self.demo_project_config.url)

            self.__inited=True
