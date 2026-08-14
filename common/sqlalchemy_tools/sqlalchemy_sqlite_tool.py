"""作用：提供sqlalchemy sqlite tool相关的通用工具能力。"""

#
# sqlalchemy_sqlite_tool.py
# @description
# @created 2022-07-25T19:11:48.078Z+08:00
# @last-modified 2022-07-25T19:58:05.872Z+08:00

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

class SQLAlchemy_Sqlite_Tool:
    def __init__(self,file_path,encoding='utf8',echo=False) -> None:
        self.url='sqlite:///%s'%(file_path)
        self.encoding=encoding
        self.echo=echo

    def get_session(self):
        engine=create_engine(url=self.url,encoding=self.encoding,echo=self.echo)
        # 线程安全
        return scoped_session(sessionmaker(bind=engine))
