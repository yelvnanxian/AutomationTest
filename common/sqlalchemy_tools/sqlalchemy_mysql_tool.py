"""作用：提供兼容SQLAlchemy 2.x的MySQL连接池和会话管理工具。"""

from sqlalchemy import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker


class SQLAlchemyMysqlTool:
    """创建可安全编码账号信息的MySQL Engine和线程隔离Session。"""

    def __init__(
        self,
        host=None,
        port=None,
        username=None,
        password=None,
        db=None,
        driver_type='pymysql',
        charset=None,
        encoding=None,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=1800,
        **engine_kwargs,
    ):
        if charset is not None and encoding is not None and charset != encoding:
            raise ValueError('charset与encoding不能设置为不同值')
        effective_charset = charset or encoding or 'utf8mb4'
        self.encoding = effective_charset
        self.url = URL.create(
            drivername='mysql+%s' % driver_type,
            username=username,
            password=password,
            host=host,
            port=int(port) if port is not None else None,
            database=db,
            query={'charset': effective_charset},
        )
        self.engine = create_engine(
            self.url,
            echo=echo,
            pool_pre_ping=pool_pre_ping,
            pool_recycle=pool_recycle,
            **engine_kwargs,
        )
        self._session_factory = scoped_session(
            sessionmaker(bind=self.engine, expire_on_commit=False)
        )

    def get_session(self):
        """返回当前线程对应的SQLAlchemy Session。"""
        return self._session_factory()

    def close(self):
        """关闭当前线程Session并释放连接池。"""
        self._session_factory.remove()
        self.engine.dispose()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class SQLAlchemy_Mysql_Tool(SQLAlchemyMysqlTool):
    """兼容旧类名、encoding参数和scoped_session返回类型。"""

    def __init__(
        self,
        host=None,
        port=None,
        username=None,
        password=None,
        db=None,
        driver_type='pymysql',
        encoding='utf8',
        echo=False,
        **engine_kwargs,
    ):
        charset = engine_kwargs.pop('charset', None)
        super().__init__(
            host=host,
            port=port,
            username=username,
            password=password,
            db=db,
            driver_type=driver_type,
            charset=charset,
            encoding=encoding,
            echo=echo,
            **engine_kwargs,
        )

    def get_session(self):
        """保持旧接口返回scoped_session代理。"""
        return self._session_factory
