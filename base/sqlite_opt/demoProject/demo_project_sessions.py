"""作用：提供demoProject sessions相关的基础封装。"""



from common.sqlalchemy_tools.sqlalchemy_sqlite_tool import SQLAlchemy_Sqlite_Tool

class DemoProject_Sessions(object):
    __instance = None
    __inited = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self,):
        if self.__inited is None:
            self.db_demoProject_session=SQLAlchemy_Sqlite_Tool('models/demoProject/demo_project.db').get_session()

        self.__inited = True
