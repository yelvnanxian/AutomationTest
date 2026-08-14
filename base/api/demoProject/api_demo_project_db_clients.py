# -*- coding:utf-8 -*-
"""作用：提供api demoProject db clients相关的基础封装。"""

from base.api.demoProject.api_demo_project_read_config import API_DemoProject_Read_Config

class API_DemoProject_DB_Clients(object):
    __instance=None
    __inited=None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance=object.__new__(cls)
        return cls.__instance

    def __init__(self):
        if self.__inited is None:
            self._demo_project_config = API_DemoProject_Read_Config().config
            # self.mysqlclient=MysqlClient('host','port','username','password','dbname')
            # self.oracleclient = OracleClient('host', 'port', 'username', 'password', 'dbname')
            self.__inited=True
